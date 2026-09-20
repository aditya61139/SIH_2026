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
