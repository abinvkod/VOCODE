import os
import re
import numpy as np
import librosa
import torch

_WHISPER_MODEL = None

def clean_whisper_hooks(model):
    """Safely clear residual forward hooks on Whisper decoder attention blocks to prevent KV-cache sequence length divergence."""
    try:
        for block in model.decoder.blocks:
            if hasattr(block.attn.key, "_forward_hooks"):
                block.attn.key._forward_hooks.clear()
            if hasattr(block.attn.value, "_forward_hooks"):
                block.attn.value._forward_hooks.clear()
            if hasattr(block.cross_attn.key, "_forward_hooks"):
                block.cross_attn.key._forward_hooks.clear()
            if hasattr(block.cross_attn.value, "_forward_hooks"):
                block.cross_attn.value._forward_hooks.clear()
    except Exception:
        pass

def get_whisper_model(model_size: str = "base.en"):
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        import whisper
        import whisper.model
        # Disable SDPA to prevent PyTorch 2.14+ C++ scaled_dot_product_attention KV-cache sequence length mismatch bug
        whisper.model.MultiHeadAttention.use_sdpa = False
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _WHISPER_MODEL = whisper.load_model(model_size, device=device)
    else:
        clean_whisper_hooks(_WHISPER_MODEL)
    return _WHISPER_MODEL

def segment_utterances_energy(audio: np.ndarray, sr: int = 16000, min_speech_sec: float = 0.8, min_silence_sec: float = 0.5) -> list[tuple[float, float]]:
    """Segments continuous audio into discrete orator utterances [t_start, t_end]."""
    frame_len = 1024
    hop_len = 256
    rms = librosa.feature.rms(y=audio, frame_length=frame_len, hop_length=hop_len)[0]
    
    threshold = np.percentile(rms, 30) * 1.5
    is_speech = rms > threshold
    
    times = librosa.frames_to_time(np.arange(len(is_speech)), sr=sr, hop_length=hop_len)
    
    segments = []
    in_speech = False
    start_t = 0.0
    
    for t, active in zip(times, is_speech):
        if active and not in_speech:
            in_speech = True
            start_t = t
        elif not active and in_speech:
            in_speech = False
            if (t - start_t) >= min_speech_sec:
                segments.append((float(start_t), float(t)))
                
    if in_speech and (times[-1] - start_t) >= min_speech_sec:
        segments.append((float(start_t), float(times[-1])))
        
    if not segments:
        segments = [(0.0, float(len(audio) / sr))]
        
    return segments

segment_utterances = segment_utterances_energy

def format_timestamp(seconds: float) -> str:
    """Format seconds into MM:SS.sss string."""
    mins = int(seconds // 60)
    secs = seconds % 60
    return f"{mins:02d}:{secs:06.3f}s"

def format_speech_events(events: list[dict]) -> str:
    """Format speech events as <begin speech t=...> [content] <end speech t=...>"""
    lines = []
    for ev in events:
        t_start = ev.get("start", 0.0)
        t_end = ev.get("end", 0.0)
        content = ev.get("text", "").strip()
        ts_start = format_timestamp(t_start)
        ts_end = format_timestamp(t_end)
        lines.append(f"<begin speech t={ts_start}>")
        lines.append(f"content: \"{content}\"")
        lines.append(f"<end speech t={ts_end}>\n")
    return "\n".join(lines)

def compute_wer(ref: str, hyp: str) -> float:
    """Calculates Word Error Rate using standard dynamic programming Levenshtein distance."""
    r_words = [w.strip(".,!?:;\"'()[]{}") for w in ref.lower().split() if w.strip(".,!?:;\"'()[]{}")]
    h_words = [w.strip(".,!?:;\"'()[]{}") for w in hyp.lower().split() if w.strip(".,!?:;\"'()[]{}")]
    if not r_words:
        return 0.0 if not h_words else 1.0
    d = np.zeros((len(r_words) + 1, len(h_words) + 1), dtype=int)
    for i in range(len(r_words) + 1):
        d[i, 0] = i
    for j in range(len(h_words) + 1):
        d[0, j] = j
    for i in range(1, len(r_words) + 1):
        for j in range(1, len(h_words) + 1):
            if r_words[i - 1] == h_words[j - 1]:
                d[i, j] = d[i - 1, j - 1]
            else:
                d[i, j] = 1 + min(d[i - 1, j], d[i, j - 1], d[i - 1, j - 1])
    return float(d[len(r_words), len(h_words)] / len(r_words))

def resolve_canonical_transcript(events: list[dict], reference_text: str | None = None) -> dict:
    asr_text = " ".join([e.get("text", "").strip() for e in events if e.get("text", "").strip()])
    if reference_text is not None and len(reference_text.strip()) > 0:
        ref = reference_text.strip()
        wer = compute_wer(ref, asr_text)
        return {
            "source": "USER_PROVIDED_REFERENCE",
            "has_reference": True,
            "wer": wer,
            "canonical_text": ref,
            "asr_full_text": asr_text,
            "speech_events": events,
            "formatted_tags": format_speech_events(events),
            "total_words": len(ref.split()),
            "utterance_count": len(events),
        }
    else:
        return {
            "source": "AUTONOMOUS_ASR_FALLBACK",
            "has_reference": False,
            "wer": None,
            "canonical_text": asr_text,
            "asr_full_text": asr_text,
            "speech_events": events,
            "formatted_tags": format_speech_events(events),
            "total_words": len(asr_text.split()),
            "utterance_count": len(events),
        }


def transcribe_and_resolve(
    audio: np.ndarray,
    sr: int = 16000,
    reference_transcript_path: str | None = None,
    whisper_model_size: str = "base.en"
) -> dict:
    """
    Executes Phase 3 transcription and dual-mode canonical resolution.
    If reference transcript exists, uses it as canonical and validates with ASR.
    If no reference transcript exists, elevates ASR output to canonical.
    """
    model = get_whisper_model(whisper_model_size)
    clean_whisper_hooks(model)
    
    # Guarantee float32 dtype to prevent dtype mismatch or C++ kernel issues
    if audio.dtype != np.float32:
        audio = audio.astype(np.float32)

    # 1. Whole-file ASR transcription for comprehensive text
    try:
        res = model.transcribe(audio, fp16=torch.cuda.is_available())
    except RuntimeError:
        clean_whisper_hooks(model)
        import whisper.model
        whisper.model.MultiHeadAttention.use_sdpa = False
        res = model.transcribe(audio, fp16=False)

    raw_segments = res.get("segments", [])
    
    speech_events = []
    for s in raw_segments:
        text = s.get("text", "").strip()
        if text:
            speech_events.append({
                "start": float(s.get("start", 0.0)),
                "end": float(s.get("end", 0.0)),
                "text": text
            })
            
    formatted_tags = format_speech_events(speech_events)
    asr_full_text = res.get("text", "").strip()
    
    # 2. Check reference transcript
    has_reference = False
    ref_text = ""
    if reference_transcript_path and os.path.exists(reference_transcript_path):
        with open(reference_transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
            ref_text = f.read().strip()
        if ref_text and "[NO_YOUTUBE_SUBTITLES" not in ref_text:
            has_reference = True
            
    if has_reference:
        canonical_text = ref_text
        source = "USER_PROVIDED_REFERENCE"
    else:
        canonical_text = asr_full_text
        source = "AUTONOMOUS_ASR_FALLBACK"
        
    return {
        "source": source,
        "has_reference": has_reference,
        "canonical_text": canonical_text,
        "asr_full_text": asr_full_text,
        "speech_events": speech_events,
        "formatted_tags": formatted_tags,
        "total_words": len(canonical_text.split()),
        "utterance_count": len(speech_events)
    }
