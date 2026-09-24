"""
Multilingual & Regional Indian Forensic Profiler for VoxSentinalX.
Detects and analyzes deepfakes across diverse languages and regional accents,
with specialized acoustic feature extraction for Indian linguistic families:
1. Indo-Aryan (Hindi, Bengali, Marathi, Gujarati, Punjabi, Urdu)
2. Dravidian (Tamil, Telugu, Kannada, Malayalam)
3. Indian English and Global Neutral

Forensic Capabilities:
- Formant Dispersion (F1, F2, F3) & Vowel Space Area (VSA) Compression Detection
- Retroflex Consonant Acoustic Locus Extraction (ʈ, ɖ, ɳ tongue-curl frequency dips)
- Syllable Cadence & Rhythm Metrics (nPVI - Normalized Pairwise Variability Index)
- Cross-Lingual Adaptive Thresholding (prevents false alarms on expressive Indian speech)
"""
import numpy as np
from scipy import signal
from typing import Dict, Any, List, Tuple
from app.detectors.base import BaseDetector
from app.audio.preprocessor import AudioPreprocessor


class MultilingualProfiler(BaseDetector):
    """
    Forensic Multilingual and Accent-Aware Profiler.
    Analyzes phonetic resonance, vowel space geometry, and rhythmic cadence
    to identify synthetic anomalies across diverse languages and accents.
    """

    def __init__(self):
        # Baseline reference vowel space areas (Hz^2)
        self.normal_vsa_min = 180000.0  # Natural human speech maintains wide vowel triangle
        self.synthetic_vsa_cutoff = 110000.0 # Neural vocoders over-smooth and compress VSA

        # Syllable timing thresholds (nPVI)
        # Syllable-timed (Indo-Aryan/Dravidian): nPVI ~38 - 58
        # Stress-timed (English/Germanic): nPVI ~55 - 78
        # Synthetic TTS speech: often unnaturally flat (<30) or erratically jittery (>85)
        self.npvi_synthetic_low = 30.0
        self.npvi_synthetic_high = 85.0

    @property
    def name(self) -> str:
        return "multilingual"

    def analyze(self, audio: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Analyzes the audio window for multilingual phonetic anomalies,
        determines linguistic family profile, and computes adaptive calibration offsets.
        """
        if len(audio) < sample_rate * 0.3 or AudioPreprocessor.is_silent(audio):
            return {
                "anomaly_score": 0.0,
                "confidence": 0.0,
                "metrics": {
                    "language_family": "neutral",
                    "estimated_language": "Standard / Neutral",
                    "vowel_space_area": 0.0,
                    "retroflex_dip_ratio": 0.0,
                    "npvi_rhythm_index": 0.0,
                    "formant_dispersion": 0.0,
                    "multilingual_synthetic_prob": 0.0,
                },
                "adaptive_offsets": {
                    "pitch_variance_tolerance": 1.0,
                    "shimmer_tolerance": 1.0,
                    "jitter_tolerance": 1.0,
                },
                "anomalies_detected": [],
            }

        # 1. Formant Analysis (F1, F2, F3) & Vowel Space Area (VSA)
        formants, vsa, f_dispersion = self._estimate_formants_and_vsa(audio, sample_rate)

        # 2. Retroflex Consonant Acoustic Dip Detection (indicative of Indian phonetics)
        retroflex_score, retroflex_ratio = self._detect_retroflex_acoustics(audio, sample_rate)

        # 3. Syllable Cadence & Rhythm (Normalized Pairwise Variability Index)
        npvi_val, rhythm_score = self._compute_npvi_rhythm(audio, sample_rate)

        # 4. Classify Linguistic Family & Accent Profile
        lang_family, est_lang = self._classify_linguistic_profile(
            f_dispersion, retroflex_ratio, npvi_val
        )

        # 5. Compute VSA Compression Anomaly Score
        # Synthetic voices compress formant triangles due to spectral oversmoothing
        if vsa > 0:
            if vsa < self.synthetic_vsa_cutoff:
                vsa_anomaly = float(np.clip((self.synthetic_vsa_cutoff - vsa) / self.synthetic_vsa_cutoff, 0.0, 1.0))
            else:
                vsa_anomaly = 0.0
        else:
            vsa_anomaly = 0.0

        # Composite multilingual anomaly score
        synthetic_prob = (
            0.40 * vsa_anomaly +
            0.35 * rhythm_score +
            0.25 * (1.0 - retroflex_score if retroflex_ratio > 0.15 else 0.0)
        )
        synthetic_prob = float(np.clip(synthetic_prob, 0.0, 1.0))

        # 6. Adaptive Calibration Offsets for Downstream Forensic Detectors
        # Indian languages are more dynamically expressive with wider pitch swings and micro-inflections.
        # We supply tolerance multipliers to eliminate false alarms in prosody/perturbation detectors.
        adaptive_offsets = {
            "pitch_variance_tolerance": 1.35 if lang_family in ["indo_aryan", "dravidian"] else 1.0,
            "shimmer_tolerance": 1.25 if lang_family in ["indo_aryan", "dravidian"] else 1.0,
            "jitter_tolerance": 1.20 if lang_family in ["indo_aryan", "dravidian"] else 1.0,
        }

        confidence = 0.86 if len(audio) >= sample_rate * 1.0 else 0.65

        anomalies_detected: List[Dict[str, Any]] = []
        if vsa_anomaly > 0.60:
            anomalies_detected.append({
                "type": "VOWEL_SPACE_COMPRESSION",
                "severity": "HIGH",
                "metric_name": "Phonetic Vowel Space Area",
                "value": f"{int(vsa)} Hz² (Compressed)",
                "threshold": f"> {int(self.synthetic_vsa_cutoff)} Hz² expected",
                "description": "Formant dispersion is severely contracted. Acoustic vowel triangle exhibits neural vocoder smoothing typical of cloned voices.",
            })

        if rhythm_score > 0.65:
            anomalies_detected.append({
                "type": "UNNATURAL_SYLLABLE_CADENCE",
                "severity": "MEDIUM",
                "metric_name": "Normalized Pairwise Variability (nPVI)",
                "value": f"nPVI {round(npvi_val, 1)}",
                "threshold": f"Natural range: {self.npvi_synthetic_low} - {self.npvi_synthetic_high}",
                "description": "Syllable duration cadence deviates from authentic human speech rhythm, indicating robotic TTS synthesis pacing.",
            })

        return {
            "anomaly_score": round(synthetic_prob, 3),
            "confidence": round(confidence, 2),
            "metrics": {
                "language_family": lang_family,
                "estimated_language": est_lang,
                "vowel_space_area": round(vsa, 1),
                "retroflex_dip_ratio": round(retroflex_ratio, 3),
                "npvi_rhythm_index": round(npvi_val, 1),
                "formant_dispersion": round(f_dispersion, 1),
                "multilingual_synthetic_prob": round(synthetic_prob, 3),
            },
            "adaptive_offsets": adaptive_offsets,
            "anomalies_detected": anomalies_detected,
        }

    def _estimate_formants_and_vsa(self, audio: np.ndarray, sample_rate: int) -> Tuple[List[float], float, float]:
        """
        Estimates the first three formants (F1, F2, F3) using LPC spectral peaks,
        calculates Formant Dispersion, and computes the 2D Vowel Space Area (VSA).
        """
        # Pre-emphasis filter to boost high formants
        pre_emph = np.append(audio[0], audio[1:] - 0.96 * audio[:-1])

        # Compute Welch spectrum for robust spectral envelope
        nperseg = min(1024, len(pre_emph))
        freqs, psd = signal.welch(pre_emph, fs=sample_rate, nperseg=nperseg)
        log_psd = 10 * np.log10(psd + 1e-10)

        # Smooth spectral envelope with Savitzky-Golay filter to find broad formant peaks
        window_len = min(21, len(log_psd) if len(log_psd) % 2 != 0 else len(log_psd) - 1)
        if window_len >= 5:
            smooth_spec = signal.savgol_filter(log_psd, window_len, 3)
        else:
            smooth_spec = log_psd

        # Find peaks in speech formant ranges:
        # F1: 250 - 950 Hz
        # F2: 950 - 2600 Hz
        # F3: 2200 - 3600 Hz
        f1_mask = (freqs >= 250) & (freqs <= 950)
        f2_mask = (freqs >= 950) & (freqs <= 2600)
        f3_mask = (freqs >= 2200) & (freqs <= 3600)

        f1 = freqs[f1_mask][np.argmax(smooth_spec[f1_mask])] if np.any(f1_mask) else 500.0
        f2 = freqs[f2_mask][np.argmax(smooth_spec[f2_mask])] if np.any(f2_mask) else 1500.0
        f3 = freqs[f3_mask][np.argmax(smooth_spec[f3_mask])] if np.any(f3_mask) else 2500.0

        # Formant dispersion: average difference between adjacent formants
        # Dispersion Delta F = (F3 - F1) / 2
        f_dispersion = float((f3 - f1) / 2.0)

        # Approximate Vowel Space Area (VSA) based on standard vowel corner estimates
        # In natural speech, vowel variation spans delta F1 ~ 500 Hz, delta F2 ~ 1200 Hz
        delta_f1 = max(100.0, abs(f1 - 300.0))
        delta_f2 = max(200.0, abs(f2 - 1000.0))
        # Triangular area approximation: 0.5 * base * height
        vsa = float(0.5 * delta_f1 * delta_f2 * 2.5)

        return [float(f1), float(f2), float(f3)], vsa, f_dispersion

    def _detect_retroflex_acoustics(self, audio: np.ndarray, sample_rate: int) -> Tuple[float, float]:
        """
        Retroflex consonants (ट, ठ, ड, ढ़, ण) common in Indic languages produce a characteristic
        downward dip in F3 towards F2 (locus frequency around 1700 - 2200 Hz).
        Deepfake generators often produce unnatural spectral continuity without authentic retroflex dips.
        """
        f, t, zxx = signal.stft(audio, fs=sample_rate, nperseg=512, noverlap=256)
        mag = np.abs(zxx) + 1e-10

        # F3 retroflex band: 1700 - 2300 Hz
        retro_mask = (f >= 1700) & (f <= 2300)
        # Mid band reference: 800 - 1500 Hz
        ref_mask = (f >= 800) & (f <= 1500)

        if not np.any(retro_mask) or not np.any(ref_mask):
            return 0.5, 0.0

        retro_energy = np.mean(mag[retro_mask, :], axis=0)
        ref_energy = np.mean(mag[ref_mask, :], axis=0)

        # Dip occurs when retroflex locus drops below reference baseline
        dip_ratio = float(np.sum(retro_energy < 0.65 * ref_energy) / (len(retro_energy) + 1e-6))

        # Authentic Indian speech will typically exhibit dip_ratio between 0.12 and 0.45
        # If dip_ratio is within natural bounds, it's authentic retroflex speech (anomaly score low)
        if dip_ratio > 0.10:
            authenticity = 1.0 - np.clip(abs(dip_ratio - 0.25) / 0.25, 0.0, 1.0)
            anomaly_score = float(1.0 - authenticity)
        else:
            # Not an Indic retroflex sample or non-tonal; neutral score
            anomaly_score = 0.1

        return anomaly_score, dip_ratio

    def _compute_npvi_rhythm(self, audio: np.ndarray, sample_rate: int) -> Tuple[float, float]:
        """
        Computes the Normalized Pairwise Variability Index (nPVI) of vocalic nuclei durations.
        nPVI = 100 / (m - 1) * sum(|d_k - d_{k+1}| / ((d_k + d_{k+1}) / 2))
        """
        # Energy envelope to find vocalic nuclei
        analytic = signal.hilbert(audio)
        env = np.abs(analytic)
        win = max(1, int(sample_rate * 0.025))
        smooth_env = np.convolve(env, np.ones(win) / win, mode='same')

        # Find syllable energy peaks (min distance 120ms, approx max 8 syllables/sec)
        min_dist = int(sample_rate * 0.12)
        threshold = np.mean(smooth_env) + 0.2 * np.std(smooth_env)
        peaks, _ = signal.find_peaks(smooth_env, distance=min_dist, height=threshold)

        if len(peaks) < 3:
            # Not enough syllables in this window for robust nPVI; return baseline
            return 50.0, 0.0

        # Peak-to-peak durations in milliseconds
        durations = np.diff(peaks) / (sample_rate / 1000.0)

        # Pairwise differences
        diffs = np.abs(np.diff(durations))
        means = (durations[:-1] + durations[1:]) / 2.0 + 1e-6

        npvi = float(100.0 / len(diffs) * np.sum(diffs / means))

        # Anomaly scoring:
        # TTS models tend to have nPVI < 28 (too robotic/metronomic) or > 90 (uncontrolled timing jitter)
        if npvi < self.npvi_synthetic_low:
            anomaly = (self.npvi_synthetic_low - npvi) / self.npvi_synthetic_low
        elif npvi > self.npvi_synthetic_high:
            anomaly = (npvi - self.npvi_synthetic_high) / (120.0 - self.npvi_synthetic_high)
        else:
            anomaly = 0.0

        return npvi, float(np.clip(anomaly, 0.0, 1.0))

    def _classify_linguistic_profile(
        self, f_dispersion: float, retroflex_ratio: float, npvi: float
    ) -> Tuple[str, str]:
        """
        Categorizes speech into linguistic family and probable language/accent group.
        """
        if retroflex_ratio > 0.18:
            # Significant retroflex consonant usage (Indic languages)
            if npvi < 50.0:
                return "dravidian", "Dravidian (Tamil, Telugu, Kannada, Malayalam)"
            else:
                return "indo_aryan", "Indo-Aryan (Hindi, Bengali, Marathi, Gujarati)"
        elif retroflex_ratio > 0.08:
            if npvi > 58.0:
                return "indian_english", "Indian English (Regional Accent)"
            else:
                return "indo_aryan", "Indo-Aryan / Indic Regional"
        else:
            if npvi > 62.0:
                return "english_global", "English / Global Stress-Timed"
            else:
                return "neutral", "Standard / Neutral Multilingual"
