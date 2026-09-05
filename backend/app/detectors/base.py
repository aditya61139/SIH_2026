"""Base Detector Interface for VoxSentinalX."""
from abc import ABC, abstractmethod
from typing import Dict, Any
import numpy as np


class BaseDetector(ABC):
    """Abstract Base Class for all forensic voice analysis detectors."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the detector."""
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
