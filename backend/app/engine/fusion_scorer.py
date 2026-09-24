"""Multi-Layer Fusion Scorer and Real-Time Detection Engine (10-Vector Forensic Suite)."""
import numpy as np
import os
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.detectors.spectral_detector import SpectralDetector
from app.detectors.prosody_detector import ProsodyDetector
from app.detectors.breathing_detector import BreathingDetector
from app.detectors.acoustic_artifacts import AcousticArtifactDetector
from app.detectors.lfcc_detector import LFCCDetector
from app.detectors.glottal_detector import GlottalFlowDetector
from app.detectors.perturbation_detector import LaryngealPerturbationDetector
from app.detectors.bispectrum_detector import BispectrumPhaseDetector
from app.detectors.neural_lcnn_detector import NeuralLCNNDetector
from app.detectors.replay_detector import ReplayDetector
from app.detectors.multilingual_profiler import MultilingualProfiler
from app.audio.speaker_separator import SpeakerSeparator
from app.engine.diagnostic_generator import DiagnosticGenerator


class DetectionEngine:
    """
    Orchestrates the 10-vector forensic detector ensemble:
    1. Spectral & Phase Discontinuity
    2. Prosodic F0 Pitch Variance & Micro-Tremors
    3. Respiration & Inhalation Cadence
    4. Neural Vocoder Filter Cutoffs
    5. Linear Frequency Cepstral Coefficients (LFCC Delta/Delta-Delta)
    6. Biomechanical Glottal Flow LPC Inverse Filtering (NAQ)
    7. Laryngeal Micro-Perturbation (Jitter & Shimmer)
    8. Higher-Order Bispectral Phase Coupling (QPC)
    9. Deep Neural LCNN-BiLSTM-Attention Model
    10. Physical Loudspeaker Replay Attack Detection
    + Multilingual Regional Indian Acoustic Profiling & Codec Normalization
    """

    def __init__(self, weights_path: str = None):
        self.spectral_detector = SpectralDetector()
        self.prosody_detector = ProsodyDetector()
        self.breathing_detector = BreathingDetector()
        self.acoustic_detector = AcousticArtifactDetector()
        self.lfcc_detector = LFCCDetector()
        self.glottal_detector = GlottalFlowDetector()
        self.perturbation_detector = LaryngealPerturbationDetector()
        self.bispectrum_detector = BispectrumPhaseDetector()
        self.neural_detector = NeuralLCNNDetector(weights_path=weights_path)
        self.replay_detector = ReplayDetector()
        self.multilingual_profiler = MultilingualProfiler()
        self.speaker_separator = SpeakerSeparator()

        self.history_scores: List[float] = []
        self.current_ema_score: float = 0.0
        self.total_windows_processed: int = 0

    def _detect_and_compensate_codec(self, audio: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """
        Detects cellular (AMR-NB / GSM) or narrow-band VoIP codecs (G.711) characterized by
        steep brickwall cutoffs at 3.4 kHz, and calculates compensation factors to prevent false alarms.
        """
        if not getattr(settings, "ENABLE_CODEC_COMPENSATION", True) or len(audio) < sample_rate * 0.2:
            return {"codec": "wideband_uncompressed", "compensation_factor": 1.0, "hf_ratio": 1.0}

        fft_mags = np.abs(np.fft.rfft(audio))
        freqs = np.fft.rfftfreq(len(audio), 1.0 / sample_rate)

        hf_mask = freqs >= settings.CELLULAR_BANDWIDTH_CUTOFF_HZ
        lf_mask = (freqs >= 300) & (freqs < settings.CELLULAR_BANDWIDTH_CUTOFF_HZ)

        hf_energy = float(np.sum(fft_mags[hf_mask] ** 2) + 1e-10)
        lf_energy = float(np.sum(fft_mags[lf_mask] ** 2) + 1e-10)
        hf_ratio = hf_energy / lf_energy

        # AMR-NB and G.711 have virtually zero energy above 3.4 kHz (ratio < 0.006)
        if hf_ratio < 0.006:
            return {
                "codec": "cellular_amr_nb",
                "hf_ratio": round(hf_ratio, 5),
                "compensation_factor": 0.72,  # Attenuates codec brickwall false alarms
            }
        elif hf_ratio < 0.035:
            return {
                "codec": "voip_opus_narrowband",
                "hf_ratio": round(hf_ratio, 5),
                "compensation_factor": 0.85,
            }
        return {"codec": "wideband_hd", "hf_ratio": round(hf_ratio, 4), "compensation_factor": 1.0}

    def analyze_window(
        self,
        audio_window: np.ndarray,
        sample_rate: int = settings.SAMPLE_RATE,
        window_index: int = 0,
        timestamp_sec: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Executes 10-vector forensic analysis on a 2.0-second audio window.
        """
        self.total_windows_processed += 1

        # 1. Separate Caller Audio from User Audio (Speakerphone mode)
        caller_audio, separation_info = self.speaker_separator.isolate_caller_audio(
            audio_window, sample_rate=sample_rate
        )

        # 2. Cellular / VoIP Codec Normalization Analysis
        codec_info = self._detect_and_compensate_codec(caller_audio, sample_rate)

        # 3. Multilingual & Regional Indian Forensic Profiling
        multilingual_res = self.multilingual_profiler.analyze(caller_audio, sample_rate)
        adaptive_offsets = multilingual_res.get("adaptive_offsets", {})

        # 4. Physical Replay Attack Detection
        replay_res = self.replay_detector.analyze(caller_audio, sample_rate)

        # 5. Core 8 Forensic Detectors
        spectral_res = self.spectral_detector.analyze(caller_audio, sample_rate)
        prosody_res = self.prosody_detector.analyze(caller_audio, sample_rate)
        breathing_res = self.breathing_detector.analyze(
            caller_audio, sample_rate, hop_duration_sec=settings.HOP_DURATION_SEC
        )
        acoustic_res = self.acoustic_detector.analyze(caller_audio, sample_rate)
        lfcc_res = self.lfcc_detector.analyze(caller_audio, sample_rate)
        glottal_res = self.glottal_detector.analyze(caller_audio, sample_rate)
        perturb_res = self.perturbation_detector.analyze(caller_audio, sample_rate)
        bispec_res = self.bispectrum_detector.analyze(caller_audio, sample_rate)
        neural_res = self.neural_detector.analyze(caller_audio, sample_rate)

        # Apply Codec Normalization: soften false alarms from low-pass telephone filters
        if codec_info["compensation_factor"] < 1.0:
            acoustic_res["anomaly_score"] *= codec_info["compensation_factor"]
            spectral_res["anomaly_score"] *= codec_info["compensation_factor"]

        # Apply Multilingual Calibration: adapt pitch/jitter tolerance for expressive Indian regional speech
        if adaptive_offsets.get("pitch_variance_tolerance", 1.0) > 1.0:
            prosody_res["anomaly_score"] = float(np.clip(
                prosody_res["anomaly_score"] / adaptive_offsets["pitch_variance_tolerance"], 0.0, 1.0
            ))
            perturb_res["anomaly_score"] = float(np.clip(
                perturb_res["anomaly_score"] / adaptive_offsets.get("jitter_tolerance", 1.0), 0.0, 1.0
            ))

        # Near-field vocal clarity safeguard:
        # If speech has high Harmonics-to-Noise Ratio (>= 15 dB) and authentic single-room decay,
        # it is physically authentic near-field human speech, even when spoken loudly.
        if replay_res["metrics"].get("hnr_db", 0.0) >= 15.0 and replay_res["metrics"].get("rt60_ratio", 1.0) < 1.45:
            replay_res["anomaly_score"] = min(replay_res["anomaly_score"], 0.15)
            replay_res["metrics"]["replay_probability"] = min(replay_res["metrics"]["replay_probability"], 0.15)
            replay_res["anomalies_detected"] = []

        detector_results = {
            "spectral": spectral_res,
            "prosody": prosody_res,
            "breathing": breathing_res,
            "acoustic_artifacts": acoustic_res,
            "lfcc": lfcc_res,
            "glottal": glottal_res,
            "perturbation": perturb_res,
            "bispectrum": bispec_res,
            "neural_lcnn": neural_res,
            "replay_attack": replay_res,
        }

        # 6. Weighted 10-Layer Fusion Score Calculation
        weights = settings.DETECTOR_WEIGHTS
        total_weight = sum(weights.values())
        raw_score = sum(
            (weights.get(name, 0.1) / total_weight) * res["anomaly_score"]
            for name, res in detector_results.items()
        )
        raw_score = float(np.clip(raw_score, 0.0, 1.0))

        # 7. Temporal Smoothing (Exponential Moving Average)
        alpha = settings.EMA_ALPHA
        if len(self.history_scores) == 0:
            smoothed_score = raw_score
        else:
            smoothed_score = alpha * raw_score + (1.0 - alpha) * self.current_ema_score

        # Check for sudden risk velocity spike (Voice Swap / Takeover Detection)
        prev_score = self.current_ema_score if len(self.history_scores) > 0 else 0.0
        is_spike = (raw_score - prev_score) >= settings.SPIKE_DELTA_THRESHOLD

        self.current_ema_score = smoothed_score
        self.history_scores.append(smoothed_score)

        # 8. Generate Rich Diagnostic Report & Actionable Countermeasures
        diagnostic_report = DiagnosticGenerator.generate_report(
            risk_score=smoothed_score,
            detector_results=detector_results,
            is_spike=is_spike,
        )

        # 9. Format Return Payload
        formatted_time = f"{int(timestamp_sec // 60):02d}:{int(timestamp_sec % 60):02d}"

        return {
            "window_index": window_index,
            "timestamp": formatted_time,
            "timestamp_sec": round(timestamp_sec, 2),
            "risk_score": round(smoothed_score, 3),
            "raw_risk_score": round(raw_score, 3),
            "is_spike": is_spike,
            "risk_level": diagnostic_report["risk_level"],
            "alert_type": diagnostic_report["alert_type"],
            "status_text": diagnostic_report["status_text"],
            "user_message": diagnostic_report["user_message"],
            "recommendation": diagnostic_report["recommendation"],
            "suggested_actions": diagnostic_report["suggested_actions"],
            "diagnostics": diagnostic_report["anomalies"],
            "layer_scores": {
                "spectral": spectral_res["anomaly_score"],
                "prosody": prosody_res["anomaly_score"],
                "breathing": breathing_res["anomaly_score"],
                "acoustic_artifacts": acoustic_res["anomaly_score"],
                "lfcc": lfcc_res["anomaly_score"],
                "glottal": glottal_res["anomaly_score"],
                "perturbation": perturb_res["anomaly_score"],
                "bispectrum": bispec_res["anomaly_score"],
                "neural_lcnn": neural_res["anomaly_score"],
                "replay_attack": replay_res["anomaly_score"],
            },
            "layer_metrics": {
                "spectral": spectral_res["metrics"],
                "prosody": prosody_res["metrics"],
                "breathing": breathing_res["metrics"],
                "acoustic_artifacts": acoustic_res["metrics"],
                "lfcc": lfcc_res["metrics"],
                "glottal": glottal_res["metrics"],
                "perturbation": perturb_res["metrics"],
                "bispectrum": bispec_res["metrics"],
                "neural_lcnn": neural_res["metrics"],
                "replay_attack": replay_res["metrics"],
            },
            "language_profile": multilingual_res["metrics"],
            "replay_profile": replay_res["metrics"],
            "codec_normalization": codec_info,
            "speaker_separation": separation_info,
        }

    def reset(self) -> None:
        """Resets engine history and detector states for a new call."""
        self.history_scores.clear()
        self.current_ema_score = 0.0
        self.total_windows_processed = 0
        self.breathing_detector.reset()
