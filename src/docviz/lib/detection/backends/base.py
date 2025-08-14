from abc import ABC, abstractmethod
from typing import List, TypeAlias

import numpy as np

from docviz.types import DetectionConfig, DetectionResult

DetectionResults: TypeAlias = List[DetectionResult]


class BaseDetectionBackend(ABC):
    """
    Base class for detection backends.
    """

    @abstractmethod
    def __init__(self, model_path: str, settings: DetectionConfig) -> None:
        """
        Initialize the detection backend.
        """
        pass

    @abstractmethod
    def detect(
        self,
        image: np.ndarray,
    ) -> DetectionResults:
        """
        Detect objects in an image and return detection results.

        Args:
            image (np.ndarray): Image to detect objects in.

        Returns:
            List[DetectionResult]: List of detection results.
        """
        pass

    @classmethod
    @abstractmethod
    def get_supported_labels(cls) -> list[str]:
        """Return the list of canonical labels this backend can emit.

        Labels must be lowercase and use hyphens instead of spaces/underscores.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def normalize_label(cls, raw_label: str) -> str:
        """Normalize a raw backend label to the canonical one for this backend."""
        raise NotImplementedError


    @classmethod
    @abstractmethod
    def get_original_labels(cls) -> list[str]:
        """Return the list of original labels this backend can emit."""
        raise NotImplementedError