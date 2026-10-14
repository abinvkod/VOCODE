import os
import numpy as np
import scipy.signal as signal
import soundfile as sf
import librosa
import pyloudnorm as pyln

def load_audio(file_path: str) -> tuple[np.ndarray, int]:
    """Load arbitrary audio file into float32 array in [-1.0, 1.0]."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    try:
        audio, sr = sf.read(file_path, dtype='float32')
        return audio, sr
    except Exception:
        pass
    try:
        audio, sr = librosa.load(file_path, sr=None, mono=False, dtype=np.float32)
        return audio, sr
    except Exception:
        pass
    # ffmpeg fallback
    import subprocess
    cmd = ['ffmpeg', '-v', 'quiet', '-i', file_path, '-f', 'wav', '-ar', '16000', '-ac', '1', 'pipe:1']
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    import io
    audio, sr = sf.read(io.BytesIO(res.stdout), dtype='float32')
    return audio, sr

def downmix_to_mono(audio: np.ndarray) -> np.ndarray:
    """Average multi-channel audio to single mono channel."""
    if audio.ndim == 1:
        return audio
    if audio.ndim == 2:
        # Check if shape is (channels, samples) or (samples, channels)
        if audio.shape[0] < audio.shape[1] and audio.shape[0] <= 8:
            return np.mean(audio, axis=0)
        else:
            return np.mean(audio, axis=1)
    return np.mean(audio.reshape(-1, audio.shape[-1]), axis=0)

def resample_to_16k(audio: np.ndarray, orig_sr: int) -> np.ndarray:
    """Resample audio to 16,000 Hz using high-quality polyphase sinc filtering."""
    if orig_sr == 16000:
        return audio
    return librosa.resample(audio, orig_sr=orig_sr, target_sr=16000, res_type='soxr_hq')

def remove_dc_and_rumble(audio: np.ndarray, sr: int = 16000, cutoff_hz: float = 70.0) -> np.ndarray:
    """Remove DC bias and apply 4th-order Butterworth high-pass filter at 70 Hz."""
    # DC centering
    audio = audio - np.mean(audio)
    
    # Butterworth 4th-order high-pass filter
    nyquist = 0.5 * sr
    norm_cutoff = cutoff_hz / nyquist
    b, a = signal.butter(4, norm_cutoff, btype='highpass')
    # Zero-phase forward-backward filter
    filtered = signal.filtfilt(b, a, audio)
    return filtered.astype(np.float32)

def normalize_loudness_ebu_r128(audio: np.ndarray, sr: int = 16000, target_lufs: float = -20.0) -> tuple[np.ndarray, float, float]:
    """Normalize integrated loudness according to EBU R128 / ITU-R BS.1770-4."""
    meter = pyln.Meter(sr)
    try:
        measured_lufs = meter.integrated_loudness(audio)
        if np.isneginf(measured_lufs) or np.isnan(measured_lufs):
            measured_lufs = -30.0
    except Exception:
        measured_lufs = -30.0
        
    gain_db = target_lufs - measured_lufs
    gain_linear = 10.0 ** (gain_db / 20.0)
    normalized = audio * gain_linear
    
    # True-peak limiting at -1.0 dBFS (approx 0.891 linear)
    max_peak = np.max(np.abs(normalized))
    ceiling = 0.891
    if max_peak > ceiling:
        reduction = ceiling / max_peak
        normalized = normalized * reduction
        gain_db += 20.0 * np.log10(reduction)
        
    return normalized.astype(np.float32), float(measured_lufs), float(gain_db)

def trim_dead_air(audio: np.ndarray, sr: int = 16000, buffer_ms: float = 200.0) -> tuple[np.ndarray, float, float]:
    """Trim leading and trailing silence beyond buffer_ms."""
    frame_len = 512
    hop_len = 160
    
    # Calculate energy envelope
    frames = librosa.util.frame(audio, frame_length=frame_len, hop_length=hop_len)
    rms = np.sqrt(np.mean(frames**2, axis=0) + 1e-9)
    
    threshold = np.max(rms) * 0.02
    active_frames = np.where(rms > threshold)[0]
    
    if len(active_frames) == 0:
        return audio, 0.0, 0.0
        
    start_frame = active_frames[0]
    end_frame = active_frames[-1]
    
    buffer_samples = int((buffer_ms / 1000.0) * sr)
    start_idx = max(0, start_frame * hop_len - buffer_samples)
    end_idx = min(len(audio), end_frame * hop_len + frame_len + buffer_samples)
    
    lead_trim_sec = start_idx / sr
    tail_trim_sec = (len(audio) - end_idx) / sr
    
    return audio[start_idx:end_idx], float(lead_trim_sec), float(tail_trim_sec)
