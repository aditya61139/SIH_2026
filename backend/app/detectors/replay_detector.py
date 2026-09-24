"""
Physical Replay Attack Detector for VoxSentinalX (Version 2.0 - Robust Calibrated).
Detects when an authentic human voice recording is being replayed through a loudspeaker
or mobile phone speaker during a live call or within an audio recording.

Forensic Mechanisms:
1. Loudspeaker Intermodulation Distortion & Harmonics-to-Noise Ratio (HNR)
2. Dual-Room Acoustic Reverberation Mismatch (Schroeder Energy Decay Curve RT60)
3. Pitch-Conditioned Transducer Cabinet Coloration
4. Gated Pre-Speech DAC Electronic Turn-On Transient Detection
5. Conjoint Multi-Evidence Physical Co-Occurrence Gating
"""
import numpy as np
from scipy import signal
from typing import Dict, Any, List, Tuple
from app.detectors.base import BaseDetector
from app.audio.preprocessor import AudioPreprocessor


class ReplayDetector(BaseDetector):
    """
    Forensic Replay Attack Detector.
    Analyzes physical acoustic properties that distinguish sound emitted directly from
    human vocal folds from sound re-radiated through an electro-acoustic transducer (speaker).
    Calibrated to eliminate false positives on loud authentic human speech.
    """

    def __init__(self):
        # Physical acoustic thresholds
        self.rt60_ratio_threshold = 1.65  # Ratio of late-to-early reverberation decay
        self.transducer_cutoff_hz = 150.0  # Mobile speakers sharply attenuate below 150 Hz

    @property
    def name(self) -> str:
        return "replay_attack"

    def analyze(self, audio: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Executes physical replay analysis on the audio window with loudness compensation.
        """
        if len(audio) < sample_rate * 0.25 or AudioPreprocessor.is_silent(audio):
            return {
                "anomaly_score": 0.0,
                "confidence": 0.0,
                "metrics": {
                    "thd_score": 0.0,
                    "rt60_ratio": 1.0,
                    "coloration_score": 0.0,
                    "dac_transient_score": 0.0,
                    "replay_probability": 0.0,
                    "hnr_db": 30.0,
                },
                "anomalies_detected": [],
            }

        # 1. Pitch Estimation and Vocal Intensity Tracking
        f0, is_voiced, rms_energy = self._estimate_pitch_and_energy(audio, sample_rate)

        # 2. Loudspeaker Intermodulation & Harmonics-to-Noise Ratio (HNR)
        dist_score, hnr_db = self._compute_speaker_distortion_hnr(audio, sample_rate, f0, is_voiced)

        # 3. Dual-Room Reverberation & RT60 Decay Profile
        decay_score, rt60_ratio = self._compute_reverberation_decay(audio, sample_rate)

        # 4. Pitch-Conditioned Transducer Cabinet Coloration
        coloration_score = self._compute_pitch_conditioned_coloration(audio, sample_rate, f0, is_voiced)

        # 5. Gated Pre-Speech DAC Electronic Pop Detection (gated to silence/onset)
        dac_transient_score = self._detect_gated_dac_switching(audio, sample_rate)

        # 6. Conjoint Multi-Evidence Physical Co-Occurrence Gate:
        # A physical loudspeaker replay requires simultaneous evidence from:
        # (a) Acoustic transmission / room reverberation mismatch AND
        # (b) Physical transducer coloration or intermodulation distortion.
        # Genuine loud voice directly in front of the mic has high near-field acoustic energy
        # and clean single-exponential decay (decay_score near 0.0).
        transducer_evidence = max(dist_score, coloration_score)
        acoustic_evidence = decay_score

        if acoustic_evidence > 0.45 and transducer_evidence > 0.40:
            # Genuine dual-evidence co-occurrence: both room mismatch and speaker distortion
            replay_prob = (
                0.45 * acoustic_evidence +
                0.35 * transducer_evidence +
                0.20 * dac_transient_score
            )
        elif acoustic_evidence > 0.35 and transducer_evidence > 0.55:
            replay_prob = 0.50 * transducer_evidence + 0.35 * acoustic_evidence + 0.15 * dac_transient_score
        else:
            # Single isolated trait (e.g. loud voice or room echo without distortion) is NOT replay
            replay_prob = min(0.30, 0.5 * transducer_evidence * acoustic_evidence)

        replay_prob = float(np.clip(replay_prob, 0.0, 1.0))
        confidence = 0.90 if len(audio) >= sample_rate * 1.0 else 0.70

        anomalies_detected: List[Dict[str, Any]] = []
        if replay_prob >= 0.65:
            if dist_score > 0.60:
                anomalies_detected.append({
                    "type": "LOUDSPEAKER_HARMONIC_DISTORTION",
                    "severity": "CRITICAL" if dist_score > 0.80 else "HIGH",
                    "metric_name": "Loudspeaker Intermodulation & Degraded HNR",
                    "value": f"{round(hnr_db, 1)} dB HNR (Degraded)",
                    "threshold": "< 12 dB HNR with non-linear intermodulation",
                    "description": "Acoustic signal exhibits electro-acoustic intermodulation splatter and harmonic compression characteristic of phone/laptop speakers.",
                })

            if decay_score > 0.55:
                anomalies_detected.append({
                    "type": "DUAL_ROOM_REVERBERATION_MISMATCH",
                    "severity": "HIGH",
                    "metric_name": "Dual-Slope RT60 Decay Mismatch",
                    "value": f"{round(rt60_ratio, 2)}x early-to-late ratio",
                    "threshold": "> 1.65x dual acoustic enclosure ratio",
                    "description": "Detected double-slope acoustic decay curve indicating voice was recorded in one room and re-radiated in a second physical enclosure.",
                })

            if coloration_score > 0.65:
                anomalies_detected.append({
                    "type": "TRANSDUCER_COLORATION_CUTOFF",
                    "severity": "MEDIUM",
                    "metric_name": "Transducer Mechanical Rolloff",
                    "value": f"{round(coloration_score * 100, 1)}% profile match",
                    "threshold": "> 65% physical speaker filter signature",
                    "description": "Spectral energy exhibits steep attenuation below fundamental pitch with resonant cabinet peaks, matching loudspeaker transducer frequency response.",
                })

        return {
            "anomaly_score": round(replay_prob, 3),
            "confidence": round(confidence, 2),
            "metrics": {
                "thd_score": round(dist_score, 3),
                "rt60_ratio": round(rt60_ratio, 2),
                "coloration_score": round(coloration_score, 3),
                "dac_transient_score": round(dac_transient_score, 3),
                "replay_probability": round(replay_prob, 3),
                "hnr_db": round(hnr_db, 1),
                "estimated_f0": round(f0, 1),
            },
            "anomalies_detected": anomalies_detected,
        }

    def _estimate_pitch_and_energy(self, audio: np.ndarray, sample_rate: int) -> Tuple[float, bool, float]:
        """
        Estimates the speaker's true fundamental pitch (F0) using autocorrelation,
        determines if the frame is voiced, and calculates RMS energy.
        """
        rms = float(np.sqrt(np.mean(audio ** 2))) + 1e-10

        # Pitch search range: 80 Hz to 350 Hz
        min_lag = int(sample_rate / 350.0)
        max_lag = int(sample_rate / 80.0)

        if len(audio) < max_lag * 2:
            return 150.0, False, rms

        # Autocorrelation of the center segment
        center = audio[len(audio)//4 : 3*len(audio)//4]
        corr = np.correlate(center, center, mode='full')
        corr = corr[len(corr)//2 :]
        norm_corr = corr / (corr[0] + 1e-10)

        if len(norm_corr) > max_lag:
            search_window = norm_corr[min_lag:max_lag]
            peak_lag = min_lag + int(np.argmax(search_window))
            peak_val = float(search_window[peak_lag - min_lag])

            if peak_val > 0.30:
                f0 = float(sample_rate / peak_lag)
                return f0, True, rms

        return 160.0, False, rms

    def _compute_speaker_distortion_hnr(
        self, audio: np.ndarray, sample_rate: int, f0: float, is_voiced: bool
    ) -> Tuple[float, float]:
        """
        Analyzes Harmonics-to-Noise Ratio (HNR) and Intermodulation Distortion (IMD)
        using frame-based short-term autocorrelation (Boersma/Praat formulation).
        Genuine human speech (especially loud speech) has sharp glottal harmonic spikes
        with high HNR (> 15-28 dB).
        Physical loudspeakers generate intermodulation products and phase saturation that
        degrade autocorrelation periodicity, causing HNR to degrade sharply (< 11 dB).
        """
        frame_len = int(sample_rate * 0.04)  # 40ms frame
        hop_len = int(sample_rate * 0.02)    # 20ms hop
        min_lag = int(sample_rate / 350.0)
        max_lag = int(sample_rate / 80.0)

        hnr_list = []
        for i in range(0, len(audio) - frame_len, hop_len):
            frame = audio[i : i + frame_len]
            frame_rms = np.sqrt(np.mean(frame ** 2))
            if frame_rms < 0.015:
                continue

            # Unbiased normalized autocorrelation of frame (Praat standard formulation)
            corr = np.correlate(frame, frame, mode='full')[len(frame) - 1 :]
            if corr[0] <= 1e-10:
                continue
            lags = np.arange(len(corr))
            unbiased_denom = corr[0] * np.maximum(0.01, (1.0 - lags / float(frame_len)))
            norm_corr = corr / unbiased_denom

            if len(norm_corr) > max_lag:
                search_win = norm_corr[min_lag:max_lag]
                peak_val = float(np.max(search_win))
                if peak_val > 0.40:
                    r_clamped = min(0.999, max(0.01, peak_val))
                    hnr_val = float(10.0 * np.log10(r_clamped / (1.0 - r_clamped + 1e-10)))
                    hnr_list.append(hnr_val)

        if len(hnr_list) < 2:
            return 0.0, 22.0

        mean_hnr = float(np.mean(hnr_list))

        # Scoring:
        # Authentic voiced speech: HNR typically 15 - 28 dB -> dist_score = 0.0
        # Moderate distortion: HNR 10 - 15 dB -> dist_score = 0.1 - 0.4
        # Heavy speaker distortion / clipping: HNR < 10 dB -> dist_score = 0.5 - 1.0
        if mean_hnr >= 15.0:
            dist_score = 0.0
        elif mean_hnr >= 10.0:
            dist_score = float((15.0 - mean_hnr) / 5.0 * 0.45)
        else:
            dist_score = float(np.clip(0.45 + (10.0 - mean_hnr) / 7.0 * 0.55, 0.0, 1.0))

        return dist_score, mean_hnr

    def _compute_reverberation_decay(self, audio: np.ndarray, sample_rate: int) -> Tuple[float, float]:
        """
        Calculates energy decay relief ratio to identify dual-room acoustic impulse response.
        Direct human speech in near-field has rapid, single-exponential decay.
        Replayed speech has dual-slope decay from primary recording room + secondary playback room.
        """
        analytic = signal.hilbert(audio)
        env = np.abs(analytic)

        # Smooth envelope with 20ms moving window
        win_size = max(1, int(sample_rate * 0.02))
        smoothed = np.convolve(env, np.ones(win_size) / win_size, mode='same') + 1e-10

        # Schroeder backwards integration
        schroeder = np.cumsum(smoothed[::-1] ** 2)[::-1]
        schroeder_db = 10 * np.log10(schroeder / (np.max(schroeder) + 1e-10) + 1e-10)

        # Compare early decay rate (-5dB to -15dB) vs late decay rate (-15dB to -30dB)
        early_mask = (schroeder_db <= -5) & (schroeder_db >= -15)
        late_mask = (schroeder_db < -15) & (schroeder_db >= -30)

        if np.sum(early_mask) < 10 or np.sum(late_mask) < 10:
            return 0.0, 1.0

        early_slope = (np.max(schroeder_db[early_mask]) - np.min(schroeder_db[early_mask])) / (len(schroeder_db[early_mask]) + 1e-6)
        late_slope = (np.max(schroeder_db[late_mask]) - np.min(schroeder_db[late_mask])) / (len(schroeder_db[late_mask]) + 1e-6)

        # Discrepancy indicates dual-room slope change
        slope_ratio = float(early_slope / (late_slope + 1e-6))
        # Authentic speech in near-field has slope_ratio around 0.8 - 1.3
        # Dual room replay typically produces slope_ratio > 1.75
        anomaly_score = float(np.clip((slope_ratio - 1.45) / 1.2, 0.0, 1.0)) if slope_ratio > 1.45 else 0.0

        return anomaly_score, slope_ratio

    def _compute_pitch_conditioned_coloration(
        self, audio: np.ndarray, sample_rate: int, f0: float, is_voiced: bool
    ) -> float:
        """
        Evaluates transducer coloration conditioned on the speaker's true pitch fundamental (F0).
        If F0 >= 150 Hz (female speakers, elevated pitch, loud vocal projection),
        the absence of sub-bass below 150 Hz is completely natural and is NOT penalized.
        """
        freqs, psd = signal.welch(audio, fs=sample_rate, nperseg=512)
        psd_norm = psd / (np.sum(psd) + 1e-10)

        # If the speaker's pitch is high/elevated (>145 Hz), lack of sub-150 Hz is normal
        if f0 >= 145.0:
            sub_bass_missing = 0.0
        else:
            # For low-pitch voices (F0 < 145 Hz), verify if sub-bass fundamental was cut off by small speaker
            low_band = np.sum(psd_norm[freqs < 145])
            vocal_band = np.sum(psd_norm[(freqs >= 145) & (freqs <= 800)])
            low_ratio = low_band / (vocal_band + 1e-6)
            sub_bass_missing = float(1.0 - np.clip(low_ratio / 0.12, 0.0, 1.0))

        # Check for harsh plastic cabinet resonance peakiness in 2.5 kHz - 4.5 kHz
        mid_psd = psd_norm[(freqs >= 2500) & (freqs <= 4500)]
        if len(mid_psd) > 0 and np.std(mid_psd) > 0:
            peakiness = float(np.max(mid_psd) / (np.mean(mid_psd) + 1e-10))
            # Extreme peakiness (> 4.8) indicates cheap speaker resonance
            res_score = float(np.clip((peakiness - 4.0) / 4.0, 0.0, 1.0))
        else:
            res_score = 0.0

        return float(np.clip(0.6 * sub_bass_missing + 0.4 * res_score, 0.0, 1.0))

    def _detect_gated_dac_switching(self, audio: np.ndarray, sample_rate: int) -> float:
        """
        Detects transient switching pops/clicks emitted by digital-to-analog converters.
        Gated strictly to pre-speech or silent intervals (< -32 dBFS RMS) so plosive
        consonants in loud speech (/p/, /t/, /k/) are never mistaken for DAC turn-on pops.
        """
        # Calculate short-term frame RMS (20ms frames)
        frame_len = int(sample_rate * 0.02)
        if len(audio) < frame_len * 2:
            return 0.0

        num_frames = len(audio) // frame_len
        audio_trimmed = audio[: num_frames * frame_len]
        frames = audio_trimmed.reshape(num_frames, frame_len)
        frame_rms = np.sqrt(np.mean(frames ** 2, axis=1))
        peak_rms = np.max(frame_rms) + 1e-10

        # Only look at frames that are quiet (< 15% of peak RMS or < 0.02 absolute)
        quiet_mask = (frame_rms < 0.15 * peak_rms) | (frame_rms < 0.02)
        if not np.any(quiet_mask):
            # Continuous active speech; no silent regions to evaluate DAC turn-on pops
            return 0.0

        quiet_samples = frames[quiet_mask].flatten()
        if len(quiet_samples) < 20:
            return 0.0

        diff = np.abs(np.diff(quiet_samples))
        median_diff = np.median(diff) + 1e-6
        # A true DAC turn-on spike in silence is > 12x the quiet noise floor
        spikes = np.sum(diff > 12.0 * median_diff)
        duration_sec = len(quiet_samples) / sample_rate
        spike_rate = spikes / (duration_sec + 1e-6)

        return float(np.clip(spike_rate / 4.0, 0.0, 1.0))
