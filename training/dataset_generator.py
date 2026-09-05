"""Adversarial Synthetic and Genuine Audio Generator for Local Model Training."""
import os
import soundfile as sf
import numpy as np
from scipy import signal
from typing import Tuple


def generate_genuine_speech_sample(duration_sec: float = 3.0, sample_rate: int = 16000) -> np.ndarray:
    """
    Synthesizes speech signal with natural human biological traits:
    - Dynamic pitch contour (F0 inflection sigma = 35 Hz)
    - 8-12 Hz involuntary vocal micro-tremors
    - Harmonic decay with formants
    - Physiological respiration pauses
    """
    n_samples = int(duration_sec * sample_rate)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)

    # 1. Human Pitch Contour F0(t) with natural vibrato and prosodic drift
    base_f0 = np.random.uniform(110.0, 220.0)
    prosody_drift = 30.0 * np.sin(2 * np.pi * np.random.uniform(0.8, 1.8) * t)
    micro_tremor = 2.5 * np.sin(2 * np.pi * np.random.uniform(9.0, 11.0) * t)  # 10 Hz tremor
    f0_t = base_f0 + prosody_drift + micro_tremor

    # Phase integration
    phase = 2 * np.pi * np.cumsum(f0_t) / sample_rate

    # 2. Source Glottal Flow Harmonics
    audio = (
        0.55 * np.sin(phase)
        + 0.28 * np.sin(2 * phase)
        + 0.16 * np.sin(3 * phase)
        + 0.09 * np.sin(4 * phase)
        + 0.05 * np.sin(5 * phase)
    )

    # 3. Formant Resonance Filters (Vocal Tract)
    # Formant 1: 500 Hz (Q=5), Formant 2: 1500 Hz (Q=7), Formant 3: 2500 Hz (Q=10)
    b1, a1 = signal.iirpeak(500.0, 5.0, fs=sample_rate)
    b2, a2 = signal.iirpeak(1500.0, 7.0, fs=sample_rate)
    b3, a3 = signal.iirpeak(2500.0, 10.0, fs=sample_rate)

    vocal_tract = signal.lfilter(b1, a1, audio) + 0.6 * signal.lfilter(b2, a2, audio) + 0.3 * signal.lfilter(b3, a3, audio)

    # 4. Insert natural breath gap / unvoiced pause
    pause_start = int(n_samples * np.random.uniform(0.4, 0.6))
    pause_len = int(sample_rate * np.random.uniform(0.15, 0.30))
    if pause_start + pause_len < n_samples:
        vocal_tract[pause_start : pause_start + pause_len] *= 0.05

    # 5. Subtle ambient room noise
    noise = np.random.normal(0, 0.015, n_samples)
    out = vocal_tract + noise
    max_val = np.max(np.abs(out)) + 1e-12
    return (out * (0.90 / max_val)).astype(np.float32)


def generate_deepfake_speech_sample(duration_sec: float = 3.0, sample_rate: int = 16000, spoof_type: str = "tts") -> np.ndarray:
    """
    Synthesizes deepfake speech with specific algorithmic failure modes:
    - 'tts': Overly flat pitch, high spectral flatness, missing micro-tremors, unbroken phonation
    - 'vocoder_phase': STFT phase discontinuities, high-frequency cutoff artifact
    - 'voice_conversion': Formant-shifted distorted harmonic decay
    """
    n_samples = int(duration_sec * sample_rate)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)

    if spoof_type == "tts":
        # Flat constant pitch with robotic uniformity
        f0 = np.random.uniform(130.0, 200.0)
        phase = 2 * np.pi * f0 * t
        audio = 0.6 * np.sin(phase) + 0.3 * np.sin(2 * phase) + 0.2 * np.sin(3 * phase)
        # High spectral flatness artifact (diffuse white noise floor)
        audio += np.random.normal(0, 0.09, n_samples)

    elif spoof_type == "vocoder_phase":
        # Phase jumps and brickwall cutoff filter at 4kHz
        f0 = np.random.uniform(120.0, 180.0)
        phase = 2 * np.pi * f0 * t + np.random.choice([0, np.pi/4, np.pi/2], n_samples)
        audio = 0.5 * np.sin(phase) + 0.25 * np.sin(2 * phase) + 0.15 * np.sin(3 * phase)
        # Lowpass filter brickwall at 4000 Hz
        sos = signal.butter(8, 4000.0, btype="low", fs=sample_rate, output="sos")
        audio = signal.sosfilt(sos, audio)

    else:  # voice conversion
        f0 = np.random.uniform(140.0, 210.0) + 5.0 * np.sin(2 * np.pi * 0.5 * t)
        phase = 2 * np.pi * np.cumsum(f0) / sample_rate
        audio = 0.7 * np.sin(phase) + 0.4 * np.sin(1.8 * phase)  # Inharmonic phase

    max_val = np.max(np.abs(audio)) + 1e-12
    return (audio * (0.90 / max_val)).astype(np.float32)


def generate_training_corpus(
    output_dir: str = "data/synthetic_corpus",
    num_samples_per_class: int = 50,
    sample_rate: int = 16000,
) -> Tuple[int, int]:
    """Generates balanced training corpus of real and fake samples."""
    real_dir = os.path.join(output_dir, "real")
    fake_dir = os.path.join(output_dir, "fake")
    os.makedirs(real_dir, exist_ok=True)
    os.makedirs(fake_dir, exist_ok=True)

    spoof_types = ["tts", "vocoder_phase", "voice_conversion"]

    # Generate Real Samples
    for i in range(num_samples_per_class):
        dur = np.random.uniform(2.0, 3.5)
        audio = generate_genuine_speech_sample(dur, sample_rate)
        fpath = os.path.join(real_dir, f"real_{i+1:04d}.wav")
        sf.write(fpath, audio, sample_rate)

    # Generate Fake Samples
    for i in range(num_samples_per_class):
        dur = np.random.uniform(2.0, 3.5)
        stype = spoof_types[i % len(spoof_types)]
        audio = generate_deepfake_speech_sample(dur, sample_rate, spoof_type=stype)
        fpath = os.path.join(fake_dir, f"fake_{stype}_{i+1:04d}.wav")
        sf.write(fpath, audio, sample_rate)

    return num_samples_per_class, num_samples_per_class


if __name__ == "__main__":
    n_real, n_fake = generate_training_corpus(num_samples_per_class=30)
    print(f"Generated {n_real} genuine and {n_fake} synthetic deepfake training samples in data/synthetic_corpus/")
