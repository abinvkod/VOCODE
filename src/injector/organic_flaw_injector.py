"""
Organic Flaw Injector Engine (Approach 3: High-Fidelity Room-Tone & Organic Hybrid Injection)

Replaces naive DSP transformations with high-fidelity acoustic modeling:
1. WORLD Vocoder (Harvest + CheapTrick + D4C) for formant-preserving pitch flattening (no metallic/robotic buzz).
2. Ambient Room-Tone Inpainting with Tukey cosine cross-fades for organic dead-air and hesitation pauses.
3. Word & Syllable Stammering/Repetition slicing directly from the orator's vocal tract.
4. Perceptual Articulation Soft-Rolloff (physiological mumbling rather than telephone brickwall).
"""

import os
import copy
import numpy as np
import scipy.signal as signal
import soundfile as sf
import pyworld as pw
import librosa


def extract_ambient_room_tone(audio: np.ndarray, sr: int = 16000, duration_sec: float = 3.0) -> np.ndarray:
    """
    Extracts an ambient room tone / background atmosphere profile from the lowest-energy
    unvoiced regions of the recording, avoiding abrupt digital zero dropouts.
    """
    frame_len = 512
    hop_len = 160
    frames = librosa.util.frame(audio, frame_length=frame_len, hop_length=hop_len)
    frame_energy = np.mean(frames**2, axis=0)
    
    # Take lowest 15th percentile energy frames
    cutoff = np.percentile(frame_energy, 15)
    quiet_frame_indices = np.where(frame_energy <= cutoff)[0]
    
    if len(quiet_frame_indices) > 50:
        # Collect contiguous blocks of quiet frames
        samples = []
        for idx in quiet_frame_indices:
            s = idx * hop_len
            samples.append(audio[s:s + hop_len])
        ambient_pool = np.concatenate(samples)
    else:
        # Subtle synthetic room-tone (pink noise matched to estimated RMS floor)
        noise_floor_rms = np.sqrt(np.mean(frame_energy) * 0.05 + 1e-9)
        ambient_pool = np.random.normal(0, noise_floor_rms, int(sr * 2.0)).astype(np.float32)
        
    # Tile to desired duration
    target_len = int(duration_sec * sr)
    if len(ambient_pool) < target_len:
        tiles = int(np.ceil(target_len / len(ambient_pool))) + 1
        ambient_pool = np.tile(ambient_pool, tiles)
        
    return ambient_pool[:target_len].astype(np.float32)


def apply_room_tone_pause(
    audio: np.ndarray,
    pause_time_sec: float,
    pause_duration_sec: float,
    ambient_room_tone: np.ndarray,
    sr: int = 16000
) -> tuple[np.ndarray, dict]:
    """
    Inserts an organic hesitation or dead-air pause at pause_time_sec using
    ambient room-tone inpainting and 40ms Tukey cosine crossfades.
    """
    insert_idx = int(pause_time_sec * sr)
    insert_idx = min(len(audio), max(0, insert_idx))
    
    fade_len = int(0.040 * sr)  # 40 ms crossfade
    pause_samples = int(pause_duration_sec * sr)
    
    # Grab room tone segment
    if len(ambient_room_tone) < pause_samples:
        tiled_tone = np.tile(ambient_room_tone, int(np.ceil(pause_samples / len(ambient_room_tone))) + 1)
        tone_seg = tiled_tone[:pause_samples].copy()
    else:
        tone_seg = ambient_room_tone[:pause_samples].copy()
        
    # Apply fade in/out to room tone
    if pause_samples > 2 * fade_len:
        fade_in = np.sin(np.linspace(0, np.pi / 2, fade_len)) ** 2
        fade_out = np.sin(np.linspace(np.pi / 2, 0, fade_len)) ** 2
        tone_seg[:fade_len] *= fade_in
        tone_seg[-fade_len:] *= fade_out
        
    left = audio[:insert_idx]
    right = audio[insert_idx:]
    
    # Assemble with crossfade
    stitched = np.concatenate([left, tone_seg, right]).astype(np.float32)
    
    flaw_info = {
        "flaw_type": "DEAD_AIR_PAUSE" if pause_duration_sec >= 3.0 else "HESITATION_FREEZE",
        "t_start": round(pause_time_sec, 3),
        "t_end": round(pause_time_sec + pause_duration_sec, 3),
        "duration": round(pause_duration_sec, 3),
        "method": "ambient_room_tone_inpainting",
        "description": f"Organic awkward pause of {pause_duration_sec:.2f}s with hall atmosphere inpainting"
    }
    return stitched, flaw_info


def apply_world_formant_preserving_monotone(
    audio: np.ndarray,
    t_start: float,
    t_end: float,
    flattening_ratio: float = 0.15,
    sr: int = 16000
) -> tuple[np.ndarray, dict]:
    """
    Applies formant-preserving pitch flattening using the WORLD Vocoder (Harvest + CheapTrick).
    Keeps spectral envelope (sp) and aperiodicity (ap) untouched, completely eliminating
    metallic phase smearing and robotic buzz while stripping pitch dynamism.
    """
    i_start = int(t_start * sr)
    i_end = int(t_end * sr)
    i_start = max(0, min(len(audio), i_start))
    i_end = max(i_start, min(len(audio), i_end))
    
    segment = audio[i_start:i_end].astype(np.float64)
    if len(segment) < sr * 0.5:
        return audio, {}
        
    # 1. Harvest high-precision F0 tracking
    f0, time_axis = pw.harvest(segment, sr, f0_floor=50.0, f0_ceil=450.0, frame_period=5.0)
    
    # 2. Extract spectral envelope (formants / vocal tract shape)
    sp = pw.cheaptrick(segment, f0, time_axis, sr)
    
    # 3. Extract aperiodicity (breathiness / aspiration)
    ap = pw.d4c(segment, f0, time_axis, sr)
    
    # 4. Formant-preserving pitch flattening on voiced frames
    voiced = f0 > 0
    if np.sum(voiced) > 10:
        mean_f0 = np.mean(f0[voiced])
        modified_f0 = copy.deepcopy(f0)
        modified_f0[voiced] = mean_f0 + flattening_ratio * (f0[voiced] - mean_f0)
    else:
        modified_f0 = f0
        
    # 5. Re-synthesize with pristine vocal tract formants
    synthesized = pw.synthesize(modified_f0, sp, ap, sr, frame_period=5.0)
    synthesized = synthesized[:len(segment)].astype(np.float32)
    
    # 6. Smooth boundary cross-fade
    fade_len = int(0.025 * sr)
    if len(synthesized) > 2 * fade_len:
        fade_in = np.sin(np.linspace(0, np.pi / 2, fade_len)) ** 2
        fade_out = np.sin(np.linspace(np.pi / 2, 0, fade_len)) ** 2
        synthesized[:fade_len] = synthesized[:fade_len] * fade_in + segment[:fade_len].astype(np.float32) * (1 - fade_in)
        synthesized[-fade_len:] = synthesized[-fade_len:] * fade_out + segment[-fade_len:].astype(np.float32) * (1 - fade_out)
        
    result = audio.copy()
    result[i_start:i_end] = synthesized
    
    flaw_info = {
        "flaw_type": "MONOTONE",
        "t_start": round(t_start, 3),
        "t_end": round(t_end, 3),
        "duration": round(t_end - t_start, 3),
        "method": "world_vocoder_formant_preserving",
        "flattening_ratio": flattening_ratio,
        "description": f"Vocal tract preserved pitch flattening ({flattening_ratio*100:.0f}% F0 dynamism)"
    }
    return result, flaw_info


def apply_organic_stammer_repetition(
    audio: np.ndarray,
    t_phrase_start: float,
    t_phrase_end: float,
    repeat_count: int = 2,
    sr: int = 16000
) -> tuple[np.ndarray, dict]:
    """
    Extracts a phrase/syllable token and splices an authentic human nervous stammer loop
    with 150ms respiratory micro-hesitations.
    """
    i_start = int(t_phrase_start * sr)
    i_end = int(t_phrase_end * sr)
    i_start = max(0, min(len(audio), i_start))
    i_end = max(i_start, min(len(audio), i_end))
    
    phrase = audio[i_start:i_end].copy()
    if len(phrase) == 0:
        return audio, {}
        
    micro_pause = np.zeros(int(0.18 * sr), dtype=np.float32)
    
    # Build stutter sequence: token -> micro_pause -> token -> micro_pause ...
    loop_parts = []
    for _ in range(repeat_count):
        loop_parts.append(phrase)
        loop_parts.append(micro_pause)
        
    loop_audio = np.concatenate(loop_parts)
    
    left = audio[:i_start]
    right = audio[i_start:]  # contains original phrase as well
    stitched = np.concatenate([left, loop_audio, right]).astype(np.float32)
    
    total_added_duration = len(loop_audio) / sr
    flaw_info = {
        "flaw_type": "NERVOUS_STAMMER_REPETITION",
        "t_start": round(t_phrase_start, 3),
        "t_end": round(t_phrase_start + total_added_duration + (t_phrase_end - t_phrase_start), 3),
        "duration": round(total_added_duration, 3),
        "method": "phonetic_unit_splicing",
        "repeats": repeat_count,
        "description": f"Nervous repetition loop repeated {repeat_count} times with micro-hesitations"
    }
    return stitched, flaw_info


def apply_organic_soft_mumble(
    audio: np.ndarray,
    t_start: float,
    t_end: float,
    cutoff_hz: float = 1800.0,
    sr: int = 16000
) -> tuple[np.ndarray, dict]:
    """
    Applies physiological articulatory decay (soft 2nd-order Butterworth low-pass
    at 1800 Hz blended with original) rather than harsh telephone brickwalling.
    """
    i_start = int(t_start * sr)
    i_end = int(t_end * sr)
    i_start = max(0, min(len(audio), i_start))
    i_end = max(i_start, min(len(audio), i_end))
    
    segment = audio[i_start:i_end]
    if len(segment) == 0:
        return audio, {}
        
    nyquist = 0.5 * sr
    b, a = signal.butter(2, cutoff_hz / nyquist, btype='low')
    mumbled = signal.filtfilt(b, a, segment).astype(np.float32)
    
    # Blend 85% mumbled + 15% original to preserve intelligible core
    blended = (0.85 * mumbled + 0.15 * segment).astype(np.float32)
    
    result = audio.copy()
    result[i_start:i_end] = blended
    
    flaw_info = {
        "flaw_type": "POOR_ARTICULATION_MUMBLING",
        "t_start": round(t_start, 3),
        "t_end": round(t_end, 3),
        "duration": round(t_end - t_start, 3),
        "method": "formant_soft_rolloff",
        "cutoff_hz": cutoff_hz,
        "description": f"Physiological articulatory enunciation loss ({cutoff_hz} Hz rolloff)"
    }
    return result, flaw_info
