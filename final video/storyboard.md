# VOCODE: 5-Minute Technical Showcase Video Storyboard

**Track:** Multimodal AI Hackathon 2026 — Track C: Contrastive Speech Analytics & Temporal Flaw Grounding  
**Target Video Duration:** 5 Minutes (300.0 Seconds)  
**Output Resolution:** 1920 × 1080 @ 30 fps (MP4 H.264 / AAC)  
**Voice-Over:** Adult Male English (`en-US-ryan-medium` / Neural TTS)  
**Deliverable Directory:** `final video/`

---

## Storyboard & Scene Progression

```
0:00        0:25               0:55             1:25                  2:05                                   3:25                  4:03            4:35        5:00
┌───────────┬──────────────────┬────────────────┬─────────────────────┬──────────────────────────────────────┬─────────────────────┬───────────────┬───────────┐
│ Scene 1   │ Scene 2          │ Scene 3        │ Scene 4             │ Scene 5                              │ Scene 6             │ Scene 7       │ Scene 8   │
│ Hook &    │ 3 Fatal Flaws    │ Dataset &      │ System Pipeline &   │ Live Web Application Demo            │ Architecture &      │ Official      │ Conclusion│
│ Crisis    │ of Adjudication  │ 4-Tier Gradient│ 7-Stage Standards   │ (Reels -> Presets -> Dial -> Wave)   │ Non-Unilateral Math │ Rubric Audit  │ & Deploy  │
└───────────┴──────────────────┴────────────────┴─────────────────────┴──────────────────────────────────────┴─────────────────────┴───────────────┴───────────┘
```

---

### Scene 1: Opening & The Adjudication Crisis (0:00 – 0:25 | 25.0s)
* **Slides:**
  * `0.0s – 10.0s`: `slide_1a_title.png` (Title card with dark-mode radial acoustics, Hackathon Track C badge, VOCODE title).
  * `10.0s – 25.0s`: `slide_1b_crisis.png` (Split comparison: Competitive Oratory vs. Real judge ballot marked *"Good energy, but work on your presence... score 78/100"*).
* **Narration (0.8s – 24.6s):**
  > *"Every year, millions of orators compete in forensics, declamation, and public keynotes. Yet speech evaluation remains trapped in an adjudication crisis: plagued by severe judge subjectivity, inconsistent scoring across ballots, and vague, non-actionable feedback. Today, we introduce VOCODE: a physics-grounded multimodal engine that transforms oratorical evaluation into an objective, reproducible, and explainable acoustic science."*
* **Visual Annotations:**
  * Badge: `MULTIMODAL AI HACKATHON 2026 • TRACK C`
  * Red callout box highlighting 0 timestamps, 0 metrics, 0 physical fixes on traditional ballots.
  * Emerald checkmarks highlighting VOCODE's 100 Hz physical telemetry and millisecond precision.

---

### Scene 2: The Three Fatal Flaws of Traditional Speech Adjudication (0:25 – 0:55 | 30.0s)
* **Slide:**
  * `25.0s – 55.0s`: `slide_2a_flaws.png` (Three-pillar forensic graphic analyzing the failure modes of traditional judging).
* **Narration (25.8s – 51.6s):**
  > *"Traditional speech tools suffer from three fatal flaws. First, unilateral penalization bias: a dramatic rhetorical pause is naively flagged as dead air, and quiet emotional inflection as mumbling. Second, human feedback lacks timestamps and acoustic measurements. Third, existing machine learning corpora evaluate only what words were spoken, completely ignoring the acoustic physics of how they were delivered. VOCODE was engineered to solve all three."*
* **Visual Annotations:**
  * Card 01 (Red): *Unilateral Penalization Bias* $\rightarrow$ Solved by Systemic Impairment Coupling ($\Psi_{\text{impair}}$).
  * Card 02 (Amber): *Subjective Feedback Gap* $\rightarrow$ Solved by Millisecond Temporal Grounding & Move Cards.
  * Card 03 (Cyan): *The ASR Corpus Void* $\rightarrow$ Solved by 4-Tier Contrastive Dataset across 48 Iconic Speeches.

---

### Scene 3: Objectives & The Custom Contrastive Dataset (0:55 – 1:25 | 30.0s)
* **Slide:**
  * `55.0s – 85.0s`: `slide_3a_dataset.png` (Dataset architecture: 48 Masterclass Speeches paired with the 4-tier synthetic degradation spectrum).
* **Narration (55.8s – 83.0s):**
  > *"To ground evaluation objectively, we constructed a custom paired contrastive speech dataset. We sourced and transcribed 48 masterclass public speeches—from Martin Luther King Jr. and John F. Kennedy to contemporary keynotes. Holding speech text constant as a scientific control, our six-dimensional flaw injection engine synthesizes a continuous four-tier degradation gradient—from pristine delivery to severe panic—temporally grounding every flaw with millisecond precision."*
* **Visual Annotations:**
  * Left Panel: *48 Iconic Masterclass Speeches* (`good speeches/`: MLK, JFK, Churchill, Jobs, McRaven, Chaplin).
  * Right Panel: *4-Tier Bad-Mirror Gradient* (Tier 0 Masterclass $\rightarrow$ Tier 1 Distinguished $\rightarrow$ Tier 2 Proficient $\rightarrow$ Tier 3 Botched).
  * Code Callout: Manifest JSON showing exact millisecond flaw intervals `[t_start, t_end]`.

---

### Scene 4: End-to-End System Pipeline & Standards (1:25 – 2:05 | 40.0s)
* **Slide:**
  * `85.0s – 125.0s`: `slide_4a_pipeline.png` (Full 6-stage engineering flowchart).
* **Narration (85.8s – 124.5s):**
  > *"The VOCODE pipeline begins with a four-layer monologue gatekeeper, rejecting multi-speaker dialogue and background noise before processing. Raw audio passes through a seven-stage physical broadcast standardization pipeline: 16-kilohertz sinc resampling, a 70-hertz high-pass filter to eliminate microphone handling rumble, and EBU R128 loudness normalization. Next, our engine extracts dense 100-hertz physical telemetry—tracking micro-prosodic pitch semitones, peak-to-average power ratio for vocal punchiness, and adherence to the 20% Oratorical Pause Law—feeding directly into our non-unilateral rubric."*
* **Visual Annotations:**
  * Stage 1: Ephemeral Ingestion (0 MB residual storage footprint).
  * Stage 2: 7-Stage Broadcast Standardization (Universal 32-bit decode, 16 kHz resample, 70 Hz HPF, -20 LUFS Norm).
  * Stage 3: 100 Hz Praat F0 & PAPR Crest Telemetry.
  * Stage 4: Non-Unilateral Scoring Engine.
  * Stage 5: Move Classifier (Rhetorical move hierarchy).
  * Stage 6: Dual LLM Reasoner (Groq Qwen 27B / Llama 3).

---

### Scene 5: Live Web Application Demonstration (2:05 – 3:25 | 80.0s)
* **Slides (Authentic 1080p Web Application Screenshots):**
  * `125.0s – 137.0s`: `slide_5a_landing.png` (Landing portal with 60 fps rotating dual tape reels on HTML5 canvas).
  * `137.0s – 149.0s`: `slide_5b_presets.png` (Audio loaded state, MLK preset selected, evaluate trigger button).
  * `149.0s – 163.0s`: `slide_5c_results_dial.png` (Baseline MLK Tier 0 run: Speedometer Score Dial at 9.20/10, 5-Pillar scores).
  * `163.0s – 177.0s`: `slide_5d_waveform.png` (Full-width Plotly waveform visualizer with Cyan/Green move bands and HTML5 player).
  * `177.0s – 191.0s`: `slide_5e_botched_freeze.png` (Contrastive MLK Tier 3 Botched mirror: Score drops to 4.70/10, Paralyzing Silence ceiling active, 4.8s dead-air freeze highlighted in crimson red).
  * `191.0s – 205.0s`: `slide_5f_coach_tab.png` (Coach Tab diagnostic suite, 1-second eye-contact reset physical drill, 4 daily practice routines).
* **Narration (125.8s – 186.5s):**
  > *"Let's see VOCODE in action on our live dashboard. The landing portal features dual rotating tape reels with zero-residual ephemeral streaming.*
  > 
  > *First, we evaluate Dr. Martin Luther King Jr.'s masterclass delivery of 'I Have a Dream.' VOCODE awards an overall score of 9.2 out of 10. The multi-track waveform highlights brilliant pitch excursions and resonant cadence across all five oratorical pillars.*
  > 
  > *Now, we load the contrastive Tier 3 botched mirror of the exact same speech text. Instantly, the composite score drops to 4.7 out of 10. Look at the waveform: VOCODE isolates a 4.8-second dead-air freeze in crimson red, and activates the dynamic Paralyzing Silence gating ceiling to cap the overall score.*
  > 
  > *Clicking on any blunder card seeks the custom HTML5 audio player directly to the millisecond of failure. In the Coach tab, VOCODE delivers actionable pedagogical training: prescribing the one-second eye-contact reset and four daily practice routines to correct vocal mechanics physically."*
* **Visual Presentation:**
  * Clean authentic 1080p application UI presentation.
  * Contrast comparison: Masterclass (9.20) vs. Botched (4.70) under identical speech text.

---

### Scene 6: Architecture & Non-Unilateral Scoring Math (3:25 – 4:03 | 38.0s)
* **Slide:**
  * `205.0s – 243.0s`: `slide_6a_architecture.png` (5 Pillars weight matrix, Dynamic Gate Ceiling formula, and Rhetorical Move hierarchy).
* **Narration (205.8s – 240.8s):**
  > *"Under the hood, VOCODE prevents unilateral false penalties through systemic impairment coupling. If an orator speaks softly but maintains agile pitch modulation and natural pausing, our engine recognizes an intimate rhetorical choice rather than penalizing low energy in isolation. Dynamic leniency calibration allows judges to toggle between strict competition forensics and novice coaching. Furthermore, continuous speech is partitioned into discrete Rhetorical Move Cards—categorizing delivery into Brilliant moves, Great transitions, Inaccuracies, Mistakes, and Blunders with complete causal explanations."*
* **Visual Structure:**
  * Formula Card: $\text{Gate Ceiling} = 10.0 - 0.55 \cdot (N_{\text{deficits}} - 1) - \Psi_{\text{impair}}$.
  * 5 Pillars breakdown: Pitch (2.5), Cadence (2.5), Pausing (2.0), Energy (1.5), Clarity (1.5).
  * Move Cards: Brilliant (Cyan), Great (Emerald), Good (Slate), Inaccuracy (Yellow), Mistake (Orange), Blunder (Red).

---

### Scene 7: Official Hackathon Rubric Alignment (4:03 – 4:35 | 32.0s)
* **Slide:**
  * `243.0s – 275.0s`: `slide_7a_rubrics.png` (Official Hackathon Track C criteria, weight percentages, and empirical benchmark results).
* **Narration (243.8s – 275.2s):**
  > *"VOCODE rigorously addresses all five official Hackathon evaluation criteria. Our 200-clip empirical benchmark demonstrates strong statistical correlation with expert human judges. We deliver 25% causal explainability through dual-layer DSP and LLM reasoning, 30% robust data engineering across 48 masterclass speeches and synthetic gradients, 20% rigorous feature extraction via 100-hertz physics, 15% interactive dashboard usability, and 10% containerized reproducibility."*
* **Visual Annotations:**
  * Official Criteria Weights: 25% Causal, 30% Data Eng, 20% Features, 15% Visualization, 10% Reproducibility.
  * Verified filepaths in repo for every judging parameter.
  * 200-Clip Benchmark Stats: Pearson $r = 0.461$ ($p < 0.001$), Spearman $\rho = 0.589$ ($p < 0.001$), MAE $= 1.17$ pts, Tier Agreement $= 71.0\%$.

---

### Scene 8: Conclusion & Reproducibility (4:35 – 5:00 | 25.0s)
* **Slide:**
  * `275.0s – 300.0s`: `slide_8a_conclusion.png` (Docker command, GitHub repository card, and closing emblem).
* **Narration (275.8s – 295.0s):**
  > *"VOCODE is fully open source, containerized with Docker, and immediately reproducible across local environments. By bridging digital signal processing, contrastive dataset engineering, and generative AI coaching, VOCODE transforms public speaking from a subjective gamble into an empowering, objective science. Thank you for watching."*
* **Visual Annotations:**
  * Docker command: `docker run -p 8501:8501 vocode:latest`.
  * GitHub repository banner: `https://github.com/lazarus/HackathonMM2`.
  * Final VOCODE emblem & Hackathon Track C credits.

---

## Technical Specifications Summary

| Property | Value |
| :--- | :--- |
| **Duration** | 300.00 Seconds (5:00.00) |
| **Resolution** | 1920 × 1080 (1080p Full HD) |
| **Frame Rate** | 30.0 fps constant |
| **Video Codec** | H.264 / AVC (`libx264`, High Profile, CRF 18, `yuv420p`) |
| **Audio Codec** | AAC-LC, 192 kbps, 44.1 kHz Stereo |
| **Voice-Over** | Offline Neural TTS (`en-US-ryan-medium`), normalized to -16 LUFS |
| **Music Track** | Subtle procedural ambient synthesizer pad, ducked to -24 LUFS |
| **Subtitles** | Synchronized SRT captions burned into video with semi-transparent backing |
