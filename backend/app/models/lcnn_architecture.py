"""PyTorch Light-CNN (LCNN) with Max-Feature-Map (MFM) for Deepfake Audio Detection."""
import torch
import torch.nn as nn
import torch.nn.functional as F


class MaxFeatureMap2D(nn.Module):
    """
    Max-Feature-Map (MFM) activation function.
    Splits channel dimension in half and takes element-wise maximum.
    Suppresses competitive features and preserves peak forensic anomalies.
    """
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = torch.split(x, x.size(1) // 2, dim=1)
        return torch.max(out[0], out[1])


class MaxFeatureMap1D(nn.Module):
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = torch.split(x, x.size(1) // 2, dim=1)
        return torch.max(out[0], out[1])


class LCNNBlock(nn.Module):
    """Standard Convolutional Block with Max-Feature-Map (MFM)."""
    def __init__(self, in_channels: int, out_channels: int, kernel_size: int = 3, stride: int = 1, padding: int = 1):
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels * 2, kernel_size, stride, padding)
        self.mfm = MaxFeatureMap2D()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.mfm(self.conv(x))


class SelfAttentionPooling(nn.Module):
    """Self-Attention Pooling over time dimension."""
    def __init__(self, in_dim: int):
        super().__init__()
        self.att = nn.Sequential(
            nn.Linear(in_dim, in_dim // 2),
            nn.Tanh(),
            nn.Linear(in_dim // 2, 1),
            nn.Softmax(dim=1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [Batch, Time, Dim]
        weights = self.att(x)  # [Batch, Time, 1]
        pooled = torch.sum(x * weights, dim=1)  # [Batch, Dim]
        return pooled


class LCNNModel(nn.Module):
    """
    Complete LCNN-BiLSTM-Attention Deep Neural Network for Voice Anti-Spoofing.
    Input shape: [Batch, 1, FreqBins, TimeFrames] (e.g. Mel-Spectrogram or LFCC)
    Output shape: [Batch, 2] (Class 0: Genuine, Class 1: Synthetic/Cloned)
    """
    def __init__(self, in_channels: int = 1, num_classes: int = 2):
        super().__init__()

        # Conv Front-End with MFM activations
        self.features = nn.Sequential(
            LCNNBlock(in_channels, 16, kernel_size=5, stride=1, padding=2),
            nn.MaxPool2d(kernel_size=2, stride=2),

            LCNNBlock(16, 32, kernel_size=3, stride=1, padding=1),
            nn.MaxPool2d(kernel_size=2, stride=2),

            LCNNBlock(32, 64, kernel_size=3, stride=1, padding=1),
            nn.MaxPool2d(kernel_size=2, stride=2),

            LCNNBlock(64, 64, kernel_size=3, stride=1, padding=1),
            nn.AdaptiveAvgPool2d((8, None)),  # Fixed frequency dimension = 8
        )

        # BiLSTM for temporal context
        self.bilstm = nn.LSTM(
            input_size=64 * 8,
            hidden_size=64,
            num_layers=1,
            batch_first=True,
            bidirectional=True,
        )

        # Attention pooling
        self.attention = SelfAttentionPooling(in_dim=128)

        # Classifier
        self.classifier = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [Batch, 1, Freq, Time]
        feat = self.features(x)  # [Batch, 64, 8, Time']
        B, C, F_dim, T = feat.shape
        feat = feat.permute(0, 3, 1, 2).contiguous().view(B, T, C * F_dim)  # [Batch, Time', 512]

        lstm_out, _ = self.bilstm(feat)  # [Batch, Time', 128]
        pooled = self.attention(lstm_out)  # [Batch, 128]
        logits = self.classifier(pooled)  # [Batch, num_classes]

        return logits

    def get_spoof_probability(self, x: torch.Tensor) -> float:
        """Helper for single sample inference returning synthetic probability in [0, 1]."""
        self.eval()
        with torch.no_grad():
            logits = self.forward(x)
            probs = F.softmax(logits, dim=1)
            return float(probs[0, 1].item())
