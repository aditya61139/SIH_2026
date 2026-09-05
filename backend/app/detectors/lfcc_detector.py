"""Linear Frequency Cepstral Coefficients (LFCC) Forensic Detector (ASVspoof Gold Standard)."""
import numpy as np
from scipy import signal, fftpack
from typing import Dict, Any, List
from app.detectors.base import BaseDetector
from app.audio.preprocessor import AudioPreprocessor


class LFCCDetector(BaseDetector):
    """
    Extracts Linear Frequency Cepstral Coefficients (LFCC) + Delta + Delta-Delta.
    Unlike Mel filterbanks which compress higher frequencies (modeled on human hearing),
    LFCC uses linear filterbanks up to the Nyquist frequency, making it the benchmark
    feature for capturing high-frequency neural vocoder artifacts and spectral quantization.
    """

    def __init__(self, num_filters: int = 24, num_ceps: int = 20):
        self.num_filters = num_filters
        self.num_ceps = num_ceps

    @property
    def name(self) -> str:
        return "lfcc"

    def analyze(self, audio: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
        if len(audio) < sample_rate * 0.2 or AudioPreprocessor.is_silent(audio):
            return {
                "anomaly_score": 0.0,
                "confidence": 0.0,
                "metrics": {
                    "lfcc_variance": 0.0,
                    "hf_lfcc_energy_ratio": 0.0,
                    "delta_acceleration": 0.0,
                },
                "anomalies_detected": [],
            }

        # 1. Framing & Windowing (25ms window, 10ms hop)
        frame_len = int(0.025 * sample_rate)  # 400 samples
        hop_len = int(0.010 * sample_rate)    # 160 samples
        n_fft = 512

        frames = []
        for i in range(0, len(audio) - frame_len, hop_len):
            frame = audio[i : i + frame_len] * np.hamming(frame_len)
            frames.append(frame)

        if len(frames) < 5:
            return {
                "anomaly_score": 0.0,
                "confidence": 0.0,
                "metrics": {},
                "anomalies_detected": [],
            }

        frames = np.array(frames)

        # 2. Power Spectrum
        mag_spec = np.abs(np.fft.rfft(frames, n=n_fft))
        pow_spec = (mag_spec ** 2) / n_fft

        # 3. Linear Filterbank Design
        linear_fb = self._create_linear_filterbank(
            num_filters=self.num_filters,
            n_fft=n_fft,
            sample_rate=sample_rate,
        )

        # Apply filterbank
        fb_energies = np.dot(pow_spec, linear_fb.T)
        fb_energies = np.maximum(fb_energies, 1e-12)
        log_fb = np.log(fb_energies)

        # 4. Discrete Cosine Transform (DCT-II) -> Static LFCCs
        lfcc_static = fftpack.dct(log_fb, type=2, axis=1, norm="ortho")[:, : self.num_ceps]

        # 5. Delta & Delta-Delta computation
        delta1 = self._compute_deltas(lfcc_static, width=2)
        delta2 = self._compute_deltas(delta1, width=2)

        # 6. Forensic Metric Extraction
        # High-frequency LFCC variance (coefficients 10-20)
        hf_lfcc_var = float(np.mean(np.var(lfcc_static[:, 10:], axis=0)))
        lfcc_total_var = float(np.mean(np.var(lfcc_static, axis=0)))
        delta_accel = float(np.mean(np.abs(delta2)))

        # HF to Total Energy Ratio in Cepstral Domain
        hf_ratio = float(hf_lfcc_var / (lfcc_total_var + 1e-12))

        # ── Anomaly Assessment ──
        anomalies = []
        score_components = []

        # Check A: High-frequency cepstral flatness / abnormal variance
        if hf_ratio < 0.12 or hf_ratio > 0.65:
            ratio_score = 0.45
            score_components.append(ratio_score)
            anomalies.append({
                "type": "LFCC_HIGH_FREQ_ANOMALY",
                "severity": "HIGH" if hf_ratio < 0.08 else "MEDIUM",
                "metric_name": "Linear Filterbank Cepstral Distribution",
                "value": round(hf_ratio, 3),
                "threshold": "Expected human range: 0.18 - 0.50",
                "description": "Linear frequency cepstrum reveals high-frequency spectral artifacts characteristic of neural vocoder interpolation.",
            })
        else:
            score_components.append(0.0)

        # Check B: Unnatural Delta Acceleration (Smoothness across frames)
        if delta_accel < 0.025:
            accel_score = min((0.025 - delta_accel) / 0.020, 1.0) * 0.40
            score_components.append(accel_score)
            anomalies.append({
                "type": "LFCC_STATIC_TRAJECTORY",
                "severity": "MEDIUM",
                "metric_name": "LFCC Delta-Delta Acceleration",
                "value": round(delta_accel, 4),
                "threshold": "< 0.025 (Natural human: 0.035 - 0.150)",
                "description": "Cepstral dynamic acceleration is unnaturally static between frames, indicating synthetic parameter continuity.",
            })
        else:
            score_components.append(0.0)

        anomaly_score = float(np.clip(np.sum(score_components), 0.0, 1.0))
        confidence = 0.85 if len(frames) >= 20 else 0.60

        return {
            "anomaly_score": round(anomaly_score, 3),
            "confidence": round(confidence, 2),
            "metrics": {
                "lfcc_variance": round(lfcc_total_var, 3),
                "hf_lfcc_energy_ratio": round(hf_ratio, 4),
                "delta_acceleration": round(delta_accel, 4),
                "num_frames_evaluated": len(frames),
            },
            "anomalies_detected": anomalies,
        }

    def _create_linear_filterbank(self, num_filters: int, n_fft: int, sample_rate: int) -> np.ndarray:
        """Constructs linearly-spaced triangular filterbank matrix."""
        num_bins = n_fft // 2 + 1
        freq_bins = np.linspace(0, sample_rate / 2, num_bins)
        filter_points = np.linspace(0, sample_rate / 2, num_filters + 2)

        fbank = np.zeros((num_filters, num_bins), dtype=np.float32)
        for m in range(1, num_filters + 1):
            f_m_minus = filter_points[m - 1]
            f_m = filter_points[m]
            f_m_plus = filter_points[m + 1]

            for k in range(num_bins):
                f_k = freq_bins[k]
                if f_m_minus <= f_k <= f_m:
                    fbank[m - 1, k] = (f_k - f_m_minus) / (f_m - f_m_minus + 1e-12)
                elif f_m < f_k <= f_m_plus:
                    fbank[m - 1, k] = (f_m_plus - f_k) / (f_m_plus - f_m + 1e-12)

        return fbank

    def _compute_deltas(self, feat: np.ndarray, width: int = 2) -> np.ndarray:
        """Computes dynamic delta feature trajectory."""
        n_frames, n_dim = feat.shape
        deltas = np.zeros_like(feat)
        denom = 2 * sum([i ** 2 for i in range(1, width + 1)])

        for t in range(n_frames):
            num = np.zeros(n_dim)
            for w in range(1, width + 1):
                t_plus = min(t + w, n_frames - 1)
                t_minus = max(t - w, 0)
                num += w * (feat[t_plus] - feat[t_minus])
            deltas[t] = num / denom

        return deltas
