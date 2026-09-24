# Phase 09 Plan: 10-Vector Forensic Integration & Live Monitor Layout Alignment

## Executive Summary
This phase addresses two interconnected goals:
1. **10-Vector Forensic Suite Integration**: Fully elevate VoxSentinalX from its previous 8-vector nomenclature to the full 10-vector operational architecture (incorporating Vector 9: Deep Neural LCNN-BiLSTM and Vector 10: Physical Loudspeaker Replay Forensics) across backend, frontend bento matrix, threat simulation scenarios, training pipelines, and documentation.
2. **Live Call Monitor Cockpit Layout Re-Architecture**: Resolve the visual misalignment where `Diagnostic Forensics Feed` in the right column expands downwards, pushing `Forensic Detection Timeline` far down and leaving a massive empty gap on the left.

---

## Technical Scope & Components

### 1. Live Call Monitor Cockpit Re-Architecture (`LiveCallMonitor.tsx`)
- **Root Cause**: The current layout places `Oscilloscope` + `Decomposition` on the left (height ~550px), while stacking `RiskGauge` + `Radar` + `DiagnosticFeed` on the right (height ~1140px). Because `Timeline` is placed outside below both columns, a 590px blank void is left on the left of `DiagnosticFeed`, pushing the timeline down.
- **New 3-Tier Cockpit Layout**:
  - **Tier 1 (Top Real-Time Telemetry Bar, 12 cols)**:
    - `Live Audio Telemetry & Oscilloscope` (`md:col-span-6`)
    - `10-Axis Forensic Radar` (`md:col-span-3`)
    - `Risk Score Gauge` (`md:col-span-3`)
    - *Result*: All three cards share a uniform height (~250-260px), creating a visually balanced top cockpit bar.
  - **Tier 2 (Forensic Deep Dive & Granular Diagnostics, 12 cols)**:
    - Left (`lg:col-span-7`): `10-Vector Forensic Decomposition` (L1 to L10 rendered symmetrically in 5 columns $\times$ 2 rows) + Channel Diarization & Linguistic Accent footer.
    - Right (`lg:col-span-5`): `Diagnostic Forensics Feed` with scrollable anomaly container (`max-h-[380px] overflow-y-auto pr-1`).
    - *Result*: Both sides sit directly adjacent at matched heights. **Zero blank space on the left of Diagnostic Feed.**
  - **Tier 3 (Historical Timeline, 12 cols)**:
    - Full-width `Forensic Detection Timeline` sitting immediately below Tier 2, unhindered and scrubbable across the entire width.

### 2. 10-Vector Forensic UI & Frontend Alignment
- **`frontend/src/types/index.ts`**: Make `replay_attack: number` non-optional in `LayerScores`.
- **`frontend/src/components/LandingView.tsx`**:
  - Expand `scenarios` from 8 vectors to 10 vectors (`neural_lcnn` and `replay`).
  - Add 4th scenario: `replay_loudspeaker` (*Physical Loudspeaker Replay Attack*).
  - Expand `forensicCards` from 8 to 10 cards:
    - Layer 9: Deep Neural LCNN & Attention (MFM-BiLSTM Net).
    - Layer 10: Physical Loudspeaker Replay Detection.
  - Adjust grid to `lg:grid-cols-5` (2 symmetric rows of 5 cards).
  - Update all section titles and telemetry headers from 8-Vector to 10-Vector.
- **`frontend/src/components/ModelTrainingSuite.tsx`**, **`App.tsx`**, **`index.html`**:
  - Update badges and metadata to "10-Vector Forensic Suite".

### 3. Backend & Training Pipeline Alignment
- **`backend/app/core/config.py`**, **`fusion_scorer.py`**, **`routes.py`**:
  - Update module docstrings and ensure clean 10-vector dictionary formatting.
- **`training/train_acoustic_ensemble.py` & `training/train.py`**:
  - Update feature extraction pipeline to compute physical replay features (autocorrelation HNR peak, sub-150Hz energy) and multilingual/regional Indian acoustic proxies (formant dispersion, nPVI rhythm).
  - Update training logs to "10-Vector Forensic & Neural Ensemble Training".

### 4. Verification & Testing
- Unit tests in `tests/test_fusion_scorer.py` asserting all 10 vectors are present in `layer_scores`.
- Run full backend test suite (`python -m pytest tests/ -v`).
- Run frontend production build (`npm run build` in `frontend/`).
