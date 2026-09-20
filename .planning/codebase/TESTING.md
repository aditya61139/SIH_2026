# VoxSentinalX Testing Architecture and Test Suite Guide

This document provides a comprehensive analysis of the automated testing suite in **VoxSentinalX**, detailing test frameworks, test inventories, synthetic signal generation patterns, execution workflows, coverage assessment, and recommendations.

---

## 1. Testing Framework and Architecture

VoxSentinalX uses **Pytest** as its core automated test framework, paired with `pytest-asyncio` for asynchronous execution and FastAPI's `TestClient` (built on Starlette and HTTPX) for REST and WebSocket integration testing.

| Component | Library / Version | Purpose |
| :--- | :--- | :--- |
| **Test Runner** | `pytest >= 8.0.0` | Test discovery, assertion evaluation, fixtures, and reporting |
| **Async Support** | `pytest-asyncio >= 0.23.0` | Coroutine and async fixture support |
| **API Client** | `fastapi.testclient.TestClient` / `httpx >= 0.27.0` | Synchronous REST and WebSocket mocking without starting a live Uvicorn daemon |
| **Audio I/O** | `soundfile >= 0.12.1` | In-memory binary WAV generation and header encoding |
| **Signal Verification**| `numpy >= 1.26.0`, `scipy >= 1.12.0` | Array comparisons, tolerance checking (`np.allclose`), and mock waveform synthesis |
| **Neural Inference** | `torch >= 2.2.0` | Forward pass verification and tensor shape matching |

All tests reside in the top-level [`tests/`](file:///p:/VoxSentinalX/tests) directory. Path resolution is standardized across test modules by injecting `backend/` and workspace root paths into `sys.path`:

```python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
```

---

## 2. Test Suite Inventory and Deep Analysis

The test suite comprises **7 test files** containing **20 test functions** evaluating unit algorithms, DSP transformations, neural models, REST endpoints, and bidirectional WebSocket streams.

```
tests/
├── test_audio_buffer.py        # Circular buffer & PCM/Float32 conversion (3 tests)
├── test_detectors.py           # Core 4 forensic detectors & audio mockups (4 tests)
├── test_file_upload.py         # REST API endpoints & multipart file upload (3 tests)
├── test_fusion_scorer.py       # Detection engine, EMA smoothing, spike detection, diagnostics (3 tests)
├── test_neural_inference.py    # PyTorch LCNN model & neural detector inference (2 tests)
├── test_new_detectors.py       # Advanced 4 forensic detectors: LFCC, Glottal, Jitter/Shimmer, Bispectrum (4 tests)
└── test_websocket_stream.py    # WebSocket connection & real-time streaming integration (1 test)
```

### 2.1 [`test_audio_buffer.py`](file:///p:/VoxSentinalX/tests/test_audio_buffer.py)
Validates real-time audio chunk ingestion, data type conversion, sliding window accumulation, and FIFO memory limits in [`StreamBuffer`](file:///p:/VoxSentinalX/backend/app/audio/stream_buffer.py).

- **`test_pcm16_float32_conversion()`**:
  - Tests bidirectional conversion between normalized `np.float32` $[-1.0, 1.0]$ and raw 16-bit signed integer PCM bytes.
  - Verifies exact byte length ($N \times 2$ bytes).
  - Asserts numerical reconstruction fidelity using `np.allclose(original, reconstructed, atol=1e-4)`.
- **`test_stream_buffer_sliding_window()`**:
  - Configures buffer with $F_s = 16000\text{ Hz}$, window $= 32000$ samples (2.0s), hop $= 16000$ samples (1.0s), capacity $= 160000$ samples (10.0s).
  - Ingests $0.5\text{s}$ (8000 samples) $\rightarrow$ asserts returned window is `None`.
  - Ingests $1.0\text{s}$ (16000 samples, total 24000) $\rightarrow$ asserts returned window is `None`.
  - Ingests $0.5\text{s}$ (8000 samples, total 32000) $\rightarrow$ asserts window returned, `len(win) == 32000`, `window_count == 1`.
  - Ingests $1.0\text{s}$ (16000 samples = 1 hop) $\rightarrow$ asserts 2nd window returned, `len(win) == 32000`, `window_count == 2`.
- **`test_stream_buffer_capacity_eviction()`**:
  - Caps circular capacity at 10,000 samples.
  - Ingests a large array of 25,000 samples.
  - Asserts that internal buffer length is clamped: `len(buffer.get_full_buffer()) <= capacity_samples`.

### 2.2 [`test_detectors.py`](file:///p:/VoxSentinalX/tests/test_detectors.py)
Tests the primary signal-processing detectors against synthetic genuine and synthetic spoofed audio. Defines the two canonical synthetic generators used across the test suite:
- **`test_spectral_detector()`**:
  - Instantiates [`SpectralDetector`](file:///p:/VoxSentinalX/backend/app/detectors/spectral_detector.py).
  - Compares natural audio against synthetic clone audio.
  - Verifies presence of keys (`anomaly_score`, `metrics`, `spectral_flatness`, `hnr_db`, `phase_coherence`).
  - Asserts `res_syn["anomaly_score"] >= res_nat["anomaly_score"]`.
- **`test_prosody_detector()`**:
  - Instantiates [`ProsodyDetector`](file:///p:/VoxSentinalX/backend/app/detectors/prosody_detector.py).
  - Verifies fundamental frequency standard deviation metric `pitch_std_hz`.
  - Asserts natural voice has higher pitch variability than flat monotone clone: `res_nat["metrics"]["pitch_std_hz"] >= res_syn["metrics"].get("pitch_std_hz", 0.0)`.
- **`test_breathing_detector()`**:
  - Instantiates [`BreathingDetector`](file:///p:/VoxSentinalX/backend/app/detectors/breathing_detector.py).
  - Validates detection output structure and metrics (`continuous_speech_sec`, `breath_events_detected`).
- **`test_acoustic_artifact_detector()`**:
  - Instantiates [`AcousticArtifactDetector`](file:///p:/VoxSentinalX/backend/app/detectors/acoustic_artifacts.py).
  - Tests high-frequency energy rolloff and brickwall cutoff detection flag `brickwall_cutoff_detected`.

### 2.3 [`test_file_upload.py`](file:///p:/VoxSentinalX/tests/test_file_upload.py)
Integration tests validating FastAPI HTTP endpoints via `TestClient(app)`.
- **`test_health_endpoint()`**:
  - Issues `GET /api/health`.
  - Verifies `status_code == 200`, `data["status"] == "healthy"`, and `data["project"] == "VoxSentinalX"`.
- **`test_config_endpoint()`**:
  - Issues `GET /api/config`.
  - Verifies `status_code == 200`, presence of `risk_thresholds` and `detector_weights`.
- **`test_file_upload_endpoint()`**:
  - Encodes a 3.0s synthetic audio recording into an in-memory WAV buffer using `soundfile.write(wav_io, audio_data, sample_rate, format="WAV")`.
  - Posts multipart form data to `POST /api/analyze-file` with `files={"file": ("test_voice.wav", wav_io.getvalue(), "audio/wav")}`.
  - Verifies response `status_code == 200`, `data["filename"] == "test_voice.wav"`, presence of `overall_verdict`, `average_risk_score`, and `timeline` with at least 1 window.

### 2.4 [`test_fusion_scorer.py`](file:///p:/VoxSentinalX/tests/test_fusion_scorer.py)
Tests multi-layer fusion scoring, temporal smoothing, sudden risk spikes, and rule-based diagnostic card synthesis in [`DetectionEngine`](file:///p:/VoxSentinalX/backend/app/engine/fusion_scorer.py) and [`DiagnosticGenerator`](file:///p:/VoxSentinalX/backend/app/engine/diagnostic_generator.py).
- **`test_detection_engine_sliding_window()`**:
  - Executes `analyze_window()` on a 2.0s audio segment.
  - Asserts structure includes `window_index`, `risk_score`, `risk_level`, `recommendation`, `suggested_actions`, `diagnostics`, and `layer_scores`.
- **`test_voice_swap_spike_detection()`**:
  - Simulates a mid-conversation voice takeover attack: feeds 3 consecutive natural voice windows followed by an abrupt switch to synthetic clone audio.
  - Verifies that risk score escalates and triggers alert tracking.
- **`test_diagnostic_generator()`**:
  - Passes mock detector results with high anomaly into `DiagnosticGenerator.generate_report(risk_score=0.88, detector_results=mock_results, is_spike=True)`.
  - Verifies classification is `"CRITICAL"`, suggested actions are generated, and spike anomaly is prioritized in `report["anomalies"]`.

### 2.5 [`test_neural_inference.py`](file:///p:/VoxSentinalX/tests/test_neural_inference.py)
Tests PyTorch Light-CNN (LCNN) architecture and detector wrapper.
- **`test_lcnn_forward_pass()`**:
  - Instantiates [`LCNNModel(in_channels=1, num_classes=2)`](file:///p:/VoxSentinalX/backend/app/models/lcnn_architecture.py#L53-L108).
  - Passes a dummy 4D tensor `[Batch=2, Channels=1, Freq=80, Time=128]` through `model.forward()`.
  - Verifies output logit shape is exactly `(2, 2)`.
- **`test_neural_detector_inference()`**:
  - Instantiates [`NeuralLCNNDetector`](file:///p:/VoxSentinalX/backend/app/detectors/neural_lcnn_detector.py).
  - Passes 2.0s audio array into `analyze()`.
  - Verifies output contains `anomaly_score`, `metrics`, and `neural_spoof_prob`.

### 2.6 [`test_new_detectors.py`](file:///p:/VoxSentinalX/tests/test_new_detectors.py)
Validates the advanced biomechanical and higher-order forensic detectors:
- **`test_lfcc_detector()`**:
  - Instantiates [`LFCCDetector`](file:///p:/VoxSentinalX/backend/app/detectors/lfcc_detector.py).
  - Analyzes natural vs synthetic audio.
  - Verifies metric `hf_lfcc_energy_ratio` and valid anomaly scores.
- **`test_glottal_detector()`**:
  - Instantiates [`GlottalFlowDetector`](file:///p:/VoxSentinalX/backend/app/detectors/glottal_detector.py).
  - Executes LPC inverse filtering and NAQ calculation.
  - Verifies metric `naq_mean`.
- **`test_perturbation_detector()`**:
  - Instantiates [`LaryngealPerturbationDetector`](file:///p:/VoxSentinalX/backend/app/detectors/perturbation_detector.py).
  - Extracts pitch cycles via lowpass peak picking.
  - Verifies metric `jitter_local_percent`.
- **`test_bispectrum_detector()`**:
  - Instantiates [`BispectrumPhaseDetector`](file:///p:/VoxSentinalX/backend/app/detectors/bispectrum_detector.py).
  - Computes 2D bispectral sum and normalized bicoherence $b^2(f_1, f_2)$.
  - Verifies metric `mean_bicoherence`.

### 2.7 [`test_websocket_stream.py`](file:///p:/VoxSentinalX/tests/test_websocket_stream.py)
Validates full bidirectional WebSocket audio streaming using `TestClient(app).websocket_connect("/ws/analyze")`.
- **`test_websocket_audio_streaming()`**:
  - Connects to `/ws/analyze`.
  - Asserts initial connection payload: `init_data["type"] == "CONNECTION_ESTABLISHED"`.
  - Generates 2.5s of audio and streams 8 consecutive chunks of 4096 samples (8192 bytes Int16 PCM) totaling 32768 samples ($> 32000$ window requirement).
  - Awaits JSON response: asserts `resp["type"] == "ANALYSIS_UPDATE"`, verifying `risk_score`, `diagnostics`, and `layer_scores`.

---

## 3. Test Execution Workflows

### 3.1 Windows Batch Runner
The project provides [`run_tests.bat`](file:///p:/VoxSentinalX/run_tests.bat) in the repository root for one-click test execution:

```bat
@echo off
title VoxSentinalX Automated Test Runner
cd /d "%~dp0"
echo Running Unit and Integration Tests via Pytest...
python -m pytest tests/ -v
pause
```

### 3.2 CLI Commands

#### Standard Verbose Test Run
```powershell
python -m pytest tests/ -v
```

#### Running Specific Test Modules
```powershell
# Run only detector tests
python -m pytest tests/test_detectors.py tests/test_new_detectors.py -v

# Run only WebSocket integration test
python -m pytest tests/test_websocket_stream.py -v

# Run only buffer unit tests
python -m pytest tests/test_audio_buffer.py -v
```

#### Running by Keyword Filter
```powershell
# Run all tests matching "spike"
python -m pytest tests/ -k "spike" -v

# Run all tests matching "glottal" or "lfcc"
python -m pytest tests/ -k "glottal or lfcc" -v
```

#### Running with Test Execution Timing
```powershell
# Highlight the 5 slowest tests
python -m pytest tests/ --durations=5
```

---

## 4. Key Testing Patterns

### 4.1 Synthetic Audio Generation Patterns
Rather than relying on large, non-deterministic binary audio files that could create git bloat or environment dependencies, the test suite generates deterministic mathematical signals with realistic physical properties.

#### Genuine Human Voice Mockup (`generate_natural_voice_mockup`)
Simulates biological speech characteristics:
1. **Dynamic $F_0$ Pitch Modulation**: Non-stationary fundamental frequency varying smoothly between 115 Hz and 185 Hz via low-frequency sinusoidal drift ($\approx 1.5\text{ Hz}$).
2. **Neuromuscular Micro-Tremor**: Laryngeal 10 Hz tremor superimposed onto the pitch contour ($2.0 \cdot \sin(2\pi \cdot 10.0 \cdot t)$).
3. **Harmonic Overtone Decay**: Four harmonic components with decaying amplitudes ($0.5$, $0.25$, $0.15$, $0.08$) representing acoustic vocal tract excitation.
4. **Physiological Aspiration Noise**: Gentle Gaussian noise ($\sigma = 0.02$) mimicking natural breath turbulence.

```python
def generate_natural_voice_mockup(duration_sec=2.0, sample_rate=16000):
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    f0 = 150.0 + 35.0 * np.sin(2 * np.pi * 1.5 * t) + 2.0 * np.sin(2 * np.pi * 10.0 * t)
    phase = 2 * np.pi * np.cumsum(f0) / sample_rate
    signal = (
        0.5 * np.sin(phase)
        + 0.25 * np.sin(2 * phase)
        + 0.15 * np.sin(3 * phase)
        + 0.08 * np.sin(4 * phase)
    )
    noise = np.random.normal(0, 0.02, len(t))
    return (signal + noise).astype(np.float32)
```

#### Synthetic Voice Clone Mockup (`generate_synthetic_clone_mockup`)
Simulates neural vocoder artifacts:
1. **Monotone Zero-Variance $F_0$**: Mathematically constant fundamental frequency ($F_0 = 160.0\text{ Hz}$), lacking pitch inflection.
2. **Absence of Micro-Tremors**: Zero laryngeal neuromuscular fluctuations.
3. **Sterile Harmonic Ratios**: Fixed harmonic weighting without phase interaction.
4. **Spectral Flatness Artifact**: Elevated high-frequency Gaussian white noise ($\sigma = 0.15$) simulating vocoder quantization noise and high Wiener entropy.

```python
def generate_synthetic_clone_mockup(duration_sec=2.0, sample_rate=16000):
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    f0 = 160.0
    phase = 2 * np.pi * f0 * t
    signal = 0.5 * np.sin(phase) + 0.3 * np.sin(2 * phase) + 0.2 * np.sin(3 * phase)
    white_noise = np.random.normal(0, 0.15, len(t))
    return (signal + white_noise).astype(np.float32)
```

### 4.2 In-Memory Mock File Uploads
To test `POST /api/analyze-file` without touching the disk, tests serialize NumPy arrays directly into an `io.BytesIO` container with valid RIFF WAV headers:

```python
wav_io = io.BytesIO()
sf.write(wav_io, audio_data, sample_rate, format="WAV")
wav_io.seek(0)
files = {"file": ("test_voice.wav", wav_io.getvalue(), "audio/wav")}
resp = client.post("/api/analyze-file", files=files)
```

### 4.3 WebSocket Streaming Mock Pattern
Integration tests use FastAPI's context-managed WebSocket client:
1. Establish handshake using `client.websocket_connect("/ws/analyze")`.
2. Verify protocol negotiation with `websocket.receive_json()`.
3. Loop over audio slices, convert to raw Int16 PCM bytes using [`AudioPreprocessor.float32_to_pcm16_bytes`](file:///p:/VoxSentinalX/backend/app/audio/preprocessor.py#L18-L23), and send via `websocket.send_bytes(pcm_bytes)`.
4. Capture emitted `ANALYSIS_UPDATE` JSON event and assert schema.

---

## 5. Coverage Assessment and Quality Gaps

### 5.1 Coverage Strengths
- **All 9 Forensic Layers Covered**: Every detector (`spectral`, `prosody`, `breathing`, `acoustic_artifacts`, `lfcc`, `glottal`, `perturbation`, `bispectrum`, `neural_lcnn`) has dedicated unit tests validating anomaly scoring and output dictionary compliance.
- **Buffer Mechanics Fully Verified**: Ingestion, conversion, hop window slicing, and circular eviction are rigorously tested.
- **End-to-End WebSocket Stream Tested**: Validates that live streaming over WebSockets correctly ingests chunks and emits analysis events.
- **Multi-layer Fusion Tested**: Smoothing algorithms, spike detection triggers, and diagnostic categorization are tested with mock feeds.

### 5.2 Identified Test Gaps

1. **Speakerphone Calibration Endpoint (`/api/calibrate` & WS `action: "calibrate"`)**:
   - `test_websocket_stream.py` tests binary audio chunk ingestion, but does not test the JSON control frames (`action: "calibrate"`, `action: "reset"`, `action: "ping"`).
   - `test_file_upload.py` does not test `POST /api/calibrate`.
2. **Audio Format Variations in File Upload**:
   - `test_file_upload.py` tests standard 16 kHz WAV.
   - Non-16kHz audio (e.g. 44.1 kHz, 48 kHz requiring `scipy.signal.resample`), multi-channel stereo downmixing, or MP3/FLAC encoding are not exercised in tests.
3. **Extreme Boundary & Malformed Inputs**:
   - Short audio rejection ($< 0.5\text{s}$) returning HTTP 400 is not explicitly tested.
   - Completely silent audio segments (all zeros) through `DetectionEngine` should verify that anomaly scores return cleanly without `ZeroDivisionError`.
   - Corrupt audio bytes uploaded to `/api/analyze-file` should verify HTTP 400 rejection.
4. **Frontend Automated Testing**:
   - The frontend (`frontend/package.json`) currently lacks a test runner (Vitest or Jest) and React Testing Library setup for testing components like `LiveCallMonitor.tsx`, `RiskGauge.tsx`, and `ForensicRadar.tsx`.

---

## 6. Recommendations for Future Enhancements

1. **Add Pytest Fixtures (`conftest.py`)**:
   - Centralize `generate_natural_voice_mockup` and `generate_synthetic_clone_mockup` into a shared [`tests/conftest.py`](file:///p:/VoxSentinalX/tests) fixture file with session-scoped generators.
2. **Add Negative and Boundary Condition Tests**:
   - Create `test_error_handling.py` to test empty files, duration $< 0.5$s, invalid audio codecs, and WebSocket client disconnects.
3. **Add Calibration Integration Test**:
   - Add a test verifying `engine.speaker_separator.calibrate()` followed by caller isolation verification in `SpeakerSeparator.isolate_caller_audio()`.
4. **Setup Code Coverage Reporting**:
   - Add `pytest-cov` to `backend/requirements.txt`.
   - Configure coverage target:
     ```powershell
     python -m pytest tests/ --cov=backend/app --cov-report=term-missing --cov-report=html:tests/coverage_report
     ```
5. **Frontend Testing Suite**:
   - Introduce Vitest and `@testing-library/react` to test component rendering, user voice recording state transitions, and canvas visualizer initialization.
