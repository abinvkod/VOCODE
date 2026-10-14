# Audio Preprocessing Pipeline Specification

## 1. Objective

The input audio preprocessing stage transforms arbitrary, heterogeneous audio uploads (variable formats, bitrates, sample rates, channels, background hum, and disparate volume levels) into a **clean, standardized, reproducible 16 kHz mono master signal**. 

Standardization guarantees that subsequent forced alignment, pitch extraction ($F_0$), and energy calculations reflect **pure oratorical delivery** rather than recording hardware, room acoustics, or microphone gain discrepancies.

---

## 2. Preprocessing Architecture

```
                       Heterogeneous Raw Audio
             (MP3 / WAV / M4A / FLAC, Stereo/Mono, 8k-48k)
                                │
                                ▼
            [Step 1: Ingestion & Universal Decoding]
            • Container parsing via FFmpeg / SoundFile
            • Floating-point representation in range [-1.0, +1.0]
                                │
                                ▼
            [Step 2: Channel Downmixing (Mono)]
            • Multi-channel averaging: x_mono[n] = 0.5 * (x_L[n] + x_R[n])
                                │
                                ▼
            [Step 3: High-Fidelity Resampling to 16 kHz]
            • Standardize to fs = 16,000 Hz via polyphase sinc filter (soxr)
            • Matches Wav2Vec2 / WhisperX acoustic model requirements
                                │
                                ▼
            [Step 4: DC Offset Removal & High-Pass Filtering]
            • DC bias centering: x[n] = x[n] - mean(x)
            • 4th-order Butterworth High-Pass at 70 Hz (removes HVAC rumble/mic thumps)
                                │
                                ▼
            [Step 5: EBU R128 Integrated Loudness Normalization]
            • Standardize perceived loudness to -20.0 LUFS (ITU-R BS.1770-4)
            • True-peak limiting at -1.0 dBFS to prevent digital clipping
                                │
                                ▼
            [Step 6: Voice Activity Boundary Trimming]
            • Energy/VAD trim of leading and trailing non-speech dead-air
            • Preserves 200ms safety pad before first syllable
                                │
                                ▼
            [Step 7: Pre-Flight Audio Quality Validation]
            • Clipping check: % samples at |x| >= 0.99
            • Estimated SNR check (Signal-to-Noise Ratio)
            • Minimum duration verification (>= 3.0 seconds)
                                │
                                ▼
              Standardized Audio Artifact: preprocessed.wav
                    + Quality Telemetry Report (JSON)
```

---

## 3. Detailed Preprocessing Methods

### 3.1 Step 1: Universal Container Decoding
* **Challenge:** Participants and public speech archives use various container formats (`.wav`, `.mp3`, `.m4a`, `.aac`, `.flac`, `.ogg`).
* **Implementation:** Audio is loaded via `soundfile` or `ffmpeg`, converting all data to **32-bit floating-point arrays** bounded in the theoretical interval $[-1.0, +1.0]$.

### 3.2 Step 2: Channel Downmixing (Stereo to Mono)
* **Rationale:** Public speaking acoustics are spatial-invariant for rhetorical analysis; multi-channel differences (e.g. binaural panning or phase interference) corrupt pitch tracking and feature comparison.
* **Method:**
  $$x_{\text{mono}}[n] = \frac{1}{C} \sum_{c=1}^{C} x_c[n]$$
  where $C$ is the number of audio channels.

### 3.3 Step 3: Resampling to 16,000 Hz
* **Rationale:** 16 kHz is the universal standard for automatic speech recognition (ASR), forced alignment models (Wav2Vec2, WhisperX), and speech prosody tools.
* **Method:** Band-limited sinc interpolation via `soxr` or `scipy.signal.resample_poly` with anti-aliasing low-pass filtering at the 8 kHz Nyquist limit.

### 3.4 Step 4: DC Offset Removal & Sub-Audible Filtering
* **DC Bias Removal:** Microphone analog-to-digital converters often introduce small constant voltage biases:
  $$x_{\text{centered}}[n] = x_{\text{mono}}[n] - \frac{1}{N}\sum_{k=0}^{N-1} x_{\text{mono}}[k]$$
* **High-Pass Filter at 70 Hz:**
  * Vocal pitch fundamentals for adult male and female speakers start above $80\text{ Hz}$.
  * A 4th-order Butterworth high-pass filter with a cutoff frequency $f_c = 70\text{ Hz}$ removes air conditioner rumble, electrical ground loops (50/60 Hz hum), and mic handling thumps without affecting voice pitch ($F_0$).

### 3.5 Step 5: EBU R128 Integrated Loudness Normalization (-20 LUFS)
* **Why Peak Normalization is Insufficient:** Peak normalization only scales by the loudest instantaneous transient (e.g., a mic pop), leaving the actual speech quiet and inconsistent.
* **The Solution (EBU R128 / ITU-R BS.1770-4):**
  * Measures psychoacoustically weighted perceived loudness (K-weighting filter).
  * Computes Integrated Loudness in LUFS (Loudness Units relative to Full Scale).
  * Applies gain adjustment $G_{\text{LUFS}}$ to achieve exactly **-20.0 LUFS**:
    $$G_{\text{LUFS}} = 10^{(-20.0 - \text{LUFS}_{\text{measured}}) / 20}$$
  * Verifies that true peak remains $\le -1.0\text{ dBFS}$ to eliminate digital inter-sample clipping.

### 3.6 Step 6: Boundary Dead-Air Trimming
* **Rationale:** Excessive silence at the beginning or end of a recording distorts total duration, average speech rate, and pause-to-speech ratios.
* **Method:** Energy-based Voice Activity Detection (VAD) detects the first and last active speech frames, trimming pre-speech and post-speech dead air while retaining a standard **200 ms ambient buffer**.

### 3.7 Step 7: Pre-Flight Audio Quality Telemetry
Before passing the audio to the feature extraction engine, a telemetry check evaluates recording health:
* **Clipping Ratio:** Percentage of samples reaching $\ge 0.99$. If $> 0.5\%$, flag a *Severe Recording Distortion* warning.
* **Estimated SNR (Signal-to-Noise Ratio):** Ratio between active speech energy and estimated noise floor in dB.
* **Duration Check:** Rejects audio files shorter than 3 seconds or longer than 15 minutes.

---

## 4. Telemetry Output Schema

The preprocessing stage outputs the normalized WAV file along with a metadata JSON:

```json
{
  "source_file": "jobs_stanford_raw.mp3",
  "processed_file": "jobs_stanford_preprocessed.wav",
  "sample_rate": 16000,
  "channels": 1,
  "original_duration_sec": 62.45,
  "trimmed_duration_sec": 59.80,
  "lead_trim_sec": 1.25,
  "tail_trim_sec": 1.40,
  "measured_lufs_before": -27.8,
  "target_lufs": -20.0,
  "gain_applied_db": 7.8,
  "clipping_percentage": 0.0,
  "estimated_snr_db": 28.4,
  "status": "READY_FOR_ALIGNMENT"
}
```

---

## 5. Advanced Speech Isolation, FFT Denoising & Independent Transcription Pipeline

To handle live, crowded, or reverberant public speaking environments (e.g. auditoriums with applause, cheering, HVAC hum, and room acoustics), a specialized 3-stage enhancement and transcription pipeline is inserted immediately after initial decoding.

```
                  Standardized Input Waveform x[n]
                                 │
                                 ▼
   [Stage A: FFT Spectral Denoising (SNR Enhancement)]
   • Short-Time Fourier Transform (STFT): Hann window, 1024-pt, 75% overlap
   • Noise floor estimation via minimum statistics during unvoiced intervals
   • Spectral Gating / Wiener Spectral Subtraction:
       |Y(t, f)| = max(|X(t, f)| - α * N_hat(f), β * |X(t, f)|)
   • Inverse STFT (iSTFT) overlap-add reconstruction (+12 to +18 dB SNR boost)
                                 │
                                 ▼
   [Stage B: Voice Isolation & Crowd / Applause Suppression]
   • Harmonic-Percussive Source Separation (HPSS):
       - Claps/clicks/pops are percussive (vertical spikes on spectrogram)
       - Human speech is harmonic (horizontal formant bands over time)
       - Masking: M_harmonic(t, f) filters out audience claps
   • Neural Speech Enhancement (DeepFilterNet / CleanUNet fallback):
       - Suppresses audience cheers, room reverberation, and background hoots
       - Isolates primary orator foreground vocal track
                                 │
                                 ▼
   [Stage C: VAD-Bounded Independent Transcription]
   • Voice Activity Detection (Silero VAD / Energy gating)
   • Slices speech into discrete utterance segments [t_start, t_end]
   • Runs local ASR (Whisper base.en) on each isolated segment
   • Formats output into timestamped orator blocks:
       <begin speech t=start_sec> content <end speech t=end_sec>
   • Computes Levenshtein Similarity & Word Error Rate (WER) against reference
```

### Detailed Component Logic

#### 1. FFT-Based Spectral Subtraction (Denoising)
* **STFT Decomposition:** Computes frequency bins $X(t, f)$ across time frames $t$.
* **Noise Fingerprint Estimation ($\hat{N}(f)$):** Samples stationary noise during introductory room-tone and inter-clause pauses.
* **Over-Subtraction Filtering:**
  $$|Y(t, f)| = \max\left(|X(t, f)| - \alpha \cdot \hat{N}(f), \; \beta \cdot |X(t, f)|\right)$$
  where $\alpha = 1.5$ (over-subtraction factor to suppress noise peaks) and $\beta = 0.02$ (spectral floor preventing "musical noise" artifacts).
* **Waveform Synthesis:** Multiplies by original phase $e^{j \angle X(t, f)}$ and inverts via iSTFT.

#### 2. Crowd, Clapping & Interference Suppression (HPSS + Vocal Isolation)
* **Audience Claps & Hoots:** Clapping consists of short, broadband acoustic impulses ($< 30\text{ms}$).
* **Separation Filter:** Median filtering along time extracts continuous vocal harmonics ($H(t, f)$); median filtering along frequency extracts transient claps ($P(t, f)$).
* By applying the soft harmonic mask:
  $$M_H(t, f) = \frac{H(t, f)^2}{H(t, f)^2 + P(t, f)^2}$$
  applause and foot-tapping are suppressed by $> 18\text{ dB}$ before pitch extraction.

#### 3. Bounded Speech Annotation Schema (`<begin speech>` ... `<end speech>`)
The pipeline slices the audio into oratorical events and emits structured annotations:

```
<begin speech t=00:04.210s>
content: "I am honored to be with you today at your commencement from one of the finest universities in the world."
<end speech t=00:10.850s>

<begin speech t=00:12.300s>
content: "I never graduated from college. Truth be told, this is the closest I've ever gotten to a college graduation."
<end speech t=00:18.940s>
```

#### 4. Automated Text Similarity Telemetry
The transcribed tokens are aligned with the reference transcript using **Needleman-Wunsch / Levenshtein Distance**, outputting:
* **Word Error Rate (WER):** Quantifies speech clarity and acoustic intelligibility.
* **Boundary Precision:** Verifies whether orator pauses match transcript punctuation.
* **Missing / Injected Token Flags:** Flags if the speaker omitted lines or hallucinated filler words.

---

## 6. Dual-Mode Transcript Resolution (Autonomous ASR Fallback)

To ensure the evaluation pipeline functions whether or not a reference transcript is provided, Phase 3 implements an **Autonomous Transcript Resolution Protocol**:

```
                         Transcript Input Check
                                    │
                  ┌─────────────────┴─────────────────┐
                  ▼                                   ▼
      [Reference Transcript Exists]       [No Transcript Provided (None)]
                  │                                   │
                  ▼                                   ▼
      • Run Phase 3 ASR                   • Run Phase 3 ASR (Whisper)
      • Align ASR tokens to Reference     • Elevate ASR output to Canonical
      • Compute WER & Omission Flags      • Format: <begin speech> ... <end speech>
      • Canonical = Reference Text        • Canonical = ASR Generated Text
      • Source: "USER_PROVIDED"           • Source: "AUTONOMOUS_ASR"
                  │                                   │
                  └─────────────────┬─────────────────┘
                                    │
                                    ▼
                 Downstream Forced Alignment & Scoring
                      (Uses Canonical Transcript)
```

### Telemetry Schema for Transcript Resolution
```json
{
  "transcript_mode": "AUTONOMOUS_ASR",
  "active_transcript": "Stay hungry. Stay foolish.",
  "confidence_score": 0.94,
  "has_reference_text": false,
  "wer": null,
  "word_count": 4,
  "utterance_count": 1
}
```
If `has_reference_text` is `false`, the downstream forced aligner and temporal flaw grounding engine ingest the generated text directly, ensuring zero interruptions in the pipeline.
