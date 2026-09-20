# VoxSentinalX

AI-Powered Real-Time Voice Cloning Impersonation Detection & Prevention Suite.

## Overview
VoxSentinalX is an audio forensics platform engineered for the Smart India Hackathon (SIH Problem Statement ID: 26104). It combines deterministic bio-acoustic signal processing (8 forensic vectors examining vocal fold physiology, respiration cadence, pitch micro-tremors, vocoder filter cutoffs, and bispectral phase coupling) with deep neural representation learning (Light-CNN with MFM activation, BiLSTM, and self-attention pooling) to detect voice cloning attacks in real time.

## Key Goals for Current Milestone
- **Humanize the Codebase**: Eliminate repetitive, generic AI-generated comments and unrealistic marketing hyperbole; adopt clean, defensible engineering practices of a capable developer team.
- **Preserve Project Identity**: Maintain official project name `VoxSentinalX` across all layers.
- **Fix Known Technical Bugs**:
  - Resolve the breathing detector's hop accumulation bug (200% time dilation).
  - Fix missing `json` import in `routes.py`.
  - Fix browser speaker feedback loop in `audioCapture.ts`.
  - Fix wildcard CORS credential configuration in `main.py`.
  - Vectorize nested loops in `bispectrum_detector.py` for real-time responsiveness.
- **Preserve 100% Functionality**: Ensure zero regressions across WebSocket streaming, REST endpoints, file analysis, and frontend dashboards.
- **Maintain Full Test Coverage**: Ensure all pytest unit tests continue to pass seamlessly.
