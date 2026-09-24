"""Adversarial Synthetic, Loud Speech, and Replay Audio Generator for Local Model Training."""
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


def generate_loud_genuine_speech_sample(duration_sec: float = 3.0, sample_rate: int = 16000) -> np.ndarray:
    """
    Synthesizes authentic human speech spoken loudly / with vocal projection:
    - Elevated pitch baseline (F0 in 150 - 270 Hz)
    - Strong glottal closure (sharper glottal flow velocity)
    - Prominent vocal tract formants with high Harmonics-to-Noise Ratio (HNR > 22 dB)
    - Single-room near-field acoustic decay (authentic near-field microphone placement)
    """
    n_samples = int(duration_sec * sample_rate)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)

    # Elevated pitch contour due to vocal effort (Lombard reflex)
    base_f0 = np.random.uniform(160.0, 260.0)
    pitch_modulation = 15.0 * np.sin(2 * np.pi * 1.5 * t)
    micro_tremor = 3.0 * np.sin(2 * np.pi * 10.0 * t)
    f0_t = base_f0 + pitch_modulation + micro_tremor

    phase = 2 * np.pi * np.cumsum(f0_t) / sample_rate

    # Glottal pulse with high harmonic overtone energy (characteristic of loud vocalization)
    harmonics = (
        0.65 * np.sin(phase)
        + 0.45 * np.sin(2 * phase)
        + 0.30 * np.sin(3 * phase)
        + 0.20 * np.sin(4 * phase)
        + 0.12 * np.sin(5 * phase)
        + 0.08 * np.sin(6 * phase)
    )

    # Dynamic vocal tract formant excitation (F1 ~ 700 Hz, F2 ~ 1700 Hz, F3 ~ 2800 Hz)
    b1, a1 = signal.iirpeak(700.0, 6.0, fs=sample_rate)
    b2, a2 = signal.iirpeak(1700.0, 8.0, fs=sample_rate)
    b3, a3 = signal.iirpeak(2800.0, 10.0, fs=sample_rate)

    vocal_tract = (
        signal.lfilter(b1, a1, harmonics)
        + 0.7 * signal.lfilter(b2, a2, harmonics)
        + 0.4 * signal.lfilter(b3, a3, harmonics)
    )

    # Near-field proximity boost in 120-250 Hz (proximity effect when speaking loud close to mic)
    b_prox, a_prox = signal.iirpeak(180.0, 2.0, fs=sample_rate)
    prox_boost = signal.lfilter(b_prox, a_prox, harmonics) * 0.25
    vocal_tract += prox_boost

    # Pause
    pause_start = int(n_samples * 0.5)
    pause_len = int(sample_rate * 0.20)
    if pause_start + pause_len < n_samples:
        vocal_tract[pause_start : pause_start + pause_len] *= 0.03

    # Clean signal with very high HNR
    noise = np.random.normal(0, 0.005, n_samples)
    out = vocal_tract + noise
    max_val = np.max(np.abs(out)) + 1e-12
    return (out * (0.95 / max_val)).astype(np.float32)


def generate_loudspeaker_replayed_sample(duration_sec: float = 3.0, sample_rate: int = 16000) -> np.ndarray:
    """
    Simulates speech replayed through a mobile/laptop physical loudspeaker:
    - Steep transducer high-pass cutoff (< 150 Hz missing)
    - Electro-acoustic intermodulation distortion and power compression
    - Dual-room impulse response (recording room + playback room reverberation)
    - Cabinet resonance peak in 2.8 - 4.0 kHz
    """
    # Start with a clean authentic speech sample
    clean = generate_genuine_speech_sample(duration_sec, sample_rate)

    # 1. Transducer Low-End Cutoff (< 160 Hz high-pass Butterworth filter)
    sos = signal.butter(4, 160.0, btype="highpass", fs=sample_rate, output="sos")
    filtered = signal.sosfilt(sos, clean)

    # 2. Electro-Acoustic Non-Linear Loudspeaker Distortion (Saturation & Intermodulation)
    # Creates harmonic flattening and inter-harmonic spurs
    distorted = filtered + 0.22 * (filtered ** 2) - 0.12 * (filtered ** 3)

    # 3. Cabinet Plastic Resonance (peak at 3200 Hz with Q=5)
    b_res, a_res = signal.iirpeak(3200.0, 5.0, fs=sample_rate)
    cabinet_res = signal.lfilter(b_res, a_res, distorted) * 0.35
    distorted += cabinet_res

    # 4. Secondary Acoustic Room Reverberation (Echo delay at 45ms and 80ms)
    delay_1 = int(sample_rate * 0.045)
    delay_2 = int(sample_rate * 0.080)
    replayed = np.copy(distorted)
    if len(replayed) > delay_2:
        replayed[delay_1:] += 0.40 * distorted[:-delay_1]
        replayed[delay_2:] += 0.22 * distorted[:-delay_2]

    max_val = np.max(np.abs(replayed)) + 1e-12
    return (replayed * (0.88 / max_val)).astype(np.float32)


def generate_deepfake_speech_sample(duration_sec: float = 3.0, sample_rate: int = 16000, spoof_type: str = "tts") -> np.ndarray:
    """
    Synthesizes deepfake speech with specific algorithmic failure modes:
    - 'tts': Overly flat pitch, high spectral flatness, missing micro-tremors, unbroken phonation
    - 'vocoder_phase': STFT phase discontinuities, high-frequency cutoff artifact
    - 'voice_conversion': Formant-shifted distorted harmonic decay
    - 'replay_loudspeaker': Physical loudspeaker playback
    """
    if spoof_type == "replay_loudspeaker":
        return generate_loudspeaker_replayed_sample(duration_sec, sample_rate)

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
    """Generates balanced training corpus of real (including loud voice) and fake/replay samples."""
    real_dir = os.path.join(output_dir, "real")
    fake_dir = os.path.join(output_dir, "fake")
    os.makedirs(real_dir, exist_ok=True)
    os.makedirs(fake_dir, exist_ok=True)

    spoof_types = ["tts", "vocoder_phase", "voice_conversion", "replay_loudspeaker"]

    # Generate Real Samples (50% conversational, 50% loud human voice)
    for i in range(num_samples_per_class):
        dur = np.random.uniform(2.0, 3.5)
        if i % 2 == 0:
            audio = generate_genuine_speech_sample(dur, sample_rate)
            fpath = os.path.join(real_dir, f"real_conv_{i+1:04d}.wav")
        else:
            audio = generate_loud_genuine_speech_sample(dur, sample_rate)
            fpath = os.path.join(real_dir, f"real_loud_{i+1:04d}.wav")
        sf.write(fpath, audio, sample_rate)

    # Generate Fake & Replay Samples
    for i in range(num_samples_per_class):
        dur = np.random.uniform(2.0, 3.5)
        stype = spoof_types[i % len(spoof_types)]
        audio = generate_deepfake_speech_sample(dur, sample_rate, spoof_type=stype)
        fpath = os.path.join(fake_dir, f"fake_{stype}_{i+1:04d}.wav")
        sf.write(fpath, audio, sample_rate)

    return num_samples_per_class, num_samples_per_class


if __name__ == "__main__":
    n_real, n_fake = generate_training_corpus(num_samples_per_class=30)
    print(f"Generated {n_real} genuine (conversational + loud) and {n_fake} synthetic/replay training samples in data/synthetic_corpus/")
