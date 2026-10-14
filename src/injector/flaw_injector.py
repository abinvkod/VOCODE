import os
import json
import numpy as np
import scipy.signal as signal
import soundfile as sf
import parselmouth

def inject_monotone_pitch(
    audio: np.ndarray,
    sr: int,
    t_start: float,
    t_end: float,
    compression_factor: float = 0.12
) -> tuple[np.ndarray, dict]:
    """
    FLAW-1: Teleprompter Flatline (Natural Pitch Compression).
    Compresses the speaker's natural dynamic pitch excursions towards their median pitch:
        f_new(t) = f_median + compression_factor * (f_orig(t) - f_median)
    This maintains 100% natural human vocal timbre, glottal pulse, and micro-texture,
    while removing oratorical melodic expressiveness (semitone range drops < 1.0 st).
    Avoids robotic synthesizer vocoder artifacts.
    """
    snd = parselmouth.Sound(audio, sampling_frequency=sr)
    pitch = snd.to_pitch(time_step=0.01, pitch_floor=75.0, pitch_ceiling=500.0)
    
    # Calculate speaker median pitch in the target window
    med = parselmouth.praat.call(pitch, "Get quantile", t_start, t_end, 0.50, "Hertz")
    if np.isnan(med) or med <= 0:
        med = parselmouth.praat.call(pitch, "Get quantile", 0.0, snd.duration, 0.50, "Hertz")
    median_f0 = float(med) if not np.isnan(med) else 200.0

    manipulation = parselmouth.praat.call(snd, "To Manipulation", 0.01, 75.0, 500.0)
    pitch_tier = parselmouth.praat.call(manipulation, "Extract pitch tier")
    
    num_pts = parselmouth.praat.call(pitch_tier, "Get number of points")
    times = []
    vals = []
    for i in range(1, num_pts + 1):
        t = parselmouth.praat.call(pitch_tier, "Get time from index", i)
        f = parselmouth.praat.call(pitch_tier, "Get value at index", i)
        if t_start <= t <= t_end:
            # Compress pitch variations towards speaker median
            f_comp = median_f0 + compression_factor * (f - median_f0)
            times.append(t)
            vals.append(f_comp)

    # Remove points in target window and add compressed points
    parselmouth.praat.call(pitch_tier, "Remove points between", t_start, t_end)
    for t, f in zip(times, vals):
        parselmouth.praat.call(pitch_tier, "Add point", t, f)
        
    parselmouth.praat.call([manipulation, pitch_tier], "Replace pitch tier")
    resynthesized = parselmouth.praat.call(manipulation, "Get resynthesis (overlap-add)")
    res_audio = resynthesized.values[0].astype(np.float32)
    
    meta = {
        "flaw_id": "FLAW-1",
        "flaw_name": "Teleprompter Flatline (Monotone Pitch)",
        "t_start": round(t_start, 3),
        "t_end": round(t_end, 3),
        "median_f0_hz": round(median_f0, 1),
        "compression_factor": compression_factor,
        "causal_explanation": f"Pitch excursions compressed by {(1-compression_factor)*100:.0f}% towards median {median_f0:.1f} Hz across [{t_start:.1f}s - {t_end:.1f}s]; lacks vocal inflection."
    }
    return res_audio, meta

def inject_rushed_cadence(
    audio: np.ndarray,
    sr: int,
    t_start: float,
    t_end: float,
    speedup: float = 1.65
) -> tuple[np.ndarray, dict]:
    """
    FLAW-2: Nervous Panic (High-Fidelity PSOLA Duration Scaling).
    Uses Praat's native DurationTier manipulation with time-domain PSOLA resynthesis.
    Preserves exact formant structure, vocal timbre, and pitch without phase vocoder
    flanging or metallic smearing.
    """
    snd = parselmouth.Sound(audio, sampling_frequency=sr)
    manipulation = parselmouth.praat.call(snd, "To Manipulation", 0.01, 75.0, 500.0)
    duration_tier = parselmouth.praat.call(manipulation, "Extract duration tier")
    
    # In Praat DurationTier, value = target_duration / original_duration = 1.0 / speedup
    dur_ratio = 1.0 / speedup
    transition = 0.03 # 30ms smooth ramp
    
    parselmouth.praat.call(duration_tier, "Add point", max(0.0, t_start - transition), 1.0)
    parselmouth.praat.call(duration_tier, "Add point", t_start, dur_ratio)
    parselmouth.praat.call(duration_tier, "Add point", t_end, dur_ratio)
    parselmouth.praat.call(duration_tier, "Add point", min(snd.duration, t_end + transition), 1.0)
    
    parselmouth.praat.call([manipulation, duration_tier], "Replace duration tier")
    resynthesized = parselmouth.praat.call(manipulation, "Get resynthesis (overlap-add)")
    res_audio = resynthesized.values[0].astype(np.float32)
    
    orig_dur = t_end - t_start
    new_dur = orig_dur * dur_ratio
    
    meta = {
        "flaw_id": "FLAW-2",
        "flaw_name": "Nervous Panic (Rushed Cadence)",
        "t_start": round(t_start, 3),
        "t_end": round(t_start + new_dur, 3),
        "original_duration_sec": round(orig_dur, 3),
        "new_duration_sec": round(new_dur, 3),
        "speedup_factor": speedup,
        "causal_explanation": f"Speech rate accelerated by {speedup:.2f}x across [{t_start:.1f}s - {t_start + new_dur:.1f}s]; syllables rushed without breathing room."
    }
    return res_audio, meta

def inject_syntactic_hesitation(
    audio: np.ndarray,
    sr: int,
    t_insert: float,
    silence_sec: float = 1.6
) -> tuple[np.ndarray, dict]:
    """
    FLAW-3: Brain Freeze (Mid-Clause Syntactic Hesitation).
    Splices silence_sec of ambient room tone right at an unnatural mid-clause word boundary
    (e.g., between adjective and noun).
    """
    n_cut = int(t_insert * sr)
    part1 = audio[:n_cut]
    part2 = audio[n_cut:]
    
    # Synthesize realistic low-level room tone (-52 dBFS smoothed pinkish noise)
    noise_samples = int(silence_sec * sr)
    room_tone = np.random.normal(0, 0.002, noise_samples).astype(np.float32)
    
    # 4th-order lowpass at 1200 Hz to simulate real room acoustics
    b, a = signal.butter(4, 1200.0 / (sr / 2), btype='lowpass')
    room_tone = signal.filtfilt(b, a, room_tone).astype(np.float32)
    
    # Smooth 15ms crossfade edges
    fade = int(0.015 * sr)
    room_tone[:fade] *= np.linspace(0, 1, fade)
    room_tone[-fade:] *= np.linspace(1, 0, fade)
    
    result = np.concatenate([part1, room_tone, part2]).astype(np.float32)
    
    meta = {
        "flaw_id": "FLAW-3",
        "flaw_name": "Brain Freeze (Mid-Clause Syntactic Hesitation)",
        "t_start": round(t_insert, 3),
        "t_end": round(t_insert + silence_sec, 3),
        "hesitation_duration_sec": silence_sec,
        "causal_explanation": f"Awkward {silence_sec:.1f}s dead-air hesitation broken mid-clause at t={t_insert:.1f}s; disrupts grammatical thought."
    }
    return result, meta

def inject_clipped_pause(
    audio: np.ndarray,
    sr: int,
    t_pause_start: float,
    t_pause_end: float,
    retain_sec: float = 0.10
) -> tuple[np.ndarray, dict]:
    """
    FLAW-4: The Steamroller (Clipped Dramatic Pause).
    Locates an intentional rhetorical dramatic pause between clauses (e.g. 6.4s silence/applause)
    and obliterates it down to retain_sec (0.10s), causing the speaker to barrel immediately
    into the next sentence.
    """
    n_start = int(t_pause_start * sr)
    n_end = int(t_pause_end * sr)
    
    part1 = audio[:n_start]
    part2 = audio[n_end:]
    
    # Retain a tiny 0.10s silence slice for natural transition
    retained_samples = int(retain_sec * sr)
    retained_silence = audio[n_start : n_start + retained_samples]
    
    # 15ms crossfade
    fade = int(0.015 * sr)
    if len(part2) > fade and len(retained_silence) > fade:
        retained_silence[-fade:] *= np.linspace(1, 0, fade)
        part2[:fade] *= np.linspace(0, 1, fade)
        
    result = np.concatenate([part1, retained_silence, part2]).astype(np.float32)
    
    original_gap = t_pause_end - t_pause_start
    meta = {
        "flaw_id": "FLAW-4",
        "flaw_name": "The Steamroller (Clipped Dramatic Pause)",
        "t_start": round(t_pause_start, 3),
        "original_pause_sec": round(original_gap, 3),
        "retained_pause_sec": retain_sec,
        "causal_explanation": f"Rhetorical dramatic pause ({original_gap:.2f}s) obliterated down to {retain_sec}s; steamrolled immediately into next sentence without breathing room."
    }
    return result, meta

def inject_energy_inversion(
    audio: np.ndarray,
    sr: int,
    t_start: float,
    t_end: float,
    attenuation_db: float = -16.0
) -> tuple[np.ndarray, dict]:
    """
    FLAW-5: Anti-Climax (Energy Inversion / Muted Punchline).
    Applies a smooth trapezoidal negative gain attenuation envelope across the climax window.
    """
    n_start = int(t_start * sr)
    n_end = int(t_end * sr)
    
    result = np.copy(audio)
    target_len = n_end - n_start
    
    linear_gain = 10.0 ** (attenuation_db / 20.0) # -16 dB = ~0.158
    ramp = min(int(0.06 * sr), target_len // 4)
    env = np.ones(target_len, dtype=np.float32) * linear_gain
    env[:ramp] = np.linspace(1.0, linear_gain, ramp)
    env[-ramp:] = np.linspace(linear_gain, 1.0, ramp)
    
    result[n_start:n_end] = result[n_start:n_end] * env
    
    meta = {
        "flaw_id": "FLAW-5",
        "flaw_name": "Anti-Climax (Energy Inversion / Volume Drop)",
        "t_start": round(t_start, 3),
        "t_end": round(t_end, 3),
        "attenuation_db": attenuation_db,
        "causal_explanation": f"Vocal intensity dipped by {attenuation_db:.1f} dB during thesis climax [{t_start:.1f}s - {t_end:.1f}s]; delivery sounded timid."
    }
    return result, meta

def inject_mumble_trail_off(
    audio: np.ndarray,
    sr: int,
    t_start: float,
    t_end: float,
    cutoff_hz: float = 600.0,
    end_gain_db: float = -28.0
) -> tuple[np.ndarray, dict]:
    """
    FLAW-6: Mumble & Trail-Off (Slurred Diction & Inaudible Decay).
    Applies a steep 6th-order Butterworth low-pass filter (cutting out consonants above 600 Hz)
    combined with an exponential volume decay.
    """
    n_start = int(t_start * sr)
    n_end = int(t_end * sr)
    
    result = np.copy(audio)
    target = np.copy(audio[n_start:n_end])
    
    # 6th-order Butterworth low-pass filter at 600 Hz (cuts out consonant clarity)
    b, a = signal.butter(6, cutoff_hz / (sr / 2), btype='lowpass')
    muffled = signal.filtfilt(b, a, target).astype(np.float32)
    
    # Exponential volume decay envelope
    t_norm = np.linspace(0.0, 1.0, len(muffled))
    decay = np.exp(-3.5 * t_norm).astype(np.float32)
    muffled = muffled * decay
    
    # 25ms crossfade at start for smooth entrance into mumble
    fade = int(0.025 * sr)
    if len(muffled) > fade:
        muffled[:fade] = muffled[:fade] * np.linspace(0, 1, fade) + target[:fade] * np.linspace(1, 0, fade)
        
    result[n_start:n_end] = muffled
    
    meta = {
        "flaw_id": "FLAW-6",
        "flaw_name": "Mumble & Trail-Off (Slurred Diction & Decay)",
        "t_start": round(t_start, 3),
        "t_end": round(t_end, 3),
        "cutoff_hz": cutoff_hz,
        "end_gain_db": end_gain_db,
        "causal_explanation": f"Consonants muffled below {cutoff_hz} Hz with exponential volume decay across [{t_start:.1f}s - {t_end:.1f}s]; final punchline slurred into inaudibility."
    }
    return result, meta
