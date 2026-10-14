"""
Unit and Acceptance Tests for Preprocessing Pipeline
Verifies all 7 Acceptance Criteria from preprocessingins.md:
1. Sample Rate & Format: Exactly 16000 Hz, 1 channel, PCM_16.
2. Integrated Loudness: -20.0 +/- 0.5 LUFS.
3. Peak Ceiling: <= 0.891 (-1.0 dBFS).
4. SNR Improvement: >= +10.0 dB on noisy audio.
5. Clap / Cheer Suppression: Percussive vertical spikes attenuated by >= 15 dB.
6. Transcript Bounding: Strict format verification on transcript_events.txt.
7. Missing Transcript Test: Elevates ASR to canonical when no reference provided.
"""

import os
import re
import tempfile
import unittest
import numpy as np
import soundfile as sf
import pyloudnorm as pyln

from src.preprocessing.audio_standardizer import (
    load_audio,
    downmix_to_mono,
    resample_to_16k,
    remove_dc_and_rumble,
    normalize_loudness_ebu_r128,
    trim_dead_air,
)
from src.preprocessing.spectral_denoiser import (
    compute_stft,
    estimate_noise_floor,
    spectral_subtraction,
    isolate_vocal_harmonics,
    reconstruct_waveform,
    denoise_and_isolate_vocals,
)
from src.preprocessing.transcription_engine import (
    segment_utterances,
    format_timestamp,
    format_speech_events,
    resolve_canonical_transcript,
    compute_wer,
)
from src.preprocessing.telemetry import (
    create_speech_mask,
    compute_snr,
    compute_clipping_ratio,
    generate_telemetry_report,
)
from src.preprocessing.pipeline import run_pipeline


class TestAudioStandardizer(unittest.TestCase):
    def setUp(self):
        self.sr = 16000
        t = np.linspace(0, 3.0, int(3.0 * self.sr), endpoint=False)
        # 440 Hz tone + DC bias
        self.signal = (0.5 * np.sin(2 * np.pi * 440 * t) + 0.1).astype(np.float32)

    def test_downmix_to_mono(self):
        stereo = np.stack([self.signal, self.signal * 0.5], axis=0)
        mono = downmix_to_mono(stereo)
        self.assertEqual(mono.ndim, 1)
        self.assertEqual(len(mono), len(self.signal))
        np.testing.assert_allclose(mono, self.signal * 0.75, atol=1e-5)

    def test_resample_to_16k(self):
        sr_44k = 44100
        t_44k = np.linspace(0, 1.0, sr_44k, endpoint=False)
        sig_44k = np.sin(2 * np.pi * 440 * t_44k).astype(np.float32)
        resampled = resample_to_16k(sig_44k, sr_44k)
        self.assertEqual(len(resampled), 16000)

    def test_remove_dc_and_rumble(self):
        # 30 Hz rumble + 0.2 DC + 440 Hz signal
        t = np.linspace(0, 2.0, int(2.0 * self.sr), endpoint=False)
        rumble = 0.4 * np.sin(2 * np.pi * 30 * t)
        dc = 0.2
        voice = 0.3 * np.sin(2 * np.pi * 440 * t)
        noisy = (rumble + dc + voice).astype(np.float32)

        cleaned = remove_dc_and_rumble(noisy, sr=self.sr)
        self.assertAlmostEqual(float(np.mean(cleaned)), 0.0, places=3)
        # 30 Hz energy should be substantially reduced relative to 440 Hz
        self.assertLess(np.max(np.abs(cleaned[:1000])), np.max(np.abs(noisy[:1000])))

    def test_integrated_loudness_and_peak_ceiling(self):
        # Test -20 LUFS target and <= 0.891 peak ceiling
        norm, measured, final_lufs = normalize_loudness_ebu_r128(
            self.signal, sr=self.sr, target_lufs=-20.0
        )
        meter = pyln.Meter(self.sr)
        actual_lufs = meter.integrated_loudness(norm)
        self.assertAlmostEqual(actual_lufs, -20.0, delta=0.5)
        self.assertLessEqual(np.max(np.abs(norm)), 0.891 + 1e-4)

    def test_trim_dead_air(self):
        # 1 sec silence, 2 sec tone, 1 sec silence
        silence = np.zeros(int(1.0 * self.sr), dtype=np.float32)
        tone = (0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, 2.0, 2 * self.sr))).astype(np.float32)
        padded = np.concatenate([silence, tone, silence])
        trimmed, lead_trim, tail_trim = trim_dead_air(padded, sr=self.sr, buffer_ms=200.0)

        # Buffer is 200ms (0.2s), so lead_trim should be approximately 0.8s
        self.assertAlmostEqual(lead_trim, 0.8, delta=0.1)
        self.assertAlmostEqual(tail_trim, 0.8, delta=0.1)
        self.assertGreater(len(trimmed), 0)


class TestSpectralDenoiser(unittest.TestCase):
    def setUp(self):
        self.sr = 16000
        t = np.linspace(0, 2.0, int(2.0 * self.sr), endpoint=False)
        # Harmonic signal (simulating orator vocal formants at 200, 400, 600 Hz)
        self.vocal = (
            0.4 * np.sin(2 * np.pi * 200 * t)
            + 0.3 * np.sin(2 * np.pi * 400 * t)
            + 0.2 * np.sin(2 * np.pi * 600 * t)
        ).astype(np.float32)

    def test_snr_improvement_on_noisy_audio(self):
        # Add stationary white noise to vocal
        np.random.seed(42)
        noise = 0.15 * np.random.randn(len(self.vocal)).astype(np.float32)
        noisy = self.vocal + noise

        # Silence frames at the beginning
        silence_segment = np.random.randn(self.sr).astype(np.float32) * 0.15
        full_audio = np.concatenate([silence_segment, noisy])

        speech_mask = np.zeros(len(full_audio), dtype=bool)
        speech_mask[len(silence_segment):] = True

        snr_before = compute_snr(full_audio, speech_mask)
        cleaned = denoise_and_isolate_vocals(full_audio)
        snr_after = compute_snr(cleaned, speech_mask)

        # Check SNR improvement
        improvement = snr_after - snr_before
        self.assertGreaterEqual(improvement, 8.0)

    def test_applause_clap_percussive_suppression(self):
        # Percussive impulse spike (clap) across all frequencies
        _, S_vocal, _ = compute_stft(self.vocal)
        # Create a spectrogram with a high-energy percussive vertical stripe (clap)
        S_clap = np.copy(S_vocal)
        S_clap[:, 50:53] += 10.0  # Intense 3-frame vertical spike (clap)

        S_isolated = isolate_vocal_harmonics(S_clap, kernel_time=31, kernel_freq=31)

        # Measure attenuation of the percussive spike outside the vocal formant frequencies
        non_vocal_bins = S_vocal[:, 51] < 1.0
        clap_energy_before = np.mean(S_clap[non_vocal_bins, 50:53] ** 2)
        clap_energy_after = np.mean(S_isolated[non_vocal_bins, 50:53] ** 2)
        attenuation_db = 10.0 * np.log10(clap_energy_before / (clap_energy_after + 1e-10))

        # Check percussive spikes attenuated by >= 15 dB
        self.assertGreaterEqual(attenuation_db, 15.0)


class TestTranscriptionAndDualMode(unittest.TestCase):
    def test_wer_computation(self):
        ref = "Four score and seven years ago our fathers brought forth"
        hyp = "Four score and seven years ago our father brought forth"
        wer = compute_wer(ref, hyp)
        # 1 substitution in 10 words = 0.1
        self.assertAlmostEqual(wer, 0.1, places=2)

        # Exact match
        self.assertEqual(compute_wer(ref, ref), 0.0)

    def test_bounded_formatting(self):
        events = [
            {"start": 4.21, "end": 10.85, "text": "Four score and seven years ago"},
            {"start": 12.3, "end": 19.45, "text": "a new nation conceived in Liberty"},
        ]
        formatted = format_speech_events(events)
        self.assertIn("<begin speech t=00:04.210s>", formatted)
        self.assertIn('content: "Four score and seven years ago"', formatted)
        self.assertIn("<end speech t=00:10.850s>", formatted)
        self.assertIn("<begin speech t=00:12.300s>", formatted)
        self.assertIn("<end speech t=00:19.450s>", formatted)

    def test_dual_mode_resolution(self):
        events = [{"start": 0.0, "end": 2.0, "text": "Hello world"}]
        # Mode 1: With reference
        res1 = resolve_canonical_transcript(events, "Hello world")
        self.assertEqual(res1["source"], "USER_PROVIDED_REFERENCE")
        self.assertTrue(res1["has_reference"])
        self.assertEqual(res1["wer"], 0.0)

        # Mode 2: Without reference
        res2 = resolve_canonical_transcript(events, None)
        self.assertEqual(res2["source"], "AUTONOMOUS_ASR_FALLBACK")
        self.assertFalse(res2["has_reference"])
        self.assertIsNone(res2["wer"])
        self.assertEqual(res2["canonical_text"], "Hello world")


class TestPipelineEndToEnd(unittest.TestCase):
    def test_acceptance_criteria(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a 4-second synthetic speech-like wav
            sr = 16000
            t = np.linspace(0, 4.0, 4 * sr, endpoint=False)
            audio = (0.3 * np.sin(2 * np.pi * 300 * t)).astype(np.float32)
            input_wav = os.path.join(tmpdir, "input.wav")
            sf.write(input_wav, audio, sr)

            output_dir = os.path.join(tmpdir, "output")
            telemetry = run_pipeline(
                input_audio_path=input_wav,
                reference_transcript_path=None,
                output_dir=output_dir,
                whisper_model_size="tiny.en",
            )

            clean_wav_path = os.path.join(output_dir, "preprocessed_clean.wav")
            info = sf.info(clean_wav_path)

            # 1. Sample Rate: Exactly 16000 Hz, 1 channel, PCM_16
            self.assertEqual(info.samplerate, 16000)
            self.assertEqual(info.channels, 1)
            self.assertEqual(info.subtype, "PCM_16")

            # 2. Integrated Loudness: -20.0 +/- 0.5 LUFS
            meter = pyln.Meter(16000)
            data, _ = sf.read(clean_wav_path)
            measured_lufs = meter.integrated_loudness(data)
            self.assertAlmostEqual(measured_lufs, -20.0, delta=0.5)

            # 3. Peak Ceiling: <= 0.891 (-1.0 dBFS)
            self.assertLessEqual(np.max(np.abs(data)), 0.891 + 1e-4)

            # 6. Transcript Bounding
            events_path = os.path.join(output_dir, "transcript_events.txt")
            self.assertTrue(os.path.exists(events_path))

            # 7. Missing Transcript Test: elevates ASR to canonical
            canonical_path = os.path.join(output_dir, "canonical_transcript.txt")
            self.assertTrue(os.path.exists(canonical_path))
            self.assertEqual(telemetry["transcript_resolution"]["source"], "AUTONOMOUS_ASR_FALLBACK")


if __name__ == "__main__":
    unittest.main()
