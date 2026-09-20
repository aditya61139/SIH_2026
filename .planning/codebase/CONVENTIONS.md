# VoxSentinalX Codebase Conventions and Patterns

This document defines the architectural patterns, coding conventions, signal processing standards, and design guidelines enforced across the **VoxSentinalX** voice cloning detection platform.

---

## 1. System Overview and Tech Stack

VoxSentinalX is an AI-powered real-time deepfake and voice cloning detection engine developed for **Smart India Hackathon Problem Statement #26104**. It operates an 8-Vector forensic decomposition pipeline coupled with a PyTorch neural classifier to detect voice impersonation attacks in real time.

| Subsystem | Primary Technologies | Key Dependencies | Root Directory |
| :--- | :--- | :--- | :--- |
| **Backend API & DSP** | Python 3.11+ | FastAPI 0.110+, PyTorch 2.2+, SciPy 1.12+, NumPy 1.26+, SoundFile 0.12+, Pydantic 2.6+, Uvicorn 0.28+ | [`backend/`](file:///p:/VoxSentinalX/backend) |
| **Detection Suite** | NumPy, SciPy Signal, PyTorch | Levinson-Durbin LPC, Welch PSD, STFT, DCT-II, LCNN-BiLSTM | [`backend/app/detectors/`](file:///p:/VoxSentinalX/backend/app/detectors) |
| **Frontend Dashboard** | React 18.3+, TypeScript 5.6+, Vite 5.4+ | Tailwind CSS 3.4+, Lucide React 0.468+, HTML5 Web Audio API | [`frontend/`](file:///p:/VoxSentinalX/frontend) |
| **Test Suite** | Pytest 8.0+, pytest-asyncio 0.23+ | FastAPI TestClient, SoundFile | [`tests/`](file:///p:/VoxSentinalX/tests) |

---

## 2. Backend Architecture and Python Conventions

The backend follows a modular domain-driven layout under [`backend/app/`](file:///p:/VoxSentinalX/backend/app/):
- `api/`: REST routing ([`routes.py`](file:///p:/VoxSentinalX/backend/app/api/routes.py)) and bidirectional WebSocket streaming ([`websocket_handler.py`](file:///p:/VoxSentinalX/backend/app/api/websocket_handler.py)).
- `audio/`: Ingestion, conversion, circular buffering ([`stream_buffer.py`](file:///p:/VoxSentinalX/backend/app/audio/stream_buffer.py)), and near-field caller separation ([`speaker_separator.py`](file:///p:/VoxSentinalX/backend/app/audio/speaker_separator.py)).
- `core/`: Centralized Pydantic application settings ([`config.py`](file:///p:/VoxSentinalX/backend/app/core/config.py)).
- `detectors/`: Forensic analyzer modules inheriting from [`BaseDetector`](file:///p:/VoxSentinalX/backend/app/detectors/base.py).
- `engine/`: Multi-layer fusion scoring ([`fusion_scorer.py`](file:///p:/VoxSentinalX/backend/app/engine/fusion_scorer.py)) and diagnostic report synthesis ([`diagnostic_generator.py`](file:///p:/VoxSentinalX/backend/app/engine/diagnostic_generator.py)).
- `models/`: PyTorch deep neural network architectures ([`lcnn_architecture.py`](file:///p:/VoxSentinalX/backend/app/models/lcnn_architecture.py)) and model weight artifacts.

### 2.1 The `BaseDetector` Contract
All forensic detectors must implement the abstract base class [`BaseDetector`](file:///p:/VoxSentinalX/backend/app/detectors/base.py#L7-L29):

```python
class BaseDetector(ABC):
    """Abstract Base Class for all forensic voice analysis detectors."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique string identifier matching settings.DETECTOR_WEIGHTS keys."""
        pass

    @abstractmethod
    def analyze(self, audio: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Runs analysis on the audio window.
        
        Returns:
            Dict containing:
            - 'anomaly_score': float between 0.0 (genuine) and 1.0 (synthetic)
            - 'confidence': float between 0.0 and 1.0
            - 'metrics': Dict of specific quantitative measurements
            - 'anomalies_detected': List of detected anomaly descriptors
        """
        pass
```

#### Contract Rules:
1. **Identifier Matching**: The `name` property must match the exact key defined in `Settings.DETECTOR_WEIGHTS` (e.g., `"spectral"`, `"prosody"`, `"breathing"`, `"acoustic_artifacts"`, `"lfcc"`, `"glottal"`, `"perturbation"`, `"bispectrum"`, `"neural_lcnn"`).
2. **Standard Output Structure**: Every return dictionary must strictly contain:
   - `anomaly_score`: `float` in range `[0.0, 1.0]`, rounded to 3 decimal places.
   - `confidence`: `float` in range `[0.0, 1.0]`, reflecting audio duration or sample reliability.
   - `metrics`: `Dict[str, Any]` with granular numerical physical measurements.
   - `anomalies_detected`: `List[Dict[str, Any]]`, where each item contains `type`, `severity` (`"LOW" | "MEDIUM" | "HIGH" | "CRITICAL"`), `metric_name`, `value`, `threshold`, and `description`.
3. **Guard Clauses**: Each detector must check for insufficient duration or silence at the top of `analyze()` using [`AudioPreprocessor.is_silent(audio)`](file:///p:/VoxSentinalX/backend/app/audio/preprocessor.py#L32-L35) and return a zero-score baseline payload rather than raising exceptions.

### 2.2 Configuration Management
Settings are centralized in [`backend/app/core/config.py`](file:///p:/VoxSentinalX/backend/app/core/config.py) using `pydantic_settings.BaseSettings`:
- Environment prefix is `VOXSENTINALX_` with `case_sensitive=True`.
- Configuration values use uppercase attribute names.
- Dynamic attributes are exposed via `@property` methods (`WINDOW_SAMPLES`, `HOP_SAMPLES`, `BUFFER_CAPACITY_SAMPLES`).

```python
class Settings(BaseSettings):
    PROJECT_NAME: str = "VoxSentinalX"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"
    DEBUG: bool = True

    # Audio Ingestion Settings
    SAMPLE_RATE: int = 16000                # Standard: 16 kHz
    CHANNELS: int = 1                       # Standard: Mono
    WINDOW_DURATION_SEC: float = 2.0        # 2.0s analysis window (32,000 samples)
    HOP_DURATION_SEC: float = 1.0           # 1.0s hop (16,000 samples, 50% overlap)
    BUFFER_CAPACITY_SEC: float = 10.0       # 10.0s circular buffer (160,000 samples)

    # Risk Classification Thresholds
    RISK_THRESHOLD_LOW: float = 0.30        # 0.00 - 0.30: Genuine Human
    RISK_THRESHOLD_MODERATE: float = 0.60   # 0.30 - 0.60: Caution / Irregularities
    RISK_THRESHOLD_HIGH: float = 0.80       # 0.60 - 0.80: Warning / Probable Fake
                                            # 0.80 - 1.00: Critical Alert / AI Synthetic

    # Weights for 8-Vector + Neural Forensic Fusion Layer
    DETECTOR_WEIGHTS: Dict[str, float] = {
        "spectral": 0.14,
        "prosody": 0.12,
        "breathing": 0.10,
        "acoustic_artifacts": 0.10,
        "lfcc": 0.16,
        "glottal": 0.12,
        "perturbation": 0.12,
        "bispectrum": 0.08,
        "neural_lcnn": 0.16,
    }

    # Temporal Smoothing
    EMA_ALPHA: float = 0.35                 # Smoothing factor
    SPIKE_DELTA_THRESHOLD: float = 0.28     # Sudden voice swap trigger (delta in < 2s)

    model_config = SettingsConfigDict(env_prefix="VOXSENTINALX_", case_sensitive=True)

settings = Settings()
```

### 2.3 Type Hinting and Docstring Norms
- Full type annotations are mandatory on public methods, return signatures, and class attributes.
- Use built-in standard types: `dict`, `list`, `str`, `float`, `int`, `bool`, or `typing` generics: `Dict[str, Any]`, `List[Dict[str, Any]]`, `Optional[np.ndarray]`, `Tuple[np.ndarray, Dict[str, Any]]`.
- Docstrings follow Google/Sphinx style, beginning with a high-level summary of the forensic physical phenomenon investigated (e.g. Wiener entropy, vocal fold biomechanics, quadratic phase coupling).

### 2.4 Error Handling and Numerical Stability
Signal processing involves potential mathematical singularities (log of zero, division by zero, empty arrays). The codebase enforces:
- **Epsilon Clamping**: Use `1e-12` for power spectra and division denominators (`+ 1e-12`), and `1e-6` for log transforms (`np.maximum(x, 1e-6)`).
- **Array Clipping**: Bounded score clipping using `np.clip(val, 0.0, 1.0)` or `np.clip(peak_val, 1e-6, 0.99999)` before inverse transforms or log odds.
- **Toeplitz Inversion Fallbacks**: In LPC estimation ([`GlottalFlowDetector._estimate_lpc`](file:///p:/VoxSentinalX/backend/app/detectors/glottal_detector.py#L152-L164)), wrap `scipy.linalg.solve_toeplitz` in a `try...except Exception:` block, returning `None` if matrix is singular.
- **HTTP Exceptions**: In API routes ([`routes.py`](file:///p:/VoxSentinalX/backend/app/api/routes.py)), raise `fastapi.HTTPException` with explicit `status_code=400` for client validation errors (e.g., duration < 0.5s, unreadable audio headers) and `status_code=500` for unexpected pipeline crashes.

---

## 3. Audio DSP Conventions

All audio operations adhere to standardized acoustic parameters across both backend signal processors and frontend audio nodes.

| Parameter | Standard Value | Description | Rationale |
| :--- | :--- | :--- | :--- |
| **Sampling Rate ($F_s$)** | `16000` Hz (16 kHz) | Nyquist frequency = 8 kHz | Telecom standard, optimal for speech analysis without high-frequency storage waste |
| **Channels** | `1` (Mono) | Single channel Float32 | Stereo inputs are downmixed by averaging channels `np.mean(data, axis=1)` |
| **Input PCM Format** | 16-bit Signed Int (`int16`) | Little-endian raw binary bytes | Matches WebSocket audio streaming format from client microphone |
| **Internal Array Type** | `numpy.float32` | Normalized between `[-1.0, 1.0]` | Standard representation for FFT, filterbanks, and neural networks |
| **Analysis Window** | `2.0` seconds | `32000` samples | Sufficient duration for pitch contours, LPC inverse filtering, and formants |
| **Hop Duration** | `1.0` second | `16000` samples (50% overlap) | Delivers 1 Hz real-time diagnostic refresh rate |
| **Circular Buffer** | `10.0` seconds | `160000` samples | Ingestion headroom managed by FIFO eviction in [`StreamBuffer`](file:///p:/VoxSentinalX/backend/app/audio/stream_buffer.py) |

### 3.1 PCM $\leftrightarrow$ Float32 Conversion Standards
Implemented in [`AudioPreprocessor`](file:///p:/VoxSentinalX/backend/app/audio/preprocessor.py#L6-L45):
- **Int16 Bytes to Float32**:
  ```python
  int16_samples = np.frombuffer(raw_bytes, dtype=np.int16)
  float32_array = int16_samples.astype(np.float32) / 32768.0
  ```
- **Float32 to Int16 Bytes**:
  ```python
  clipped = np.clip(audio, -1.0, 1.0)
  int16_bytes = (clipped * 32767.0).astype(np.int16).tobytes()
  ```
- **Energy & Silence Detection**:
  - RMS energy: $\sqrt{\text{mean}(x^2)}$
  - Default silence threshold: $\text{RMS} < 0.005$

### 3.2 Windowing, Filterbanks, and Transform Specifications

Each detector uses specific, calibrated window sizes and transforms:

1. **Spectral Detector** ([`SpectralDetector`](file:///p:/VoxSentinalX/backend/app/detectors/spectral_detector.py)):
   - Welch PSD: `nperseg = min(len(audio), 1024)`
   - Wiener Spectral Flatness: $\exp(\text{mean}(\ln(S))) / (\text{mean}(S) + 10^{-12})$
   - Autocorrelation HNR: Lag range $F_s / 400$ (40 samples) to $F_s / 70$ (228 samples)
   - STFT Phase Coherence: `nperseg = 512`, `noverlap = 256`, 2nd-order discrete phase derivative $\Delta^2 \phi$ across unwrapped phase trajectories.
2. **Prosody Detector** ([`ProsodyDetector`](file:///p:/VoxSentinalX/backend/app/detectors/prosody_detector.py)):
   - Short-time framing: 40 ms frame (`640` samples), 20 ms hop (`320` samples)
   - Pitch ($F_0$) search: 65 Hz to 450 Hz via peak autocorrelation ($\text{threshold} > 0.40$)
   - Micro-Tremor Index: PSD analysis of $F_0$ detrended contour sampled at 50 Hz, bandpass energy isolated at 8–12 Hz.
3. **Respiration Detector** ([`BreathingDetector`](file:///p:/VoxSentinalX/backend/app/detectors/breathing_detector.py)):
   - Framing: 50 ms frames (`800` samples)
   - Breath detection signature: Low energy ($0.003 \le \text{RMS} \le 0.02$) combined with High Zero-Crossing Rate ($\text{ZCR} > 0.15$)
   - Continuous speech accumulator: Triggers anomaly when speech persists $> 6.0$ seconds without an inhalation pause.
4. **Vocoder / Acoustic Artifact Detector** ([`AcousticArtifactDetector`](file:///p:/VoxSentinalX/backend/app/detectors/acoustic_artifacts.py)):
   - PSD resolution: `nperseg = min(len(audio), 2048)`
   - Brickwall cutoff: First derivative of PSD in dB $< -25.0\text{ dB/bin}$ in the 3.5 kHz–7.8 kHz band
   - Spectral tilt: Linear regression of $P_{\text{dB}}$ against $\log_2(f)$ over 200 Hz–7 kHz (human normal: $-6.0$ to $-14.0\text{ dB/octave}$).
5. **LFCC Detector** ([`LFCCDetector`](file:///p:/VoxSentinalX/backend/app/detectors/lfcc_detector.py)):
   - Framing: 25 ms window (`400` samples), 10 ms hop (`160` samples), Hamming window, $N_{\text{FFT}} = 512$
   - Filterbank: 24 linearly-spaced triangular filters spanning $0\text{ Hz}$ to $F_s/2$ ($8000\text{ Hz}$)
   - Cepstrum: DCT-II, retaining 20 static cepstral coefficients ($C_0$ to $C_{19}$)
   - Dynamic Features: $\Delta$ and $\Delta^2$ with regression width $w = 2$.
6. **Glottal Flow Detector** ([`GlottalFlowDetector`](file:///p:/VoxSentinalX/backend/app/detectors/glottal_detector.py)):
   - Framing: 30 ms frame (`480` samples), 15 ms hop (`240` samples)
   - Pre-emphasis: Filter $H(z) = 1 - 0.97 z^{-1}$
   - LPC order: $p = 16$ via Levinson-Durbin recursion
   - Inverse filtering: Glottal residual $e(n) = s(n) + \sum_{k=1}^{16} a_k s(n-k)$
   - Glottal flow estimation: Cumulative integration $\sum e(n)$ followed by linear detrending
   - Normalized Amplitude Quotient: $\text{NAQ} = \frac{f_{\text{ac}}}{d_{\text{peak}} \cdot T_0}$ (biological range: $0.060 - 0.280$).
7. **Laryngeal Perturbation Detector** ([`LaryngealPerturbationDetector`](file:///p:/VoxSentinalX/backend/app/detectors/perturbation_detector.py)):
   - Filter: 4th-order Butterworth lowpass at 800 Hz (SOS filter)
   - Peak picking: Inter-peak intervals bounded by 70 Hz–400 Hz limits
   - Jitter metrics: Local jitter $(\frac{\text{mean}(\Delta p)}{\text{mean}(p)} \times 100\%)$ and RAP (3-point smoothed)
   - Shimmer metrics: Local shimmer $(\frac{\text{mean}(\Delta A)}{\text{mean}(A)} \times 100\%)$ and APQ3 (3-point smoothed).
8. **Bispectrum Phase Detector** ([`BispectrumPhaseDetector`](file:///p:/VoxSentinalX/backend/app/detectors/bispectrum_detector.py)):
   - STFT: $N_{\text{FFT}} = 128$, `noverlap = 64`
   - Bispectrum: $B(k_1, k_2) = \frac{1}{M} \sum_{m=1}^M X_m(k_1) X_m(k_2) X_m^*(k_1 + k_2)$ computed on the principal non-redundant domain ($k_1 + k_2 \le F_s/2$)
   - Normalized Bicoherence: $b^2(k_1, k_2) = \frac{|B(k_1, k_2)|^2}{\text{Norm}(k_1, k_2)}$ in $[0, 1]$. Evaluated in harmonic band 0–1500 Hz.
9. **Deep Neural LCNN Detector** ([`NeuralLCNNDetector`](file:///p:/VoxSentinalX/backend/app/detectors/neural_lcnn_detector.py)):
   - STFT: $N_{\text{FFT}} = 512$, `hop_length = 160` (10 ms)
   - Mel Filterbank: 80 triangular Mel bins from 0 Hz to 8000 Hz
   - Feature Scaling: Log compression followed by zero-mean unit-variance normalization (MVN)
   - Network: Light-CNN with Max-Feature-Map (MFM), BiLSTM context layer, Self-Attention temporal pooling.

---

## 4. Frontend Architecture and TypeScript Conventions

The frontend dashboard is implemented in React 18 with TypeScript in [`frontend/src/`](file:///p:/VoxSentinalX/frontend/src/):
- `components/`: UI components and forensic visualizations.
- `lib/`: Web Audio API capture engine and Canvas 2D oscilloscope visualizers.
- `types/`: Shared TypeScript data contracts and payload schemas.

### 4.1 Component Design and Hook Patterns
- Components are written as functional components typed with `React.FC<Props>`.
- Internal state is managed with standard React hooks: `useState`, `useEffect`, `useRef`, and `useMemo`.
- Clean teardown: All audio nodes, animation frames (`requestAnimationFrame`), timers (`setInterval`), and WebSockets must be cancelled or disconnected in cleanup return functions of `useEffect` or dedicated `stop()` methods.
- Prop interfaces are defined explicitly at the top of each component file (e.g. `LiveCallMonitorProps`, `RiskGaugeProps`, `ForensicRadarProps`).

### 4.2 Tailwind CSS Styling Methodology
The visual design uses a **Cyber/Forensic Defense Aesthetic** configured in [`tailwind.config.js`](file:///p:/VoxSentinalX/frontend/tailwind.config.js):
- **Palette**: Dark foundation (`#070a10`, `#0a0d14`, `#0f1422`), slate borders (`#1e293b`), with cyan (`#06b6d4`), emerald (`#10b981`), amber (`#f59e0b`), and crimson (`#ef4444`) semantic accents.
- **Dynamic Risk Coloring**:
  - `CRITICAL`: Red (`#ef4444`), glow class `glow-red`, border `border-red-500/40`.
  - `HIGH`: Orange (`#f97316`), glow class `glow-amber`, border `border-orange-500/30`.
  - `MODERATE`: Amber (`#f59e0b`), glow class `glow-amber`, border `border-amber-500/30`.
  - `LOW`: Emerald (`#10b981`), glow class `glow-green`, border `border-emerald-500/30`.
- **Custom Animations**: `pulse-slow`, `pulse-glow`, `radar-sweep`, `scanline`, and `float`.
- **Theme Support**: Dark mode default with light mode toggle persisted in `localStorage('vox_theme')`.

### 4.3 Custom Audio Modules

#### 1. Audio Capture Engine ([`VoxSentinalAudioCapture`](file:///p:/VoxSentinalX/frontend/src/lib/audioCapture.ts))
- Uses `navigator.mediaDevices.getUserMedia` with raw speech settings:
  ```typescript
  {
    sampleRate: 16000,
    channelCount: 1,
    echoCancellation: false,
    noiseSuppression: false,
    autoGainControl: true,
  }
  ```
- Downsamples/buffers using `ScriptProcessorNode(4096, 1, 1)` (delivering 256 ms audio blocks at 16 kHz).
- Converts Web Audio `Float32Array` to 16-bit signed integer PCM (`Int16Array`) and streams binary array buffers directly over WebSocket.
- Handles two-step user voiceprint recording and calibration against `/api/calibrate`.

#### 2. Canvas Audio Visualizer ([`CanvasAudioVisualizer`](file:///p:/VoxSentinalX/frontend/src/lib/audioVisualizer.ts))
- Binds to an HTML5 `<canvas>` and an `AnalyserNode` (`fftSize = 512`).
- Operates a 60 FPS animation loop with `requestAnimationFrame`.
- Renders dual-layer forensic visualizers:
  1. Background translucent FFT spectrum bars (`dataArray` from `getByteFrequencyData`).
  2. Foreground neon glowing oscilloscope waveform with shadow blur (`getByteTimeDomainData`).
  3. Dynamic stroke coloring linked to real-time `RiskLevel`.

### 4.4 Data Contracts ([`frontend/src/types/index.ts`](file:///p:/VoxSentinalX/frontend/src/types/index.ts))
The TypeScript schema strictly mirrors the FastAPI JSON serialization:

```typescript
export type RiskLevel = 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
export type AlertType = 'NORMAL' | 'CAUTION' | 'WARNING' | 'IMMEDIATE_ACTION_REQUIRED';

export interface AnomalyItem {
  type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  metric_name: string;
  value: string | number;
  threshold: string;
  description: string;
  source_detector?: string;
}

export interface LayerScores {
  spectral: number;
  prosody: number;
  breathing: number;
  acoustic_artifacts: number;
  lfcc: number;
  glottal: number;
  perturbation: number;
  bispectrum: number;
  neural_lcnn: number;
}

export interface AnalysisUpdate {
  type?: string;
  window_index: number;
  timestamp: string;
  timestamp_sec: number;
  risk_score: number;
  raw_risk_score: number;
  is_spike: boolean;
  risk_level: RiskLevel;
  alert_type: AlertType;
  status_text: string;
  user_message: string;
  recommendation: string;
  suggested_actions: string[];
  diagnostics: AnomalyItem[];
  layer_scores: LayerScores;
  layer_metrics: Record<string, Record<string, any>>;
  speaker_separation: {
    caller_ratio: number;
    user_ratio: number;
    calibrated: boolean;
  };
}
```

---

## 5. Summary of Coding Checklists

Before committing changes to VoxSentinalX:
1. **Audio Compatibility**: Is audio sampled at exactly 16000 Hz, mono Float32, bounded in $[-1.0, 1.0]$?
2. **Detector Compliance**: Does the new detector inherit from `BaseDetector`, define a unique `name`, and return `anomaly_score`, `confidence`, `metrics`, and `anomalies_detected`?
3. **Weight Synchrony**: If a detector is added or modified, is its weight properly assigned in `Settings.DETECTOR_WEIGHTS` in [`config.py`](file:///p:/VoxSentinalX/backend/app/core/config.py) and registered in `DetectionEngine`?
4. **Type Checking**: Have full type annotations been added to Python methods and TypeScript interfaces?
5. **Stability Verification**: Are STFT, LPC, Welch, and bicoherence calculations guarded against division by zero and log of zero with appropriate epsilons?
