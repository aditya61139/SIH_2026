"""Spectral & Acoustic Anomaly Detector."""
import numpy as np
from scipy import signal
from typing import Dict, Any, List
from app.detectors.base import BaseDetector
from app.audio.preprocessor import AudioPreprocessor


class SpectralDetector(BaseDetector):
    """
    Analyzes frequency domain characteristics:
    1. Spectral Flatness Ratio (smoothness of neural vocoders)
    2. Harmonic-to-Noise Ratio (HNR)
    3. STFT Phase Coherence Discontinuity (GAN artifacts)
    4. High-Frequency Rolloff / Cutoff Analysis
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
                    "hnr_db": 0.0,
                    "phase_coherence": 1.0,
                    "hf_energy_ratio": 0.0,
                },
                "anomalies_detected": [],
            }

        # 1. Compute Power Spectral Density via Welch
        freqs, psd = signal.welch(audio, fs=sample_rate, nperseg=min(len(audio), 1024))
        psd = np.maximum(psd, 1e-12)

        # 2. Spectral Flatness (Wiener entropy: geom_mean / arith_mean)
        log_psd = np.log(psd)
        geom_mean = np.exp(np.mean(log_psd))
        arith_mean = np.mean(psd)
        spectral_flatness = float(geom_mean / (arith_mean + 1e-12))

        # 3. Harmonic-to-Noise Ratio (HNR) via Autocorrelation
        autocorr = signal.correlate(audio, audio, mode="full")
        autocorr = autocorr[len(autocorr) // 2 :]
        if autocorr[0] > 1e-12:
            autocorr_norm = autocorr / autocorr[0]
            min_lag = int(sample_rate / 400)
            max_lag = int(sample_rate / 70)
            if len(autocorr_norm) > max_lag:
                peak_val = np.max(autocorr_norm[min_lag:max_lag])
                peak_val = np.clip(peak_val, 1e-6, 0.99999)
                hnr_db = float(10 * np.log10(peak_val / (1.0 - peak_val)))
            else:
                hnr_db = 15.0
        else:
            hnr_db = 0.0

        # 4. Phase Coherence Analysis via STFT with Phase Unwrapping
        f_stft, t_stft, zxx = signal.stft(audio, fs=sample_rate, nperseg=512, noverlap=256)
        phases = np.angle(zxx)
        unwrapped_phases = np.unwrap(phases, axis=1)
        phase_diff2 = np.diff(unwrapped_phases, n=2, axis=1)
        phase_variance = float(np.mean(np.var(phase_diff2, axis=1)))
        # Normalize: Natural speech has coherent unwrapped phase trajectories
        phase_coherence = float(np.clip(1.0 / (1.0 + phase_variance * 0.1), 0.0, 1.0))

        # 5. High-Frequency Energy Ratio (4kHz - 8kHz vs Total)
        hf_mask = (freqs >= 4000) & (freqs <= 8000)
        hf_energy = np.sum(psd[hf_mask])
        total_energy = np.sum(psd)
        hf_energy_ratio = float(hf_energy / (total_energy + 1e-12))

        # ── Anomaly Scoring Logic ──
        anomalies = []
        score_components = []

        # Check A: Unnatural Spectral Flatness (Neural vocoders produce flat/uniform frequency distributions)
        if spectral_flatness > 0.60:
            flatness_score = min((spectral_flatness - 0.60) / 0.30, 1.0)
            score_components.append(flatness_score * 0.50)
            anomalies.append({
                "type": "SPECTRAL_SMOOTHNESS",
                "severity": "HIGH" if spectral_flatness > 0.75 else "MEDIUM",
                "metric_name": "Spectral Flatness",
                "value": round(spectral_flatness, 3),
                "threshold": "> 0.60 (Human speech: 0.05 - 0.45)",
                "description": "Voice spectrum exhibits unnatural flatness characteristic of neural vocoder synthesis.",
            })
        else:
            score_components.append(0.0)

        # Check B: Phase Incoherence / Discontinuities
        if phase_coherence < 0.40:
            phase_score = min((0.40 - phase_coherence) / 0.30, 1.0)
            score_components.append(phase_score * 0.35)
            anomalies.append({
                "type": "PHASE_DISCONTINUITY",
                "severity": "HIGH" if phase_coherence < 0.25 else "MEDIUM",
                "metric_name": "Phase Coherence",
                "value": round(phase_coherence, 3),
                "threshold": "< 0.40 (Natural human range: 0.55 - 0.95)",
                "description": "Phase spectrum exhibits discontinuities characteristic of neural vocoder STFT inversion.",
            })
        else:
            score_components.append(0.0)

        # Check C: Sterile HNR
        if hnr_db > 32.0:
            score_components.append(0.20)
            anomalies.append({
                "type": "ARTIFICIAL_CLARITY",
                "severity": "LOW",
                "metric_name": "Harmonic-to-Noise Ratio",
                "value": f"{round(hnr_db, 1)} dB",
                "threshold": "> 32.0 dB (Normal: 12 - 28 dB)",
                "description": "Harmonic signal is unnaturally sterile, lacking subtle breath noise.",
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
                "hnr_db": round(hnr_db, 2),
                "phase_coherence": round(phase_coherence, 3),
                "hf_energy_ratio": round(hf_energy_ratio, 4),
            },
            "anomalies_detected": anomalies,
        }
