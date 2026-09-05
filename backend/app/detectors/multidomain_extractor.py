"""Multi-Domain Feature Extraction Pipeline.
Implements the 6 feature families from:
1. Chhatriwala et al., 'A Multi-Domain Feature Framework for Robust Deepfake Audio Detection' (ITEGAM-JETIA 2026).
2. Gong & Li, 'Deepfake Voice Detection: An Approach Using End-to-End Transformer with Acoustic Feature Fusion by Cross-Attention' (MDPI Electronics 2025).
"""
import numpy as np
from scipy import signal
from typing import Dict, Any, Tuple, List
from app.audio.codec_simulator import CodecSimulator
from app.audio.preprocessor import AudioPreprocessor


class MultiDomainFeatureExtractor:
    """
    Extracts 6 interconnected feature families for deepfake audio detection:
    1. Compression-Related Features (Mel-band Delta_k statistics)
    2. Acoustic Features (MFCC + Delta + Delta-Delta 39-dim dynamics)
    3. Prosodic & Perturbation Features (Jitter, Shimmer, F0 contour with interpolation)
    4. Phase-Based Features (Group Delay tau_g, Instantaneous Frequency omega_inst)
    5. Emotional & Low-Level Descriptors (HNR, Spectral Flux, ZCR, Centroid)
    6. Statistical & Spectral Entropy Features (STE, Hs, Spectral Flatness)
    """

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.codec_sim = CodecSimulator(n_mels=40, sample_rate=sample_rate)

    def extract_all(self, audio: np.ndarray) -> Dict[str, Any]:
        """Extracts complete multi-domain feature representation."""
        if len(audio) < self.sample_rate * 0.1 or AudioPreprocessor.is_silent(audio):
            return self._get_empty_features()

        # Domain 1: Compression Features
        comp_feat = self.codec_sim.extract_compression_features(audio)

        # Domain 2: Acoustic MFCC + Deltas
        acoust_feat = self._extract_acoustic_mfcc_dynamics(audio)

        # Domain 3: Prosodic, Jitter & Shimmer
        pros_feat = self._extract_prosody_perturbations(audio)

        # Domain 4: Phase & Group Delay
        phase_feat = self._extract_phase_group_delay(audio)

        # Domain 5: Emotional & LLDs
        emobase_feat = self._extract_emotional_llds(audio)

        # Domain 6: Statistical & Spectral Entropy
        spec_stat_feat = self._extract_statistical_spectral(audio)

        # Build concatenated unified feature vector
        vector_parts = [
            comp_feat["delta_mean"],
            comp_feat["delta_var"],
            comp_feat["delta_skew"],
            comp_feat["distortion_irregularity"],
            acoust_feat["mfcc_mean_norm"],
            acoust_feat["mfcc_var_norm"],
            acoust_feat["delta_var_norm"],
            pros_feat["jitter"],
            pros_feat["shimmer"],
            pros_feat["f0_std_norm"],
            pros_feat["voiced_ratio"],
            phase_feat["group_delay_var"],
            phase_feat["phase_entropy"],
            phase_feat["inst_freq_var"],
            emobase_feat["hnr_norm"],
            emobase_feat["spectral_flux"],
            emobase_feat["zcr_mean"],
            emobase_feat["centroid_norm"],
            spec_stat_feat["spectral_entropy"],
            spec_stat_feat["spectral_flatness"],
            spec_stat_feat["ste_variance"],
        ]

        feature_vector = np.array(vector_parts, dtype=np.float32)

        return {
            "compression": comp_feat,
            "acoustic": acoust_feat,
            "prosody": pros_feat,
            "phase": phase_feat,
            "emotional_lld": emobase_feat,
            "statistical_spectral": spec_stat_feat,
            "fused_vector": feature_vector,
        }

    def _extract_acoustic_mfcc_dynamics(self, audio: np.ndarray) -> Dict[str, Any]:
        """
        Domain 2: 13 MFCCs + Delta + Delta^2 (39-dim acoustic vector per frame).
        Analyzes smooth continuous formant transitions vs neural vocoder quantization.
        """
        n_fft = 512
        hop_length = int(0.010 * self.sample_rate)  # 10ms step
        win_length = int(0.025 * self.sample_rate)  # 25ms Hamming window

        f, t, zxx = signal.stft(
            audio,
            fs=self.sample_rate,
            nperseg=win_length,
            noverlap=win_length - hop_length,
            nfft=n_fft,
        )
        mag_spec = np.abs(zxx) ** 2

        # 40 Mel filters
        mel_fb = self.codec_sim.mel_filterbank
        mel_spec = np.dot(mel_fb, mag_spec)
        log_mel = np.log(np.maximum(mel_spec, 1e-10))

        # Discrete Cosine Transform (DCT-II) for 13 MFCCs
        # c_n(t) = sum_k log E_k(t) * cos(pi * n / K * (k - 0.5))
        K, T_frames = log_mel.shape
        n_mfcc = 13
        n_idx = np.arange(n_mfcc)[:, None]
        k_idx = (np.arange(K) + 0.5)[None, :]
        dct_basis = np.cos(np.pi * n_idx * k_idx / K)

        mfcc = np.dot(dct_basis, log_mel)  # Shape: (13, T_frames)

        # Delta & Delta-Delta computation
        if mfcc.shape[1] >= 5:
            delta1 = signal.savgol_filter(mfcc, window_length=5, polyorder=2, deriv=1, axis=1)
            delta2 = signal.savgol_filter(mfcc, window_length=5, polyorder=2, deriv=2, axis=1)
        else:
            delta1 = np.diff(mfcc, axis=1, prepend=mfcc[:, :1])
            delta2 = np.diff(delta1, axis=1, prepend=delta1[:, :1])

        # Frame-wise pooling
        mfcc_mean = float(np.mean(mfcc))
        mfcc_var = float(np.var(mfcc))
        delta_var = float(np.var(delta1))
        delta2_var = float(np.var(delta2))

        # Synthetic voice anomaly indicator: severely collapsed delta MFCC variance (< 1.5)
        # typical of quantized neural speech synthesis
        delta_anomaly = max(0.0, 1.0 - (delta_var / 1.5)) if delta_var < 1.5 else 0.0
        delta2_anomaly = max(0.0, 1.0 - (delta2_var / 2.5)) if delta2_var < 2.5 else 0.0
        acoustic_anomaly = float(np.clip(
            delta_anomaly * 0.5 + delta2_anomaly * 0.5,
            0.0,
            1.0,
        ))

        return {
            "mfcc_mean_norm": round(mfcc_mean / 100.0, 4),
            "mfcc_var_norm": round(mfcc_var / 500.0, 4),
            "delta_var_norm": round(delta_var / 10.0, 4),
            "delta2_var_norm": round(delta2_var / 20.0, 4),
            "anomaly_score": round(acoustic_anomaly, 3),
        }

    def _extract_prosody_perturbations(self, audio: np.ndarray) -> Dict[str, Any]:
        """
        Domain 3: Prosodic Dynamics, Jitter, Shimmer, and Pitch F0 tracking
        with Linear Interpolation across silence (from MDPI Electronics 2025).
        """
        frame_len = int(0.030 * self.sample_rate)  # 30ms frames
        hop_len = int(0.010 * self.sample_rate)    # 10ms hop
        num_frames = (len(audio) - frame_len) // hop_len

        f0_raw = []
        peak_amps = []
        periods = []

        for i in range(max(1, num_frames)):
            frame = audio[i * hop_len : i * hop_len + frame_len]
            if AudioPreprocessor.is_silent(frame, 0.004):
                f0_raw.append(np.nan)
                continue

            corr = signal.correlate(frame, frame, mode="full")
            corr = corr[len(corr) // 2 :]
            if corr[0] > 1e-10:
                corr /= corr[0]
                min_lag = int(self.sample_rate / 450)
                max_lag = int(self.sample_rate / 65)
                if len(corr) > max_lag:
                    peak_idx = min_lag + np.argmax(corr[min_lag:max_lag])
                    if corr[peak_idx] > 0.35:
                        f0_val = self.sample_rate / peak_idx
                        f0_raw.append(f0_val)
                        periods.append(1.0 / f0_val)
                        peak_amps.append(np.max(np.abs(frame)))
                    else:
                        f0_raw.append(np.nan)
                else:
                    f0_raw.append(np.nan)
            else:
                f0_raw.append(np.nan)

        f0_array = np.array(f0_raw)
        voiced_ratio = float(np.mean(~np.isnan(f0_array))) if len(f0_array) > 0 else 0.0

        # Linear Interpolation of unvoiced/silent NaN segments (Gong & Li 2025)
        valid_idx = np.where(~np.isnan(f0_array))[0]
        if len(valid_idx) >= 5:
            interp_f0 = np.interp(np.arange(len(f0_array)), valid_idx, f0_array[valid_idx])
            mean_f0 = float(np.mean(interp_f0))
            std_f0 = float(np.std(interp_f0))
            f0_range = float(np.ptp(interp_f0))
        else:
            mean_f0 = 150.0
            std_f0 = 25.0
            f0_range = 30.0

        # ── Jitter Calculation (Equation 4) ──
        if len(periods) >= 5:
            p_arr = np.array(periods)
            mean_p = np.mean(p_arr)
            jitter = float(np.mean(np.abs(np.diff(p_arr))) / (mean_p + 1e-8))
        else:
            jitter = 0.025

        # ── Shimmer Calculation (Equation 5) ──
        if len(peak_amps) >= 5:
            a_arr = np.array(peak_amps)
            mean_a = np.mean(a_arr)
            shimmer = float(np.mean(np.abs(np.diff(a_arr))) / (mean_a + 1e-8))
        else:
            shimmer = 0.065

        # In natural human speech, Jitter is typically 0.008 - 0.065
        # and Shimmer is 0.025 - 0.160.
        if voiced_ratio >= 0.30:
            jitter_anomaly = max(0.0, (0.005 - jitter) / 0.004) if jitter < 0.005 else (min((jitter - 0.095) / 0.05, 1.0) if jitter > 0.095 else 0.0)
            shimmer_anomaly = max(0.0, (0.016 - shimmer) / 0.012) if shimmer < 0.016 else (min((shimmer - 0.24) / 0.10, 1.0) if shimmer > 0.24 else 0.0)
            pitch_anomaly = max(0.0, (5.5 - std_f0) / 4.5) if (std_f0 < 5.5 and voiced_ratio >= 0.50) else 0.0
            prosody_anomaly_score = float(np.clip(
                0.40 * jitter_anomaly + 0.35 * shimmer_anomaly + 0.25 * pitch_anomaly,
                0.0,
                1.0
            ))
        else:
            prosody_anomaly_score = 0.0

        return {
            "jitter": round(jitter, 5),
            "shimmer": round(shimmer, 5),
            "mean_f0_hz": round(mean_f0, 1),
            "std_f0_hz": round(std_f0, 1),
            "f0_range_hz": round(f0_range, 1),
            "f0_std_norm": round(min(std_f0 / 50.0, 1.0), 4),
            "voiced_ratio": round(voiced_ratio, 3),
            "anomaly_score": round(prosody_anomaly_score, 3),
        }

    def _extract_phase_group_delay(self, audio: np.ndarray) -> Dict[str, Any]:
        """
        Domain 4: Phase-Based Features:
        Group delay tau_g(f,t) = -d(phi)/df (unwrapped along frequency axis 0)
        Instantaneous frequency omega_inst(f,t) = d(phi)/dt (unwrapped along time axis 1)
        """
        n_fft = 512
        f, t, zxx = signal.stft(audio, fs=self.sample_rate, nperseg=n_fft, noverlap=n_fft // 2)
        phases = np.angle(zxx)  # Range: [-pi, pi]

        # Group delay: -d(phi)/df unwrapped across frequency bins (axis 0)
        unwrapped_f = np.unwrap(phases, axis=0)
        group_delay = -np.diff(unwrapped_f, axis=0)
        group_delay_var = float(np.mean(np.var(group_delay, axis=0)))

        # Instantaneous frequency: d(phi)/dt unwrapped across time frames (axis 1)
        unwrapped_t = np.unwrap(phases, axis=1)
        inst_freq = np.diff(unwrapped_t, axis=1)
        inst_freq_var = float(np.mean(np.var(inst_freq, axis=1)))

        # Phase entropy
        phase_probs = np.histogram(phases, bins=20, density=True)[0] + 1e-12
        phase_probs /= np.sum(phase_probs)
        phase_entropy = float(-np.sum(phase_probs * np.log2(phase_probs)))

        # Genuine speech has smooth group delay governed by vocal tract;
        # synthetic audio exhibits high phase discontinuities (> 25.0)
        phase_anomaly = max(0.0, (group_delay_var - 15.0) / 25.0)
        entropy_anomaly = max(0.0, 4.0 - phase_entropy) / 2.0
        phase_score = float(np.clip(phase_anomaly * 0.6 + entropy_anomaly * 0.4, 0.0, 1.0))

        return {
            "group_delay_var": round(group_delay_var, 4),
            "inst_freq_var": round(inst_freq_var, 4),
            "phase_entropy": round(phase_entropy, 4),
            "anomaly_score": round(phase_score, 3),
        }

    def _extract_emotional_llds(self, audio: np.ndarray) -> Dict[str, Any]:
        """
        Domain 5: Low-Level Descriptors (LLDs):
        Harmonic-to-Noise Ratio (HNR), Spectral Flux, Zero-Crossing Rate (ZCR), Spectral Centroid.
        """
        # 1. ZCR
        zcr = float(np.mean(np.abs(np.diff(np.signbit(audio)))))

        # 2. Spectral Centroid & Flux
        n_fft = 512
        f, t, zxx = signal.stft(audio, fs=self.sample_rate, nperseg=n_fft, noverlap=n_fft // 2)
        mag = np.abs(zxx)
        
        sum_mag = np.sum(mag, axis=0) + 1e-12
        centroids = np.sum(f[:, None] * mag, axis=0) / sum_mag
        mean_centroid = float(np.mean(centroids))

        # Spectral Flux: frame-to-frame normalized magnitude difference
        diff_mag = np.diff(mag, axis=1)
        spectral_flux = float(np.mean(np.sqrt(np.sum(diff_mag ** 2, axis=0) + 1e-12)))

        # 3. Autocorrelation HNR
        corr = signal.correlate(audio, audio, mode="full")
        corr = corr[len(corr) // 2 :]
        if corr[0] > 1e-10:
            corr_norm = corr / corr[0]
            min_lag = int(self.sample_rate / 400)
            max_lag = int(self.sample_rate / 70)
            if len(corr_norm) > max_lag:
                pk = np.clip(np.max(corr_norm[min_lag:max_lag]), 1e-5, 0.9999)
                hnr_db = float(10 * np.log10(pk / (1.0 - pk)))
            else:
                hnr_db = 15.0
        else:
            hnr_db = 0.0

        # High HNR (>30dB) or very flat spectral flux indicates artificial vocoder smoothness
        lld_anomaly = float(np.clip(
            max(0.0, (hnr_db - 28.0) / 12.0) * 0.5 + max(0.0, 1.0 - (spectral_flux / 0.8)) * 0.5,
            0.0,
            1.0
        ))

        return {
            "hnr_db": round(hnr_db, 2),
            "hnr_norm": round(min(hnr_db / 35.0, 1.0), 4),
            "zcr_mean": round(zcr, 4),
            "spectral_flux": round(spectral_flux, 4),
            "centroid_hz": round(mean_centroid, 1),
            "centroid_norm": round(min(mean_centroid / 4000.0, 1.0), 4),
            "anomaly_score": round(lld_anomaly, 3),
        }

    def _extract_statistical_spectral(self, audio: np.ndarray) -> Dict[str, Any]:
        """
        Domain 6: Statistical & Spectral Features:
        Short-Time Energy (STE), Spectral Entropy (Hs, Equations 6-7), Spectral Flatness (SF, Equation 8).
        """
        n_fft = 512
        f, t, zxx = signal.stft(audio, fs=self.sample_rate, nperseg=n_fft, noverlap=n_fft // 2)
        power_spec = np.abs(zxx) ** 2  # |S(f,t)|^2

        # Spectral Entropy: H_s(t) = -sum_f p(f,t) * log p(f,t)
        total_p = np.sum(power_spec, axis=0, keepdims=True) + 1e-12
        p_dist = power_spec / total_p  # p(f,t)
        p_dist = np.maximum(p_dist, 1e-12)
        entropy_t = -np.sum(p_dist * np.log(p_dist), axis=0)
        mean_entropy = float(np.mean(entropy_t))

        # Spectral Flatness: SF(t) = exp(mean(log |S|^2)) / mean(|S|^2)
        log_power = np.log(np.maximum(power_spec, 1e-12))
        geom_mean_t = np.exp(np.mean(log_power, axis=0))
        arith_mean_t = np.mean(power_spec, axis=0) + 1e-12
        sf_t = geom_mean_t / arith_mean_t
        mean_flatness = float(np.mean(sf_t))

        # Short-Time Energy (STE)
        ste = np.sum(power_spec, axis=0)
        ste_variance = float(np.var(ste / (np.max(ste) + 1e-12)))

        # Synthetic speech yields high spectral flatness and high entropy
        stat_anomaly = float(np.clip(
            max(0.0, (mean_flatness - 0.45) / 0.40) * 0.6 + max(0.0, (mean_entropy - 4.2) / 1.5) * 0.4,
            0.0,
            1.0
        ))

        return {
            "spectral_entropy": round(mean_entropy, 4),
            "spectral_flatness": round(mean_flatness, 4),
            "ste_variance": round(ste_variance, 4),
            "anomaly_score": round(stat_anomaly, 3),
        }

    def _get_empty_features(self) -> Dict[str, Any]:
        return {
            "compression": {"anomaly_score": 0.0, "delta_mean": 0.0, "delta_var": 0.0, "delta_skew": 0.0},
            "acoustic": {"anomaly_score": 0.0, "mfcc_mean_norm": 0.0, "delta_var_norm": 0.0},
            "prosody": {"anomaly_score": 0.0, "jitter": 0.0, "shimmer": 0.0, "std_f0_hz": 0.0},
            "phase": {"anomaly_score": 0.0, "group_delay_var": 0.0, "phase_entropy": 0.0},
            "emotional_lld": {"anomaly_score": 0.0, "hnr_db": 0.0, "spectral_flux": 0.0},
            "statistical_spectral": {"anomaly_score": 0.0, "spectral_entropy": 0.0, "spectral_flatness": 0.0},
            "fused_vector": np.zeros(21, dtype=np.float32),
        }
