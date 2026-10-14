"""
Ingestion Service: Universal Audio Format Normalizer
Accepts arbitrary audio formats (.mp3, .wav, .m4a, .ogg, .flac) and converts them
into standardized 16,000 Hz, single-channel mono master WAV files (-20.0 LUFS, 70Hz HPF).
"""

import os
import tempfile
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

def normalize_uploaded_audio(
    uploaded_file_bytes: bytes,
    original_filename: str,
    output_dir: str | None = None
) -> dict:
    """
    Standardizes any audio upload into a 16kHz mono, -20 LUFS master WAV file.
    Returns metadata dict containing clean_wav_path, duration, and telemetry.
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="speech_eval_")
    os.makedirs(output_dir, exist_ok=True)

    # 1. Save raw uploaded bytes to temporary file for universal decoding
    ext = os.path.splitext(original_filename)[-1].lower() or ".wav"
    raw_path = os.path.join(output_dir, f"raw_upload{ext}")
    with open(raw_path, "wb") as f:
        f.write(uploaded_file_bytes)

    # 2. Universal decoding (FFmpeg/SoundFile/Librosa fallback)
    raw_audio, orig_sr = load_audio(raw_path)

    # 3. Channel downmixing to mono
    mono_audio = downmix_to_mono(raw_audio)

    # 4. Sinc polyphase resampling to 16,000 Hz
    resampled_audio = resample_to_16k(mono_audio, orig_sr)

    # 5. 70 Hz Butterworth HPF rumble removal
    dc_cleaned = remove_dc_and_rumble(resampled_audio, sr=16000, cutoff_hz=70.0)

    # 6. EBU R128 loudness normalization to -20.0 LUFS
    normalized_audio, measured_lufs, gain_db = normalize_loudness_ebu_r128(
        dc_cleaned, sr=16000, target_lufs=-20.0
    )

    # 7. Boundary dead-air trimming
    trimmed_audio, lead_trim, tail_trim = trim_dead_air(
        normalized_audio, sr=16000, buffer_ms=200.0
    )

    # 8. Clean Master Audio (Pristine Intelligibility)
    # Preserve full vocal clarity, crisp consonants (/s/, /t/, /k/, /p/), and natural timbre.
    # Avoid destructive HPSS and 1.5x oversubtraction which muffle speech.
    clean_master = trimmed_audio
    clean_master, _, _ = normalize_loudness_ebu_r128(clean_master, sr=16000, target_lufs=-20.0)

    # 9. Save standardized clean master WAV
    clean_wav_path = os.path.join(output_dir, "preprocessed_clean.wav")
    sf.write(clean_wav_path, clean_master, 16000, subtype='PCM_16')

    duration_sec = float(len(clean_master) / 16000)

    return {
        "output_dir": output_dir,
        "clean_wav_path": clean_wav_path,
        "raw_path": raw_path,
        "original_filename": original_filename,
        "original_sr": orig_sr,
        "standardized_sr": 16000,
        "duration_sec": round(duration_sec, 2),
        "measured_lufs_raw": round(measured_lufs, 2),
        "gain_applied_db": round(gain_db, 2),
        "lead_trim_sec": round(lead_trim, 3),
        "tail_trim_sec": round(tail_trim, 3),
        "status": "NORMALIZED_SUCCESS"
    }
