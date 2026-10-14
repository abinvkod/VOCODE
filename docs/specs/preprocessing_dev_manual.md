# Preprocessing Stage: Complete Developer Implementation Instructions

**File:** `preprocessing/preprocessingins.md`  
**Target Module:** `src/preprocessing/`  
**Purpose:** End-to-end developer manual and technical specifications for implementing the input audio preprocessing, denoising, vocal isolation, and autonomous transcription pipeline.

---

## 1. Executive Summary & Objective

The preprocessing stage accepts arbitrary raw audio recordings (variable formats, bitrates, sample rates, channels, gains, and background noise levels) along with an optional reference text transcript. 

It produces:
1. **`preprocessed_clean.wav`**: A standardized, 16,000 Hz, mono, -20.0 LUFS master audio file with environmental noise removed and orator vocal formants isolated from audience applause/cheers.
2. **`transcript_events.txt`**: Timestamped oratorical segments formatted strictly as `<begin speech t=t_start> [content] <end speech t=t_end>`.
3. **`canonical_transcript.txt`**: The ground-truth text to be used by all downstream forced aligners and evaluation models (resolved via user input or autonomous ASR).
4. **`telemetry_report.json`**: An audit trail of audio health metrics (SNR before/after, LUFS, clipping, Word Error Rate).

---

## 2. Required Software Environment & Dependencies

All dependencies are maintained within the local Python virtual environment (`./venv`):

```bash
# Core audio DSP & ML dependencies
./venv/bin/pip install numpy scipy soundfile librosa praat-parselmouth pyloudnorm openai-whisper torch torchaudio
```

### Required Imports in Code:
```python
import os
import json
import math
import numpy as np
import scipy.signal as signal
import soundfile as sf
import librosa
import pyloudnorm as pyln
import whisper
import torch
```

---

## 3. Architecture & Execution Order

```
Raw Audio File (+ Optional Reference Transcript)
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: PHYSICAL AUDIO STANDARDIZATION                     │
│ 1.1 Universal Ingestion & Floating-Point Conversion        │
│ 1.2 Channel Downmixing to Mono                              │
│ 1.3 High-Fidelity Sinc Resampling to 16,000 Hz              │
│ 1.4 DC Bias Removal & 70 Hz Butterworth High-Pass Filter    │
│ 1.5 EBU R128 Integrated Loudness Normalization (-20 LUFS)   │
│ 1.6 Boundary Dead-Air Trimming (with 200ms onset buffer)    │
└─────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: SPECTRAL DENOISING & VOCAL ISOLATION (SNR BOOST)   │
│ 2.1 STFT Time-Frequency Decomposition                       │
│ 2.2 Stationary Noise Estimation via Silence Frames          │
│ 2.3 Wiener / Spectral Gating Subtraction                    │
│ 2.4 Harmonic-Percussive Source Separation (HPSS)            │
│     (Isolates voice harmonics; suppresses claps & cheers)   │
│ 2.5 Phase-Preserved iSTFT Waveform Reconstruction           │
└─────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: BOUNDED TRANSCRIPTION & DUAL-MODE RESOLUTION       │
│ 3.1 Energy/VAD Utterance Slicing [t_start, t_end]           │
│ 3.2 Whisper ASR Transcription on Each Slice                 │
│ 3.3 Emit Formatted Tags (<begin speech> ... <end speech>)   │
│ 3.4 Dual-Mode Canonical Transcript Resolution Protocol      │
│ 3.5 Text Alignment & Word Error Rate (WER) Calculation     │
└─────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: TELEMETRY & PRE-FLIGHT VERIFICATION                │
│ 4.1 SNR Calculation (Before vs After)                       │
│ 4.2 True-Peak & Digital Clipping Ratio Validation           │
│ 4.3 Output Artifact Serialization                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Phase 1 Implementation: Physical Audio Standardization

### Step 1.1: File Ingestion & Format Decoding
* **Function:** `load_audio(file_path: str) -> tuple[np.ndarray, int]`
* Support all standard containers: `.wav`, `.mp3`, `.m4a`, `.aac`, `.flac`, `.ogg`.
* Load audio using `soundfile` with fallback to `librosa.load(..., sr=None, mono=False)`.
* Convert all sample values to `np.float32` in the range $[-1.0, +1.0]$.

### Step 1.2: Channel Downmixing (Stereo to Mono)
* **Function:** `downmix_to_mono(audio: np.ndarray) -> np.ndarray`
* If input has shape `(channels, samples)` or `(samples, channels)` where `channels > 1`:
  $$x_{\text{mono}}[n] = \frac{1}{C}\sum_{c=1}^{C} x_c[n]$$
* Flatten output to a 1D array of shape `(N,)`.

### Step 1.3: Sinc Resampling to 16,000 Hz
* **Function:** `resample_to_16k(audio: np.ndarray, orig_sr: int) -> np.ndarray`
* Target sample rate: $f_s = 16000\text{ Hz}$.
* If `orig_sr == 16000`, return unchanged.
* Otherwise, use `librosa.resample(audio, orig_sr=orig_sr, target_sr=16000, res_type='soxr_hq')`.

### Step 1.4: DC Offset Removal & 70 Hz Butterworth High-Pass Filtering
* **Function:** `remove_dc_and_rumble(audio: np.ndarray, sr: int = 16000) -> np.ndarray`
* **DC Centering:**
  $$x[n] = x[n] - \frac{1}{N}\sum_{k=0}^{N-1} x[k]$$
* **High-Pass Filter:**
  * Type: 4th-order Butterworth high-pass filter.
  * Cutoff frequency: $f_c = 70.0\text{ Hz}$.
  * Design: `b, a = signal.butter(4, 70.0 / (sr / 2), btype='highpass')`.
  * Application: Zero-phase forward-backward filtering via `signal.filtfilt(b, a, audio)`.
  * *Rationale:* Cuts HVAC drone, electrical ground hum, and mechanical mic handling thumps while preserving male fundamental pitch ($F_0 \ge 85\text{ Hz}$).

### Step 1.5: EBU R128 Integrated Loudness Normalization
* **Function:** `normalize_loudness_ebu_r128(audio: np.ndarray, sr: int = 16000, target_lufs: float = -20.0) -> tuple[np.ndarray, float, float]`
* **Implementation:**
  1. Initialize meter: `meter = pyln.Meter(sr)`.
  2. Measure initial loudness: `measured_lufs = meter.integrated_loudness(audio)`.
  3. Compute gain adjustment:
     $$G_{\text{LUFS}} = 10^{(\text{target\_lufs} - \text{measured\_lufs}) / 20}$$
  4. Apply gain: $x_{\text{norm}}[n] = audio[n] \cdot G_{\text{LUFS}}$.
  5. Check true peak: If $\max(|x_{\text{norm}}|) > 0.891$ ($-1.0\text{ dBFS}$), scale by $\frac{0.891}{\max(|x_{\text{norm}}|)}$ to prevent digital clipping.

### Step 1.6: Boundary Dead-Air Trimming
* **Function:** `trim_dead_air(audio: np.ndarray, sr: int = 16000, buffer_ms: float = 200.0) -> tuple[np.ndarray, float, float]`
* Compute short-time RMS energy (frame size = 512, hop = 160).
* Define threshold: $\theta_{\text{silence}} = \max(\text{RMS}) \times 0.015$.
* Detect first active speech frame $n_{\text{start}}$ and last active speech frame $n_{\text{end}}$.
* Add a 200 ms safety buffer before $n_{\text{start}}$ and after $n_{\text{end}}$ to preserve the natural room attack.
* Slice audio: `audio[start_idx : end_idx]`.

---

## 5. Phase 2 Implementation: Spectral Denoising & Vocal Isolation

### Step 2.1: STFT Time-Frequency Analysis
* **Parameters:**
  * FFT Size: $N_{\text{fft}} = 1024$ samples (64 ms at 16 kHz).
  * Hop Size: $H = 256$ samples (16 ms, 75% overlap).
  * Window: Hann window (`np.hanning(1024)`).
* Compute complex STFT:
  $$X(t, f) = \text{STFT}(x[n]), \quad S(t, f) = |X(t, f)|, \quad \Phi(t, f) = \angle X(t, f)$$

### Step 2.2: Stationary Noise Estimation
* **Function:** `estimate_noise_floor(magnitude: np.ndarray, silence_frames: np.ndarray) -> np.ndarray`
* Average the magnitude spectrum over the detected silence/unvoiced frames:
  $$\hat{N}(f) = \frac{1}{|T_{\text{silence}}|} \sum_{t \in T_{\text{silence}}} S(t, f)$$

### Step 2.3: Wiener Spectral Subtraction
* **Function:** `spectral_subtraction(magnitude: np.ndarray, noise_floor: np.ndarray, alpha: float = 1.5, beta: float = 0.02) -> np.ndarray`
* Apply over-subtraction with spectral floor:
  $$S_{\text{clean}}(t, f) = \max\left(S(t, f) - \alpha \cdot \hat{N}(f), \; \beta \cdot S(t, f)\right)$$
* $\alpha = 1.5$ prevents residual noise spikes; $\beta = 0.02$ eliminates musical artifacts.

### Step 2.4: Harmonic-Percussive Source Separation (HPSS)
* **Function:** `isolate_vocal_harmonics(magnitude: np.ndarray, kernel_time: int = 31, kernel_freq: int = 31) -> np.ndarray`
* Public speech clapping, cheers, and clicks are percussive vertical spikes; orator voice is harmonic horizontal formant tracks.
* Extract harmonic and percussive components using median filters:
  $$H(t, f) = \text{median\_filter}_{\text{time}}(S_{\text{clean}}(t, f), \text{size}=(1, \text{kernel\_time}))$$
  $$P(t, f) = \text{median\_filter}_{\text{freq}}(S_{\text{clean}}(t, f), \text{size}=(\text{kernel\_freq}, 1))$$
* Compute soft harmonic mask:
  $$M_H(t, f) = \frac{H(t, f)^2}{H(t, f)^2 + P(t, f)^2 + \epsilon}$$
* Filtered magnitude: $S_{\text{voice}}(t, f) = S_{\text{clean}}(t, f) \cdot M_H(t, f)$.

### Step 2.5: Waveform Reconstruction
* Combine cleaned magnitude with original phase:
  $$Y(t, f) = S_{\text{voice}}(t, f) \cdot e^{j \Phi(t, f)}$$
* Compute inverse STFT via overlap-add:
  $$y[n] = \text{iSTFT}(Y(t, f), \text{hop\_length}=256, \text{win\_length}=1024)$$

---

## 6. Phase 3 Implementation: Bounded Transcription & Dual-Mode Resolution

### Step 3.1: Voice Activity Utterance Segmentation
* **Function:** `segment_utterances(audio: np.ndarray, sr: int = 16000, min_silence_duration_sec: float = 0.5) -> list[tuple[float, float]]`
* Detect speech intervals $[t_{\text{start}}^{(k)}, t_{\text{end}}^{(k)}]$ using energy envelope or Silero VAD.
* Merge pauses $< 250\text{ms}$ into continuous phrases.
* Split at silences $\ge 500\text{ms}$.
* Returns list of `[(t_start_1, t_end_1), (t_start_2, t_end_2), ...]`.

### Step 3.2: Whisper ASR Transcription
* **Function:** `transcribe_segments(audio: np.ndarray, segments: list[tuple[float, float]], sr: int = 16000, model_size: str = "base.en") -> list[dict]`
* Load Whisper model once: `model = whisper.load_model(model_size)`.
* For each segment $[t_{\text{start}}, t_{\text{end}}]$:
  * Extract slice: `chunk = audio[int(t_start * sr) : int(t_end * sr)]`.
  * Transcribe: `result = model.transcribe(chunk, fp16=torch.cuda.is_available())`.
  * Store `{ "start": t_start, "end": t_end, "text": result["text"].strip() }`.

### Step 3.3: Bounded Output Formatting
* **Format Specification:**
  ```
  <begin speech t=00:04.210s>
  content: "Four score and seven years ago our fathers brought forth on this continent"
  <end speech t=00:10.850s>

  <begin speech t=00:12.300s>
  content: "a new nation, conceived in Liberty, and dedicated to the proposition that all men are created equal."
  <end speech t=00:19.450s>
  ```
* Serialize into `transcript_events.txt`.

### Step 3.4: Dual-Mode Canonical Transcript Resolution Protocol
* **Function:** `resolve_canonical_transcript(asr_events: list[dict], reference_text: str | None) -> dict`
* **Rule Engine:**
  ```python
  if reference_text and len(reference_text.strip()) > 0:
      canonical_text = reference_text.strip()
      source = "USER_PROVIDED_REFERENCE"
      # Compute Word Error Rate (WER) against ASR
      wer_score = compute_wer(reference_text, full_asr_text)
  else:
      # AUTONOMOUS FALLBACK: Elevate ASR output to Canonical
      canonical_text = full_asr_text
      source = "AUTONOMOUS_ASR_FALLBACK"
      wer_score = None
  ```
* Write `canonical_text` to `canonical_transcript.txt`. Downstream forced alignment **always reads this file**, ensuring 100% pipeline reliability regardless of user input.

### Step 3.5: Word Error Rate & Alignment Telemetry
* Compute WER using Levenshtein distance on normalized word tokens:
  $$\text{WER} = \frac{S + D + I}{N}$$
  where $S$ = substitutions, $D$ = deletions, $I$ = insertions, $N$ = total reference words.

---

## 7. Phase 4 Implementation: Telemetry & Quality Assurance

### Step 4.1: Signal-to-Noise Ratio (SNR) Measurement
* **Function:** `compute_snr(audio: np.ndarray, speech_mask: np.ndarray) -> float`
* $$P_{\text{speech}} = \frac{1}{|T_{\text{speech}}|} \sum_{n \in T_{\text{speech}}} x[n]^2$$
* $$P_{\text{noise}} = \frac{1}{|T_{\text{noise}}|} \sum_{n \in T_{\text{noise}}} x[n]^2$$
* $$\text{SNR}_{\text{dB}} = 10 \log_{10}\left(\frac{P_{\text{speech}}}{P_{\text{noise}} + \epsilon}\right)$$
* Compute both $\text{SNR}_{\text{raw}}$ and $\text{SNR}_{\text{clean}}$ to quantify the SNR boost.

### Step 4.2: Digital Clipping Ratio Validation
* **Formula:** $\text{Ratio}_{\text{clipped}} = \frac{\sum (|x[n]| \ge 0.99)}{N}$.
* If $\text{Ratio}_{\text{clipped}} > 0.005$ ($0.5\%$), set telemetry flag `"clipping_warning": true`.

### Step 4.3: Output Telemetry Schema (`telemetry_report.json`)
```json
{
  "source_file": "speech_input.mp3",
  "clean_file": "preprocessed_clean.wav",
  "sample_rate": 16000,
  "channels": 1,
  "original_duration_sec": 64.20,
  "clean_duration_sec": 61.85,
  "lead_trim_sec": 1.15,
  "tail_trim_sec": 1.20,
  "measured_lufs_raw": -26.4,
  "normalized_lufs": -20.0,
  "snr_raw_db": 14.2,
  "snr_clean_db": 28.7,
  "snr_improvement_db": 14.5,
  "clipping_ratio": 0.0,
  "transcript_resolution": {
    "source": "AUTONOMOUS_ASR_FALLBACK",
    "has_reference": false,
    "total_words": 142,
    "total_utterances": 6,
    "wer": null
  },
  "status": "READY_FOR_EVALUATION"
}
```

---

## 8. Modular Code Architecture Contract

All preprocessing logic must be packaged cleanly under `src/preprocessing/`:

```
src/
└── preprocessing/
    ├── __init__.py
    ├── audio_standardizer.py    # Phase 1: Ingestion, Resampling, High-pass, EBU R128, Trimming
    ├── spectral_denoiser.py     # Phase 2: STFT, Wiener subtraction, HPSS voice isolation
    ├── transcription_engine.py  # Phase 3: VAD slicing, Whisper ASR, Bounded tags, Dual-mode
    ├── telemetry.py             # Phase 4: SNR, Clipping, Telemetry report generation
    └── pipeline.py              # Master orchestrator executing Phases 1 -> 4
```

### Master CLI Invocation Contract
```bash
./venv/bin/python -m src.preprocessing.pipeline \
    --input "good speeches/01_Martin_Luther_King/audio.mp3" \
    --transcript "good speeches/01_Martin_Luther_King/transcript.txt" \
    --output_dir "processed/01_MLK"
```

---

## 9. Developer Acceptance Criteria Checklist

| Test Item | Verification Criteria | Target Result |
| :--- | :--- | :--- |
| **Sample Rate** | Inspect output audio format with `sox` or `sf.info()`. | Exactly `16000 Hz, 1 channel, PCM_16`. |
| **Integrated Loudness** | Measure output audio with `pyloudnorm.Meter`. | $-20.0 \pm 0.5\text{ LUFS}$. |
| **Peak Ceiling** | Maximum absolute sample value. | $\le 0.891$ ($-1.0\text{ dBFS}$, zero clipping). |
| **SNR Improvement** | Compare `snr_raw_db` vs. `snr_clean_db`. | $\ge +10.0\text{ dB}$ improvement on noisy audio. |
| **Clap / Cheer Suppression** | Spectrogram inspection of crowd applause sections. | Percussive vertical spikes attenuated by $\ge 15\text{ dB}$. |
| **Transcript Bounding** | Inspect `transcript_events.txt`. | Strict `<begin speech t=...> content <end speech t=...>` tags. |
| **Missing Transcript Test** | Run pipeline without `--transcript` argument. | Pipeline completes successfully; elevates ASR to canonical. |
