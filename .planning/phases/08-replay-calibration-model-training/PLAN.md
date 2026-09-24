# Phase 08 Plan: Robust Loudspeaker Replay Calibration & Model Training

## Objective
Eliminate false positive "Loudspeaker Replay Attack" triggers when users speak loudly or close to the microphone, by replacing naive formant-harmonic THD estimation with true psychoacoustic Harmonics-to-Noise Ratio (HNR) and pitch-conditioned intermodulation distortion, gating DAC transient detection to pre-speech silence, enforcing multi-evidence co-occurrence, and training the forensic model on loud authentic speech vs. physical loudspeaker replay profiles.

---

## Root Cause Analysis (Why Loud Speech Triggers Replay)
1. **Formant-Harmonic Confusion in `_compute_loudspeaker_thd`**:
   - The original code searched for a "fundamental" in 400–1200 Hz and checked multiples ($2\times, 3\times$).
   - Human speech fundamental pitch $F_0$ is 85–255 Hz; 400–1200 Hz contains the first vocal tract formant ($F_1$). Multiples ($2\times, 3\times$) coincide directly with higher formants ($F_2, F_3$).
   - Speaking loudly naturally boosts higher formant resonance and glottal harmonic energy, causing the formula to compute 80–100% false "THD".
2. **Pitch-Agnostic Sub-Bass Cutoff**:
   - The code checked for energy below 150 Hz. In female, child, or loud elevated-pitch speech, $F_0 > 180\text{ Hz}$, meaning there is naturally zero energy below 150 Hz. This falsely penalizes authentic high/loud pitch voices.
3. **Plosive Speech Falsely Flagged as DAC Switching**:
   - Loud speech produces strong unvoiced plosive bursts (/p/, /t/, /k/) with high sample-to-sample difference (`np.diff`), falsely triggering DAC electronic switching pops.
4. **Isolated Metric Elevation Without Physical Co-Occurrence**:
   - An isolated score of 0.55 triggered an immediate global `REPLAY_ATTACK_DETECTED` verdict and purple UI alert banners without verifying room reverberation decay or acoustic enclosure reflections.

---

## Technical Architecture & Implementation Strategy

```
                          ┌──────────────────────────────────────────────┐
                          │            INCOMING AUDIO WINDOW             │
                          │          (Loud or Conversational PCM)        │
                          └───────────────────────┬──────────────────────┘
                                                  │
                         ┌────────────────────────┴────────────────────────┐
                         ▼                                                 ▼
            ┌─────────────────────────┐                       ┌─────────────────────────┐
            │ AUTOCORRELATION F0 &    │                       │ PRE-SPEECH ONSET GATING │
            │ DYNAMIC RANGE ESTIMATOR │                       │ • Detects silence floor │
            │ • True pitch 80-350 Hz  │                       │ • Gated DAC transient   │
            │ • Vocal intensity / RMS │                       │   detection only during │
            │ • Whitelists loud voice │                       │   inter-speech pauses   │
            └────────────┬────────────┘                       └────────────┬────────────┘
                         │                                                 │
                         └────────────────────────┬────────────────────────┘
                                                  │
                                                  ▼
                         ┌─────────────────────────────────────────────────┐
                         │      RE-ENGINEERED REPLAY DETECTOR V2           │
                         │ 1. Harmonics-to-Noise Ratio (HNR):              │
                         │    • Loud speech = Clean high HNR (>22 dB)      │
                         │    • Replay speaker = Degraded HNR & IMD spurs  │
                         │ 2. Pitch-Conditioned Sub-Bass Analysis:         │
                         │    • Only checks <150 Hz if F0 < 150 Hz         │
                         │ 3. Schroeder Dual-Slope Reverberation:          │
                         │    • Genuine loud speech = 1 room decay         │
                         │    • Replay = Dual-slope EDC (2 physical rooms) │
                         │ 4. Multi-Evidence Co-Occurrence Gate:           │
                         │    • Replay requires BOTH acoustic mismatch     │
                         │      AND physical transducer distortion         │
                         └────────────────────────┬────────────────────────┘
                                                  │
                         ┌────────────────────────┴────────────────────────┐
                         ▼                                                 ▼
            ┌─────────────────────────┐                       ┌─────────────────────────┐
            │ MODEL DATASET SYNTHESIS │                       │ FUSION & UI THRESHOLD   │
            │ • Add loud human voice  │                       │ • Calibrate threshold   │
            │   samples to generator  │                       │   to 0.72 (require dual │
            │ • Add physical speaker  │                       │   evidence co-occurrence│
            │   replay distortions    │                       │ • Update live monitor & │
            │ • Train classifier      │                       │   file analyzer banners │
            └─────────────────────────┘                       └─────────────────────────┘
```

---

## Detailed Tasks

### Task 1: Re-engineer Replay Detector (`replay_detector.py`)
- Implement autocorrelation pitch estimator ($F_0$ in 80–350 Hz).
- Replace naive peak-harmonic THD with **Harmonics-to-Noise Ratio (HNR)** and **Intermodulation Distortion (IMD)**:
  - Genuine loud speech has high HNR (>20 dB) with natural glottal tilt (-12 to -6 dB/octave).
  - Loudspeaker playback introduces spurious inter-harmonic energy and power compression, dropping HNR in the 1–4 kHz band.
- Make sub-bass cutoff check pitch-aware:
  - If $F_0 \ge 150\text{ Hz}$, bypass or normalize the sub-bass cutoff check.
- Gate DAC transient pop detector so it only runs during silence/unvoiced pauses (< -32 dBFS RMS), ignoring plosives in active loud speech.
- Enforce **Dual-Evidence Co-Occurrence**:
  - Replay probability is high ONLY when acoustic room decay mismatch ($RT_{60}$) AND physical transducer coloration/distortion co-occur.

### Task 2: Update Fusion Scorer & Route Verdicts (`fusion_scorer.py`, `routes.py`)
- Tune `REPLAY_PROBABILITY_THRESHOLD` from 0.55 to 0.70 (or requiring co-occurrence confirmation).
- In `analyze_window`, check if audio is high-energy near-field speech:
  - Check near-field vocal energy and suppress false replay flags when reverberation decay indicates authentic near-field speech.
- Update `routes.py` and `websocket_handler.py` with the calibrated logic.

### Task 3: Dataset Augmentation & Model Training (`dataset_generator.py`, `train_acoustic_ensemble.py`)
- Add `generate_loud_genuine_speech_sample(...)` in `dataset_generator.py`:
  - Simulates high vocal effort, elevated pitch ($F_0 + 30\text{ Hz}$), strong vocal tract resonance, high HNR, and near-field proximity.
- Add `generate_physical_loudspeaker_replayed_sample(...)` in `dataset_generator.py`:
  - Simulates non-linear speaker power compression, transducer cabinet rolloff, and dual-room acoustic reverberation.
- Train the acoustic classifier / neural model to recognize and distinguish loud speech from loudspeaker replay.
- Save evaluation metrics verifying < 1% false alarm rate on loud speech.

### Task 4: Unit Testing & Verification
- Add comprehensive test fixtures in `tests/test_replay_detector.py`:
  - `test_loud_genuine_speech_does_not_trigger_replay()`: Tests loud synthetic speech with varying volumes and pitches.
  - `test_female_high_pitch_does_not_trigger_coloration()`: Tests pitch > 200 Hz.
  - `test_actual_loudspeaker_replay_detected()`: Verifies real replayed audio with dual-room decay and IMD is accurately flagged.
- Run `python -m pytest tests/ -v` to ensure 100% pass across all tests.
- Run `npm run build` in `frontend/` to ensure frontend integrity.
