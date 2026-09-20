# 📁 VoxSentinalX Repository Structure & File Directory Layout

> **Project Name:** VoxSentinalX  
> **Problem Statement ID:** SIH 26104 (*AI-Powered Real-Time Detection and Prevention of Voice Cloning Impersonation Attacks*)  
> **Version:** 2.0.0  
> **Repository Path:** `p:\VoxSentinalX`  

---

## 1. Exhaustive Repository Directory Tree

Below is the complete filesystem layout of the VoxSentinalX repository (excluding transient directories such as `.git`, `.venv`, and `node_modules`):

```text
p:\VoxSentinalX\
├── .gitignore                                    # Git exclusion rules for artifacts, virtual environments, caches
├── README.md                                     # Core project overview, quickstart guide, test documentation
├── VoxSentinalX_SIH_Project_Dossier.pdf          # Official Smart India Hackathon submission technical dossier
├── run_all.bat                                   # One-click dual-launcher for Windows (FastAPI backend + React frontend)
├── run_tests.bat                                 # Windows batch runner for automated pytest test suite
├── start_backend.bat                             # Windows batch runner to start the FastAPI backend on port 8000
├── start_frontend.bat                            # Windows batch runner to start the React/Vite frontend on port 3000
│
├── .planning/                                    # Planning and architecture specifications directory
│   └── codebase/                                 # Codebase map and system architecture documentation
│       ├── ARCHITECTURE.md                       # Comprehensive system architecture & technical specification
│       └── STRUCTURE.md                          # Exhaustive repository structure & directory layout map
│
├── backend/                                      # Python FastAPI backend server & signal processing engine
│   ├── requirements.txt                          # Python package dependency specifications
│   ├── run.py                                    # Uvicorn entry point runner for backend on port 8000
│   └── app/                                      # Core application package
│       ├── __init__.py                           # App package initializer
│       ├── main.py                               # FastAPI application root, CORS configuration, router mounting
│       ├── api/                                  # API transport layer & route definitions
│       │   ├── __init__.py
│       │   ├── routes.py                         # REST endpoints: file upload, health, config, calibration, training
│       │   └── websocket_handler.py              # Full-duplex WebSocket stream handler (/ws/analyze)
│       ├── audio/                                # Low-level audio DSP, buffers, and acoustic isolation
│       │   ├── __init__.py
│       │   ├── preprocessor.py                   # PCM conversion, amplitude normalization, RMS energy, silence check
│       │   ├── speaker_separator.py              # Voiceprint calibration & near-field speakerphone audio isolation
│       │   └── stream_buffer.py                  # Circular 10s ring buffer & 2.0s/1.0s sliding window manager
│       ├── core/                                 # Core settings and configuration
│       │   ├── __init__.py
│       │   └── config.py                         # Pydantic Settings: sample rates, thresholds, weights, EMA alpha
│       ├── detectors/                            # 8-Vector forensic decomposition suite & neural inference
│       │   ├── __init__.py
│       │   ├── base.py                           # Abstract Base Class (BaseDetector) interface contract
│       │   ├── spectral_detector.py              # Layer 1: Spectral flatness, phase coherence, HNR, HF energy ratio
│       │   ├── prosody_detector.py               # Layer 2: Pitch (F0) tracking, pitch std dev, 8-12 Hz micro-tremors
│       │   ├── breathing_detector.py             # Layer 3: Respiration events, continuous speech without pause counter
│       │   ├── acoustic_artifacts.py             # Layer 4: Brickwall cutoff filter detection, spectral decay tilt
│       │   ├── lfcc_detector.py                  # Layer 5: ASVspoof 24-filter linear cepstral coefficients (Δ + ΔΔ)
│       │   ├── glottal_detector.py               # Layer 6: LPC order-16 inverse filtering, NAQ, residual kurtosis
│       │   ├── perturbation_detector.py          # Layer 7: Laryngeal cycle perturbation (Jitter local/RAP, Shimmer APQ3)
│       │   ├── bispectrum_detector.py            # Layer 8: 2D Bispectrum, bicoherence, Quadratic Phase Coupling (QPC)
│       │   └── neural_lcnn_detector.py           # Layer 9: Deep neural LCNN-BiLSTM-Attention inference
│       ├── engine/                               # Score aggregation and diagnostic reporting
│       │   ├── __init__.py
│       │   ├── fusion_scorer.py                  # DetectionEngine orchestrator, weighted fusion, EMA, spike detection
│       │   └── diagnostic_generator.py           # Rule-based generator for human-readable diagnostics & countermeasures
│       └── models/                               # Neural network architectures, checkpoints, and benchmark metrics
│           ├── __init__.py
│           ├── lcnn_architecture.py              # PyTorch LCNN with Max-Feature-Map (MFM), BiLSTM, Self-Attention
│           ├── model_metrics.json                # Serialized evaluation metrics (86.27% Acc, 6.86% EER, 87.63% F1)
│           ├── pretrained_weights.pt             # PyTorch trained state dictionary checkpoint
│           ├── ensemble_weights.npz              # NumPy-optimized serialized weights for forensic ensemble
│           └── archive_weights.pt                # Backup model weight checkpoint
│
├── frontend/                                     # React 18 + Vite 5 + TypeScript + TailwindCSS user interface
│   ├── index.html                                # HTML5 root document and mount container
│   ├── package.json                              # Node.js dependencies, scripts, and build configuration
│   ├── package-lock.json                         # Exact dependency lockfile
│   ├── postcss.config.js                         # PostCSS configuration for TailwindCSS
│   ├── tailwind.config.js                        # Tailwind CSS theme configuration (custom cyber colors & animations)
│   ├── tsconfig.json                             # TypeScript compiler configuration
│   ├── vite.config.ts                            # Vite build tool and development server configuration (port 3000)
│   └── src/                                      # React application source code
│       ├── main.tsx                              # React DOM root entry point
│       ├── App.tsx                               # Primary stateful application controller & tab navigation
│       ├── index.css                             # Global stylesheet, custom glassmorphic utilities, glow effects
│       ├── types/                                # TypeScript type definitions
│       │   └── index.ts                          # Shared data contracts (RiskLevel, AnalysisUpdate, FileAnalysisReport)
│       ├── lib/                                  # Client-side audio processing & canvas utilities
│       │   ├── audioCapture.ts                   # Web Audio API engine, ScriptProcessorNode, WebSocket stream controller
│       │   └── audioVisualizer.ts                # HTML5 Canvas 60 FPS oscilloscope & frequency spectrum renderer
│       └── components/                           # Modular React UI components
│           ├── AlertOverlay.tsx                  # Full-screen emergency modal triggered upon critical spoof or swap
│           ├── CalibrationModal.tsx              # Voiceprint recording modal for near-field acoustic calibration
│           ├── DiagnosticFeed.tsx                # Forensic telemetry cards, measured metrics, and security guidance
│           ├── FileAnalyzer.tsx                  # Drag-and-drop file/video analyzer with synchronized video playback
│           ├── ForensicRadar.tsx                 # 8-Axis dynamic SVG radar polygon visualizer
│           ├── LandingView.tsx                   # Showcase overview, interactive waveform hero, threat sandbox
│           ├── LiveCallMonitor.tsx               # Real-time call monitoring dashboard with oscilloscope & radar
│           ├── ModelTrainingSuite.tsx            # Dataset inventory manager, training trigger, benchmark dashboard
│           ├── Navbar.tsx                        # Application header, tab navigation, connectivity badge, theme toggle
│           ├── RiskGauge.tsx                     # 270-degree animated SVG radial gauge with risk badge
│           ├── SettingsPanel.tsx                 # WebSocket/REST API configuration and sensitivity settings
│           └── WaveformHeroVisualizer.tsx        # Cybernetic multi-band frequency waveform visualizer on landing page
│
├── training/                                     # Model training, dataset generation, harvesting, and evaluation
│   ├── __init__.py
│   ├── dataset.py                                # PyTorch Dataset with SpecAugment, noise injection, and multi-generator loader
│   ├── dataset_generator.py                      # Local synthetic/genuine speech audio generator
│   ├── download_datasets.py                      # Hugging Face Parquet dataset harvester & unified corpus integrator
│   ├── evaluate.py                               # Comprehensive evaluation script: EER sweep, confusion matrix, per-generator stats
│   ├── export_onnx.py                            # ONNX Runtime exporter with dynamic batch and time dimensions
│   ├── generate_advanced_ai_voices.py            # Advanced AI voice simulator (HiFi-GAN, Diffusion, Zero-Shot, Indic)
│   ├── generate_sample_inventory.py              # Automated dataset inventory scanner generating markdown and CSV indices
│   ├── pretrain_weights.py                       # Checkpoint initialization script
│   ├── train.py                                  # PyTorch training pipeline with CUDA AMP Mixed Precision & Focal Loss
│   └── train_acoustic_ensemble.py                # High-throughput NumPy 8-vector ensemble trainer (32-dim features)
│
├── tests/                                        # Automated pytest test suite (100% pass rate across 20 test cases)
│   ├── test_audio_buffer.py                      # Tests for Int16/Float32 conversion, ring buffer capacity, sliding window hops
│   ├── test_detectors.py                         # Tests for Layer 1-4 detectors (spectral, prosody, breathing, vocoder)
│   ├── test_new_detectors.py                     # Tests for Layer 5-8 detectors (LFCC, glottal, perturbation, bispectrum)
│   ├── test_neural_inference.py                  # Tests for LCNN model forward pass and spoof probability output
│   ├── test_fusion_scorer.py                     # Tests for weighted fusion score calculation, EMA smoothing, voice swap spikes
│   ├── test_websocket_stream.py                  # Full-duplex WebSocket stream simulation and message validation
│   └── test_file_upload.py                       # Tests for multipart file upload, sliding analysis, and report generation
│
├── data/                                         # Training corpus and dataset storage
│   └── unified_corpus/                           # Unified 5,497-sample balanced training dataset
│       ├── TRAINING_DATASET_INVENTORY.md         # Comprehensive markdown catalog of dataset composition and samples
│       ├── real/                                 # 2,577 bona fide human speech audio samples (.wav)
│       └── fake/                                 # 2,920 synthetic speech samples across 15+ neural generators (.wav)
│
├── dataset_samples/                              # Evaluation & demo audio recordings of public figures
│   ├── Andrew Tate.wav
│   ├── Barack Obama.wav
│   ├── Bill Gates.wav
│   ├── Donald Trump.wav
│   ├── Elon Musk.wav
│   ├── Greta Thunberg.wav
│   ├── Hillary Clinton.wav
│   ├── J.K. Rowling.wav
│   ├── Jensen Huang.wav
│   ├── Joe Biden.wav
│   ├── Kamala Harris.wav
│   ├── Mark Zuckerberg.wav
│   ├── Oprah Winfrey.wav
│   └── Steve Jobs.wav
│
└── docs/                                         # Visual documentation assets and figures
    └── figures/
        ├── architecture_diagram.png              # High-level system architecture flowchart
        ├── benchmark_chart.png                   # Model evaluation benchmark comparison chart
        └── radar_diagram.png                     # 8-axis forensic radar representation diagram
```

---

## 2. Directory-by-Directory & File-by-File Responsibility Breakdown

### 2.1 Root Directory

| File Name | Responsibility & Technical Details |
| :--- | :--- |
| [`README.md`](file:///p:/VoxSentinalX/README.md) | Comprehensive project documentation covering problem statement (#26104), system architecture, step-by-step launch instructions, benchmark performance results, test coverage, and SIH attribution. |
| [`run_all.bat`](file:///p:/VoxSentinalX/run_all.bat) | Windows batch script that simultaneously spawns the FastAPI backend (Port 8000) and Vite React frontend (Port 3000) in separate interactive command-prompt windows. |
| [`run_tests.bat`](file:///p:/VoxSentinalX/run_tests.bat) | Convenience batch wrapper executing `python -m pytest tests/ -v`. |
| [`start_backend.bat`](file:///p:/VoxSentinalX/start_backend.bat) | Launches the backend server via `cd backend && python run.py`. |
| [`start_frontend.bat`](file:///p:/VoxSentinalX/start_frontend.bat) | Launches the frontend dev server via `cd frontend && npm run dev`. |
| [`VoxSentinalX_SIH_Project_Dossier.pdf`](file:///p:/VoxSentinalX/VoxSentinalX_SIH_Project_Dossier.pdf) | Technical document outlining the end-to-end hackathon solution, architecture diagrams, mathematical formulations, and competitive differentiators. |
| [`.gitignore`](file:///p:/VoxSentinalX/.gitignore) | Standard git exclusions for Python virtual environments, compiled bytecode (`__pycache__`), Node modules, and build outputs. |

---

### 2.2 Backend Package (`backend/`)

#### Root Files
- [`backend/requirements.txt`](file:///p:/VoxSentinalX/backend/requirements.txt): Declares Python dependencies including `fastapi>=0.110.0`, `uvicorn>=0.28.0`, `websockets>=12.0`, `pydantic>=2.6.0`, `pydantic-settings>=2.2.0`, `numpy>=1.26.0`, `scipy>=1.12.0`, `soundfile>=0.12.1`, `torch>=2.2.0`, `torchaudio>=2.2.0`, `huggingface_hub>=0.20.0`, `pyarrow>=14.0.0`, and `pytest>=8.0.0`.
- [`backend/run.py`](file:///p:/VoxSentinalX/backend/run.py): Backend runner script executing `uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")`. Ensures workspace root and backend path are appended to `sys.path`.

#### Application Initialization & Configuration (`backend/app/` & `backend/app/core/`)
- [`backend/app/main.py`](file:///p:/VoxSentinalX/backend/app/main.py): Instantiates the primary `FastAPI` app with metadata, registers CORS middleware for cross-origin frontend communication, mounts the REST router (`/api`) and WebSocket router (`/ws`), and serves a root metadata payload at `/`.
- [`backend/app/core/config.py`](file:///p:/VoxSentinalX/backend/app/core/config.py): Contains the `Settings` class inheriting from `BaseSettings`. Houses audio DSP parameters (`SAMPLE_RATE = 16000`, `WINDOW_DURATION_SEC = 2.0`, `HOP_DURATION_SEC = 1.0`, `BUFFER_CAPACITY_SEC = 10.0`), risk classification thresholds (`LOW = 0.30`, `MODERATE = 0.60`, `HIGH = 0.80`), 8-vector fusion weights (`DETECTOR_WEIGHTS`), and temporal smoothing factors (`EMA_ALPHA = 0.35`, `SPIKE_DELTA_THRESHOLD = 0.28`).

#### Transport & API Handlers (`backend/app/api/`)
- [`backend/app/api/routes.py`](file:///p:/VoxSentinalX/backend/app/api/routes.py):
  - `POST /api/calibrate`: Calibrates near-field user voiceprint from uploaded audio samples.
  - `GET /api/health`: Health status probe returning version, sample rate, and list of active detectors.
  - `GET /api/config`: Returns active thresholds and fusion weightings.
  - `GET /api/training/datasets`: Retrieves dataset catalog and local sample counts.
  - `GET /api/training/metrics`: Returns serialized benchmark evaluation metrics from `model_metrics.json`.
  - `POST /api/training/generate-corpus`: Generates balanced synthetic adversarial samples.
  - `POST /api/training/train`: Triggers model training run.
  - `POST /api/analyze-file`: Multi-part audio/video file upload handler. Decodes audio, converts to mono, resamples to 16 kHz, slices sliding windows, executes forensic detection, and compiles an aggregate report with timeline.
- [`backend/app/api/websocket_handler.py`](file:///p:/VoxSentinalX/backend/app/api/websocket_handler.py):
  - `WebSocket /ws/analyze`: Bidirectional streaming endpoint. Ingests raw Int16 PCM chunks into `StreamBuffer`, executes sliding-window forensic detection, and pushes `ANALYSIS_UPDATE` JSON payloads to the frontend. Handles JSON control messages (`calibrate`, `reset`, `ping`).

#### Audio Signal Processing (`backend/app/audio/`)
- [`backend/app/audio/preprocessor.py`](file:///p:/VoxSentinalX/backend/app/audio/preprocessor.py): `AudioPreprocessor` class providing static DSP utilities: `pcm16_bytes_to_float32`, `float32_to_pcm16_bytes`, `compute_rms_energy`, `is_silent`, and `normalize_amplitude`.
- [`backend/app/audio/stream_buffer.py`](file:///p:/VoxSentinalX/backend/app/audio/stream_buffer.py): `StreamBuffer` class managing a circular FIFO ring buffer of 160,000 samples (10.0 seconds) in memory. Emits 32,000-sample (2.0s) windows when 16,000 new samples (1.0s hop) accumulate.
- [`backend/app/audio/speaker_separator.py`](file:///p:/VoxSentinalX/backend/app/audio/speaker_separator.py): `SpeakerSeparator` class implementing voiceprint calibration (mean energy, spectral centroid, spectral rolloff). Identifies and strips local near-field user speech frames (50ms) from speakerphone microphone audio.

#### Forensic Detection Modules (`backend/app/detectors/`)
- [`backend/app/detectors/base.py`](file:///p:/VoxSentinalX/backend/app/detectors/base.py): Abstract base class `BaseDetector` establishing the interface contract: `name` property and `analyze(audio, sample_rate)` method.
- [`backend/app/detectors/spectral_detector.py`](file:///p:/VoxSentinalX/backend/app/detectors/spectral_detector.py): `SpectralDetector` (Layer 1). Evaluates Spectral Flatness Ratio (Wiener entropy via Welch PSD), Harmonic-to-Noise Ratio (HNR via autocorrelation), and STFT Phase Coherence Discontinuities (second-order difference of unwrapped phase).
- [`backend/app/detectors/prosody_detector.py`](file:///p:/VoxSentinalX/backend/app/detectors/prosody_detector.py): `ProsodyDetector` (Layer 2). Extracts fundamental frequency ($F_0$) contour across 40ms sliding frames, computes pitch standard deviation ($\sigma$), and extracts 8–12 Hz involuntary vocal micro-tremor power via Welch PSD of the detrended pitch track.
- [`backend/app/detectors/breathing_detector.py`](file:///p:/VoxSentinalX/backend/app/detectors/breathing_detector.py): `BreathingDetector` (Layer 3). Detects low-energy, high-ZCR inhalation events and tracks continuous phonation duration to flag continuous speech exceeding biological limits (>6.0s).
- [`backend/app/detectors/acoustic_artifacts.py`](file:///p:/VoxSentinalX/backend/app/detectors/acoustic_artifacts.py): `AcousticArtifactDetector` (Layer 4). Identifies steep brickwall cutoff filters ($< -25$ dB/bin cliff drops) between 3.5 kHz and 7.8 kHz, evaluates spectral decay slope ($-6$ to $-14$ dB/octave normal), and checks sub-band energy discontinuities.
- [`backend/app/detectors/lfcc_detector.py`](file:///p:/VoxSentinalX/backend/app/detectors/lfcc_detector.py): `LFCCDetector` (Layer 5). Computes 24 linear triangular filterbank energies up to 8 kHz Nyquist, generates 20 static cepstral coefficients via DCT-II, computes Delta ($\Delta$) and Delta-Delta ($\Delta\Delta$) accelerations, and evaluates high-frequency cepstral energy distribution.
- [`backend/app/detectors/glottal_detector.py`](file:///p:/VoxSentinalX/backend/app/detectors/glottal_detector.py): `GlottalFlowDetector` (Layer 6). Performs 16th-order Linear Predictive Coding (LPC) inverse filtering via Levinson-Durbin to reconstruct glottal flow pulses. Computes Normalized Amplitude Quotient (NAQ) and excitation residual kurtosis.
- [`backend/app/detectors/perturbation_detector.py`](file:///p:/VoxSentinalX/backend/app/detectors/perturbation_detector.py): `LaryngealPerturbationDetector` (Layer 7). Filters audio below 800 Hz, picks glottal cycle peaks, and computes period-to-period micro-instability (Jitter local and 3-point RAP) and amplitude perturbation (Shimmer local and 3-point APQ3).
- [`backend/app/detectors/bispectrum_detector.py`](file:///p:/VoxSentinalX/backend/app/detectors/bispectrum_detector.py): `BispectrumPhaseDetector` (Layer 8). Computes 2D bispectrum $B(f_1, f_2)$ and normalized bicoherence matrix across the principal non-redundant domain ($f_1 + f_2 \le f_s/2$) to quantify non-linear Quadratic Phase Coupling (QPC) between vocal harmonics.
- [`backend/app/detectors/neural_lcnn_detector.py`](file:///p:/VoxSentinalX/backend/app/detectors/neural_lcnn_detector.py): `NeuralLCNNDetector`. Computes 80-bin Mel-spectrograms and executes forward inference through the deep Light-CNN (LCNN) architecture to predict neural spoof probability.

#### Fusion & Engine Orchestration (`backend/app/engine/`)
- [`backend/app/engine/fusion_scorer.py`](file:///p:/VoxSentinalX/backend/app/engine/fusion_scorer.py): `DetectionEngine` class. Orchestrates all 9 detector modules, performs speaker separation, computes normalized weighted fusion scores, applies EMA temporal smoothing ($\alpha=0.35$), detects velocity spikes ($\Delta > 0.28$), and bundles diagnostic results.
- [`backend/app/engine/diagnostic_generator.py`](file:///p:/VoxSentinalX/backend/app/engine/diagnostic_generator.py): `DiagnosticGenerator` class. Transforms quantitative anomaly measurements into 4-tier risk categorizations (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`), user-facing explanations, and actionable security countermeasure instructions.

#### Models & Checkpoints (`backend/app/models/`)
- [`backend/app/models/lcnn_architecture.py`](file:///p:/VoxSentinalX/backend/app/models/lcnn_architecture.py): PyTorch neural network definition containing `MaxFeatureMap2D`, `MaxFeatureMap1D`, `LCNNBlock`, `SelfAttentionPooling`, and the complete `LCNNModel` (4 conv blocks, bidirectional LSTM, attention pooling, classifier).
- [`backend/app/models/model_metrics.json`](file:///p:/VoxSentinalX/backend/app/models/model_metrics.json): JSON record of benchmark metrics (86.27% accuracy, 6.86% EER, 88.28% precision, 86.99% recall, 87.63% F1).
- [`backend/app/models/pretrained_weights.pt`](file:///p:/VoxSentinalX/backend/app/models/pretrained_weights.pt): Serialized PyTorch state dictionary checkpoint for the trained LCNN model.
- [`backend/app/models/ensemble_weights.npz`](file:///p:/VoxSentinalX/backend/app/models/ensemble_weights.npz): Serialized NumPy weight matrices ($W_1, b_1, W_2, b_2, W_3, b_3$) and normalization statistics (mean, std) for the forensic ensemble.
- [`backend/app/models/archive_weights.pt`](file:///p:/VoxSentinalX/backend/app/models/archive_weights.pt): Backup PyTorch weights checkpoint.

---

### 2.3 Frontend Application (`frontend/`)

#### Configuration & Build Files
- [`frontend/package.json`](file:///p:/VoxSentinalX/frontend/package.json): Defines frontend package metadata, scripts (`dev`, `build`, `preview`), and dependencies (`react 18.3.1`, `lucide-react 0.468.0`, `tailwindcss 3.4.16`, `vite 5.4.11`, `typescript 5.6.3`).
- [`frontend/vite.config.ts`](file:///p:/VoxSentinalX/frontend/vite.config.ts): Vite configuration configuring `@vitejs/plugin-react` and setting dev server port to 3000 with network host binding.
- [`frontend/tailwind.config.js`](file:///p:/VoxSentinalX/frontend/tailwind.config.js): Custom Tailwind CSS configuration defining cybernetic color palettes, glow effects, radial gradients, and animations.
- [`frontend/postcss.config.js`](file:///p:/VoxSentinalX/frontend/postcss.config.js): PostCSS pipeline configuring TailwindCSS and Autoprefixer.
- [`frontend/tsconfig.json`](file:///p:/VoxSentinalX/frontend/tsconfig.json): TypeScript compilation parameters for React JSX and ES modules.
- [`frontend/index.html`](file:///p:/VoxSentinalX/frontend/index.html): HTML5 application entry template containing viewport settings, fonts, and `#root` container.

#### Source Code Core (`frontend/src/`)
- [`frontend/src/main.tsx`](file:///p:/VoxSentinalX/frontend/src/main.tsx): Mounts the React root application inside `#root`.
- [`frontend/src/App.tsx`](file:///p:/VoxSentinalX/frontend/src/App.tsx): Root stateful controller managing active tab navigation (`overview`, `live`, `upload`, `train`, `settings`), global theme (`dark`/`light`), calibration modal visibility, backend health polling, and instantiation of the persistent `VoxSentinalAudioCapture` instance.
- [`frontend/src/index.css`](file:///p:/VoxSentinalX/frontend/src/index.css): Global styling rules, cyber-grid backgrounds, scanner animations, and custom scrollbars.
- [`frontend/src/types/index.ts`](file:///p:/VoxSentinalX/frontend/src/types/index.ts): Central TypeScript definitions: `RiskLevel`, `AlertType`, `AnomalyItem`, `LayerScores`, `AnalysisUpdate`, `FileAnalysisReport`, `DatasetItem`, and `ModelMetrics`.

#### Audio & DSP Engine (`frontend/src/lib/`)
- [`frontend/src/lib/audioCapture.ts`](file:///p:/VoxSentinalX/frontend/src/lib/audioCapture.ts): `VoxSentinalAudioCapture` class. Requests raw microphone access via `getUserMedia` (disabling echo cancellation and noise suppression), instantiates `AudioContext` and `ScriptProcessorNode` (4096 samples = 256ms), encodes Float32 samples to Int16 PCM, streams binary packets over WebSocket, receives `ANALYSIS_UPDATE` packets, and manages calibration recording sessions.
- [`frontend/src/lib/audioVisualizer.ts`](file:///p:/VoxSentinalX/frontend/src/lib/audioVisualizer.ts): `CanvasAudioVisualizer` class. Renders 60 FPS oscilloscope waveforms and frequency spectrum bars using `requestAnimationFrame`. Dynamically modifies canvas stroke colors based on real-time risk level.

#### UI Components (`frontend/src/components/`)
- [`frontend/src/components/Navbar.tsx`](file:///p:/VoxSentinalX/frontend/src/components/Navbar.tsx): Top navigation bar with logo, tab links, live monitoring status badge, backend health indicator, voiceprint calibration button, and theme switcher.
- [`frontend/src/components/LandingView.tsx`](file:///p:/VoxSentinalX/frontend/src/components/LandingView.tsx): Cybernetic showcase overview featuring the `WaveformHeroVisualizer`, 8-vector forensic bento grid, and interactive threat simulation sandbox (Wire Fraud, Authentic Human, Indic Dialect Clones).
- [`frontend/src/components/WaveformHeroVisualizer.tsx`](file:///p:/VoxSentinalX/frontend/src/components/WaveformHeroVisualizer.tsx): Interactive multi-band frequency visualizer canvas simulating live spectral bars and threat intercepts.
- [`frontend/src/components/LiveCallMonitor.tsx`](file:///p:/VoxSentinalX/frontend/src/components/LiveCallMonitor.tsx): Real-time call monitoring tab. Displays live oscilloscope canvas, `RiskGauge`, `ForensicRadar`, and `DiagnosticFeed`.
- [`frontend/src/components/RiskGauge.tsx`](file:///p:/VoxSentinalX/frontend/src/components/RiskGauge.tsx): Dynamic 270-degree radial SVG gauge displaying smoothed risk score ($0-100\%$), classification badges (`GENUINE HUMAN`, `CAUTION`, `SUSPICIOUS`, `CRITICAL AI CLONE`), and voice swap velocity spike alerts.
- [`frontend/src/components/ForensicRadar.tsx`](file:///p:/VoxSentinalX/frontend/src/components/ForensicRadar.tsx): 8-axis SVG radar polygon charting scores across Spectral, Prosody, Breathing, Vocoder, LFCC, Glottal, Jitter/Shimmer, and Bispectrum dimensions.
- [`frontend/src/components/DiagnosticFeed.tsx`](file:///p:/VoxSentinalX/frontend/src/components/DiagnosticFeed.tsx): Real-time feed rendering anomaly cards with exact measured telemetry values, biological normal thresholds, severity badges, and recommended security actions.
- [`frontend/src/components/AlertOverlay.tsx`](file:///p:/VoxSentinalX/frontend/src/components/AlertOverlay.tsx): High-priority full-screen modal triggered when risk exceeds $80\%$ or upon sudden voice takeover spikes.
- [`frontend/src/components/CalibrationModal.tsx`](file:///p:/VoxSentinalX/frontend/src/components/CalibrationModal.tsx): Interactive 5-second voice calibration modal with visual audio meters, recording countdown, and REST/WebSocket baseline profile dispatch.
- [`frontend/src/components/FileAnalyzer.tsx`](file:///p:/VoxSentinalX/frontend/src/components/FileAnalyzer.tsx): File upload interface supporting audio and video formats (.wav, .mp3, .flac, .mp4). Displays interactive forensic timeline scrubbers, risk peaks, synchronized HTML5 video playback, and countermeasure reports.
- [`frontend/src/components/ModelTrainingSuite.tsx`](file:///p:/VoxSentinalX/frontend/src/components/ModelTrainingSuite.tsx): Training operations center displaying dataset catalog, sample counts, benchmark accuracy/EER metrics, and one-click retraining triggers.
- [`frontend/src/components/SettingsPanel.tsx`](file:///p:/VoxSentinalX/frontend/src/components/SettingsPanel.tsx): Configuration dashboard allowing modification of WebSocket URIs, API base endpoints, and detector sensitivity levels.

---

### 2.4 Training & Dataset Pipeline (`training/`)

| File Name | Purpose & Technical Functions |
| :--- | :--- |
| [`training/dataset.py`](file:///p:/VoxSentinalX/training/dataset.py) | PyTorch `AudioDeepfakeDataset` subclassing `torch.utils.data.Dataset`. Scans nested folder structures, parses audio formats, resamples to 16 kHz, crops/pads to 32,000 samples (2.0s), performs random gain (0.7x–1.2x) and Gaussian noise augmentation, applies SpecAugment time/frequency masking, and computes 80-bin log-Mel spectrograms using precomputed filterbanks. |
| [`training/train.py`](file:///p:/VoxSentinalX/training/train.py) | GPU-accelerated PyTorch training pipeline. Implements Mixed Precision training (`torch.cuda.amp.autocast` & `GradScaler`), Focal Loss ($\gamma=2.0, \alpha=0.5$), AdamW optimizer (`lr=1e-3`, `weight_decay=1e-4`), Cosine Annealing learning rate scheduler, and stratified 80/20 train/validation splits. |
| [`training/train_acoustic_ensemble.py`](file:///p:/VoxSentinalX/training/train_acoustic_ensemble.py) | Standalone high-throughput NumPy forensic ensemble trainer. Extracts 32-dimensional forensic feature vectors across STFT flatness, phase variance, F0/micro-tremors, respiration gaps, vocoder cutoff, LFCC bands, glottal NAQ, shimmer, and bispectral kurtosis. Trains a 3-layer MLP classifier (`W1`, `W2`, `W3`) with Focal Loss and Adam optimizer, saving weights to `ensemble_weights.npz`. |
| [`training/evaluate.py`](file:///p:/VoxSentinalX/training/evaluate.py) | Benchmark evaluation script. Loads model checkpoints, evaluates accuracy, precision, recall, and F1-score, performs linear threshold sweeps to compute Equal Error Rate (EER), and generates per-generator accuracy breakdowns (OpenAI, XTTS, Seed-TTS, VALL-E, VoiceBox, etc.). |
| [`training/download_datasets.py`](file:///p:/VoxSentinalX/training/download_datasets.py) | Internet dataset harvester. Connects to Hugging Face Hub (`huggingface_hub`, `pyarrow.parquet`) to download ASVspoof, IndicSynth, and TTS datasets. Extracts audio bytes, computes SHA256 hashes to prevent duplicate ingestion, and organizes samples directly into `data/unified_corpus/`. |
| [`training/dataset_generator.py`](file:///p:/VoxSentinalX/training/dataset_generator.py) | Algorithmic speech generator synthesizing paired genuine human voice samples (dynamic pitch contour, 10 Hz micro-tremor, vocal tract formant filters, natural breath gaps) and deepfake failure modes (flat pitch, phase jitter, brickwall cutoff). |
| [`training/generate_advanced_ai_voices.py`](file:///p:/VoxSentinalX/training/generate_advanced_ai_voices.py) | Advanced synthetic speech generator producing simulated samples for HiFi-GAN (harmonic phase shift and ripple), Diffusion Grad-TTS (flat prosody and stochastic noise), Zero-Shot VALL-E (codebook pitch steps and boundary clicks), and Griffin-Lim (phase incoherence). |
| [`training/generate_sample_inventory.py`](file:///p:/VoxSentinalX/training/generate_sample_inventory.py) | Automated scanner that inspects `data/unified_corpus`, extracts sample metadata (duration, sample rate, file size, SHA256 hash), and writes `TRAINING_DATASET_INVENTORY.md` alongside CSV indices. |
| [`training/export_onnx.py`](file:///p:/VoxSentinalX/training/export_onnx.py) | Exports trained PyTorch LCNN models to ONNX Runtime format (`lcnn_deepfake.onnx`) with dynamic axes for batch size and time frames. |
| [`training/pretrain_weights.py`](file:///p:/VoxSentinalX/training/pretrain_weights.py) | Model initialization script ensuring valid default checkpoints exist before first execution. |

---

### 2.5 Automated Test Suite (`tests/`)

| File Name | Test Scope & Coverage (20/20 Passing Tests) |
| :--- | :--- |
| [`tests/test_audio_buffer.py`](file:///p:/VoxSentinalX/tests/test_audio_buffer.py) | Validates `AudioPreprocessor` Int16 $\leftrightarrow$ Float32 conversions, amplitude normalization, RMS energy calculation, silence detection, and `StreamBuffer` sliding-window hop boundaries and 10s memory eviction. |
| [`tests/test_detectors.py`](file:///p:/VoxSentinalX/tests/test_detectors.py) | Validates baseline forensic detectors (Layer 1–4): Spectral flatness, phase coherence, autocorrelation $F_0$ pitch tracking, 8–12 Hz micro-tremors, breathing pattern monitoring, and brickwall cutoff detection. |
| [`tests/test_new_detectors.py`](file:///p:/VoxSentinalX/tests/test_new_detectors.py) | Validates advanced forensic detectors (Layer 5–8): ASVspoof LFCC ($\Delta + \Delta\Delta$), Glottal flow LPC-NAQ inverse filtering, Laryngeal Jitter/Shimmer micro-perturbation, and higher-order Bispectrum bicoherence (QPC). |
| [`tests/test_neural_inference.py`](file:///p:/VoxSentinalX/tests/test_neural_inference.py) | Validates `LCNNModel` forward pass tensor shapes, output logit dimensions, and `NeuralLCNNDetector` spoof probability calibrations. |
| [`tests/test_fusion_scorer.py`](file:///p:/VoxSentinalX/tests/test_fusion_scorer.py) | Validates `DetectionEngine` weighted fusion arithmetic, exponential moving average temporal smoothing ($\alpha=0.35$), and rapid velocity spike detection for mid-call voice swaps ($\Delta > 0.28$). |
| [`tests/test_websocket_stream.py`](file:///p:/VoxSentinalX/tests/test_websocket_stream.py) | Simulates full-duplex WebSocket connections using `fastapi.testclient.TestClient`, streaming binary Int16 PCM chunks and verifying JSON `ANALYSIS_UPDATE` and `CALIBRATION_RESULT` payloads. |
| [`tests/test_file_upload.py`](file:///p:/VoxSentinalX/tests/test_file_upload.py) | Tests the `POST /api/analyze-file` endpoint with synthetic WAV buffers, verifying mono conversion, windowed timeline generation, and aggregate risk score calculation. |

---

### 2.6 Data & Documentation Assets (`data/`, `dataset_samples/`, `docs/`)

- [`data/unified_corpus/`](file:///p:/VoxSentinalX/data/unified_corpus/): Consolidated training dataset containing 5,497 audio files organized into `real/` ($2,577$ bona fide human files) and `fake/` ($2,920$ deepfake voice clone files).
- [`data/unified_corpus/TRAINING_DATASET_INVENTORY.md`](file:///p:/VoxSentinalX/data/unified_corpus/TRAINING_DATASET_INVENTORY.md): Full dataset audit detailing sample counts, class distributions, generator descriptions, audio durations, and SHA256 hashes.
- [`dataset_samples/`](file:///p:/VoxSentinalX/dataset_samples/): 14 real-world test audio clips of public figures (Barack Obama, Donald Trump, Elon Musk, Jensen Huang, Mark Zuckerberg, etc.) for testing file analysis and demonstration.
- [`docs/figures/`](file:///p:/VoxSentinalX/docs/figures/): System architecture diagrams (`architecture_diagram.png`), radar charts (`radar_diagram.png`), and benchmark evaluation graphs (`benchmark_chart.png`).

---

## 3. Key Entry Points & Critical Execution Paths

### 3.1 Backend Application Startup
```text
run_all.bat / start_backend.bat
  └─► python backend/run.py
        └─► uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
              ├─► Load settings from app/core/config.py
              ├─► Register CORS middleware (CORS_ORIGINS=["*"])
              ├─► Mount api_router at /api (routes.py)
              └─► Mount ws_router at /ws (websocket_handler.py)
```

### 3.2 Frontend Application Startup
```text
run_all.bat / start_frontend.bat
  └─► npm run dev (in frontend/)
        └─► vite (port 3000, host: true)
              └─► index.html
                    └─► src/main.tsx
                          └─► src/App.tsx
                                ├─► Periodic backend health polling (GET /api/health)
                                ├─► Persistent VoxSentinalAudioCapture instantiation
                                └─► Render active tab (LandingView, LiveCallMonitor, FileAnalyzer, etc.)
```

### 3.3 Live Call Monitoring Streaming Loop
```text
LiveCallMonitor.tsx ("Start Live Monitoring")
  └─► captureEngine.startMonitoring(wsUrl, onUpdate, onStatusChange, onAudioLevel)
        ├─► navigator.mediaDevices.getUserMedia({ sampleRate: 16000, channelCount: 1, ... })
        ├─► AudioContext(sampleRate: 16000)
        ├─► createScriptProcessor(4096, 1, 1)
        ├─► new WebSocket("ws://localhost:8000/ws/analyze")
        │
        [onaudioprocess event every 256ms]:
          ├─► Transcode Float32Array to Int16Array
          └─► ws.send(int16Data.buffer)
                │
                ▼ [WebSocket Server]
                websocket_analyze_endpoint (websocket_handler.py)
                  ├─► buffer.add_pcm16_bytes(raw_bytes)
                  │     └─► AudioPreprocessor.pcm16_bytes_to_float32()
                  │
                  └─► If hop boundary reached (>= 16,000 new samples & >= 32,000 total):
                        ├─► isolate_caller_audio() (SpeakerSeparator)
                        ├─► DetectionEngine.analyze_window() (fusion_scorer.py)
                        │     ├─► SpectralDetector.analyze()
                        │     ├─► ProsodyDetector.analyze()
                        │     ├─► BreathingDetector.analyze()
                        │     ├─► AcousticArtifactDetector.analyze()
                        │     ├─► LFCCDetector.analyze()
                        │     ├─► GlottalFlowDetector.analyze()
                        │     ├─► LaryngealPerturbationDetector.analyze()
                        │     ├─► BispectrumPhaseDetector.analyze()
                        │     └─► NeuralLCNNDetector.analyze()
                        ├─► Compute weighted linear fusion score
                        ├─► Apply EMA temporal smoothing (alpha=0.35)
                        ├─► Check velocity spike delta (>= 0.28)
                        ├─► DiagnosticGenerator.generate_report()
                        └─► websocket.send_json(result)
                              │
                              ▼ [WebSocket Client]
                              ws.onmessage (audioCapture.ts)
                                └─► onUpdate(payload)
                                      ├─► Update RiskGauge.tsx
                                      ├─► Update ForensicRadar.tsx
                                      ├─► Update DiagnosticFeed.tsx
                                      └─► If CRITICAL -> Trigger AlertOverlay.tsx
```

### 3.4 File Upload Analysis Execution Path
```text
FileAnalyzer.tsx (File Drop / Selection)
  └─► handleAnalyze() -> POST /api/analyze-file (multipart/form-data)
        └─► analyze_audio_file() (routes.py)
              ├─► soundfile.read(audio_io)
              ├─► Downmix multi-channel to mono
              ├─► scipy.signal.resample to 16,000 Hz if necessary
              ├─► Segment into 32,000-sample windows stepping by 16,000-sample hops
              ├─► Iterate: DetectionEngine.analyze_window() for each temporal slice
              ├─► Calculate peak_risk and average_risk
              ├─► Formulate overall_verdict (CRITICAL_AI_CLONE, PROBABLE_SYNTHETIC, etc.)
              ├─► Deduplicate detected anomalies
              └─► Return JSON report to frontend
                    └─► Render interactive risk timeline and synchronized video player
```

---

## 4. Data & Artifact Storage Layout

| Storage Component | Directory Path | Format | Lifecycle / Persistence |
| :--- | :--- | :--- | :--- |
| **Unified Training Corpus** | `data/unified_corpus/` | `.wav` (16 kHz Mono) | Persistent. Houses 5,497 audio training samples (`real/` and `fake/`). |
| **Dataset Metadata Index** | `data/unified_corpus/TRAINING_DATASET_INVENTORY.md` | Markdown | Persistent. Contains catalog metrics, class distribution, and SHA256 hashes. |
| **Public Figure Test Clips** | `dataset_samples/` | `.wav` (16 kHz Mono) | Persistent. Evaluation samples of 14 prominent public figures. |
| **Model Weights (PyTorch)** | `backend/app/models/pretrained_weights.pt` | PyTorch State Dict | Persistent. Updated upon completion of `training/train.py`. |
| **Model Weights (NumPy)** | `backend/app/models/ensemble_weights.npz` | NumPy Compressed Array | Persistent. Updated upon completion of `training/train_acoustic_ensemble.py`. |
| **Model Evaluation Metrics** | `backend/app/models/model_metrics.json` | JSON | Persistent. Stores Accuracy, EER, Precision, Recall, and sample counts. |
| **ONNX Runtime Export** | `backend/app/models/lcnn_deepfake.onnx` | ONNX Binary | Optional. Generated via `training/export_onnx.py`. |
| **In-Memory Ring Buffer** | `StreamBuffer._buffer` | NumPy Float32 Array | Ephemeral. Lives in process RAM (max 10.0s / 160k samples); cleared via reset. |
| **User Voiceprint Profile** | `SpeakerSeparator.user_profile` | In-Memory Dictionary | Ephemeral per session. Calibrated via `/api/calibrate` or WebSocket control. |
