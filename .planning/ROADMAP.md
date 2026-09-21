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
