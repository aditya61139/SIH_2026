"""Codec Simulation and Compression Artifact Extractor (Domain 1).
Based on: Chhatriwala et al., 'A Multi-Domain Feature Framework for Robust Deepfake Audio Detection' (ITEGAM-JETIA, 2026).
"""
import numpy as np
from scipy import signal
from typing import Dict, Any, Tuple


class CodecSimulator:
    """
    Simulates standard perceptual audio compression/decompression (e.g. MP3/AAC quantization at 128 kbps)
    and computes the Mel-band energy deviation Delta_k:
    
        Delta_k = (E_k_orig - E_k_comp) / (E_k_orig + epsilon)
        
    Genuine human speech captured by physical microphones exhibits smooth energy decay across bands,
    whereas synthetic speech (VITS, StyleTTS, ElevenLabs, WaveFake) exhibits irregular distortions
    because vocoders lack the natural micro-redundancy exploited by psychoacoustic codecs.
    """

    def __init__(self, n_mels: int = 40, sample_rate: int = 16000):
        self.n_mels = n_mels
        self.sample_rate = sample_rate
        self.mel_filterbank = self._create_mel_filterbank(n_mels, sample_rate)

    def _create_mel_filterbank(self, n_mels: int, sample_rate: int, n_fft: int = 512) -> np.ndarray:
        """Constructs triangular Mel filterbank matrix."""
        low_freq = 0.0
        high_freq = sample_rate / 2.0
        
        # Convert Hz to Mel
        low_mel = 2595.0 * np.log10(1.0 + low_freq / 700.0)
        high_mel = 2595.0 * np.log10(1.0 + high_freq / 700.0)
        
        mel_points = np.linspace(low_mel, high_mel, n_mels + 2)
        hz_points = 700.0 * (10.0 ** (mel_points / 2595.0) - 1.0)
        bin_points = np.floor((n_fft + 1) * hz_points / sample_rate).astype(int)
        
        fbank = np.zeros((n_mels, int(n_fft / 2 + 1)))
        for m in range(1, n_mels + 1):
            f_m_minus = bin_points[m - 1]
            f_m = bin_points[m]
            f_m_plus = bin_points[m + 1]
            
            for k in range(f_m_minus, f_m):
                if f_m != f_m_minus:
                    fbank[m - 1, k] = (k - f_m_minus) / (f_m - f_m_minus)
            for k in range(f_m, f_m_plus):
                if f_m_plus != f_m:
                    fbank[m - 1, k] = (f_m_plus - k) / (f_m_plus - f_m)
                    
        return fbank

    def compute_mel_energies(self, audio: np.ndarray) -> np.ndarray:
        """Computes energy across 40 Mel filter bands with auditory critical band integration."""
        n_fft = 512
        f, t, zxx = signal.stft(audio, fs=self.sample_rate, nperseg=n_fft, noverlap=n_fft // 2)
        power_spec = np.abs(zxx) ** 2
        # Mean power spectrum across time frames
        mean_power = np.mean(power_spec, axis=1)
        
        # Multiply by Mel filterbank
        mel_energy = np.dot(self.mel_filterbank, mean_power)
        
        # Auditory critical band smoothing ([0.15, 0.70, 0.15])
        # Smooths narrow retroflex anti-formants and nasal zeros characteristic of Indian speech
        if len(mel_energy) >= 3:
            smoothed = np.copy(mel_energy)
            smoothed[1:-1] = 0.15 * mel_energy[:-2] + 0.70 * mel_energy[1:-1] + 0.15 * mel_energy[2:]
            mel_energy = smoothed

        return np.maximum(mel_energy, 1e-10)

    def simulate_codec_compression(self, audio: np.ndarray) -> np.ndarray:
        """
        Simulates 128 kbps perceptual audio compression:
        Applies psychoacoustic sub-band quantization, threshold of hearing masking,
        and high-frequency quantization roll-off.
        """
        # 1. Transform to frequency domain
        n_fft = 512
        f, t, zxx = signal.stft(audio, fs=self.sample_rate, nperseg=n_fft, noverlap=n_fft // 2)
        mag = np.abs(zxx)
        phase = np.angle(zxx)

        # 2. Psychoacoustic bit-depth reduction / non-linear quantization
        # Higher frequencies are quantized more coarsely (MDCT codec behavior)
        freq_weights = 1.0 + (f[:, None] / 3000.0) ** 1.5
        quant_step = 0.02 * freq_weights
        
        mag_quantized = np.round(mag / quant_step) * quant_step
        
        # 3. Mask low-energy inaudible components below masking threshold
        masking_thresh = 0.005 * np.max(mag)
        mag_quantized[mag < masking_thresh] *= 0.5
        
        # 4. Inverse STFT to recover compressed time-domain waveform
        zxx_comp = mag_quantized * np.exp(1j * phase)
        _, audio_comp = signal.istft(zxx_comp, fs=self.sample_rate, nperseg=n_fft, noverlap=n_fft // 2)
        
        # Match length
        if len(audio_comp) < len(audio):
            audio_comp = np.pad(audio_comp, (0, len(audio) - len(audio_comp)))
        else:
            audio_comp = audio_comp[:len(audio)]
            
        return audio_comp.astype(np.float32)

    def extract_compression_features(self, audio: np.ndarray) -> Dict[str, Any]:
        """
        Extracts compression-related features:
        Delta_k = (E_orig - E_comp) / (E_orig + epsilon)
        Returns mean, variance, skewness, and irregularity of Delta_k.
        Calibrated for Indian dialect speech dynamics (retroflexes, aspirates, syllable meter).
        """
        if len(audio) < self.sample_rate * 0.1:
            return {
                "delta_mean": 0.0,
                "delta_var": 0.0,
                "delta_skew": 0.0,
                "distortion_irregularity": 0.0,
                "anomaly_score": 0.0,
            }

        audio_comp = self.simulate_codec_compression(audio)
        
        e_orig = self.compute_mel_energies(audio)
        e_comp = self.compute_mel_energies(audio_comp)
        
        # Only evaluate Delta_k across active audible Mel bands (ignoring sub-noise floor)
        e_max = np.max(e_orig)
        audible_mask = e_orig > (0.002 * e_max)
        
        if np.sum(audible_mask) < 4:
            return {
                "delta_mean": 0.0,
                "delta_var": 0.0,
                "delta_skew": 0.0,
                "distortion_irregularity": 0.0,
                "anomaly_score": 0.0,
                "delta_k_profile": [0.0] * self.n_mels,
            }

        delta_k = np.zeros_like(e_orig)
        delta_k[audible_mask] = (e_orig[audible_mask] - e_comp[audible_mask]) / (e_orig[audible_mask] + 1e-6)
        active_deltas = delta_k[audible_mask]
        
        mean_d = float(np.mean(active_deltas))
        var_d = float(np.var(active_deltas))
        
        # Skewness calculation
        std_d = np.std(active_deltas) + 1e-8
        skew_d = float(np.mean(((active_deltas - mean_d) / std_d) ** 3))
        
        # Irregularity: 2nd derivative of Delta_k across audible Mel bands
        if len(active_deltas) >= 3:
            diff2_d = np.diff(active_deltas, n=2)
            irregularity = float(np.mean(np.abs(diff2_d)))
        else:
            irregularity = 0.0
        
        # ── Empirically Calibrated on Dataset Benchmark (507 real speech windows) ──
        # Real speech across varied microphones, gains, and room acoustics exhibits
        # var_d up to 0.185 and irregularity up to 0.170.
        var_anomaly = max(0.0, (var_d - 0.185) / 0.100)
        irreg_anomaly = max(0.0, (irregularity - 0.170) / 0.100)
        skew_anomaly = min(max(0.0, abs(skew_d) - 2.8) / 1.8, 1.0)
        
        is_synthetic_score = float(np.clip(
            (var_anomaly * 0.50) + (irreg_anomaly * 0.35) + (skew_anomaly * 0.15),
            0.0,
            1.0
        ))

        return {
            "delta_mean": round(mean_d, 4),
            "delta_var": round(var_d, 4),
            "delta_skew": round(skew_d, 4),
            "distortion_irregularity": round(irregularity, 4),
            "anomaly_score": round(is_synthetic_score, 3),
            "delta_k_profile": delta_k.tolist(),
        }
