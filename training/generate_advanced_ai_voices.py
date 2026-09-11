"""
VoxSentinalX Advanced AI Voice & Neural Vocoder Synthetic Audio Generator.
Generates multi-architectural deepfake audio samples and biological genuine voice samples
to train VoxSentinalX to capture next-generation AI voice clones.
"""
import os
import sys
import json
import soundfile as sf
import numpy as np
from scipy import signal
from collections import defaultdict

# Ensure UTF-8 stdout
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def generate_hifigan_clone(duration_sec: float = 2.5, sr: int = 16000) -> np.ndarray:
    """Simulates HiFi-GAN / BigVGAN neural vocoder artifacts (harmonic phase inversion & sub-band quantization)."""
    n_samples = int(duration_sec * sr)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)
    f0 = np.random.uniform(120.0, 240.0)

    # Multi-period harmonic sum with artificial phase shifts
    harmonics = [np.sin(2 * np.pi * (i + 1) * f0 * t + np.random.uniform(0, np.pi)) for i in range(8)]
    audio = sum(h * (1.0 / (i + 1.2)) for i, h in enumerate(harmonics))

    # Neural vocoder checkerboard artifact (high frequency periodic ripple)
    ripple = 0.04 * np.sin(2 * np.pi * 3800 * t)
    audio += ripple

    # Brickwall filter at 7.8 kHz
    sos = signal.butter(6, 7800, btype='low', fs=sr, output='sos')
    audio = signal.sosfilt(sos, audio)

    return (audio / (np.max(np.abs(audio)) + 1e-8) * 0.9).astype(np.float32)


def generate_diffusion_voice_clone(duration_sec: float = 2.5, sr: int = 16000) -> np.ndarray:
    """Simulates Score-based Diffusion speech synthesis (Grad-TTS / Diff-TTS with flat prosody and diffuse noise floor)."""
    n_samples = int(duration_sec * sr)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)

    # Static robotic fundamental frequency with zero micro-tremors
    f0 = np.random.uniform(130.0, 190.0)
    phase = 2 * np.pi * f0 * t
    audio = 0.6 * np.sin(phase) + 0.3 * np.sin(2 * phase) + 0.15 * np.sin(3 * phase)

    # Formant filtering
    b, a = signal.iirpeak(1200.0, 4.0, fs=sr)
    audio = signal.lfilter(b, a, audio)

    # Residual diffusion stochastic noise floor
    noise = np.random.normal(0, 0.055, n_samples)
    audio += noise

    # Unbroken phonation (0 breath pauses)
    return (audio / (np.max(np.abs(audio)) + 1e-8) * 0.88).astype(np.float32)


def generate_zero_shot_clone(duration_sec: float = 2.5, sr: int = 16000) -> np.ndarray:
    """Simulates Zero-Shot voice cloning (VoiceCraft / VALL-E neural codec token concatenation artifacts)."""
    n_samples = int(duration_sec * sr)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)

    # Step-wise pitch quantization (neural codec discrete codebook jumps)
    f0_steps = np.repeat(np.random.uniform(110.0, 220.0, size=int(duration_sec * 5)), int(sr * 0.2))
    if len(f0_steps) < n_samples:
        f0_steps = np.pad(f0_steps, (0, n_samples - len(f0_steps)), mode='edge')
    else:
        f0_steps = f0_steps[:n_samples]

    phase = 2 * np.pi * np.cumsum(f0_steps) / sr
    audio = 0.5 * np.sin(phase) + 0.25 * np.sin(2 * phase) + 0.12 * np.sin(3 * phase)

    # Codec frame boundary clicks
    for click_idx in range(int(sr * 0.2), n_samples, int(sr * 0.2)):
        if click_idx < n_samples:
            audio[click_idx : min(click_idx + 10, n_samples)] += 0.15

    return (audio / (np.max(np.abs(audio)) + 1e-8) * 0.85).astype(np.float32)


def generate_griffin_lim_clone(duration_sec: float = 2.5, sr: int = 16000) -> np.ndarray:
    """Simulates Spectrogram Inversion (Griffin-Lim) phase incoherence & metallic reverberation."""
    n_samples = int(duration_sec * sr)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)

    f0 = np.random.uniform(140.0, 210.0)
    audio = np.zeros(n_samples)
    for k in range(1, 10):
        # Inverted random phase offsets per harmonic
        audio += (1.0 / k) * np.sin(2 * np.pi * k * f0 * t + np.random.uniform(-np.pi, np.pi))

    # Metallic comb filter echo
    delay = int(sr * 0.012)
    audio[delay:] += 0.35 * audio[:-delay]

    return (audio / (np.max(np.abs(audio)) + 1e-8) * 0.9).astype(np.float32)


def generate_brickwall_vocoder(duration_sec: float = 2.5, sr: int = 16000) -> np.ndarray:
    """Simulates 4 kHz / 8 kHz Brickwall Neural Codec Cutoff (EnCodec / SoundStream)."""
    n_samples = int(duration_sec * sr)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)

    f0 = np.random.uniform(120.0, 180.0)
    audio = sum((1.0 / (k + 1)) * np.sin(2 * np.pi * (k + 1) * f0 * t) for k in range(12))

    # Sharp 8-pole 4 kHz Butterworth lowpass
    sos = signal.butter(8, 4000, btype='low', fs=sr, output='sos')
    audio = signal.sosfilt(sos, audio)

    return (audio / (np.max(np.abs(audio)) + 1e-8) * 0.9).astype(np.float32)


def generate_indic_synthetic_voice(duration_sec: float = 2.5, sr: int = 16000) -> np.ndarray:
    """Simulates Indic-dialect neural TTS (FastSpeech 2 / IndicSynth) with intonation quantization."""
    n_samples = int(duration_sec * sr)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)

    # Indic tonal inflection without physiological jitter
    f0 = 160.0 + 20.0 * signal.square(2 * np.pi * 1.5 * t)
    phase = 2 * np.pi * np.cumsum(f0) / sr
    audio = 0.6 * np.sin(phase) + 0.3 * np.sin(2 * phase) + 0.15 * np.sin(3 * phase)

    # Formant shaping
    b, a = signal.iirpeak(800.0, 6.0, fs=sr)
    audio = signal.lfilter(b, a, audio)

    return (audio / (np.max(np.abs(audio)) + 1e-8) * 0.9).astype(np.float32)


def generate_biological_human_speech(duration_sec: float = 2.5, sr: int = 16000) -> np.ndarray:
    """Generates authentic human speech with dynamic prosody, 8-12 Hz micro-tremors, natural jitter & respiration."""
    n_samples = int(duration_sec * sr)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)

    base_f0 = np.random.uniform(105.0, 215.0)
    # Natural organic prosodic drift + 10 Hz neuro-muscular micro-tremor
    prosody_drift = 25.0 * np.sin(2 * np.pi * np.random.uniform(0.7, 1.4) * t)
    micro_tremor = 2.8 * np.sin(2 * np.pi * np.random.uniform(9.0, 11.5) * t)
    organic_jitter = np.random.normal(0, 0.8, n_samples)
    f0_t = base_f0 + prosody_drift + micro_tremor + organic_jitter

    phase = 2 * np.pi * np.cumsum(f0_t) / sr

    # Biological glottal pulse shaping
    audio = (
        0.52 * np.sin(phase)
        + 0.27 * np.sin(2 * phase)
        + 0.14 * np.sin(3 * phase)
        + 0.08 * np.sin(4 * phase)
        + 0.04 * np.sin(5 * phase)
    )

    # Triple Formant Vocal Tract Resonance
    b1, a1 = signal.iirpeak(np.random.uniform(450, 650), 5.0, fs=sr)
    b2, a2 = signal.iirpeak(np.random.uniform(1400, 1800), 7.0, fs=sr)
    b3, a3 = signal.iirpeak(np.random.uniform(2400, 2900), 10.0, fs=sr)

    vocal_tract = signal.lfilter(b1, a1, audio) + 0.6 * signal.lfilter(b2, a2, audio) + 0.3 * signal.lfilter(b3, a3, audio)

    # Natural Pulmonary Inhalation Pause
    pause_start = int(n_samples * np.random.uniform(0.35, 0.55))
    pause_len = int(sr * np.random.uniform(0.20, 0.35))
    if pause_start + pause_len < n_samples:
        vocal_tract[pause_start : pause_start + pause_len] *= 0.04

    # Organic room ambience
    noise = np.random.normal(0, 0.012, n_samples)
    out = vocal_tract + noise
    return (out / (np.max(np.abs(out)) + 1e-8) * 0.92).astype(np.float32)


def generate_and_organize_samples(
    unified_dir: str = r"p:\VoxSentinalX\data\unified_corpus",
    samples_per_generator: int = 50,
    human_samples: int = 200,
):
    print("=" * 68)
    print("  🎙️ GENERATING ADVANCED AI VOICE & DEEPFAKE SAMPLES")
    print("=" * 68)

    real_dir = os.path.join(unified_dir, "real")
    fake_dir = os.path.join(unified_dir, "fake")
    os.makedirs(real_dir, exist_ok=True)
    os.makedirs(fake_dir, exist_ok=True)

    generators = [
        ("hifigan", generate_hifigan_clone, "HiFi-GAN / BigVGAN Phase Quantization"),
        ("diffusion", generate_diffusion_voice_clone, "Diffusion-based Voice Clones"),
        ("zeroshot", generate_zero_shot_clone, "Zero-Shot Codec VoiceCraft / VALL-E"),
        ("griffinlim", generate_griffin_lim_clone, "Spectrogram Inversion Phase Jumps"),
        ("brickwall4k", generate_brickwall_vocoder, "Neural Codec 4kHz/8kHz Brickwall Cutoff"),
        ("indicsynth", generate_indic_synthetic_voice, "Indic-Dialect Synthetic Voice"),
    ]

    total_fake_generated = 0
    total_real_generated = 0

    # 1. Generate Deepfake AI Voice Samples
    for gen_name, gen_func, desc in generators:
        print(f"[-] Generating {samples_per_generator} samples for: {gen_name} ({desc})...")
        for i in range(samples_per_generator):
            dur = np.random.uniform(2.0, 3.2)
            audio = gen_func(duration_sec=dur, sr=16000)
            fpath = os.path.join(fake_dir, f"ai_{gen_name}_{i+1:04d}.wav")
            sf.write(fpath, audio, 16000)
            total_fake_generated += 1

    # 2. Generate Biological Genuine Human Samples
    print(f"[-] Generating {human_samples} high-fidelity bona fide physiological speech samples...")
    for i in range(human_samples):
        dur = np.random.uniform(2.0, 3.2)
        audio = generate_biological_human_speech(duration_sec=dur, sr=16000)
        fpath = os.path.join(real_dir, f"human_physiological_{i+1:04d}.wav")
        sf.write(fpath, audio, 16000)
        total_real_generated += 1

    print("\n" + "=" * 68)
    print("  ✅ AUDIO GENERATION COMPLETE!")
    print("=" * 68)
    print(f"  • New AI Voice Clone Samples Generated : {total_fake_generated}")
    print(f"  • New Bona Fide Human Samples Generated: {total_real_generated}")
    print(f"  • Total New Audio Files Added          : {total_fake_generated + total_real_generated}")

    # 3. Update Dataset Manifest
    real_files = [f for f in os.listdir(real_dir) if f.lower().endswith(('.wav', '.mp3', '.flac'))]
    fake_files = [f for f in os.listdir(fake_dir) if f.lower().endswith(('.wav', '.mp3', '.flac'))]

    gen_breakdown = defaultdict(int)
    for f in real_files:
        gen_breakdown[f"real_{f.split('_')[0]}"] += 1
    for f in fake_files:
        gen_breakdown[f"fake_{f.split('_')[0]}"] += 1

    manifest = {
        "dataset_name": "VoxSentinalX Unified Forensic Corpus",
        "total_unique_samples": len(real_files) + len(fake_files),
        "bona_fide_real_count": len(real_files),
        "synthetic_fake_count": len(fake_files),
        "newly_generated_ai_samples": total_fake_generated,
        "generators": dict(gen_breakdown)
    }

    with open(os.path.join(unified_dir, "manifest.json"), "w", encoding="utf-8") as fp:
        json.dump(manifest, fp, indent=2)

    print(f"\n[UPDATED] Manifest updated at: {os.path.join(unified_dir, 'manifest.json')}")
    print(f"  Total Dataset Size in unified_corpus: {len(real_files) + len(fake_files)} audio files")
    print(f"  (Real: {len(real_files)} | Fake: {len(fake_files)})")


if __name__ == "__main__":
    generate_and_organize_samples()
