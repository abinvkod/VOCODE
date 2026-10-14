# Analysis Plan: Batch Preprocessing, Acoustic Number Crunching & Archetype Clustering

## 1. Objective
Preprocess all raw speeches in the `good speeches/` corpus, extract high-density 100 Hz time-series acoustic features (Pitch, Energy, Pauses, Cadence, Spectral Timbre), compute summary statistical distributions, and perform unsupervised clustering (K-Means, PCA) to discover the core oratorical archetypes and global invariant laws of masterclass speeches.

---

## 2. Execution Pipeline

### Stage 1: Batch Audio Preprocessing
1. **Physical Standardization:**
   * Universal format decoding to 32-bit float array `[-1.0, 1.0]`.
   * Stereo-to-mono downmixing: $x_{\text{mono}} = \frac{x_L + x_R}{2}$.
   * High-quality sinc resampling to **16,000 Hz** (`soxr_hq`).
   * DC bias removal and 4th-order **70 Hz Butterworth high-pass filter** (zero-phase forward-backward `filtfilt`).
   * **EBU R128 Integrated Loudness Normalization** to **-20.0 LUFS** with a **-1.0 dBFS** true-peak limit ceiling.
   * Boundary dead-air trimming with a **200 ms onset buffer**.
2. **Spectral Denoising & HPSS Vocal Isolation:**
   * STFT Wiener spectral subtraction to eliminate stationary background noise floor (+12 to +18 dB SNR boost).
   * Harmonic-Percussive Source Separation (HPSS) to strip audience clapping, cheers, and room clicks while preserving vocal harmonics.
3. **Autonomous Bounded Transcription:**
   * Voice Activity Detection (VAD) slicing into utterance intervals.
   * Whisper ASR on slices missing transcripts, generating `<begin speech t=t_start> [content] <end speech t=t_end>`.
   * Dual-mode resolution: elevate ASR output to canonical transcript if no reference transcript exists.
4. **Artifact Storage:**
   * Save `preprocessed_clean.wav`, `canonical_transcript.txt`, and `telemetry.json` in each speech folder.

---

### Stage 2: Time-Series Acoustic Feature Extraction
Extract 100 Hz (10 ms hop) acoustic parameters for each preprocessed speech:
* **Pitch ($F_0$ via Praat Parselmouth):** Median, Mean, Std Dev $\sigma(F_0)$, Dynamic Range in Semitones ($12 \log_2(P_{95}/P_{05})$), Pitch Velocity $|dF_0/dt|$, Voiced Ratio.
* **Energy (RMS dB):** Mean dB, Dynamic Range ($P_{95} - P_{05}$), Crest Factor / PAPR (vocal punchiness).
* **Pauses & Rhythm:** Pause-to-Speech Ratio, Pause frequency (pauses/min), Rhetorical-to-Micro pause ratio, Estimated Articulation Rate (syllables/sec).
* **Spectral Timbre:** Spectral Centroid, Spectral Flux, Harmonics-to-Noise Ratio (HNR proxy).

---

### Stage 3: Statistical Synthesis & Archetype Clustering
* Construct an $N \times D$ normalized feature matrix.
* Run PCA for 2D visualization and variance explanation.
* Run K-Means and Hierarchical Ward clustering (optimal $k$ evaluated via Silhouette analysis).
* Map discovered clusters to Oratorical Archetypes (e.g. *Dramatic Crescendo*, *Authoritative/Measured Persuasion*, *High-Urgency Declamation*).
* Extract corpus-wide invariant boundaries that define masterclass delivery.
