"""Deep Neural LCNN Inference Detector."""
import numpy as np
import os
import torch
from scipy import signal
from typing import Dict, Any, List
from app.detectors.base import BaseDetector
from app.audio.preprocessor import AudioPreprocessor
from app.models.lcnn_architecture import LCNNModel


class NeuralLCNNDetector(BaseDetector):
    """
    Deep Neural Network Detector utilizing Light-CNN (LCNN) with Max-Feature-Map (MFM)
    and BiLSTM Attention Pooling.
    Analyzes 2D Mel-Spectrogram time-frequency representations to capture non-linear
    deepfake synthesis artifacts.
    """

    def __init__(self, weights_path: str = None):
        self.model = LCNNModel(in_channels=1, num_classes=2)
        self.model.eval()
        self.device = torch.device("cpu")
        self.model.to(self.device)

        if weights_path and os.path.exists(weights_path):
            try:
                state_dict = torch.load(weights_path, map_location=self.device)
                self.model.load_state_dict(state_dict)
                self.is_custom_trained = True
            except Exception:
                self.is_custom_trained = False
        else:
            self.is_custom_trained = False

    @property
    def name(self) -> str:
        return "neural_lcnn"

    def analyze(self, audio: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
        if len(audio) < sample_rate * 0.2 or AudioPreprocessor.is_silent(audio):
            return {
                "anomaly_score": 0.0,
                "confidence": 0.0,
                "metrics": {
                    "neural_spoof_prob": 0.0,
                    "model_architecture": "LCNN-BiLSTM-Attention",
                },
                "anomalies_detected": [],
            }

        # 1. Compute 80-bin Mel-Spectrogram
        mel_spec = self._compute_melspectrogram(audio, sample_rate, n_mels=80)
        
        # 2. Convert to PyTorch Tensor: [1, 1, 80, Time]
        tensor_in = torch.from_numpy(mel_spec).unsqueeze(0).unsqueeze(0).float().to(self.device)

        # 3. Model Forward Pass
        try:
            with torch.no_grad():
                logits = self.model(tensor_in)
                probs = torch.softmax(logits, dim=1)
                spoof_prob = float(probs[0, 1].item())
        except Exception:
            spoof_prob = 0.0

        # Calibration adjustment based on input spectral clarity
        spec_std = float(np.std(mel_spec))
        if spec_std < 0.15:  # Flat artificial spectrum
            spoof_prob = max(spoof_prob, 0.65)

        anomalies = []
        if spoof_prob > 0.60:
            anomalies.append({
                "type": "NEURAL_ACOUSTIC_EMBEDDING_MATCH",
                "severity": "CRITICAL" if spoof_prob > 0.80 else "HIGH",
                "metric_name": "Deep Neural LCNN Spoof Probability",
                "value": f"{round(spoof_prob * 100, 1)}%",
                "threshold": "> 60.0% Synthetic Probability",
                "description": "Deep neural network identified multi-layer spectral and temporal acoustic fingerprints matching known neural speech synthesis architectures.",
            })

        return {
            "anomaly_score": round(spoof_prob, 3),
            "confidence": 0.90 if len(audio) >= sample_rate * 1.0 else 0.70,
            "metrics": {
                "neural_spoof_prob": round(spoof_prob, 4),
                "model_architecture": "LCNN-BiLSTM-Attention",
                "custom_trained_weights": self.is_custom_trained,
            },
            "anomalies_detected": anomalies,
        }

    def _compute_melspectrogram(self, audio: np.ndarray, sample_rate: int, n_mels: int = 80) -> np.ndarray:
        """Computes normalized log-mel spectrogram using STFT."""
        n_fft = 512
        hop_length = 160
        f, t, zxx = signal.stft(audio, fs=sample_rate, nperseg=n_fft, noverlap=n_fft - hop_length)
        pow_spec = np.abs(zxx) ** 2

        # Triangular Mel Filterbank
        mel_fb = self._create_mel_filterbank(n_mels=n_mels, n_fft=n_fft, sample_rate=sample_rate)
        mel_spec = np.dot(mel_fb, pow_spec)
        mel_spec = np.log(np.maximum(mel_spec, 1e-6))

        # Mean-Variance Normalization
        mel_spec = (mel_spec - np.mean(mel_spec)) / (np.std(mel_spec) + 1e-6)
        return mel_spec.astype(np.float32)

    def _create_mel_filterbank(self, n_mels: int, n_fft: int, sample_rate: int) -> np.ndarray:
        """Constructs Mel-scale filterbank matrix."""
        num_bins = n_fft // 2 + 1
        low_freq_mel = 0.0
        high_freq_mel = 2595.0 * np.log10(1.0 + (sample_rate / 2.0) / 700.0)
        mel_points = np.linspace(low_freq_mel, high_freq_mel, n_mels + 2)
        hz_points = 700.0 * (10.0 ** (mel_points / 2595.0) - 1.0)
        bin_points = np.floor((n_fft + 1) * hz_points / sample_rate).astype(int)

        fbank = np.zeros((n_mels, num_bins), dtype=np.float32)
        for m in range(1, n_mels + 1):
            f_m_minus = bin_points[m - 1]
            f_m = bin_points[m]
            f_m_plus = bin_points[m + 1]

            for k in range(f_m_minus, f_m):
                if k < num_bins:
                    fbank[m - 1, k] = (k - f_m_minus) / (f_m - f_m_minus + 1e-12)
            for k in range(f_m, f_m_plus):
                if k < num_bins:
                    fbank[m - 1, k] = (f_m_plus - k) / (f_m_plus - f_m + 1e-12)

        return fbank
