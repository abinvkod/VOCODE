# Frontend Architecture Specification

**Project:** Track C: Contrastive Speech Analytics & Temporal Flaw Grounding  
**Framework:** Streamlit + Plotly + Custom HTML5 / JS Audio Engine  
**Target Module:** `app/` & `app/components/`  
**Status:** Validated Architecture  

---

## 1. Executive Summary

The frontend delivers an interactive, high-fidelity oratorical analytics dashboard. It features format-agnostic audio ingestion, a full HTML5 audio player with millisecond-accurate timestamp seeking, a Plotly speedometer scoring dial, a Chess.com-style rhetorical move waveform visualizer, and a tabbed analytics suite offering itemized rubric breakdowns and dual-layer Groq open-source LLM explanations.

---

## 2. Frontend Layout & Visual Wireframe

```
┌────────────────────────────────────────────────────────────────────────┐
│                        SIDEBAR CONTROLS                                │
│  • Groq Cloud API Key Input (llama-3.1-8b-instant status)              │
│  • Dynamic Leniency Slider (λ ∈ [0, 100])                              │
│  • One-Click Sample Audio Pre-loader (MLK, JFK, Chaplin, Real Flaws)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ 1. INGESTION HERO ZONE                                                 │
│  • Drag-and-Drop Audio Uploader (.mp3, .wav, .m4a, .ogg, .flac)        │
│  • Optional Reference Transcript Upload / Paste Box                    │
│  • "Process & Evaluate Speech" Trigger Button                          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ 2. OVERALL SCORE & SPEEDOMETER HERO                                    │
│  • Plotly Speedometer Gauge Dial (0.0 to 10.0 scale)                   │
│  • Qualitative Performance Band Badge (Masterclass to Botched)         │
│  • Gate Ceiling Indicator & Systemic Impairment Index (Ψ) Pill         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ 3. AUDIO PLAYBACK & CHESS.COM WAVEFORM VISUALIZER                      │
│  • Full HTML5 Player: [Play/Pause] [Rewind -5s] [+5s] [Speed Selector] │
│  • Interactive Scrubbable Timebar with Millisecond Seeking             │
│  • Waveform with Colored Bands:                                        │
│    🟦 Brilliant (Cyan) | 🟩 Great (Green) | 🟨 Inaccuracy (Yellow)      │
│    🟧 Mistake (Orange) | 🟥 Blunder (Red)                              │
│  • Move Count Summary Badges                                           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ 4. TABBED ANALYTICS SUITE                                              │
│                                                                        │
│  [Tab 1: 🎯 Chess.com Move Inspector]                                 │
│  • Interactive move cards with text, duration, and click-to-seek audio │
│                                                                        │
│  [Tab 2: 📊 Rubrics & 5 Oratorical Pillars]                            │
│  • Progress bars for 5 Pillars (/2.5, /2.5, /2.0, /1.5, /1.5)          │
│  • 5-Pillar Radar Chart vs Normative Corpus Baselines                  │
│  • Itemized Mathematical Deduction Ledger                              │
│                                                                        │
│  [Tab 3: 🧠 Groq Dual-Layer Explanation]                               │
│  • Column 1: Deterministic Physics (Exact DSP deltas, semitones, secs) │
│  • Column 2: Semantic Audience Perception (Human feels, psychology)    │
│  • Actionable Vocal Coaching Drills & Prescriptions                    │
│                                                                        │
│  [Tab 4: 📈 Deep 100 Hz Acoustic Telemetry]                            │
│  • Pitch F0 Contour (Hz) overlaid with RMS Energy Envelope (dB)        │
│  • Spectrogram & Speech Rate Velocity Time-Series                      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Architecture & Responsibilities

### 3.1. Audio Ingestion Widget (`app/components/uploader.py`)
- Accepts arbitrary containers: `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`.
- Triggers universal backend conversion into a clean 16 kHz mono master `.wav` (-20 LUFS).
- Dual-mode transcript input: Accepts `.txt` file upload or text area paste. If empty, triggers autonomous Whisper ASR fallback.

---

### 3.2. Audio Playback Engine (`app/components/audio_player.py`)
- **Full Player Capabilities**:
  - Play / Pause toggling.
  - Rewind `-5s` and Fast-Forward `+5s` buttons.
  - Variable playback rate selector (`0.75x`, `1.0x`, `1.25x`, `1.5x`).
  - Native scrubbable timebar (`00:00 / MM:SS`).
- **Millisecond Click-to-Seek Synchronization**:
  - Embedded JavaScript listener responds to timeline card clicks.
  - Clicking any **Blunder** or **Brilliant** card automatically jumps the audio cursor directly to that exact second $[t_{\text{start}}]$ and begins playback.

---

### 3.3. Speedometer Score Dial (`app/components/score_dial.py`)
- Interactive Plotly Gauge Indicator (`0.0 - 10.0`).
- Color gradient steps:
  - Red ($0.0 - 5.0$): Botched / Severe Deficits
  - Amber ($5.0 - 6.5$): Developing / Noticeable Flaws
  - Gold ($6.5 - 8.0$): Proficient
  - Emerald ($8.0 - 10.0$): Masterclass Oratory
- Displays the **Non-Unilateral Gate Ceiling** as a highlighted threshold marker, visually illustrating whether the speaker hit an acoustic penalty ceiling.
- Companion pill badges displaying the Systemic Impairment Index ($\Psi_{\text{impair}}$) and Leniency setting ($\lambda$).

---

### 3.4. Chess.com Move Waveform Visualizer (`app/components/move_waveform.py`)
- Downsamples 16 kHz audio into a smooth 1,200-point waveform envelope.
- Injects vertical colored rectangular regions (`vrect`) corresponding to every segmented rhetorical move:
  - 🟦 **Brilliant (`#00E5FF`)**: High pitch excursion ($>3.5\text{ st}$) + punchy vocal crest ($>28\text{ dB}$).
  - 🟩 **Great / Good (`#00E676`)**: Optimal cadence ($130 - 175\text{ WPM}$) and balanced pauses.
  - 🟨 **Inaccuracy (`#FFEA00`)**: Mild hesitation ($1.2\text{s} - 2.0\text{s}$) or slight pitch leveling.
  - 🟧 **Mistake (`#FF9100`)**: Pacing runaway ($>220\text{ WPM}$), clipped breath, or strain.
  - 🟥 **Blunder (`#FF1744`)**: Dead-air freeze ($>3.0\text{s}$), monotone flatline, or stammer loop.
- Interactive summary badges showing counts of each move category.

---

### 3.5. Tabbed Analytics Suite

#### Tab 1: Chess.com Move Inspector
- Displays discrete move cards sorted chronologically or filtered by category (*All*, *Blunders*, *Brilliants*).
- Each card contains:
  - Timestamp badge (e.g., `[00:35.000s - 00:39.770s]`)
  - Move quality badge (e.g., `❌ BLUNDER`)
  - Spoken text snippet
  - Acoustic reason
  - **"Jump to Audio"** button seeking playback to $[t_{\text{start}}]$.

#### Tab 2: Rubrics & 5 Oratorical Pillars (`app/components/rubrics_tab.py`)
- Progress bars displaying scores for each pillar:
  1. Pitch Modulation (`/2.5`)
  2. Cadence & Tempo (`/2.5`)
  3. Rhetorical Pausing (`/2.0`)
  4. Dynamic Energy (`/1.5`)
  5. Spectral Clarity (`/1.5`)
- Interactive Plotly Radar Chart comparing the candidate speaker against the normative masterclass corpus distribution.
- Itemized deduction audit trail showing exact mathematical triggers.

#### Tab 3: Groq Dual-Layer Explanation (`app/components/explanation_view.py`)
- Side-by-side comparison cards powered by Groq's open-source `llama-3.1-8b-instant`:
  - **Left Card (Deterministic Science)**: Hard physics, exact decibel thresholds, pause durations in seconds, and semitone ranges.
  - **Right Card (Semantic Perception)**: Human audience reaction, emotional resonance, and rhetorical authority.
- Actionable Vocal Drills section presenting step-by-step physical exercises tailored to the candidate's weakest pillar.

#### Tab 4: Raw 100 Hz Acoustic Telemetry
- Multi-track time-series charts displaying:
  - $F_0$ Pitch Contour (Hz) across time.
  - Short-Time RMS Energy Envelope (dB FS).
  - Syllable rate onset markers.

---

## 4. State Management & Reactivity

- `st.session_state["audio_data"]`: Cached standardized 16 kHz WAV path and metadata.
- `st.session_state["evaluation_results"]`: Cached 100 Hz telemetry and 10.0-point grading report.
- `st.session_state["speech_moves"]`: Cached Chess.com rhetorical moves array.
- `st.session_state["llm_explanation"]`: Cached Groq Cloud dual-layer explanation.
- `st.session_state["seek_time"]`: Reactive timestamp trigger passed to the HTML5 audio player.
- **Leniency Reactivity**: Adjusting the Leniency slider ($\lambda$) triggers instant re-grading of the cached telemetry without needing to re-run audio decoding or Whisper ASR.
