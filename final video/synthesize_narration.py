import os
import subprocess
import json

SCENES = [
    {
        "id": "scene1_intro",
        "title": "Opening & The Adjudication Crisis",
        "target_duration": 25.0,
        "text": "Every year, millions of orators compete in forensics, declamation, and public keynotes. Yet speech evaluation remains trapped in an adjudication crisis: plagued by severe judge subjectivity, inconsistent scoring, and vague feedback. Today, we introduce VOCODE—a physics-grounded multimodal engine that transforms oratorical evaluation into an objective, reproducible, and explainable acoustic science."
    },
    {
        "id": "scene2_problem",
        "title": "Problem Statement & The Three Fatal Flaws",
        "target_duration": 30.0,
        "text": "Traditional speech tools suffer from three fatal flaws. First, unilateral penalization: a dramatic rhetorical pause is naively flagged as dead air, and quiet emotional inflection as mumbling. Second, human feedback lacks timestamps and acoustic measurements. Third, existing machine learning corpora evaluate only what words were spoken, completely ignoring the acoustic physics of how they were delivered. VOCODE was engineered to solve all three."
    },
    {
        "id": "scene3_dataset",
        "title": "Objectives & The Contrastive Dataset",
        "target_duration": 30.0,
        "text": "To ground evaluation objectively, we constructed a custom contrastive speech dataset. We sourced and transcribed 48 masterclass public speeches—from Martin Luther King Jr. and John F. Kennedy to contemporary keynotes. Holding speech text constant as a control variable, our six-dimensional flaw injection engine synthesizes a continuous four-tier degradation gradient—from pristine delivery to severe panic—temporally grounding every flaw with millisecond precision."
    },
    {
        "id": "scene4_pipeline",
        "title": "End-to-End System Pipeline & Standards",
        "target_duration": 40.0,
        "text": "The VOCODE pipeline begins with a four-layer monologue gatekeeper, rejecting multi-speaker dialogue and background noise before processing. Raw audio passes through a seven-stage physical broadcast standardization pipeline: 16-kilohertz sinc resampling, a 70-hertz high-pass filter to eliminate microphone handling rumble, and EBU R128 loudness normalization. Next, our engine extracts dense 100-hertz physical telemetry—tracking micro-prosodic pitch semitones, peak-to-average power ratio for vocal punchiness, and adherence to the 20% Oratorical Pause Law—feeding directly into our non-unilateral rubric."
    },
    {
        "id": "scene5_demo",
        "title": "Live Web Application Demonstration",
        "target_duration": 80.0,
        "text": "Let's see VOCODE in action on our live dashboard. The landing portal features dual rotating tape reels with zero-residual ephemeral streaming. First, we evaluate Dr. Martin Luther King Jr.'s masterclass delivery of 'I Have a Dream.' VOCODE awards an overall score of 9.2 out of 10. The multi-track waveform highlights brilliant pitch excursions and resonant cadence across all five oratorical pillars. Now, we load the contrastive Tier 3 botched mirror of the exact same speech text. Instantly, the composite score drops to 4.7 out of 10. Look at the waveform: VOCODE isolates a 4.8-second dead-air freeze in crimson red, and activates the dynamic Paralyzing Silence gating ceiling to cap the overall score. Clicking on any blunder card seeks the custom HTML5 audio player directly to the millisecond of failure. In the Coach tab, VOCODE delivers actionable pedagogical training: prescribing the one-second eye-contact reset and four daily practice routines to correct vocal mechanics physically."
    },
    {
        "id": "scene6_architecture",
        "title": "Architecture & Non-Unilateral Scoring Math",
        "target_duration": 40.0,
        "text": "Under the hood, VOCODE prevents unilateral false penalties through systemic impairment coupling. If an orator speaks softly but maintains agile pitch modulation and natural pausing, our engine recognizes an intimate rhetorical choice rather than penalizing low energy in isolation. Dynamic leniency calibration allows judges to toggle between strict competition forensics and novice coaching. Furthermore, continuous speech is partitioned into discrete Rhetorical Move Cards—categorizing delivery into Brilliant moves, Great transitions, Inaccuracies, Mistakes, and Blunders with complete causal explanations."
    },
    {
        "id": "scene7_rubrics",
        "title": "Official Hackathon Rubric Alignment",
        "target_duration": 30.0,
        "text": "VOCODE rigorously addresses all five official Hackathon evaluation criteria. Our 200-clip empirical benchmark demonstrates strong statistical correlation with expert human judges. We deliver 25% causal explainability through dual-layer DSP and LLM reasoning, 30% robust data engineering across 48 masterclass speeches and synthetic gradients, 20% rigorous feature extraction via 100-hertz physics, 15% interactive dashboard usability, and 10% containerized reproducibility."
    },
    {
        "id": "scene8_conclusion",
        "title": "Conclusion & Reproducibility",
        "target_duration": 25.0,
        "text": "VOCODE is fully open source, containerized with Docker, and immediately reproducible across local environments. By bridging digital signal processing, contrastive dataset engineering, and generative AI coaching, VOCODE transforms public speaking from a subjective gamble into an empowering, objective science. Thank you for watching."
    }
]

AUDIO_DIR = "final video/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

MODEL = "piper_models/en_US-ryan-medium.onnx"
CONFIG = "piper_models/en_US-ryan-medium.onnx.json"

results = []

for idx, sc in enumerate(SCENES):
    out_wav = os.path.join(AUDIO_DIR, f"{sc['id']}.wav")
    print(f"Synthesizing {sc['id']} ({sc['title']})...")
    # Piper synthesis with length-scale 1.05 for clear, deliberate speech
    cmd = [
        "./venv/bin/piper",
        "-m", MODEL,
        "-c", CONFIG,
        "-f", out_wav,
        "--length-scale", "1.08"
    ]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate(input=sc["text"].encode("utf-8"))
    
    # Check duration using ffprobe
    probe_cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", out_wav
    ]
    dur = float(subprocess.check_output(probe_cmd).decode("utf-8").strip())
    print(f"  -> Generated {dur:.2f}s (Target: {sc['target_duration']}s)")
    
    results.append({
        "index": idx,
        "id": sc["id"],
        "title": sc["title"],
        "target_duration": sc["target_duration"],
        "speech_duration": dur,
        "text": sc["text"],
        "wav_path": out_wav
    })

with open("final video/audio/narration_manifest.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nSynthesis complete! Total speech duration:", sum(r["speech_duration"] for r in results), "seconds.")
