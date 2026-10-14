import os
import json
import soundfile as sf
import numpy as np

from src.preprocessing.audio_standardizer import (
    load_audio,
    downmix_to_mono,
    resample_to_16k,
    remove_dc_and_rumble,
    normalize_loudness_ebu_r128,
    trim_dead_air
)
from src.preprocessing.spectral_denoiser import spectral_denoise_and_isolate
from src.preprocessing.transcription_engine import transcribe_and_resolve
from src.preprocessing.telemetry import generate_telemetry_report

def preprocess_speech(
    audio_path: str,
    transcript_path: str | None = None,
    output_dir: str | None = None,
    run_transcription: bool = True
) -> dict:
    """
    Executes the complete 4-phase audio preprocessing pipeline:
    1. Physical Audio Standardization (Mono, 16kHz, 70Hz Highpass, EBU R128 to -20 LUFS, Dead-air trimming)
    2. Spectral Denoising & HPSS Vocal Isolation (SNR boost, clap/cheer suppression)
    3. Bounded Independent Transcription & Dual-Mode Resolution
    4. Telemetry Generation & Artifact Serialization
    """
    if output_dir is None:
        output_dir = os.path.dirname(audio_path)
    os.makedirs(output_dir, exist_ok=True)
    
    clean_audio_path = os.path.join(output_dir, "preprocessed_clean.wav")
    events_path = os.path.join(output_dir, "transcript_events.txt")
    canonical_transcript_path = os.path.join(output_dir, "canonical_transcript.txt")
    telemetry_path = os.path.join(output_dir, "telemetry.json")
    
    # --- PHASE 1: Physical Standardization ---
    raw_audio, orig_sr = load_audio(audio_path)
    mono_audio = downmix_to_mono(raw_audio)
    resampled_audio = resample_to_16k(mono_audio, orig_sr)
    dc_filtered_audio = remove_dc_and_rumble(resampled_audio, sr=16000, cutoff_hz=70.0)
    loudness_audio, measured_lufs_raw, gain_db = normalize_loudness_ebu_r128(dc_filtered_audio, sr=16000, target_lufs=-20.0)
    trimmed_audio, lead_trim, tail_trim = trim_dead_air(loudness_audio, sr=16000, buffer_ms=200.0)
    
    # --- PHASE 2: Spectral Denoising & Vocal Isolation ---
    enhanced_audio = spectral_denoise_and_isolate(trimmed_audio, sr=16000)
    
    # Normalize final clean master to -20 LUFS with true peak headroom
    clean_master, _, _ = normalize_loudness_ebu_r128(enhanced_audio, sr=16000, target_lufs=-20.0)
    
    # Save preprocessed clean audio
    sf.write(clean_audio_path, clean_master, 16000, subtype='PCM_16')
    
    # --- PHASE 3: Bounded Transcription & Dual-Mode Resolution ---
    if run_transcription:
        trans_res = transcribe_and_resolve(clean_master, sr=16000, reference_transcript_path=transcript_path)
        with open(events_path, 'w', encoding='utf-8') as f:
            f.write(trans_res["formatted_tags"])
        with open(canonical_transcript_path, 'w', encoding='utf-8') as f:
            f.write(trans_res["canonical_text"])
    else:
        trans_res = {
            "source": "BYPASSED",
            "has_reference": bool(transcript_path and os.path.exists(transcript_path)),
            "total_words": 0,
            "utterance_count": 0
        }
        
    # --- PHASE 4: Telemetry & Quality Report ---
    report = generate_telemetry_report(
        source_path=audio_path,
        output_path=clean_audio_path,
        raw_audio=resampled_audio,
        clean_audio=clean_master,
        sr=16000,
        measured_lufs_raw=measured_lufs_raw,
        gain_db=gain_db,
        lead_trim_sec=lead_trim,
        tail_trim_sec=tail_trim,
        transcription_meta=trans_res
    )
    
    with open(telemetry_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

def run_pipeline(
    input_audio_path: str,
    reference_transcript_path: str | None = None,
    output_dir: str | None = None,
    whisper_model_size: str = "base.en"
) -> dict:
    """Wrapper alias for end-to-end preprocessing pipeline."""
    return preprocess_speech(
        audio_path=input_audio_path,
        transcript_path=reference_transcript_path,
        output_dir=output_dir,
        run_transcription=True
    )

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Preprocess speech audio.")
    parser.add_argument("--input", required=True, help="Input audio path")
    parser.add_argument("--transcript", default=None, help="Optional reference transcript path")
    parser.add_argument("--output_dir", default=None, help="Output directory")
    args = parser.parse_args()
    
    rep = preprocess_speech(args.input, args.transcript, args.output_dir)
    print(json.dumps(rep, indent=2))
