import os
import subprocess
import numpy as np
import scipy.io.wavfile as wavfile

AUDIO_DIR = "final video/audio"
SAMPLE_RATE = 44100
TOTAL_DURATION = 300.0
TOTAL_SAMPLES = int(SAMPLE_RATE * TOTAL_DURATION)

# Scene timetable: (scene_id, scene_start_sec, speech_offset_sec)
TIMETABLE = [
    ("scene1_intro", 0.0, 0.6),
    ("scene2_problem", 28.0, 0.6),
    ("scene3_dataset", 58.0, 0.6),
    ("scene4_pipeline", 88.0, 0.6),
    ("scene5_demo", 128.0, 0.6),
    ("scene6_architecture", 203.0, 0.6),
    ("scene7_rubrics", 242.0, 0.6),
    ("scene8_conclusion", 277.0, 0.6),
]

def load_and_resample(wav_path, target_sr=SAMPLE_RATE):
    cmd = [
        "ffmpeg", "-v", "error", "-i", wav_path,
        "-ar", str(target_sr), "-ac", "1", "-f", "f32le", "-"
    ]
    raw = subprocess.check_output(cmd)
    return np.frombuffer(raw, dtype=np.float32)

master_voice = np.zeros(TOTAL_SAMPLES, dtype=np.float32)

for sc_id, sc_start, sp_offset in TIMETABLE:
    wav_path = os.path.join(AUDIO_DIR, f"{sc_id}.wav")
    audio = load_and_resample(wav_path)
    
    start_sec = sc_start + sp_offset
    start_idx = int(start_sec * SAMPLE_RATE)
    end_idx = start_idx + len(audio)
    
    if end_idx > TOTAL_SAMPLES:
        audio = audio[:TOTAL_SAMPLES - start_idx]
        end_idx = TOTAL_SAMPLES
        
    master_voice[start_idx:end_idx] += audio
    print(f"Placed {sc_id}: {start_sec:.2f}s -> {(start_idx + len(audio))/SAMPLE_RATE:.2f}s")

# Normalize master voice
voice_peak = np.max(np.abs(master_voice))
if voice_peak > 0:
    master_voice = (master_voice / voice_peak) * 0.90  # -0.9 dBFS peak

voice_out = "final video/audio/vocode_narration_master.wav"
wavfile.write(voice_out, SAMPLE_RATE, (master_voice * 32767).astype(np.int16))
print(f"Master voice track written to {voice_out}")

# Load ambient music
music_sr, music_data = wavfile.read("final video/audio/ambient_music_300s.wav")
music_float = music_data.astype(np.float32) / 32767.0
if len(music_float) < TOTAL_SAMPLES:
    pad = np.zeros((TOTAL_SAMPLES - len(music_float), 2), dtype=np.float32)
    music_float = np.vstack([music_float, pad])
else:
    music_float = music_float[:TOTAL_SAMPLES]

# Convert mono voice to stereo and mix with smooth ducking
voice_stereo = np.column_stack([master_voice, master_voice])
voice_activity = np.abs(master_voice)

kernel_size = int(SAMPLE_RATE * 0.4)
kernel = np.ones(kernel_size) / kernel_size
ducking_envelope = np.convolve(voice_activity, kernel, mode='same')
ducking_gain = 1.0 - 0.45 * np.clip(ducking_envelope * 4.0, 0.0, 1.0)
ducking_gain_stereo = np.column_stack([ducking_gain, ducking_gain])

final_mix = voice_stereo + (music_float * ducking_gain_stereo * 0.65)
mix_peak = np.max(np.abs(final_mix))
if mix_peak > 0.95:
    final_mix = (final_mix / mix_peak) * 0.95

mix_out = "final video/audio/vocode_audio_mix_master.wav"
wavfile.write(mix_out, SAMPLE_RATE, (final_mix * 32767).astype(np.int16))
print(f"Master audio mix written to {mix_out}")

# Synchronized SRT captions
def format_timestamp(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

CAPTION_CHUNKS = [
    # Scene 1: 0.6s - 27.5s
    (0.6, 7.0, "Every year, millions of orators compete in forensics, declamation, and public keynotes."),
    (7.3, 14.2, "Yet speech evaluation remains trapped in an adjudication crisis: plagued by severe judge subjectivity..."),
    (14.5, 20.5, "...inconsistent scoring across ballots, and vague, non-actionable feedback."),
    (20.8, 27.5, "Today, we introduce VOCODE: a physics-grounded multimodal engine that transforms oratorical evaluation."),

    # Scene 2: 28.6s - 57.0s
    (28.6, 35.0, "Traditional speech tools suffer from three fatal flaws. First: unilateral penalization bias."),
    (35.3, 42.5, "A dramatic rhetorical pause is naively flagged as dead air, and quiet emotional inflection as mumbling."),
    (42.8, 49.5, "Second, human feedback lacks timestamps and acoustic measurements."),
    (49.8, 57.0, "Third, existing ML corpora evaluate only what words were spoken, completely ignoring how they were delivered."),

    # Scene 3: 58.6s - 87.5s
    (58.6, 65.2, "To ground evaluation objectively, we constructed a custom paired contrastive speech dataset."),
    (65.5, 72.8, "We sourced and transcribed 48 masterclass public speeches—from MLK and JFK to Churchill and Steve Jobs."),
    (73.1, 80.5, "Holding speech text constant as a scientific control, our 6-dimensional flaw injection engine synthesizes a 4-tier spectrum..."),
    (80.8, 87.5, "...from pristine delivery to severe panic, temporally grounding every flaw with millisecond precision."),

    # Scene 4: 88.6s - 127.5s
    (88.6, 95.8, "The VOCODE pipeline begins with a 4-layer monologue gatekeeper, rejecting multi-speaker dialogue and background noise."),
    (96.1, 103.5, "Raw audio passes through a 7-stage broadcast standardization pipeline: 16 kHz sinc resampling..."),
    (103.8, 111.0, "...a 70 Hz high-pass filter eliminating microphone handling rumble, and EBU R128 loudness normalization."),
    (111.3, 119.0, "Next, our engine extracts dense 100 Hz physical telemetry: micro-prosodic pitch semitones, PAPR crest factor in dB..."),
    (119.3, 127.5, "...and adherence to the 20% Oratorical Pause Law, feeding directly into our non-unilateral rubric."),

    # Scene 5: 128.6s - 198.5s
    (128.6, 136.0, "Let's see VOCODE in action on our live dashboard. The landing portal features dual rotating tape reels with zero-storage streaming."),
    (136.5, 145.0, "First, we evaluate Dr. Martin Luther King Jr.'s masterclass delivery of 'I Have a Dream'. Overall score: 9.20 out of 10."),
    (145.5, 153.5, "The multi-track waveform highlights brilliant pitch excursions and resonant cadence across all five oratorical pillars."),
    (154.0, 162.0, "Now, we load the contrastive Tier 3 botched mirror of the exact same speech text. Instantly, the score drops to 4.70 out of 10."),
    (162.5, 171.0, "Look at the waveform: VOCODE isolates a 4.8-second dead-air freeze in crimson red, capping the score under the Paralyzing Silence ceiling."),
    (171.5, 180.0, "Clicking on any blunder card seeks the custom HTML5 audio player directly to the millisecond of failure."),
    (180.5, 198.5, "In the Coach tab, VOCODE delivers actionable pedagogical training: prescribing the 1-second eye-contact reset and 4 daily practice routines."),

    # Scene 6: 203.6s - 241.5s
    (203.6, 211.5, "Under the hood, VOCODE prevents unilateral false penalties through systemic impairment coupling."),
    (212.0, 220.5, "If an orator speaks softly but maintains agile pitch modulation and natural pausing, our engine recognizes an intimate rhetorical choice."),
    (221.0, 230.0, "Dynamic leniency calibration allows judges to toggle between strict competition forensics and novice coaching."),
    (230.5, 241.5, "Furthermore, continuous speech is partitioned into discrete Rhetorical Move Cards: Brilliant moves, Mistakes, and Blunders."),

    # Scene 7: 242.6s - 276.5s
    (242.6, 249.5, "VOCODE rigorously addresses all five official Hackathon evaluation criteria."),
    (250.0, 257.5, "Our 200-clip empirical benchmark demonstrates strong statistical correlation with expert human judges."),
    (258.0, 267.0, "We deliver 25% causal explainability through dual DSP and LLM reasoning, 30% robust data engineering across 48 masterclass speeches..."),
    (267.5, 276.5, "...20% feature extraction via 100 Hz physics, 15% interactive dashboard usability, and 10% containerized reproducibility."),

    # Scene 8: 277.6s - 296.0s
    (277.6, 284.5, "VOCODE is fully open source, containerized with Docker, and immediately reproducible across local environments."),
    (285.0, 291.5, "By bridging digital signal processing, contrastive dataset engineering, and generative AI coaching..."),
    (292.0, 296.0, "...VOCODE transforms public speaking into an empowering, objective science. Thank you.")
]

srt_out = "final video/vocode_captions.srt"
with open(srt_out, "w") as f:
    for idx, (t_start, t_end, txt) in enumerate(CAPTION_CHUNKS, 1):
        f.write(f"{idx}\n")
        f.write(f"{format_timestamp(t_start)} --> {format_timestamp(t_end)}\n")
        f.write(f"{txt}\n\n")

print(f"Synchronized SRT captions written to {srt_out}")
