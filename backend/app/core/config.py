"""Core configuration module for VoxSentinalX with 8-Vector Forensic Decomposition."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict, List


class Settings(BaseSettings):
    PROJECT_NAME: str = "VoxSentinalX"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"
    DEBUG: bool = True

    # Audio Ingestion Settings
    SAMPLE_RATE: int = 16000                # Expected sample rate: 16 kHz
    CHANNELS: int = 1                       # Mono
    WINDOW_DURATION_SEC: float = 2.0        # 2.0 second analysis window
    HOP_DURATION_SEC: float = 1.0           # 1.0 second slide / hop (50% overlap)
    BUFFER_CAPACITY_SEC: float = 10.0       # 10.0 second circular memory buffer

    @property
    def WINDOW_SAMPLES(self) -> int:
        return int(self.SAMPLE_RATE * self.WINDOW_DURATION_SEC)  # 32000 samples

    @property
    def HOP_SAMPLES(self) -> int:
        return int(self.SAMPLE_RATE * self.HOP_DURATION_SEC)      # 16000 samples

    @property
    def BUFFER_CAPACITY_SAMPLES(self) -> int:
        return int(self.SAMPLE_RATE * self.BUFFER_CAPACITY_SEC)   # 160000 samples

    # Risk Classification Thresholds
    RISK_THRESHOLD_LOW: float = 0.30        # 0.00 - 0.30: Normal / Genuine
    RISK_THRESHOLD_MODERATE: float = 0.60   # 0.30 - 0.60: Caution / Inconclusive
    RISK_THRESHOLD_HIGH: float = 0.80       # 0.60 - 0.80: Warning / Probable Fake
    # 0.80 - 1.00: Critical Alert / Synthetic

    # Dynamic Weightings for 8-Vector Forensic Fusion Layer
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

    # Temporal Smoothing (Exponential Moving Average)
    EMA_ALPHA: float = 0.35                 # Responsiveness vs smoothness factor
    SPIKE_DELTA_THRESHOLD: float = 0.28     # Rapid jump detection threshold

    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(env_prefix="VOXSENTINALX_", case_sensitive=True)


settings = Settings()
