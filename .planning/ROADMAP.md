# Project Roadmap: Humanization & Refactoring

## Phase 1: Audit & Baseline Verification [COMPLETED]
- Comprehensive repository audit across backend, frontend, training, and tests.
- Baselined existing test suite: 20/20 pytest tests passing in 40.68s.
- Created architectural codebase map in `.planning/codebase/`.
- Authored initial project contracts (`PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`).

## Phase 2: Backend Core & Detection Pipeline Refactoring [COMPLETED]
- Fixed `breathing_detector.py` continuous speech hop accumulation bug.
- Fixed missing `json` import and added 25MB file upload safeguard in `routes.py`.
- Fixed CORS wildcard credentials in `main.py` and `config.py`.
- Optimized `bispectrum_detector.py` with NumPy vectorization (dropped test execution from 40.7s to 7.1s).
- Smoothed frame duration fallback in `speaker_separator.py`.
- Grounded diagnostic messages in `diagnostic_generator.py`.

## Phase 3: Frontend Refactoring & Humanization [COMPLETED]
- Fixed speaker screech / microphone feedback loop in `audioCapture.ts` using zero-gain nodes.
- Toned down exaggerated claims in `LandingView.tsx` to realistic, technically defensible engineering copy.
- Grounded benchmark metrics to evaluated numbers (86.3% accuracy, 6.86% EER).
- Verified project name **VoxSentinalX** across `Navbar.tsx` and UI headers.

## Phase 4: Documentation & Developer Experience [COMPLETED]
- Rewrote `README.md` to read like a polished student/developer engineering hackathon project.
- Updated `run_tests.bat` to reflect accurate 20+ test suite count.

## Phase 5: Verification & Testing [COMPLETED]
- Added unit tests for `/api/training/metrics` and 25MB upload limit.
- Verified test suite: 22/22 pytest tests passing in 7.14s.
- Verified frontend build (`npm run build`): 1,595 modules transformed with zero errors.

## Phase 6: Swadesi & Patriotic UI Overhaul [COMPLETED]
- Replaced dark cyberpunk styling with official Swadesi / Made in Bharat palette:
  - Page Background `#FDFBF7`, Secondary `#F8F5EF`, Cards `#FFFFFF`.
  - Primary Headings `#1E293B`, Secondary Text `#64748B`, Disabled `#94A3B8`.
  - Primary Buttons & Active Tabs `#C2410C`, Button Hover `#9A3412`, Active Pill `#FFF1E8`.
  - Waveforms: Active `#C2410C`, Inactive `#94A3B8`, Verified `#15803D`.
  - Verification & Backend Connected `#15803D`, Suspicious `#D97706`, Critical Alert `#DC2626`.
  - Borders `#E7E2DA`, Dividers `#ECE8E1`.
- Dignified Tiranga micro-stripe accents and SIH 2026 Smart India Hackathon emblem.
- High-appeal, clean, uncluttered components across Navbar, Hero Visualizer, Live Call Monitor, Radar, Risk Gauge, and Modals.
- Production build and automated test verification.

## Phase 7: Advanced Forensics Expansion (Multilingual, Replay Attack & Interactive Timeline) [COMPLETED]
- **Multilingual Forensic Support**: Formant space & phoneme tracking across Indian language families (Indo-Aryan, Dravidian, English) with adaptive threshold calibration.
- **Physical Replay Attack Detection**: Detects genuine voice playback through loudspeakers via Total Harmonic Distortion (THD), dual-room reverberation ($RT_{60}$ decay mismatch), and transducer coloration.
- **Interactive Detection Timeline**: Scrubbable temporal risk trajectory with timestamped event pins, threat ribbons, and live rolling call history.
- **VoIP / Cellular Codec Normalization**: Compensates for standard GSM/AMR/Opus compression to eliminate false positive vocoder alarms.
- **Cryptographic Forensic Audit Exporter**: Generates verifiable PDF/JSON compliance certificates with SHA-256 evidence seals.

## Phase 8: Robust Loudspeaker Replay Calibration & Model Training [COMPLETED]
- **Acoustic Physics Re-Engineering**: Replaced naive formant-harmonic THD with frame-based short-term autocorrelation Harmonics-to-Noise Ratio (HNR) (Praat formulation) and pitch-conditioned intermodulation distortion.
- **Pitch-Conditioned Sub-Bass Analysis**: Eliminated false transducer coloration penalties for high/elevated pitch speech ($F_0 > 145\text{ Hz}$).
- **Pre-Speech Plosive Gating**: Gated DAC transient detection strictly to silent intervals ($< 15\%$ peak RMS) to prevent loud speech plosives from triggering false DAC pops.
- **Dual-Evidence Co-Occurrence**: Enforced simultaneous acoustic room decay ($RT_{60} > 1.45$) mismatch and physical transducer distortion to flag replay attacks.
- **Model Training on Loud Voice vs Replay**: Augmented dataset generator with loud authentic human speech (Lombard effect, elevated pitch, formant resonance) and physical loudspeaker replay samples, calibrated thresholds to 0.65 across backend and frontend, and verified with 32/32 tests passing.

## Phase 9: System-Wide 10-Vector Forensic Integration & Live Monitor Layout Alignment [COMPLETED]
- **10-Vector Architecture Alignment**: Elevated platform from 8-vector to 10-vector architecture across frontend types (`LayerScores`), Bento Grid matrix (10 cards across 5 columns $\times$ 2 rows), threat simulation scenarios (`neural_lcnn` and `replay` added + dedicated *Physical Loudspeaker Replay* scenario), training scripts, docstrings, and documentation.
- **Live Call Monitor Cockpit Realignment**: Restructured `LiveCallMonitor.tsx` into a balanced 3-Tier Cockpit Layout:
  - **Tier 1 (Cockpit Monitoring Bar)**: `Live Audio Telemetry & Oscilloscope` (6 cols) + `10-Axis Forensic Radar` (3 cols) + `Risk Score Gauge` (3 cols) with uniform horizontal heights.
  - **Tier 2 (Deep Forensics & Diagnostics)**: `10-Vector Forensic Decomposition` (7 cols, 5 cols $\times$ 2 rows) adjacent to `Diagnostic Forensics Feed` (5 cols, scroll-capped container), completely eliminating the blank space on the left.
  - **Tier 3 (Historical Timeline)**: Full-width `Forensic Detection Timeline` sitting directly below Tier 2 without being pushed down the page.
- **Training Pipeline & Automated Verification**: Updated `extract_forensic_features` to compute Vector 9 (Replay HNR / sub-bass) and Vector 10 (Multilingual formant / rhythm), added unit tests for 10-vector completeness, and verified full test suite and frontend build.


