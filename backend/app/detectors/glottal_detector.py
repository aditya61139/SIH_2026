"""Biomechanical Glottal Flow and Vocal Tract Inverse Filtering Detector."""
import numpy as np
from scipy import signal, linalg
from typing import Dict, Any, List
from app.detectors.base import BaseDetector
from app.audio.preprocessor import AudioPreprocessor


class GlottalFlowDetector(BaseDetector):
    """
    Biomechanical Source-Filter Forensic Analyzer.
    Applies Linear Predictive Coding (LPC) inverse filtering to strip vocal tract resonances
    and isolate the reconstructed glottal airflow excitation pulse.
    Quantifies Normalized Amplitude Quotient (NAQ) and glottal closure deceleration to identify
    violations of human vocal fold biomechanics in neural speech models.
    """

    def __init__(self, lpc_order: int = 16):
        self.lpc_order = lpc_order

    @property
    def name(self) -> str:
        return "glottal"

    def analyze(self, audio: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
        if len(audio) < sample_rate * 0.3 or AudioPreprocessor.is_silent(audio):
            return {
                "anomaly_score": 0.0,
                "confidence": 0.0,
                "metrics": {
                    "naq_mean": 0.0,
                    "glottal_symmetry": 0.0,
                    "lpc_residual_kurtosis": 0.0,
                },
                "anomalies_detected": [],
            }

        # 1. Framing for LPC Inverse Filtering (30ms frames, 15ms hop)
        frame_len = int(0.030 * sample_rate)  # 480 samples
        hop_len = int(0.015 * sample_rate)    # 240 samples

        naq_values = []
        residual_kurtosis_list = []

        for i in range(0, len(audio) - frame_len, hop_len):
            frame = audio[i : i + frame_len]
            if AudioPreprocessor.is_silent(frame, rms_threshold=0.008):
                continue

            # Pre-emphasis
            preemp_frame = np.append(frame[0], frame[1:] - 0.97 * frame[:-1]) * np.hamming(frame_len)

            # LPC Coefficient Estimation via Levinson-Durbin
            lpc_coeffs = self._estimate_lpc(preemp_frame, self.lpc_order)
            if lpc_coeffs is None:
                continue

            # Inverse filtering: residual = A(z) * s(n)
            glottal_residual = signal.lfilter(lpc_coeffs, [1.0], frame)

            # Compute Glottal Pulse Metrics on integrated residual (estimated glottal flow)
            glottal_flow = np.cumsum(glottal_residual)
            glottal_flow = signal.detrend(glottal_flow)

            # Normalized Amplitude Quotient (NAQ)
            f_ac = float(np.ptp(glottal_flow))  # Peak-to-peak amplitude
            d_peak = float(np.abs(np.min(glottal_residual)))  # Max negative slope of closure
            
            # Estimate local pitch period T0 via autocorrelation
            t0_samples = int(sample_rate * 0.008)  # default ~125 Hz
            autocorr = signal.correlate(frame, frame, mode="full")[len(frame) // 2 :]
            if autocorr[0] > 1e-12:
                autocorr_norm = autocorr / autocorr[0]
                min_l, max_l = int(sample_rate / 400), int(sample_rate / 75)
                if len(autocorr_norm) > max_l:
                    t0_samples = int(min_l + np.argmax(autocorr_norm[min_l:max_l]))

            if d_peak > 1e-6 and t0_samples > 0:
                naq = f_ac / (d_peak * t0_samples + 1e-6)
                if 0.01 < naq < 1.0:
                    naq_values.append(naq)

            # Kurtosis of excitation residual (human glottal impulse is super-Gaussian/peaky)
            m4 = np.mean((glottal_residual - np.mean(glottal_residual)) ** 4)
            m2 = np.var(glottal_residual) ** 2 + 1e-12
            kurt = (m4 / m2) - 3.0
            residual_kurtosis_list.append(kurt)

        if not naq_values:
            return {
                "anomaly_score": 0.1,
                "confidence": 0.3,
                "metrics": {
                    "naq_mean": 0.15,
                    "glottal_symmetry": 0.5,
                    "lpc_residual_kurtosis": 3.0,
                },
                "anomalies_detected": [],
            }

        mean_naq = float(np.mean(naq_values))
        mean_kurt = float(np.mean(residual_kurtosis_list)) if residual_kurtosis_list else 3.0

        # ── Anomaly Assessment ──
        anomalies = []
        score_components = []

        # Check A: NAQ Biomechanical Deviation (Normal human range: 0.06 - 0.28)
        if mean_naq < 0.055 or mean_naq > 0.35:
            naq_score = 0.50
            score_components.append(naq_score)
            anomalies.append({
                "type": "GLOTTAL_BIOMECHANICAL_DEVIATION",
                "severity": "HIGH",
                "metric_name": "Glottal Normalized Amplitude Quotient (NAQ)",
                "value": round(mean_naq, 4),
                "threshold": "Biological human range: 0.060 - 0.280",
                "description": "Inverse LPC filtering reveals non-physical glottal flow velocity slope. Excitation pulse violates human laryngeal aerodynamic boundaries.",
            })
        else:
            score_components.append(0.0)

        # Check B: Unnatural Excitation Residual Kurtosis (Neural models have overly Gaussian residuals)
        if mean_kurt < 1.2:
            kurt_score = min((1.2 - mean_kurt) / 1.0, 1.0) * 0.40
            score_components.append(kurt_score)
            anomalies.append({
                "type": "DIFFUSE_GLOTTAL_EXCITATION",
                "severity": "MEDIUM",
                "metric_name": "Glottal Pulse Peakiness (Kurtosis)",
                "value": round(mean_kurt, 2),
                "threshold": "< 1.20 (Natural human glottal closure: > 2.50)",
                "description": "Glottal source pulse lacks the sharp impulsive closing event characteristic of true vocal fold contact.",
            })
        else:
            score_components.append(0.0)

        anomaly_score = float(np.clip(np.sum(score_components), 0.0, 1.0))
        confidence = 0.80 if len(naq_values) >= 10 else 0.50

        return {
            "anomaly_score": round(anomaly_score, 3),
            "confidence": round(confidence, 2),
            "metrics": {
                "naq_mean": round(mean_naq, 4),
                "lpc_residual_kurtosis": round(mean_kurt, 2),
                "frames_analyzed": len(naq_values),
            },
            "anomalies_detected": anomalies,
        }

    def _estimate_lpc(self, x: np.ndarray, order: int) -> np.ndarray:
        """Autocorrelation method for LPC coefficient estimation."""
        if len(x) < order + 1:
            return None
        r = signal.correlate(x, x, mode="full")[len(x) - 1 : len(x) + order]
        if r[0] <= 1e-12:
            return None
        try:
            a = linalg.solve_toeplitz((r[:-1], r[:-1]), r[1:])
            return np.concatenate(([1.0], -a))
        except Exception:
            return None
