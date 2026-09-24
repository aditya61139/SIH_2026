# Phase 07 Plan: Advanced Forensics Expansion (Multilingual Support, Replay Attack Detection & Interactive Timeline)

## Objective
Scale **VoxSentinalX** with three transformative capabilities to make it a world-class, production-ready speech security platform for SIH 2026:
1. **Multilingual & Indic Accent Forensic Profiler**: Language-aware phonetic & acoustic profiling across Indian language families (Indo-Aryan, Dravidian, English) to adapt forensic thresholds and catch cross-lingual accent voice clones without false positives on regional phonemes.
2. **Physical Replay Attack Detector**: Forensic detection of pre-recorded authentic voice playback through loudspeakers/phone speakers via acoustic reverberation decay ($RT_{60}$ dual-room mismatch), loudspeaker Total Harmonic Distortion (THD), and transducer cabinet coloration.
3. **Interactive Forensic Detection Timeline**: High-precision, scrubbable temporal risk trajectory with timestamped anomaly flags, threat category ribbons, synchronized audio/video seek, and live rolling call history.
4. **Additional High-Impact Additions**:
   - **VoIP / Cellular Codec Normalizer**: Prevents AMR-NB / G.711 / Opus compression artifacts from generating false synthetic vocoder alarms.
   - **Cryptographic Forensic Audit Exporter**: Generates verifiable PDF / JSON audit certificates with SHA-256 evidence seals.

---

## Architecture & Data Flow

```
                      ┌───────────────────────────────────────────────┐
                      │             INCOMING AUDIO STREAM             │
                      │         (16 kHz PCM / Live or File)           │
                      └───────────────────────┬───────────────────────┘
                                              │
                     ┌────────────────────────┴────────────────────────┐
                     ▼                                                 ▼
        ┌─────────────────────────┐                       ┌─────────────────────────┐
        │  CODEC NORMALIZER       │                       │  MULTILINGUAL PROFILER  │
        │  • AMR/G.711/Opus filter│                       │  • Formant band ratios  │
        │  • Compensates packet   │                       │  • Indic/Dravidian/Eng  │
        │    loss & jitter buffer │                       │  • Adaptive thresholds  │
        └────────────┬────────────┘                       └────────────┬────────────┘
                     │                                                 │
                     └────────────────────────┬────────────────────────┘
                                              ▼
                             ┌─────────────────────────────────┐
                             │    10-LAYER FORENSIC SUITE      │
                             │  • L1: STFT Phase & Flatness    │
                             │  • L2: Prosody & 8-12Hz Tremors │
                             │  • L3: Respiration Cadence      │
                             │  • L4: Vocoder Brickwall Cutoff │
                             │  • L5: ASVspoof LFCC (Δ+ΔΔ)     │
                             │  • L6: Glottal Flow LPC-NAQ     │
                             │  • L7: Jitter & Shimmer         │
                             │  • L8: Bispectrum Coupling      │
                             │  • L9: PyTorch / Ensemble LCNN  │
                             │  • L10: REPLAY ATTACK DETECTOR  │  <-- [NEW]
                             │    - Loudspeaker THD Distortion │
                             │    - Dual-Room RT60 Decay       │
                             │    - Transducer Peak Coloration │
                             └────────────────┬────────────────┘
                                              │
                                              ▼
                             ┌─────────────────────────────────┐
                             │   DYNAMIC FUSION & TIMELINE     │
                             │  • Sliding window trajectory    │
                             │  • Anomaly timestamp markers    │
                             │  • Category color ribbons       │
                             └────────────────┬────────────────┘
                                              │
                     ┌────────────────────────┴────────────────────────┐
                     ▼                                                 ▼
        ┌─────────────────────────┐                       ┌─────────────────────────┐
        │ INTERACTIVE UI TIMELINE │                       │ CRYPTOGRAPHIC AUDIT LOG │
        │ • Scrubbable waveform   │                       │ • SHA-256 evidence seal │
        │ • Synchronized playback │                       │ • Verifiable PDF export │
        │ • Live rolling history  │                       │ • Banking compliance    │
        └─────────────────────────┘                       └─────────────────────────┘
```

---

## Detailed Task Breakdown

### Task 1: Replay Attack Detector Backend (`replay_detector.py`)
- **File**: `backend/app/detectors/replay_detector.py`
- **Responsibilities**:
  1. **Loudspeaker Physical Non-Linearity & THD**:
     - Computes Total Harmonic Distortion (THD) and intermodulation products in the 800 Hz–4.5 kHz band where miniature mobile speakers clip.
  2. **Dual-Room Reverberation & RT60 Mismatch**:
     - Evaluates energy decay curve (EDC) using Schroeder reverse integration.
     - Detects double-slope decay curves characteristic of an acoustic space recorded in one room and replayed in another.
  3. **High-Frequency DAC & Playback Transducer Signature**:
     - Detects steep physical speaker rolloffs (<150 Hz and >14 kHz) and transient DAC electronic turn-on spikes preceding speech bursts.
  4. Returns quantitative metrics: `loudspeaker_thd_percent`, `rt60_decay_mismatch`, `transducer_spectral_peakiness`, `replay_probability`.

### Task 2: Multilingual Forensic Profiler & Adaptive Calibrator
- **File**: `backend/app/detectors/multilingual_profiler.py`
- **Responsibilities**:
  1. Analyzes vowel formant dispersion ($F_1, F_2, F_3$) and acoustic vowel space area (VSA).
  2. Profiles acoustic family: `indo_aryan` (Hindi, Marathi, Bengali, Punjabi), `dravidian` (Tamil, Telugu, Kannada, Malayalam), and `global_english` / `neutral`.
  3. Dynamically adjusts forensic thresholds:
     - Prevents Indic retroflex stops (`ṭ`, `ḍ`) from triggering false vocoder cutoff alerts.
     - Adapts natural pitch variance baselines for tonal and syllable-timed cadence.
     - Flags cross-lingual accent transfer artifacts common in multilingual zero-shot voice clones.

### Task 3: Engine Integration & Codec Normalization
- **Files**:
  - `backend/app/engine/fusion_scorer.py`
  - `backend/app/core/config.py`
  - `backend/app/api/routes.py`
- **Responsibilities**:
  1. Add `ReplayDetector` and `MultilingualProfiler` into `DetectionEngine`.
  2. Update `LayerScores` to include `replay_attack` and `language_profile`.
  3. Add VoIP / GSM cellular codec compensation filter to prevent AMR / G.711 compression from triggering false positive vocoder alarms.
  4. Update `/api/analyze-file` and WebSocket `/ws/analyze` to return full timestamped replay metrics, language profile, and timeline events.

### Task 4: Interactive Detection Timeline Component
- **File**: `frontend/src/components/DetectionTimeline.tsx` [NEW]
- **Responsibilities**:
  1. **Scrubbable Visual Waveform & Threat Ribbon**:
     - Color-coded temporal ribbon (India Green = Genuine, Amber = Suspicious, Red = AI Voice Clone, Purple = Replay Attack).
     - Synchronized playhead tracking with active audio/video playback.
  2. **Pinpointed Timestamp Markers**:
     - Flag icons showing exact moments anomalies were detected (e.g. `00:04.2s Loudspeaker THD 14.8%`, `00:12.6s Missing Respiration`, `00:18.4s Phase Discontinuity`).
  3. **Interactive Inspection**:
     - Clicking any point on the timeline jumps playback to that second and updates the forensic radar and diagnostic cards to reflect that exact window.
  4. **Live Call Monitor Integration**:
     - Provides a rolling 60-second real-time timeline for the active live call so users can see when threat spikes occurred during the call.

### Task 5: Cryptographic Forensic Audit Certificate & PDF Exporter
- **Files**:
  - `backend/app/engine/audit_generator.py` [NEW]
  - `frontend/src/components/FileAnalyzer.tsx`
  - `frontend/src/components/AlertOverlay.tsx`
- **Responsibilities**:
  1. Generates cryptographic SHA-256 evidence hash of analyzed recording + ISO-8601 timestamp + detector telemetry.
  2. Provides one-click downloadable verifiable Forensic Audit Report (printable PDF / JSON) formatted for financial fraud investigation, cyber cell filing, and bank dispute resolution.

### Task 6: Unit & Integration Test Suite
- **Files**:
  - `tests/test_replay_detector.py` [NEW]
  - `tests/test_multilingual_profiler.py` [NEW]
  - `tests/test_timeline_integration.py` [NEW]
- **Responsibilities**:
  1. Test replay detector against synthetic clean vs loudspeaker-distorted audio.
  2. Test multilingual profiler across Indic and English vowel formant fixtures.
  3. Verify timeline serialization and ensure 100% of test suite passes without regressions.
