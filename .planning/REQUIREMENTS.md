# Requirements: Humanization & Refactoring

## 1. Functional Invariance
- [ ] REQ-FUNC-1: Maintain full bidirectional WebSocket streaming at `/ws/analyze` (Int16 PCM streaming, circular buffer ingestion, 2.0s analysis window, 1.0s hop).
- [ ] REQ-FUNC-2: Preserve all 8 physical forensic vectors (Spectral, Prosody, Breathing, Vocoder, LFCC, Glottal LPC-NAQ, Jitter/Shimmer, Bispectrum QPC) and LCNN neural inference.
- [ ] REQ-FUNC-3: Maintain near-field speakerphone calibration and speaker separation functionality.
- [ ] REQ-FUNC-4: Maintain audio and video file upload analysis via `/api/analyze-file`.
- [ ] REQ-FUNC-5: Keep all training catalog and evaluation metric endpoints functioning.

## 2. Bug Fixes & Performance
- [ ] REQ-BUG-1: Fix breathing detector accumulation to advance by hop duration (`1.0s`) rather than full window duration (`2.0s`).
- [ ] REQ-BUG-2: Fix missing `json` import in `backend/app/api/routes.py`.
- [ ] REQ-BUG-3: Fix microphone audio feedback loop in `frontend/src/lib/audioCapture.ts` using a muted gain node.
- [ ] REQ-BUG-4: Replace wildcard CORS credentials with specific local origins and configurable environment settings.
- [ ] REQ-BUG-5: Optimize `BispectrumPhaseDetector` computation using NumPy vectorization to reduce synchronous loop blocking.
- [ ] REQ-BUG-6: Add upload size safeguard (25MB limit) to `/api/analyze-file` to prevent memory exhaustion.

## 3. Humanization & Code Quality
- [ ] REQ-QUAL-1: Remove obvious generic AI boilerplate comments ("This function performs...", "Note:", "Here we...").
- [ ] REQ-QUAL-2: Preserve official project name **VoxSentinalX** across configuration, UI, and docs.
- [ ] REQ-QUAL-3: Tone down unrealistic marketing hyperbole ("military-grade", "defense-grade shield") in favor of realistic engineering descriptions.
- [ ] REQ-QUAL-4: Align benchmark evaluation numbers across documentation, UI scenarios, and API routes.
- [ ] REQ-QUAL-5: Ensure consistent naming, clean error responses, and clean imports.

## 4. Verification & Testing
- [ ] REQ-TEST-1: All 20 unit tests in `tests/` pass with zero failures.
- [ ] REQ-TEST-2: Frontend compiles cleanly with `npm run build`.
- [ ] REQ-TEST-3: Add test coverage for fixed bug edge cases.
