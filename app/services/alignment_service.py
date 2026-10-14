"""
Alignment Service: Dual-Mode Transcript Resolution & Timestamp Extraction
Aligns user-provided or autonomously transcribed text to audio timestamps.
"""

import os
import soundfile as sf
import numpy as np

from src.preprocessing.transcription_engine import transcribe_and_resolve

def resolve_and_align_transcript(
    clean_wav_path: str,
    user_transcript_text: str | None = None,
    whisper_model_size: str = "base.en"
) -> dict:
    """
    Executes dual-mode transcript alignment:
    - If user transcript provided: resolves canonical text and aligns with Whisper timestamps.
    - If no transcript provided: autonomous ASR fallback with word/utterance timestamps.
    """
    audio, sr = sf.read(clean_wav_path, dtype='float32')

    temp_ref_path = None
    if user_transcript_text and user_transcript_text.strip():
        temp_dir = os.path.dirname(clean_wav_path)
        temp_ref_path = os.path.join(temp_dir, "user_reference.txt")
        with open(temp_ref_path, "w", encoding="utf-8") as f:
            f.write(user_transcript_text.strip())

    trans_result = transcribe_and_resolve(
        audio=audio,
        sr=sr,
        reference_transcript_path=temp_ref_path,
        whisper_model_size=whisper_model_size
    )

    return trans_result
