"""Spectral & Acoustic Anomaly Detector (Domain 6 & Domain 4).
Based on: Chhatriwala et al. (ITEGAM-JETIA 2026), Equations 6, 7, 8.
"""
import numpy as np
from scipy import signal
from typing import Dict, Any, List
from app.detectors.base import BaseDetector
from app.audio.preprocessor import AudioPreprocessor


class SpectralDetector(BaseDetector):
    """
    Analyzes frequency domain characteristics:
    1. Spectral Flatness Ratio (Wiener entropy)
    2. Spectral Entropy (Hs, Equation 6)
    3. Harmonic-to-Noise Ratio (HNR)
    4. STFT Phase Coherence Discontinuity (GAN/Vocoder artifacts)
    """

    @property
    def name(self) -> str:
        return "spectral"

    def analyze(self, audio: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
        if len(audio) < sample_rate * 0.1 or AudioPreprocessor.is_silent(audio):
            return {
                "anomaly_score": 0.0,
                "confidence": 0.0,
                "metrics": {
                    "spectral_flatness": 0.0,
                    "spectral_entropy": 0.0,
                    "hnr_db": 0.0,
                    "phase_coherence": 1.0,
                    "hf_energy_ratio": 0.0,
                },
                "anomalies_detected": [],
            }

        # 1. Compute Power Spectral Density via Welch
        freqs, psd = signal.welch(audio, fs=sample_rate, nperseg=min(len(audio), 1024))
        psd = np.maximum(psd, 1e-12)

        # 2. Spectral Flatness (Equation 8: geom_mean / arith_mean)
        log_psd = np.log(psd)
        geom_mean = np.exp(np.mean(log_psd))
        arith_mean = np.mean(psd)
        spectral_flatness = float(geom_mean / (arith_mean + 1e-12))

        # 3. Spectral Entropy (Equations 6 & 7): Hs = -sum p(f) * log(p(f))
        p_dist = psd / np.sum(psd)
        p_dist = np.maximum(p_dist, 1e-12)
        spectral_entropy = float(-np.sum(p_dist * np.log2(p_dist)))

        # 4. Harmonic-to-Noise Ratio (HNR) via Autocorrelation
        autocorr = signal.correlate(audio, audio, mode="full")
        autocorr = autocorr[len(autocorr) // 2 :]
        if autocorr[0] > 1e-12:
            autocorr_norm = autocorr / autocorr[0]
            min_lag = int(sample_rate / 450)
            max_lag = int(sample_rate / 70)
            if len(autocorr_norm) > max_lag:
                peak_val = np.max(autocorr_norm[min_lag:max_lag])
                peak_val = np.clip(peak_val, 1e-6, 0.99999)
                hnr_db = float(10 * np.log10(peak_val / (1.0 - peak_val)))
            else:
                hnr_db = 15.0
        else:
            hnr_db = 0.0

        # 5. Phase Coherence Analysis via STFT with Phase Unwrapping
        f_stft, t_stft, zxx = signal.stft(audio, fs=sample_rate, nperseg=512, noverlap=256)
        phases = np.angle(zxx)
        unwrapped_phases = np.unwrap(phases, axis=1)
        phase_diff2 = np.diff(unwrapped_phases, n=2, axis=1)
        phase_variance = float(np.mean(np.var(phase_diff2, axis=1)))
        phase_coherence = float(np.clip(1.0 / (1.0 + phase_variance * 0.1), 0.0, 1.0))

        # 6. High-Frequency Energy Ratio (4kHz - 8kHz vs Total)
        hf_mask = (freqs >= 4000) & (freqs <= 8000)
        hf_energy = np.sum(psd[hf_mask])
        total_energy = np.sum(psd)
        hf_energy_ratio = float(hf_energy / (total_energy + 1e-12))

        # ── Anomaly Scoring Logic ──
        anomalies = []
        score_components = []

        # Check A: Unnatural Spectral Flatness (Vocoder flat spectrum)
        if spectral_flatness > 0.65:
            flatness_score = min((spectral_flatness - 0.65) / 0.25, 1.0)
            score_components.append(flatness_score * 0.40)
            anomalies.append({
                "type": "SPECTRAL_SMOOTHNESS",
                "severity": "HIGH" if spectral_flatness > 0.78 else "MEDIUM",
                "metric_name": "Spectral Flatness (SF)",
                "value": round(spectral_flatness, 3),
                "threshold": "> 0.65 (Human speech: 0.05 - 0.45)",
                "description": "Voice spectrum exhibits unnatural flatness characteristic of neural vocoder synthesis.",
            })
        else:
            score_components.append(0.0)

        # Check B: High Spectral Entropy (Uniform energy spread)
        if spectral_entropy > 7.4:
            ent_score = min((spectral_entropy - 7.4) / 1.6, 1.0)
            score_components.append(ent_score * 0.30)
            anomalies.append({
                "type": "HIGH_SPECTRAL_ENTROPY",
                "severity": "MEDIUM",
                "metric_name": "Spectral Entropy (Hs)",
                "value": round(spectral_entropy, 2),
                "threshold": "> 7.4 (Human normal: 4.5 - 6.8)",
                "description": "Energy distribution across frequency bands is unnaturally uniform.",
            })
        else:
            score_components.append(0.0)

        # Check C: Severe Phase Incoherence / Discontinuities
        if phase_coherence < 0.20:
            phase_score = min((0.20 - phase_coherence) / 0.15, 1.0)
            score_components.append(phase_score * 0.30)
            anomalies.append({
                "type": "PHASE_DISCONTINUITY",
                "severity": "HIGH" if phase_coherence < 0.12 else "MEDIUM",
                "metric_name": "Phase Coherence",
                "value": round(phase_coherence, 3),
                "threshold": "< 0.20 (Natural human range: 0.40 - 0.95)",
                "description": "Phase spectrum exhibits severe discontinuities characteristic of neural vocoder STFT inversion.",
            })
        else:
            score_components.append(0.0)

        raw_anomaly_score = float(np.sum(score_components))
        anomaly_score = float(np.clip(raw_anomaly_score, 0.0, 1.0))
        confidence = 0.85 if len(audio) >= sample_rate * 1.5 else 0.60

        return {
            "anomaly_score": round(anomaly_score, 3),
            "confidence": round(confidence, 2),
            "metrics": {
                "spectral_flatness": round(spectral_flatness, 4),
                "spectral_entropy": round(spectral_entropy, 3),
                "hnr_db": round(hnr_db, 2),
                "phase_coherence": round(phase_coherence, 3),
                "hf_energy_ratio": round(hf_energy_ratio, 4),
            },
            "anomalies_detected": anomalies,
        }
