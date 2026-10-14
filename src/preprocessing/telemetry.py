import numpy as np
import json

def create_speech_mask(audio: np.ndarray, threshold: float | None = None) -> np.ndarray:
    """Creates a boolean speech activity mask based on frame energy."""
    frame_len = 512
    hop_len = 160
    pad_len = int(np.ceil(len(audio) / hop_len) * hop_len)
    padded = np.pad(audio, (0, pad_len - len(audio)))
    frames = padded.reshape(-1, hop_len)
    frame_powers = np.mean(frames**2, axis=1)
    if threshold is None:
        threshold = np.percentile(frame_powers, 25.0)
    frame_mask = frame_powers > threshold
    sample_mask = np.repeat(frame_mask, hop_len)[:len(audio)]
    return sample_mask

def compute_snr(audio: np.ndarray, speech_mask: np.ndarray | None = None, percentile_threshold: float = 25.0) -> float:
    """Estimates Signal-to-Noise Ratio (dB) via energy partitioning or provided mask."""
    if speech_mask is not None:
        speech_samples = audio[speech_mask]
        noise_samples = audio[~speech_mask]
        if len(speech_samples) == 0 or len(noise_samples) == 0:
            return 20.0
        p_speech = np.mean(speech_samples**2)
        p_noise = np.mean(noise_samples**2)
        snr = 10.0 * np.log10((p_speech + 1e-12) / (p_noise + 1e-12))
        return float(np.clip(snr, -10.0, 50.0))

    frame_len = 512
    hop_len = 160
    pad_len = int(np.ceil(len(audio) / hop_len) * hop_len)
    padded = np.pad(audio, (0, pad_len - len(audio)))
    frames = padded.reshape(-1, hop_len)
    frame_powers = np.mean(frames**2, axis=1) + 1e-12
    
    cutoff = np.percentile(frame_powers, percentile_threshold)
    noise_powers = frame_powers[frame_powers <= cutoff]
    speech_powers = frame_powers[frame_powers > cutoff]
    
    if len(noise_powers) == 0 or len(speech_powers) == 0:
        return 20.0
        
    p_speech = np.mean(speech_powers)
    p_noise = np.mean(noise_powers)
    
    snr = 10.0 * np.log10(p_speech / (p_noise + 1e-12))
    return float(np.clip(snr, -10.0, 50.0))


def compute_clipping_ratio(audio: np.ndarray, ceiling: float = 0.99) -> float:
    """Computes the percentage of samples at or exceeding digital ceiling."""
    if len(audio) == 0:
        return 0.0
    clipped = np.sum(np.abs(audio) >= ceiling)
    return float(clipped / len(audio))

def generate_telemetry_report(
    source_path: str,
    output_path: str,
    raw_audio: np.ndarray,
    clean_audio: np.ndarray,
    sr: int,
    measured_lufs_raw: float,
    gain_db: float,
    lead_trim_sec: float,
    tail_trim_sec: float,
    transcription_meta: dict
) -> dict:
    """Compiles audio telemetry health report."""
    snr_raw = compute_snr(raw_audio)
    snr_clean = compute_snr(clean_audio)
    clipping_ratio = compute_clipping_ratio(clean_audio)
    
    report = {
        "source_file": source_path,
        "clean_file": output_path,
        "sample_rate": sr,
        "channels": 1,
        "original_duration_sec": round(float(len(raw_audio) / sr), 3),
        "clean_duration_sec": round(float(len(clean_audio) / sr), 3),
        "lead_trim_sec": round(lead_trim_sec, 3),
        "tail_trim_sec": round(tail_trim_sec, 3),
        "measured_lufs_raw": round(measured_lufs_raw, 2),
        "target_lufs": -20.0,
        "gain_applied_db": round(gain_db, 2),
        "snr_raw_db": round(snr_raw, 2),
        "snr_clean_db": round(snr_clean, 2),
        "snr_improvement_db": round(snr_clean - snr_raw, 2),
        "clipping_ratio": round(clipping_ratio, 4),
        "clipping_warning": bool(clipping_ratio > 0.005),
        "transcript_resolution": {
            "source": transcription_meta.get("source"),
            "has_reference": transcription_meta.get("has_reference"),
            "total_words": transcription_meta.get("total_words"),
            "utterance_count": transcription_meta.get("utterance_count")
        },
        "status": "READY_FOR_EVALUATION"
    }
    return report
