# Vocode: Contrastive Speech Analytics & Temporal Flaw Grounding
## A Physics-Grounded Multimodal Framework for Objective Oratorical Evaluation

**Authors:** Team Vocode (Hackathon 2026 - Track C)  
**Track:** Contrastive Speech Analytics & Temporal Flaw Grounding  
**Problem Statement Reference:** `ps.pdf`  
**Repository:** `./` | **Live Web App:** `http://localhost:8501`

---

### Abstract
Evaluating competitive spoken rhetoric (interpretive reading, persuasive oratory, declamation, and extemporaneous speech) has historically suffered from extreme judge subjectivity, halo effects, and vague post-hoc feedback. In this paper, we present **Vocode**, a physics-grounded speech evaluation system built on a custom contrastive dataset of paired ideal and flawed speeches across a 4-tier degradation spectrum. Vocode extracts 100 Hz frame-rate acoustic telemetry (fundamental frequency $F_0$, semitone dynamic range, PAPR crest factor, pause distributions, and spectral flux) aligned via Whisper automatic speech recognition. Rather than relying on black-box classification, Vocode implements a **Non-Unilateral 5-Pillar Rubric** with dynamic leniency calibration ($\lambda \in [0, 100]$) and a systemic impairment index ($\Psi_{\text{impair}}$) to eliminate unilateral false penalties. Furthermore, Vocode grounds failure intervals $[t_{\text{start}}, t_{\text{end}}]$ with millisecond precision, classifies oratorical maneuvers into Chess.com-style move cards (*Brilliant*, *Mistake*, *Blunder*), and generates prescriptive physical vocal remediation through an interactive web dashboard.

---

### 1. Introduction & Problem Formulation
Competitive forensics and public address evaluate two orthogonal dimensions: **what** is said (semantic argument quality) and **how** it is delivered (acoustic prosody, cadence, volume modulation, and pausing). Human adjudication suffers from three systemic failure modes:
1. **Unilateral Scoring Bias:** Single transient anomalies (e.g., a deliberate dramatic silence or a quiet emotional whisper) are often penalized as "dead-air freezes" or "mumbling" by naive acoustic thresholds.
2. **Subjective Feedback Gap:** Competitors receive qualitative impressions (e.g., *"work on your energy"*) rather than mathematically reproducible diagnoses.
3. **Absence of Paired Contrastive Ground Truth:** Standard speech corpora (e.g., LibriSpeech, CommonVoice) isolate word error rate (WER) rather than delivery quality, lacking paired recordings of the exact same text delivered across masterclass and failed styles.

Vocode resolves these challenges through an end-to-end architecture:
```
[Raw Audio + Text] 
       │
       ▼
[Phase 1: Broadcast Standardization] (16kHz Mono, 70Hz HPF, -20 LUFS EBU R128, Silence Trim)
       │
       ▼
[Phase 2: ASR Forced Alignment & Disfluency Parsing] (Whisper Timestamps + Lexical Stutter Detection)
       │
       ▼
[Phase 3: 100 Hz Acoustic Telemetry] (Parselmouth Praat F0, RMS dB, PAPR Crest Factor, 20% Pause Law)
       │
       ▼
[Phase 4: Non-Unilateral Scoring & Gating] (5 Pillars, PSI Coupling, Leniency Continuum λ)
       │
       ▼
[Phase 5: Temporal Grounding & Move Classification] (Chess.com Move Cards, Jump Seeking)
       │
       ▼
[Phase 6: Dual-Layer Causal Explainability & Coach Tab] (DSP Physics + Semantic Perception + Drills)
```

---

### 2. Custom Contrastive Dataset & 4-Tier Gradient
To establish empirical ground truth, we engineered a three-part dataset:

#### 2.1 The Masterclass Baseline Corpus (48 Speeches)
We sourced, cleaned, and cataloged 48 iconic speeches spanning:
* Historic Political Orators: JFK (Inaugural Address), MLK ("I Have a Dream"), Winston Churchill ("We Shall Fight on the Beaches"), Franklin D. Roosevelt ("Day of Infamy"), Abraham Lincoln (Gettysburg Address).
* Dramatic & Cultural Champions: Charlie Chaplin (*The Great Dictator*), Denzel Washington, Steve Jobs (Stanford Commencement), Rick Rigsby, Jon Stewart (9/11 First Responders Testimony).
* Contemporary Keynotes & Awards: Barack Obama (2008 Acceptance), Leonardo DiCaprio (88th Oscars Best Actor).

#### 2.2 Empirical Real-World Failure Corpus
We curated benchmark real-world oratorical collapses to stress-test detection under actual stage failure:
* Miss South Carolina 2007 (severe syntactic disorientation and filler word loop).
* Michael Bay CES 2014 (paralyzing 16.4s dead-air freeze leading to stage walk-off).
* Miss California 2016 (nervous cadence runaway and cadence collapse).
* Mariah Carey Palm Springs Gala (monotone slurred delivery).

#### 2.3 The 4-Tier Synthetic & Organic Flaw Injection Engine
Using PSOLA (Pitch Synchronous Overlap-Add) and Butterworth dynamic spectral filtering (`src/injector/`), we synthesized paired contrastive gradients across 6 mandatory acoustic failure dimensions:
1. *Monotone Compression:* Pitch modulation flattened to $< 5.0$ semitones.
2. *Cadence Runaway:* Speech rate accelerated beyond $> 220$ WPM ($> 6.4$ syl/s).
3. *Dead-Air Freeze:* Zero-energy pauses exceeding $> 3.0$ seconds.
4. *Clipped Pauses:* Respiratory pauses compressed below $< 200$ ms.
5. *Inverted Energy Dynamics:* PAPR inversion damping emphatic peaks.
6. *Spectral Mumbling:* Low-pass filter at 1200 Hz attenuating consonant formants.

We packaged canonical 4-tier paired benchmarks for MLK, JFK, and Chaplin (`dataset/approach3_experiment/`):
* **Tier 0 (Masterclass):** Unaltered, high-dynamism delivery ($\ge 8.5/10$).
* **Tier 1 (Distinguished):** Subtle inflection restraint or minor pause deviation ($7.5 - 8.4/10$).
* **Tier 2 (Proficient / Compromised):** Noticeable pacing rushes and clipped breaths ($6.0 - 7.4/10$).
* **Tier 3 (Botched / Failure):** Paralyzing dead-air freezes, monotone flatlines, and stammer loops ($< 5.5/10$).

---

### 3. Multimodal Feature Extraction & Signal Processing
To guarantee speaker-agnostic comparison, audio is processed through physical standardization:
* **Resampling:** 16,000 Hz polyphase sinc filtering (`soxr_hq`).
* **DC & Sub-Rumble Stripping:** 4th-order Butterworth high-pass filter at 70 Hz.
* **Loudness Normalization:** ITU-R BS.1770-4 / EBU R128 integrated loudness calibrated to $-20.0 \pm 0.5$ LUFS with true-peak limiter ceiling at $-1.0$ dBFS.
* **Consonant Protection:** Preservation of high-frequency sibilants ($> 2.5$ kHz), completely eliminating destructive HPSS transient attenuation.

#### 100 Hz Acoustic Telemetry Metrics
Extracted at a 10 ms hop size using Parselmouth Praat and librosa:
* **Pitch Modulation ($F_0$):** Micro-prosodic tracking in semitones:
  $$\Delta F_{0,\text{st}} = 12 \log_2 \left(\frac{P_{95}(F_0)}{P_{05}(F_0)}\right), \quad \text{Pitch Velocity } v_{F_0} = \left\langle \left|\frac{dF_0}{dt}\right| \right\rangle$$
* **Dynamic Energy & PAPR Crest Factor:**
  $$\text{PAPR} = \frac{\max(s^2(t))}{\langle s^2(t) \rangle}$$
  Quantifies vocal punchiness and emphasis contrast.
* **The 20% Pause Law:** Ratio of acoustic silence frames to total utterance duration:
  $$\rho_{\text{pause}} = \frac{T_{\text{pause}}}{T_{\text{total}}} \quad (\text{Optimal Masterclass Window: } 17\% - 23\%)$$
* **Disfluency & Stutter Parsing:** Consecutive adjacent lexical word runs ($w_i = w_{i+1}$), multi-word phrase loops, and filler density ($\text{fillers}/\text{min}$).

---

### 4. Non-Unilateral Scoring Engine & Multi-Leniency Calibration
The speech is graded on a calibrated **10.0-point rubric** partitioned across 5 core pillars:
1. **Pitch Modulation & Expressiveness:** Max 2.5 pts (penalizes flatlines $< 10.56$ st and sluggish velocity).
2. **Cadence, Pacing & Speech Rate:** Max 2.5 pts (penalizes runaways $> 220$ WPM and dragging $< 110$ WPM).
3. **Rhetorical Pausing & Fluency:** Max 2.0 pts (penalizes breathless run-ons $< 14\%$, freezes $> 3.0$s, and lexical stutters).
4. **Dynamic Energy & Vocal Projection:** Max 1.5 pts (penalizes PAPR $< 20$ dB and vocal shouting strain).
5. **Spectral Clarity & Enunciation:** Max 1.5 pts (penalizes spectral slurring and low-frequency rolloff).

#### Systemic Impairment Index ($\Psi_{\text{impair}}$) & Dynamic Gating
To prevent unilateral failures from collapsing good speeches, penalties are coupled:
$$\text{Gate Ceiling} = 10.0 - 0.55 \cdot (N_{\text{deficits}} - 1) - \Psi_{\text{impair}}$$
If a speaker has isolated quiet dynamics but high pitch inflection and optimal cadence, the score is not unilaterally destroyed.

#### Dynamic Leniency Calibration ($\lambda \in [0, 100]$)
A continuous user-adjustable slider scales penalties:
$$\text{Penalty}_{\text{effective}}(\lambda) = \text{Penalty}_{\text{strict}} \cdot \left(1.0 - 0.65 \cdot \frac{\lambda}{100}\right)$$
* $\lambda = 0$: Strict competition judging standard (penalizes severe flaws down to $4.0 - 5.5/10$).
* $\lambda = 50$: Balanced corporate / professional standard ($6.5 - 7.5/10$).
* $\lambda = 100$: Encouraging pedagogical / novice standard (forgiving flaws up to $7.5 - 8.5/10$).

---

### 5. Temporal Grounding & Move Classification
Vocode maps rhetorical performance onto a temporal continuum using **Chess.com-style Move Cards**:
* ✨ **Brilliant Move:** Emphatic pitch excursion ($\Delta F_0 > 14$ st) synchronized with high PAPR crest factor ($> 30$ dB) and dramatic pause.
* 🎯 **Great Move:** Fluid cadence ($130 - 175$ WPM) with natural vocal inflection.
* 👍 **Good Move:** Baseline clear delivery meeting standard criteria.
* ⚠️ **Inaccuracy:** Mild hesitation or slightly restrained pitch modulation.
* ⚡ **Mistake:** Rushed runaway ($> 220$ WPM), clipped respiratory pauses, or lexical word repetitions.
* ❌ **Blunder:** Stage dead-air freeze ($> 3.0$s), robotic monotone flatline ($< 5.0$ st), or stammer repetition loops.

Each move card renders with a **▶ Jump** button that seeks the HTML5 raw audio player to the exact millisecond of the event.

---

### 6. Experimental Evaluation & Validation

#### 6.1 Contrastive Gradient Validation (MLK, JFK, Chaplin)
| Benchmark Speech | Tier 0 (Masterclass) | Tier 1 (Distinguished) | Tier 2 (Proficient) | Tier 3 (Botched) |
| :--- | :---: | :---: | :---: | :---: |
| **MLK: "I Have a Dream"** | **9.2 / 10** | **8.1 / 10** | **6.8 / 10** | **4.7 / 10** |
| **JFK: Inaugural Address** | **8.9 / 10** | **8.0 / 10** | **6.6 / 10** | **4.9 / 10** |
| **Chaplin: The Great Dictator** | **9.5 / 10** | **8.3 / 10** | **6.9 / 10** | **4.8 / 10** |

#### 6.2 Real-World Edge Case Validation
* **Miss South Carolina 2007:** Graded **4.8 / 10** (Tier 3). System caught severe filler word clutter (14.2/min), syntactic restarts, and rapid cadence runaway (212 WPM).
* **Michael Bay CES Freeze:** Graded **4.2 / 10** (Tier 3). System isolated the 16.4s dead-air freeze $[t=24.1\text{s}, t=40.5\text{s}]$, capping the score via the Paralyzing Silence gating ceiling.
* **Leonardo DiCaprio 88th Oscars Acceptance:** Graded **6.2 / 10** (Strict) / **7.2 / 10** (Professional). System identified perfect spectral clarity (1.5/1.5) but penalized the 12.0% breathless run-on pause ratio and 3 teleprompter-induced monotone flatline zones (<5 st).

---

### 7. Interactive Dashboard & Implementation
The frontend is implemented in Streamlit and Plotly (`app/app.py`):
1. **Landing Portal:** Interactive HTML5 Canvas audio signal particle background with a central Evaluator square.
2. **Main Dashboard:** Glitch-animated `VOCODE` title, clean audio file uploader, and quick contrastive preset picker.
3. **Multi-Track Plotly Visualizer:** Synchronized pitch $F_0$ contour and RMS energy overlay with colored rhetorical move bands.
4. **Tabbed Suite:**
   * `🧑‍🏫 Coach`: Mistake-by-mistake forensic analysis, audience psychological impact, exact physical fix, and 4 daily practice routines.
   * `🔬 Technical Breakdown`: Deterministic acoustic physics & DSP threshold explanations.
   * `🎭 Qualitative Breakdown`: Semantic audience perception via Groq Qwen 27B LLM.
   * `🎯 Breakdown`: Chronological Chess.com move cards with filtering.
   * `📊 Rubrics`: 5-Pillar Scorecards, 5-Pillar Radar Chart, and itemized mathematical deduction audit ledger.
   * `📈 Deep Telemetry`: Full 12-factor acoustic metrics.

---

### 8. Conclusion
Vocode proves that oratorical speech evaluation can be transformed from subjective human guesswork into an objective, reproducible, and pedagogically actionable science. By combining a 4-tier contrastive dataset, physical DSP feature extraction, non-unilateral rubric scoring, and Chess.com-style temporal grounding, Vocode delivers exact mathematical accountability alongside empathetic, world-class coaching.
