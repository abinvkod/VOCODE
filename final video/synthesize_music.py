import numpy as np
import scipy.io.wavfile as wavfile
import os

SAMPLE_RATE = 44100
TOTAL_DURATION = 300.0  # 5 minutes
NUM_SAMPLES = int(SAMPLE_RATE * TOTAL_DURATION)

print("Synthesizing 5-minute ambient background music track...")

# Chord progression (A minor, F major, C major, G major)
# Frequencies in Hz:
# Am: A2 (110.0), C3 (130.81), E3 (164.81), A3 (220.0)
# F:  F2 (87.31),  A2 (110.0),  C3 (130.81), F3 (174.61)
# C:  C2 (65.41),  G2 (98.00),  C3 (130.81), E3 (164.81)
# G:  G2 (98.00),  B2 (123.47), D3 (146.83), G3 (196.00)

chords = [
    [110.0, 130.81, 164.81, 220.0, 329.63], # Am
    [87.31, 110.0, 130.81, 174.61, 261.63], # F
    [65.41, 98.00, 130.81, 164.81, 261.63], # C
    [98.00, 123.47, 146.83, 196.0, 293.66], # G
]

chord_duration = 7.5 # seconds per chord
total_chords = int(TOTAL_DURATION / chord_duration) + 1

t = np.linspace(0, TOTAL_DURATION, NUM_SAMPLES, endpoint=False)
music_left = np.zeros(NUM_SAMPLES, dtype=np.float32)
music_right = np.zeros(NUM_SAMPLES, dtype=np.float32)

for i in range(total_chords):
    c = chords[i % len(chords)]
    t_start = i * chord_duration
    t_end = min(TOTAL_DURATION, (i + 1) * chord_duration)
    
    idx_start = int(t_start * SAMPLE_RATE)
    idx_end = int(t_end * SAMPLE_RATE)
    num_chord_samples = idx_end - idx_start
    if num_chord_samples <= 0:
        continue
        
    t_local = np.linspace(0, (t_end - t_start), num_chord_samples, endpoint=False)
    
    # Smooth bell envelope (raised cosine fade in / fade out)
    env = 0.5 * (1 - np.cos(2 * np.pi * t_local / (t_end - t_start)))
    
    # Layer soft sines with slight chorus detune
    chord_wave_l = np.zeros(num_chord_samples, dtype=np.float32)
    chord_wave_r = np.zeros(num_chord_samples, dtype=np.float32)
    
    for f in c:
        # Fundamental + gentle 2nd harmonic
        f_detune_l = f * 0.998
        f_detune_r = f * 1.002
        chord_wave_l += np.sin(2 * np.pi * f_detune_l * t_local) * 0.25
        chord_wave_l += np.sin(2 * np.pi * (f * 2) * t_local) * 0.05
        
        chord_wave_r += np.sin(2 * np.pi * f_detune_r * t_local) * 0.25
        chord_wave_r += np.sin(2 * np.pi * (f * 2) * t_local) * 0.05
        
    music_left[idx_start:idx_end] += chord_wave_l * env
    music_right[idx_start:idx_end] += chord_wave_r * env

# Normalize to peak -18 dB (very soft, ambient background)
peak = max(np.max(np.abs(music_left)), np.max(np.abs(music_right)))
if peak > 0:
    music_left = (music_left / peak) * 0.12  # Subtle background level
    music_right = (music_right / peak) * 0.12

# Master fade in at start (2s) and fade out at end (3s)
fade_in_samples = int(2.0 * SAMPLE_RATE)
music_left[:fade_in_samples] *= np.linspace(0, 1, fade_in_samples)
music_right[:fade_in_samples] *= np.linspace(0, 1, fade_in_samples)

fade_out_samples = int(3.0 * SAMPLE_RATE)
music_left[-fade_out_samples:] *= np.linspace(1, 0, fade_out_samples)
music_right[-fade_out_samples:] *= np.linspace(1, 0, fade_out_samples)

stereo = np.column_stack((music_left, music_right))
stereo_int16 = (stereo * 32767).astype(np.int16)

out_music_path = "final video/audio/ambient_music_300s.wav"
wavfile.write(out_music_path, SAMPLE_RATE, stereo_int16)

print(f"Ambient music synthesized successfully: {out_music_path}")
