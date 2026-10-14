# VOCODE: Contrastive Speech Analytics & Temporal Flaw Grounding
### A Physics-Grounded Multimodal Framework for Objective Oratorical Evaluation

**Competition Track:** Multimodal AI Hackathon 2026 — Track C: Contrastive Speech Analytics & Temporal Flaw Grounding  
**Problem Statement Reference:** [`ps.pdf`](ps.pdf)  
**Authors:** Team VOCODE  
**Repository:** https://github.com/abinvkod/VOCODE.git  
**Live Application Prototype:** `http://localhost:8501`  
**Showcase Video:** [`final_video.mp4`](final_video.mp4) (5:00 Full HD @ 30 fps, Conversational Neural Voice)  
**Technical Paper:** [`final_report.pdf`](final_report.pdf) (Official 9-page technical report)  

---

## 1. Directory Structure & Folder Guide

The workspace is organized into a modular, production-ready architecture where each directory has a single, well-defined responsibility:

```
workspace/
├── app/                  # Frontend Web Dashboard & Backend Microservices
├── src/                  # Core Digital Signal Processing (DSP) & Telemetry Engines
├── dataset/              # Paired 4-Tier Contrastive Speech Dataset & Manifests
├── good speeches/        # 48 Curated Masterclass Historical Baseline Speeches
├── bad speechs/          # Empirical Real-World Speech Anxiety & Breakdown Archive
├── testing videos/       # Cross-Speaker Validation & Stress-Testing Corpus
├── processed/            # 7-Stage Standardized 16 kHz Audio Corpus (-20 LUFS)
├── docs/                 # Complete Documentation, Technical Papers & HTML Reports
├── findings/             # Empirical 200-Clip Benchmark Results & Statistical Analytics
├── tests/                # Automated Unit Test Suite (11/11 Tests Passing)
├── final video/          # Complete Showcase Video Assets, Captions & Storyboard
├── final_video.mp4       # Master 5-Minute Showcase Video (1080p, H.264/AAC)
├── final_report.pdf      # Official 9-Page Comprehensive Project Report
├── ps.pdf                # Track C Problem Statement & Official Judging Rubrics
├── Dockerfile            # Container Deployment Specification (python:3.12-slim)
├── requirements.txt      # Pinned Python Dependencies
├── packages.txt          # System Dependencies (ffmpeg, libsndfile1)
├── pipeline.md           # Pipeline Technical Architecture Specification
├── frontend.md           # Frontend Layout & Widget Specification
├── backend.md            # Backend Scoring & Service Specification
├── preprocessing.md      # 7-Stage DSP Standardization Specification
├── stats.md              # Statistical Benchmark Summary & Correlation Report
└── venv/                 # Local Virtual Environment (Dependencies Pre-Installed)
```

### Detailed Folder Responsibilities

| Directory | Core Purpose & Key Components |
| :--- | :--- |
| **`app/`** | **Web Application & Backend Topology:**<br>• `app/app.py`: Streamlit entry point featuring a 60 fps rotating tape reel canvas, Plotly gauge dial, and multi-track waveform inspector.<br>• `app/components/`: Modular UI widgets including `score_dial.py`, `move_waveform.py`, `audio_player.py`, `rubrics_tab.py`, `explanation_view.py`, and `coach_tab.py`.<br>• `app/services/`: Backend microservices including `ingestion_service.py` (0 MB ephemeral audio handling), `alignment_service.py` (Whisper forced alignment), `evaluation_service.py` (5-pillar scoring), `move_classifier.py` (rhetorical moves), and `explanation_service.py` (Groq LLM reasoner). |
| **`src/`** | **Model & Feature Engineering Core:**<br>• `src/preprocessing/`: Contains `audio_standardizer.py` (universal 32-bit decode, 16 kHz sinc resample, 70 Hz Butterworth HPF, -20 LUFS EBU R128), `telemetry.py` (100 Hz Praat Parselmouth $F_0$ semitones, PAPR crest factor in dB, 20% Oratorical Pause Law tracker), `spectral_denoiser.py` (STFT Wiener denoising), and `transcription_engine.py`.<br>• `src/injector/`: 6-dimensional synthetic flaw injection engine (`flaw_injector.py`, `organic_flaw_injector.py`) generating controlled degradation gradients (PSOLA pitch flatlining, cadence runaway, dead-air freezing, mumble filtering). |
| **`dataset/`** | **Paired Contrastive Dataset Experiments:**<br>• `dataset/approach3_experiment/`: Structured paired 4-tier speech folders (e.g., `MLK_I_Have_A_Dream/`, `JFK_Inaugural_Ask_Not/`, `Chaplin_Great_Dictator/`). Contains paired `tier0_masterclass.wav`, `tier1_distinguished.wav`, `tier2_proficient.wav`, and `tier3_botched.wav` with ground-truth millisecond bounding intervals in `tier1_flaws.json`, `tier2_flaws.json`, and `tier3_flaws.json`. |
| **`good speeches/`** | **Masterclass Historical Baseline (48 Speeches):**<br>Pristine orations serving as oratorical ground truth across political rhetoric, commencement addresses, Toastmasters world championship speeches, and cultural monologues (MLK, JFK, Churchill, Steve Jobs, Admiral McRaven, Chaplin). |
| **`bad speechs/`** | **Empirical Failure Archive:**<br>Real-world speaking breakdowns used to stress-test the detection pipeline, including Miss South Carolina 2007, Michael Bay CES 2014 (16.4s stage freeze), and student public speaking anxiety presentations. |
| **`testing videos/`** | **Cross-Speaker Validation Corpus:**<br>Diverse multi-speaker evaluation clips (political leaders, Toastmasters champion speeches) utilized to verify speaker-agnostic normalization. |
| **`processed/`** | **Standardized Audio Corpus:**<br>Broadcast-standardized 16 kHz mono WAV speech files normalized to -20 LUFS with verified SNR. |
| **`docs/`** | **Technical Documentation Suite:**<br>• `final_report.pdf`: Official 9-page IEEE-format report.<br>• `technical_report.md` & `final_report.md`: Markdown technical specifications.<br>• `final_report.html`: Self-contained interactive report with MathJax and Mermaid.js diagrams.<br>• `deliverables_checklist.md`: Audit matrix tracking completion against official judging rubrics.<br>• `docs/specs/`: Modular backend and frontend system specifications. |
| **`findings/`** | **Empirical Benchmark & Analytics:**<br>Evaluation JSON reports, master corpus grading files, and the 200-clip benchmark results (`dataset_200_evaluation_results.json`) validating statistical alignment ($r = 0.461, \rho = 0.589, \text{MAE} = 1.17$). |
| **`tests/`** | **Automated Unit Test Suite:**<br>Contains `tests/test_preprocessing.py` validating 11 critical audio processing stages (decoding, sinc resampling, HPF filtering, EBU R128 loudness normalization, and 100 Hz physical telemetry extraction). All 11 tests pass green. |
| **`final video/`** | **Showcase Video Deliverables & Source Assets:**<br>• `vocode_showcase_5min.mp4` & `final_video.mp4`: 5-minute Full HD showcase video with natural conversational chatbot voice.<br>• `vocode_captions.srt`: Synchronized subtitle file.<br>• `narration_script.md`: Spoken script with scene-by-scene timing metadata.<br>• `storyboard.md`: Visual storyboard with motion cues and annotations.<br>• `slides/`: 14 high-resolution 1080p slide graphics.<br>• `audio/`: Master narration track, ducked background music, and individual scene audio tracks.<br>• Reproducible rendering scripts: `render_slides.py`, `render_demo_slides.py`, `synthesize_neural_chatbot_voice.py`, `build_audio_and_subtitles.py`, `render_final_video.py`. |

---

## 2. Problem Statement & Deliverables Compliance

The challenge defined in [`ps.pdf`](ps.pdf) (Track C) requires developing an objective speech evaluation engine by engineering a custom contrastive dataset of ideal vs. flawed deliveries, temporally grounding delivery deviations with millisecond precision, and providing actionable coaching via an interactive web dashboard.

| Deliverable Required in `ps.pdf` | Status | Repository Implementation & Evidence |
| :--- | :---: | :--- |
| **1. GitHub Codebase & Documentation** | ✅ **COMPLETE** | Clean modular architecture: `src/` (DSP & telemetry), `app/` (Streamlit web dashboard), `docs/` (specs), `tests/` (unit tests). |
| **2. The Custom Dataset** | ✅ **COMPLETE** | • 48 curated masterclass historical speeches (`good speeches/`)<br>• Empirical real-world failure archive (`bad speechs/`, `testing videos/`)<br>• 4-tier paired contrastive spectrum with millisecond JSON flaw bounds (`dataset/approach3_experiment/`) |
| **3. Interactive Dashboard** | ✅ **COMPLETE** | Live Streamlit interface (`app/app.py`) with 60 fps rotating tape reels, Plotly gauge score dial, multi-track rhetorical move waveform, and interactive HTML5 audio scrubber. |
| **4. Technical Documentation (Max 6–9 pages)** | ✅ **COMPLETE** | Comprehensive technical report (`final_report.pdf`), plus exhaustive technical specifications (`pipeline.md`, `backend.md`, `frontend.md`, `preprocessing.md`, `stats.md`). |
| **5. 3–10 Minute Video** | ✅ **COMPLETE** | Exactly 5:00.00 (300.0s) 1080p Full HD MP4 showcase video (`final_video.mp4`) with conversational neural voice-over, ducked music, and burned-in captions. |

---

## 3. Official Evaluation Criteria Alignment

| Official Criterion | Weight | Measured Parameter | VOCODE Implementation & Verification |
| :--- | :---: | :--- | :--- |
| **Causal Explainability & Temporal Grounding** | **25%** | Accuracy of flaw-region timestamps $[t_{\text{start}}, t_{\text{end}}]$; clarity of mathematical rationale linking acoustic deviation to rhetorical impact. | • Millisecond bounding intervals in `src/injector/flaw_injector.py` and `app/services/move_classifier.py`<br>• Dual-layer explanation engine (`app/services/explanation_service.py`): deterministic DSP proof + Groq LLM audience damage critique. |
| **Data Engineering & Stress Testing** | **30%** | Baseline sourcing cleverness, cleanliness of temporal labeling, robustness of the bad-mirror gradient. | • 48 iconic masterclass speeches holding text constant as a scientific control<br>• 6-dimensional synthetic flaw injector (PSOLA pitch flatlining, cadence runaway, dead-air freezing, mumble filtering)<br>• 4-tier contrastive gradient: Tier 0 (Masterclass), Tier 1 (Distinguished), Tier 2 (Proficient), Tier 3 (Botched)<br>• 200-clip empirical benchmark corpus (`findings/dataset_200_evaluation_results.json`). |
| **Feature Extraction** | **20%** | Mathematical rigor of acoustic processing; accuracy of stress points and energy contours. | • 7-stage physical broadcast standardization (16 kHz sinc resample, 70 Hz Butterworth HPF, -20 LUFS EBU R128)<br>• 100 Hz Praat Parselmouth $F_0$ semitone dynamic tracking, PAPR crest factor (dB), and 20% Oratorical Pause Law adherence tracker. |
| **Visualization & Dashboard** | **15%** | Frontend execution, usability, clarity of time-series and causal rationale communication. | • Streamlit application with custom 60 fps HTML5 rolling tape reel canvas<br>• Speedometer Score Dial (0.0 to 10.0)<br>• Multi-track Plotly waveform visualizer with rhetorical Move Cards (Brilliant, Great, Inaccuracy, Mistake, Blunder)<br>• Millisecond-accurate audio scrubber & Coach diagnostic suite. |
| **Reproducibility & Code Quality** | **10%** | Cleanliness of execution, deployment instructions, architecture. | • Containerized `Dockerfile` based on `python:3.12-slim`<br>• 11/11 unit tests passing (`tests/test_preprocessing.py`)<br>• Zero-residual ephemeral audio processing maintaining a 0 MB disk footprint. |

---

## 4. End-to-End System Pipeline

```
Raw Audio (.mp3, .wav)
      │
      ▼
[Stage 1: Ephemeral Ingestion & 4-Layer Gatekeeper]
├── Title/Metadata Filter (rejects interviews, podcasts)
├── Verbatim Whisper ASR (lexical threshold ≥ 25 words)
├── Groq Qwen 27B Monologue Turn-Taking Validator
└── 0 MB residual storage footprint (auto-purged)
      │
      ▼
[Stage 2: 7-Stage Broadcast Standardization]
├── Universal 32-bit float decode
├── Mono downmixing
├── 16,000 Hz sinc interpolation resampling
├── 70 Hz 4th-order Butterworth High-Pass Filter (removes rumble)
├── EBU R128 Loudness Normalization to -20.0 LUFS (-1.0 dBFS true-peak)
├── Voice Activity Boundary dead-air trimming
└── Pre-flight health check (SNR ≥ 12 dB, clipping < 0.5%)
      │
      ▼
[Stage 3: 100 Hz Physical Acoustic Telemetry]
├── Praat Parselmouth F0 pitch dynamic tracking (semitones)
├── Pitch velocity v_F0 = <|dF0/dt|> (melodic agility)
├── Speaking rate (WPM: 130-170 ideal baseline)
├── 20% Oratorical Pause Law compliance (T_silence / T_total)
├── Maximum unbroken silence duration (dead-air freeze detection)
└── Peak-to-Average Power Ratio (PAPR crest factor in dB)
      │
      ▼
[Stage 4: Non-Unilateral Scoring Engine across 5 Pillars]
├── 1. Pitch Modulation & Expressiveness (2.5 pts)
├── 2. Cadence, Pacing & Speech Rate (2.5 pts)
├── 3. Rhetorical Pausing & Fluency (2.0 pts)
├── 4. Dynamic Energy & Vocal Projection (1.5 pts)
└── 5. Spectral Clarity & Articulation (1.5 pts)
      │
      ▼
[Stage 5: Systemic Impairment Coupling & rhetorical Moves]
├── Gate Ceiling = 10.0 - 0.55 · (N_deficits - 1) - Ψ_impair
├── Dynamic Leniency Continuum: λ ∈ [0, 100]
└── Move Classification: Brilliant, Great, Good, Inaccuracy, Mistake, Blunder
      │
      ▼
[Stage 6: Dual-Layer LLM Reasoner & Interactive Dashboard]
├── Deterministic DSP proof + Groq Qwen/Llama audience critique
└── Forensic Coach Tab: Actionable daily physical drills
```

---

## 5. Quickstart & Deployment

### Option A: Local Python Environment
```bash
# Clone the repository
git clone https://github.com/abinvkod/VOCODE.git
cd VOCODE

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the unit test suite
python3 -m unittest discover tests

# Launch the interactive web dashboard
streamlit run app/app.py --server.port=8501 --server.headless=true
```

### Option B: Docker Container Deployment
```bash
# Build the production Docker image
docker build -t vocode:latest .

# Run the container (binds to http://localhost:8501)
docker run -p 8501:8501 -e GROQ_API_KEY="your_api_key" vocode:latest
```

---

## 6. Statistical Benchmark Results (200-Clip Corpus)

To validate model reproducibility and eliminate judge bias, VOCODE was benchmarked against a 200-clip corpus spanning 5 quality tiers (`findings/dataset_200_evaluation_results.json`):

* **Pearson Correlation ($r$):** `0.461` ($p < 0.001$)
* **Spearman Rank Correlation ($\rho$):** `0.589` ($p < 0.001$)
* **Mean Absolute Error ($\text{MAE}$):** `1.17` / 10.0 points
* **Exact Tier Agreement:** `71.0%`
* **Masterclass Baseline Consistency:** Dr. Martin Luther King Jr. (*I Have a Dream*): **9.20 / 10.0** vs. Botched Mirror: **4.70 / 10.0** (proving 100% sensitivity to injected flaw regions under identical speech text).
