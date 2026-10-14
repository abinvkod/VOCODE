# Backend Architecture Specification

**Project:** Track C: Contrastive Speech Analytics & Temporal Flaw Grounding  
**Target Module:** `app/services/` & `src/`  
**LLM Engine:** Groq Cloud (`llama-3.1-8b-instant`)  
**Status:** Validated Architecture  

---

## 1. Executive Summary

The backend acts as an objective, physics-grounded acoustic laboratory and reasoning engine. It ingests arbitrary multi-format audio files, standardizes them into a pristine 16 kHz acoustic master, extracts 100 Hz physical telemetry, evaluates delivery against a 10.0-point non-unilateral rubric across 5 oratorical pillars, categorizes phrase intervals into Chess.com-style rhetorical moves, and prompts Groq Cloud's open-source `llama-3.1-8b-instant` to synthesize deterministic acoustic proofs and semantic audience perceptions.

---

## 2. High-Level Backend Service Topology

```
                  Arbitrary Raw Audio Upload
         (.mp3, .wav, .m4a, .ogg, .flac) + Optional Transcript
                                │
                                ▼
         ┌──────────────────────────────────────────────┐
         │ 1. INGESTION SERVICE (ingestion_service.py)  │
         │ • Universal decoding via FFmpeg / SoundFile  │
         │ • Downmix to mono, resample to 16,000 Hz     │
         │ • 70 Hz Butterworth HPF & -20.0 LUFS EBU R128│
         │ • Boundary silence trimming & STFT Denoising │
         └──────────────────────┬───────────────────────┘
                                │ Standardized 16kHz Master WAV
                                ▼
         ┌──────────────────────────────────────────────┐
         │ 2. ALIGNMENT SERVICE (alignment_service.py)  │
         │ • Dual-Mode Canonical Transcript Resolution  │
         │ • Whisper base.en forced alignment           │
         │ • Word-level millisecond intervals [ts, te]  │
         │ • WER pronunciation validation               │
         └──────────────────────┬───────────────────────┘
                                │ Timestamped Speech Events
                                ▼
         ┌──────────────────────────────────────────────┐
         │ 3. EVALUATION SERVICE (evaluation_service.py)│
         │ • 100 Hz Parselmouth Praat F0 Pitch Tracking │
         │ • Short-Time RMS dB Energy & PAPR Crest      │
         │ • 20% Pause Law & Max Silence (max Δt)       │
         │ • Non-Unilateral Gate (Psi_impair & lambda)  │
         │ • 10.0-Point Rubric across 5 Pillars         │
         └──────────────────────┬───────────────────────┘
                                │ Deductions & Telemetry JSON
                                ▼
         ┌──────────────────────────────────────────────┐
         │ 4. MOVE CLASSIFIER (move_classifier.py)      │
         │ • Chess.com rhetorical categorization        │
         │ • Brilliant, Great/Good, Inaccuracy,         │
         │   Mistake, Blunder intervals                 │
         └──────────────────────┬───────────────────────┘
                                │ Move Metadata Array
                                ▼
         ┌──────────────────────────────────────────────┐
         │ 5. EXPLANATION SERVICE (explanation_service) │
         │ • Groq Cloud API (llama-3.1-8b-instant)      │
         │ • Deterministic Physical Acoustic Rationale  │
         │ • Semantic Human Audience Perception         │
         │ • Actionable Vocal Coaching Drills           │
         │ • Rule-Based Forensic Fallback Engine        │
         └──────────────────────────────────────────────┘
```

---

## 3. Detailed Service Specifications

### 3.1. Ingestion Service (`app/services/ingestion_service.py`)
- **Universal Container Ingestion**: Accepts `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`. Decodes to floating-point representation in range $[-1.0, +1.0]$.
- **Physical Standardization**:
  1. Downmix: $x_{\text{mono}}[n] = \frac{1}{C}\sum_{c=1}^C x_c[n]$.
  2. Resample: Polyphase sinc filter to exactly $16,000\text{ Hz}$.
  3. DC & Rumble Filter: 4th-order zero-phase Butterworth high-pass filter with $f_c = 70.0\text{ Hz}$ to eliminate mechanical microphone handling thumps.
  4. Integrated Loudness Calibration: Dual-gated EBU R128 / ITU-R BS.1770-4 normalization to target $-20.0\text{ LUFS}$ with true-peak limiting at $-1.0\text{ dBFS}$ ($0.891$ linear ceiling).
  5. Boundary Trimming: Trims dead-air padding exceeding $200\text{ ms}$ at onset and offset.
  6. STFT Wiener Denoising: Spectral subtraction with oversubtraction factor $\alpha = 1.5$ and noise floor spectral floor $\beta = 0.03$.

---

### 3.2. Alignment Service (`app/services/alignment_service.py`)
- **Dual-Mode Canonical Resolution**:
  - **Mode A (User Transcript Provided)**: Uploaded text is treated as canonical ground truth. Aligned against audio using Whisper forced-alignment to extract word timestamps $[t_{\text{start}}, t_{\text{end}}]$. Word Error Rate (WER) is computed using Levenshtein distance on token sequences to audit enunciation.
  - **Mode B (No Transcript Provided)**: Autonomous Whisper ASR fallback transcribes speech into text events formatted as `<begin speech t=...> [content] <end speech t=...>`.
- **Output Contract**:
  - `canonical_text`: Resolved ground-truth string.
  - `speech_events`: Array of discrete oratorical utterances with start and end times.
  - `wer`: Pronunciation error metric (or `null` if autonomous fallback).

---

### 3.3. Evaluation & Gating Service (`app/services/evaluation_service.py`)
Extracts 100 Hz frame-rate acoustic telemetry and grades on the 10.0-point rubric across 5 pillars:

#### Pillar Breakdown:
1. **Pitch Modulation & Expressiveness (Max 2.5 pts)**:
   - Parselmouth Praat pitch extraction ($75 - 500\text{ Hz}$).
   - Dynamic semitone range: $F_{0,\text{st}} = 12 \log_2\left(\frac{F_{0,95}}{F_{0,05}}\right)$.
   - Pitch velocity $|\frac{dF_0}{dt}|$ (Hz/sec).
2. **Cadence, Pacing & Speech Rate (Max 2.5 pts)**:
   - Words Per Minute (WPM) and Syllabic articulation rate ($SPS$).
   - Cadence stability across sliding 5-second windows.
3. **Rhetorical Pausing & Fluency (Max 2.0 pts)**:
   - 20% Pause Law compliance: Ratio of silence to total time ($\frac{t_{\text{pause}}}{t_{\text{total}}}$).
   - Maximum unbroken silence duration ($\max \Delta t_{\text{silence}}$).
   - 10-token sliding n-gram sentence repetition penalty.
4. **Dynamic Energy & Vocal Projection (Max 1.5 pts)**:
   - Short-Time RMS energy envelope in dB FS.
   - Peak-to-Average Power Ratio (PAPR) crest factor: $\text{PAPR} = \frac{\max(P_{\text{frame}})}{\text{mean}(P_{\text{frame}})}$.
   - Shouting strain / uncontrolled yelling detection.
5. **Spectral Clarity & Phonetic Enunciation (Max 1.5 pts)**:
   - Spectral flux (rate of timbre variation) and spectral centroid dynamics.

#### Non-Unilateral Compound Gating:
Eliminates unilateral false positives (where natural rhetorical applause pauses artificially zero out grades):
$$\Psi_{\text{impair}} = \sum w_i \cdot \mathbb{I}(\text{Deficit}_i)$$
$$\text{Gate Ceiling} = 10.0 - 4.8 \tanh\left(0.55 \cdot \max(0, \Psi_{\text{impair}} - 0.70)\right)$$
- If an orator takes a natural dramatic pause, the gate **does not engage** ($\Psi < 0.70$).
- If acute freezing co-occurs with monotonic flatlining and nervous stammering ($N \ge 2$), $\Psi$ spikes $\ge 1.50$, clamping the score ceiling to $\le 6.0 / 10.0$.
- **Leniency Parameter ($\lambda \in [0, 100]$)**: Dynamically scales penalty thresholds from strict competition forensics ($\lambda = 0$) to supportive coaching ($\lambda = 100$).

---

### 3.4. Chess.com Rhetorical Move Classifier (`app/services/move_classifier.py`)
Segments speech into time-series intervals and classifies every region into an oratorical move quality:

| Move Tag | Color Code | Mathematical Trigger Criteria |
|---|---|---|
| **Brilliant (✨)** | `#00E5FF` (Cyan) | Local pitch jump $> 3.5\text{ st}$ or velocity $> 850\text{ Hz/s}$ AND PAPR $> 28.0\text{ dB}$ followed by a dramatic pause ($0.6\text{s} - 1.8\text{s}$). |
| **Great (🎯)** | `#00E676` (Green) | Cadence in optimal range ($130 - 175\text{ WPM}$), $F_0 \ge 11.0\text{ st}$, balanced pause ratio ($0.15 - 0.25$). |
| **Good (👍)** | `#76FF03` (Lime) | Standard, stable delivery meeting baseline expectations. |
| **Inaccuracy (⚠️)** | `#FFEA00` (Yellow) | Mild hesitation ($1.5\text{s} - 2.2\text{s}$) or slight pitch leveling ($F_0 < 8.0\text{ st}$). |
| **Mistake (⚡)** | `#FF9100` (Orange) | Cadence runaway ($> 220\text{ WPM}$), clipped pause ($< 250\text{ ms}$), or shouting strain. |
| **Blunder (❌)** | `#FF1744` (Red) | Paralyzing dead-air freeze ($> 3.0\text{s}$), monotone flatline ($F_0 < 5.0\text{ st}$ for $\ge 4.0\text{s}$), or stammer loop. |

---

### 3.5. Groq Cloud Open-Source LLM Explanation Engine (`app/services/explanation_service.py`)
- **API Provider**: Groq Cloud (`https://api.groq.com/openai/v1/chat/completions`).
- **Model**: `llama-3.1-8b-instant` (sub-second LPU inference, ~500 tokens/sec).
- **Temperature**: `0.25` (strict, deterministic, low-variance).
- **Response Format**: Strict JSON object schema.

#### Dual-Layer Output Contract:
1. `executive_verdict`: High-level summary of performance and core grade driver.
2. `deterministic_explanation`: Hard physical DSP acoustic rationale citing exact numbers (semitones, seconds, decibels, gate ceiling).
3. `semantic_explanation`: Human audience perception explaining how the delivery felt emotionally and its impact on audience engagement.
4. `pillar_critiques`: 5 itemized diagnostic critiques for Pitch, Cadence, Pauses, Energy, and Clarity.
5. `actionable_vocal_drills`: 2 to 3 targeted physical exercises (e.g. Diaphragmatic Breath Anchor, Three-Tier Pitch Glides, Dynamic Syllable Punch).
6. **Built-in Fallback**: If no Groq API key is present or network is unreachable, an internal deterministic rule engine generates the complete structured diagnosis instantly without failing.
