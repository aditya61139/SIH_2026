# 📊 VoxSentinalX Training Dataset & Sample Inventory

> **Generated:** 2026-09-11 15:23:53  
> **Total Samples:** 5,497 audio files  
> **Total Audio Duration:** 9.54 hours (34,329.1 seconds)  
> **Total Corpus Disk Size:** 1442.52 MB  

---

## ⚖️ Class Distribution

| Class | Label ID | Audio Sample Count | Percentage |
| :--- | :--- | :--- | :--- |
| **Bona Fide Human Speech (Real)** | `0` | **2,577** | 46.9% |
| **Synthetic AI Voice Clones (Fake)** | `1` | **2,920** | 53.1% |

---

## 🧬 Generator & Model Breakdown

| Generator / Model Category | Target Class | Discovered Samples | Architecture Description |
| :--- | :--- | :--- | :--- |
| `brickwall4k` | ⚠️ Deepfake | **50** | FAKE acoustic training partition |
| `diffusion` | ⚠️ Deepfake | **50** | FAKE acoustic training partition |
| `flashspeech` | ⚠️ Deepfake | **118** | FAKE acoustic training partition |
| `griffinlim` | ⚠️ Deepfake | **50** | FAKE acoustic training partition |
| `hifigan` | ⚠️ Deepfake | **50** | FAKE acoustic training partition |
| `indicsynth` | ⚠️ Deepfake | **50** | FAKE acoustic training partition |
| `local` | ⚠️ Deepfake | **447** | FAKE acoustic training partition |
| `naturalspeech3` | ⚠️ Deepfake | **32** | FAKE acoustic training partition |
| `openai` | ⚠️ Deepfake | **600** | FAKE acoustic training partition |
| `prompttts2` | ⚠️ Deepfake | **25** | FAKE acoustic training partition |
| `seedtts` | ⚠️ Deepfake | **599** | FAKE acoustic training partition |
| `valle` | ⚠️ Deepfake | **95** | FAKE acoustic training partition |
| `voicebox` | ⚠️ Deepfake | **104** | FAKE acoustic training partition |
| `xtts` | ⚠️ Deepfake | **600** | FAKE acoustic training partition |
| `zeroshot` | ⚠️ Deepfake | **50** | FAKE acoustic training partition |
| `local` | ✅ Human | **103** | REAL acoustic training partition |
| `physiological` | ✅ Human | **200** | REAL acoustic training partition |
| `samples` | ✅ Human | **2,274** | REAL acoustic training partition |

---

## 📋 First 25 Training Samples Preview

| # | File Name | Class | Generator | Duration | Sample Rate | Size | Hash (SHA256) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `human_physiological_0001.wav` | `real` | `physiological` | 2.79s | 16000 Hz | 89,432 B | `c705532d5a8cc451...` |
| 2 | `human_physiological_0002.wav` | `real` | `physiological` | 2.8s | 16000 Hz | 89,562 B | `c47a822e0c712637...` |
| 3 | `human_physiological_0003.wav` | `real` | `physiological` | 2.55s | 16000 Hz | 81,530 B | `ef636ec49174fe5f...` |
| 4 | `human_physiological_0004.wav` | `real` | `physiological` | 3.02s | 16000 Hz | 96,616 B | `72f01b99ec9ab307...` |
| 5 | `human_physiological_0005.wav` | `real` | `physiological` | 2.87s | 16000 Hz | 91,934 B | `83c3fe2835920513...` |
| 6 | `human_physiological_0006.wav` | `real` | `physiological` | 2.82s | 16000 Hz | 90,252 B | `3e09d2dac834cac1...` |
| 7 | `human_physiological_0007.wav` | `real` | `physiological` | 2.73s | 16000 Hz | 87,454 B | `a9d574e4863bd76b...` |
| 8 | `human_physiological_0008.wav` | `real` | `physiological` | 3.09s | 16000 Hz | 98,828 B | `8884b51110caa87f...` |
| 9 | `human_physiological_0009.wav` | `real` | `physiological` | 2.85s | 16000 Hz | 91,098 B | `9cfe280b6f8d2095...` |
| 10 | `human_physiological_0010.wav` | `real` | `physiological` | 2.85s | 16000 Hz | 91,334 B | `86975d46d2084d43...` |
| 11 | `human_physiological_0011.wav` | `real` | `physiological` | 2.3s | 16000 Hz | 73,588 B | `178fa16d7ba034a3...` |
| 12 | `human_physiological_0012.wav` | `real` | `physiological` | 2.28s | 16000 Hz | 73,074 B | `9534470b0a1dfba9...` |
| 13 | `human_physiological_0013.wav` | `real` | `physiological` | 3.08s | 16000 Hz | 98,556 B | `2e6387bf9139ad4a...` |
| 14 | `human_physiological_0014.wav` | `real` | `physiological` | 2.97s | 16000 Hz | 95,226 B | `3325659c4e9d11c0...` |
| 15 | `human_physiological_0015.wav` | `real` | `physiological` | 2.39s | 16000 Hz | 76,608 B | `b7132c023795a346...` |
| 16 | `human_physiological_0016.wav` | `real` | `physiological` | 2.81s | 16000 Hz | 89,968 B | `fb06cec213877a23...` |
| 17 | `human_physiological_0017.wav` | `real` | `physiological` | 2.82s | 16000 Hz | 90,224 B | `4284f780b2773659...` |
| 18 | `human_physiological_0018.wav` | `real` | `physiological` | 2.99s | 16000 Hz | 95,778 B | `919afe0c8aeed9be...` |
| 19 | `human_physiological_0019.wav` | `real` | `physiological` | 2.16s | 16000 Hz | 69,252 B | `7dc30761f7bb1445...` |
| 20 | `human_physiological_0020.wav` | `real` | `physiological` | 2.72s | 16000 Hz | 87,130 B | `f874c3a05ed1a648...` |
| 21 | `human_physiological_0021.wav` | `real` | `physiological` | 2.5s | 16000 Hz | 79,956 B | `b73414f21978adb8...` |
| 22 | `human_physiological_0022.wav` | `real` | `physiological` | 2.86s | 16000 Hz | 91,502 B | `2168d2d09a79ff4d...` |
| 23 | `human_physiological_0023.wav` | `real` | `physiological` | 2.53s | 16000 Hz | 81,150 B | `ba570e8283dad92d...` |
| 24 | `human_physiological_0024.wav` | `real` | `physiological` | 2.02s | 16000 Hz | 64,680 B | `e0c01bdec92173b1...` |
| 25 | `human_physiological_0025.wav` | `real` | `physiological` | 3.19s | 16000 Hz | 102,114 B | `c9f601c620bb09f9...` |

*...and 5,472 more samples cataloged in `trained_samples_inventory.csv` and `trained_samples_inventory.json`.*
