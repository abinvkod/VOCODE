import numpy as np
import scipy.signal as signal
import librosa

def compute_stft(audio: np.ndarray, n_fft: int = 1024, hop_length: int = 256):
    """Computes STFT and returns complex matrix, magnitude, and phase."""
    stft_matrix = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length, win_length=n_fft, window='hann')
    return stft_matrix, np.abs(stft_matrix), np.angle(stft_matrix)

def estimate_noise_floor(magnitude: np.ndarray, percentile: float = 12.0) -> np.ndarray:
    """Estimates stationary noise floor from lowest energy frames."""
    frame_energy = np.sum(magnitude**2, axis=0)
    cutoff = np.percentile(frame_energy, percentile)
    noise_frames = np.where(frame_energy <= cutoff)[0]
    if len(noise_frames) > 0:
        return np.mean(magnitude[:, noise_frames], axis=1, keepdims=True)
    return np.min(magnitude, axis=1, keepdims=True)

def spectral_subtraction(magnitude: np.ndarray, noise_profile: np.ndarray, alpha: float = 1.5, beta: float = 0.03) -> np.ndarray:
    """Spectral subtraction with oversubtraction factor alpha and floor beta."""
    return np.maximum(magnitude - alpha * noise_profile, beta * magnitude)

def isolate_vocal_harmonics(magnitude: np.ndarray, kernel_time: int = 31, kernel_freq: int = 31, margin: tuple = (1.5, 1.5)) -> np.ndarray:
    """Isolates vocal harmonics using 2D median filtering / HPSS, suppressing percussive bursts."""
    harmonic_mag, percussive_mag = librosa.decompose.hpss(magnitude, kernel_size=(kernel_freq, kernel_time), margin=margin)
    eps = 1e-8
    vocal_mask = (harmonic_mag**2) / (harmonic_mag**2 + percussive_mag**2 + eps)
    return magnitude * (0.15 + 0.85 * vocal_mask)

def reconstruct_waveform(magnitude: np.ndarray, phase: np.ndarray, hop_length: int = 256, n_fft: int = 1024, length: int | None = None) -> np.ndarray:
    """Reconstructs time-domain audio from magnitude and phase via inverse STFT."""
    stft_recon = magnitude * np.exp(1j * phase)
    return librosa.istft(stft_recon, hop_length=hop_length, win_length=n_fft, window='hann', length=length).astype(np.float32)

def spectral_denoise_and_isolate(
    audio: np.ndarray,
    sr: int = 16000,
    n_fft: int = 1024,
    hop_length: int = 256,
    alpha: float = 1.5,
    beta: float = 0.03
) -> np.ndarray:
    """
    Applies STFT Wiener Spectral Subtraction for static noise reduction
    combined with Harmonic-Percussive Source Separation (HPSS) to suppress
    impulsive audience clapping, cheers, and clicks while preserving vocal harmonics.
    """
    _, magnitude, phase = compute_stft(audio, n_fft=n_fft, hop_length=hop_length)
    noise_profile = estimate_noise_floor(magnitude, percentile=12.0)
    clean_mag = spectral_subtraction(magnitude, noise_profile, alpha=alpha, beta=beta)
    enhanced_mag = isolate_vocal_harmonics(clean_mag)
    enhanced_audio = reconstruct_waveform(enhanced_mag, phase, hop_length=hop_length, n_fft=n_fft, length=len(audio))
    return enhanced_audio

denoise_and_isolate_vocals = spectral_denoise_and_isolate

