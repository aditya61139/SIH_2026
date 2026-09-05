"""Higher-Order Bispectral Statistics and Quadratic Phase Coupling (QPC) Detector."""
import numpy as np
from scipy import signal
from typing import Dict, Any, List
from app.detectors.base import BaseDetector
from app.audio.preprocessor import AudioPreprocessor


class BispectrumPhaseDetector(BaseDetector):
    """
    Higher-Order Spectral (HOS) Forensic Analyzer.
    Computes the 2D Bispectrum B(f1, f2) and normalized Bicoherence b^2(f1, f2).
    Quantifies Non-linear Quadratic Phase Coupling (QPC) between harmonics.
    Natural human vocal tract aerodynamics generate non-linear phase interactions across harmonics.
    Neural speech synthesizers lack physical aerodynamic phase coupling, yielding near-zero bicoherence.
    """

    def __init__(self, n_fft: int = 128):
        self.n_fft = n_fft

    @property
    def name(self) -> str:
        return "bispectrum"

    def analyze(self, audio: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
        if len(audio) < sample_rate * 0.3 or AudioPreprocessor.is_silent(audio):
            return {
                "anomaly_score": 0.0,
                "confidence": 0.0,
                "metrics": {
                    "mean_bicoherence": 0.0,
                    "peak_qpc_score": 0.0,
                    "phase_coupling_ratio": 0.0,
                },
                "anomalies_detected": [],
            }

        # 1. Segment into overlapping frames
        nperseg = self.n_fft
        noverlap = nperseg // 2
        
        f, t, zxx = signal.stft(audio, fs=sample_rate, nperseg=nperseg, noverlap=noverlap)
        num_freqs, num_frames = zxx.shape
        if num_frames < 8:
            return {
                "anomaly_score": 0.0,
                "confidence": 0.0,
                "metrics": {},
                "anomalies_detected": [],
            }

        # 2. Compute Bispectrum over non-redundant principal domain
        # f1 + f2 <= fs/2
        max_k = num_freqs // 2
        bispec_sum = np.zeros((max_k, max_k), dtype=np.complex128)
        norm_sum = np.zeros((max_k, max_k), dtype=np.float64)

        for frame_idx in range(num_frames):
            x = zxx[:, frame_idx]
            for k1 in range(1, max_k):
                for k2 in range(1, max_k - k1):
                    k3 = k1 + k2
                    product = x[k1] * x[k2] * np.conj(x[k3])
                    bispec_sum[k1, k2] += product
                    norm_sum[k1, k2] += (np.abs(x[k1] * x[k2]) ** 2) * (np.abs(x[k3]) ** 2)

        bispec_avg = bispec_sum / num_frames
        norm_avg = np.sqrt(norm_sum / num_frames + 1e-12)

        # 3. Normalized Bicoherence Matrix: b^2(k1, k2) in [0, 1]
        bicoherence = np.abs(bispec_avg) / (norm_avg + 1e-12)
        bicoherence = np.clip(bicoherence, 0.0, 1.0)

        # Harmonic interaction zone (first 1.5 kHz = bins 1 to 12 at 16kHz with 128 FFT)
        active_zone = bicoherence[1:12, 1:12]
        mean_bic = float(np.mean(active_zone))
        peak_bic = float(np.max(active_zone)) if active_zone.size > 0 else 0.0

        # ── Anomaly Assessment ──
        anomalies = []
        score_components = []

        # Check A: Low Non-linear Phase Coupling (Characteristic of linear additive neural vocoders)
        if mean_bic < 0.045:
            bic_score = min((0.045 - mean_bic) / 0.040, 1.0) * 0.50
            score_components.append(bic_score)
            anomalies.append({
                "type": "ABSENT_QUADRATIC_PHASE_COUPLING",
                "severity": "HIGH",
                "metric_name": "Higher-Order Bicoherence (QPC)",
                "value": round(mean_bic, 4),
                "threshold": "< 0.045 (Natural human vocal tract: 0.075 - 0.350)",
                "description": "Bispectral analysis shows absence of non-linear aerodynamic quadratic phase coupling between vocal harmonics.",
            })
        else:
            score_components.append(0.0)

        anomaly_score = float(np.clip(np.sum(score_components), 0.0, 1.0))
        confidence = 0.80 if num_frames >= 20 else 0.50

        return {
            "anomaly_score": round(anomaly_score, 3),
            "confidence": round(confidence, 2),
            "metrics": {
                "mean_bicoherence": round(mean_bic, 4),
                "peak_qpc_score": round(peak_bic, 4),
                "frames_evaluated": num_frames,
            },
            "anomalies_detected": anomalies,
        }
