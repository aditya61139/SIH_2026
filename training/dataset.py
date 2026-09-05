"""PyTorch Audio Dataset for Deepfake Detection with Audio Augmentations and Multi-Generator Support."""
import os
import glob
import soundfile as sf
import numpy as np
import torch
from torch.utils.data import Dataset
from scipy import signal
from typing import Tuple, List, Optional, Dict, Any


class AudioDeepfakeDataset(Dataset):
    """
    PyTorch Dataset for Real vs Deepfake Audio classification.
    Supports:
    - Multi-generator datasets (e.g., K:\\dataSet\\archive with real_samples, OpenAI, xTTS, VALL-E, VoiceBox, etc.)
    - Standard real/fake folder structures
    - Precomputed Mel filterbank for maximum throughput
    - SpecAugment (Time & Frequency masking)
    - Additive Gaussian noise & random gain perturbations
    """

    def __init__(
        self,
        data_dir: str,
        sample_rate: int = 16000,
        fixed_length_sec: float = 2.0,
        augment: bool = False,
        n_mels: int = 80,
        n_fft: int = 512,
        hop_length: int = 160,
    ):
        self.data_dir = data_dir
        self.sample_rate = sample_rate
        self.target_samples = int(sample_rate * fixed_length_sec)
        self.augment = augment
        self.n_mels = n_mels
        self.n_fft = n_fft
        self.hop_length = hop_length

        # Precompute Mel Filterbank once
        self.mel_fbank = self._create_mel_filterbank(self.n_mels, self.n_fft)

        # Discovered samples: (filepath, label: 0=real, 1=fake, generator_name: str)
        self.samples: List[Tuple[str, int, str]] = []
        self._scan_dataset(data_dir)
        np.random.shuffle(self.samples)

    def _scan_dataset(self, data_input: Any) -> None:
        if isinstance(data_input, str):
            dirs = [d.strip() for d in data_input.split(",") if d.strip()]
        elif isinstance(data_input, (list, tuple)):
            dirs = list(data_input)
        else:
            dirs = [str(data_input)]

        real_indicators = {"real", "real_samples", "genuine", "bonafide", "human", "authentic"}

        for d_path in dirs:
            if not os.path.exists(d_path):
                continue

            subdirs = [d for d in os.listdir(d_path) if os.path.isdir(os.path.join(d_path, d))]
            if subdirs:
                for d in subdirs:
                    d_lower = d.lower()
                    is_real = any(ind in d_lower for ind in real_indicators)
                    label = 0 if is_real else 1
                    gen_name = d

                    full_sub = os.path.join(d_path, d)
                    for root, _, files in os.walk(full_sub):
                        # Also check if sub-sub-directory specifies real vs fake
                        sub_label = label
                        parent_name = os.path.basename(root).lower()
                        if any(ind in parent_name for ind in real_indicators):
                            sub_label = 0
                        elif any(ind in parent_name for ind in ["fake", "spoof", "synthetic"]):
                            sub_label = 1

                        for f in files:
                            if f.lower().endswith((".wav", ".mp3", ".flac", ".ogg", ".m4a")):
                                self.samples.append((os.path.join(root, f), sub_label, gen_name))
            else:
                real_files = glob.glob(os.path.join(d_path, "real", "*.*"))
                fake_files = glob.glob(os.path.join(d_path, "fake", "*.*"))
                for rf in real_files:
                    if rf.lower().endswith((".wav", ".mp3", ".flac", ".ogg")):
                        self.samples.append((rf, 0, "genuine_real"))
                for ff in fake_files:
                    if ff.lower().endswith((".wav", ".mp3", ".flac", ".ogg")):
                        self.samples.append((ff, 1, "synthetic_fake"))

    def __len__(self) -> int:
        return len(self.samples)

    def get_class_counts(self) -> Dict[str, int]:
        counts = {}
        for _, label, gen in self.samples:
            counts[gen] = counts.get(gen, 0) + 1
        return counts

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        fpath, label, _ = self.samples[idx]

        try:
            audio, sr = sf.read(fpath)
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)
            if sr != self.sample_rate and len(audio) > 0:
                target_len = int(len(audio) * (self.sample_rate / sr))
                audio = signal.resample(audio, target_len)
        except Exception:
            # Fallback to zeros if audio is unreadable
            audio = np.zeros(self.target_samples, dtype=np.float32)

        audio = audio.astype(np.float32)

        # Pad or crop to target_samples (32000 for 2.0s at 16kHz)
        if len(audio) < self.target_samples:
            pad_len = self.target_samples - len(audio)
            audio = np.pad(audio, (0, pad_len), mode="constant")
        else:
            if self.augment and len(audio) > self.target_samples:
                max_start = len(audio) - self.target_samples
                start = np.random.randint(0, max_start)
                audio = audio[start : start + self.target_samples]
            else:
                audio = audio[: self.target_samples]

        # On-the-fly audio augmentations
        if self.augment:
            # Random gain variation (0.7x - 1.2x)
            audio = audio * np.random.uniform(0.7, 1.2)
            # Add subtle acoustic noise (50% probability)
            if np.random.rand() < 0.5:
                audio += np.random.normal(0, np.random.uniform(0.001, 0.015), len(audio))

        # Compute Log-Mel Spectrogram using precomputed filterbank
        mel_spec = self._compute_melspec(audio)

        # SpecAugment (Time & Frequency masking)
        if self.augment:
            mel_spec = self._spec_augment(mel_spec)

        # Convert to Tensor [1, N_mels, Time]
        tensor = torch.from_numpy(mel_spec).unsqueeze(0).float()
        return tensor, label

    def _compute_melspec(self, audio: np.ndarray) -> np.ndarray:
        f, t, zxx = signal.stft(
            audio,
            fs=self.sample_rate,
            nperseg=self.n_fft,
            noverlap=self.n_fft - self.hop_length,
        )
        pow_spec = np.abs(zxx) ** 2
        mel_spec = np.dot(self.mel_fbank, pow_spec)
        mel_spec = np.log(np.maximum(mel_spec, 1e-6))
        # Zero-mean unit-variance normalization
        mel_spec = (mel_spec - np.mean(mel_spec)) / (np.std(mel_spec) + 1e-6)
        return mel_spec.astype(np.float32)

    def _create_mel_filterbank(self, n_mels: int, n_fft: int) -> np.ndarray:
        num_bins = n_fft // 2 + 1
        low_mel = 0.0
        high_mel = 2595.0 * np.log10(1.0 + (self.sample_rate / 2.0) / 700.0)
        mel_pts = np.linspace(low_mel, high_mel, n_mels + 2)
        hz_pts = 700.0 * (10.0 ** (mel_pts / 2595.0) - 1.0)
        bin_pts = np.floor((n_fft + 1) * hz_pts / self.sample_rate).astype(int)

        fbank = np.zeros((n_mels, num_bins), dtype=np.float32)
        for m in range(1, n_mels + 1):
            f_m_minus, f_m, f_m_plus = bin_pts[m - 1], bin_pts[m], bin_pts[m + 1]
            for k in range(f_m_minus, f_m):
                if k < num_bins:
                    fbank[m - 1, k] = (k - f_m_minus) / (f_m - f_m_minus + 1e-12)
            for k in range(f_m, f_m_plus):
                if k < num_bins:
                    fbank[m - 1, k] = (f_m_plus - k) / (f_m_plus - f_m + 1e-12)
        return fbank

    def _spec_augment(self, spec: np.ndarray, max_mask_f: int = 12, max_mask_t: int = 20) -> np.ndarray:
        """Applies Time & Frequency Masking to Spectrogram."""
        augmented = spec.copy()
        n_mels, n_time = augmented.shape

        # Frequency Masking
        f_mask_len = np.random.randint(0, max_mask_f)
        f_start = np.random.randint(0, max(1, n_mels - f_mask_len))
        augmented[f_start : f_start + f_mask_len, :] = 0.0

        # Time Masking
        t_mask_len = np.random.randint(0, max_mask_t)
        t_start = np.random.randint(0, max(1, n_time - t_mask_len))
        augmented[:, t_start : t_start + t_mask_len] = 0.0

        return augmented
