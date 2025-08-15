
import numpy as np

from docviz.lib.detection.backends import (
    DetectionBackendEnum,
    DoclayoutYoloBackend,
    YoloDoclaynetBackend,
)
from docviz.lib.detection.backends.base import DetectionResult
from docviz.types import DetectionConfig


class Detector:
    """
    Document layout detector supporting multiple backends.

    Attributes:
        backend (DetectionBackend): The backend type used for detection.
        model_path (str): Path to the model file.
        detector (DoclayoutYoloBackend | YoloDoclaynetBackend): The backend detector instance.
    """

    def __init__(
        self,
        backend: DetectionBackendEnum | str,
        model_path: str,
        settings: DetectionConfig,
    ) -> None:
        """
        Initialize the Detector with the specified backend and model path.

        Args:
            backend (DetectionBackend): The backend type to use.
            model_path (str): Path to the model file.
            settings (Settings): The settings for the backend.
        """
        if isinstance(backend, str):
            backend = DetectionBackendEnum(backend)

        self.backend = backend
        self.model_path = model_path
        self.detector = self._create_detector(settings)

    def _create_detector(
        self, settings: DetectionConfig
    ) -> DoclayoutYoloBackend | YoloDoclaynetBackend:
        """
        Create the backend detector instance.

        Returns:
            DoclayoutYoloBackend | YoloDoclaynetBackend: The backend detector instance.

        Raises:
            ValueError: If the backend is not supported.
        """
        if self.backend == DetectionBackendEnum.DOCLAYOUT_YOLO:
            return DoclayoutYoloBackend(self.model_path, settings)
        if self.backend == DetectionBackendEnum.YOLO_DOCLAYNET:
            return YoloDoclaynetBackend(self.model_path, settings)
        raise ValueError(f"Unsupported detection backend: {self.backend}")

    def parse_layout(self, image: np.ndarray, **kwargs) -> list[DetectionResult]:
        """
        Detect document layout objects in the given image.

        Args:
            image (np.ndarray): Image to detect objects in.
            **kwargs: Additional keyword arguments for the backend detector.

        Returns:
            List[DetectionResult]: List of detection results.
        """
        if hasattr(self.detector, "detect"):
            detections = self.detector.detect(image, **kwargs)
            detections.sort(key=lambda x: x.bbox[1])
            return detections
        raise RuntimeError(
            f"Detection backend {self.backend.__class__} does not implement 'detect' method."
        )

    def get_possible_labels(self) -> list[str]:
        """
        Get the possible labels for the current backend (canonicalized per-backend).
        """
        if self.backend == DetectionBackendEnum.DOCLAYOUT_YOLO:
            return DoclayoutYoloBackend.get_supported_labels()
        if self.backend == DetectionBackendEnum.YOLO_DOCLAYNET:
            return YoloDoclaynetBackend.get_supported_labels()
        if hasattr(self.detector, "get_supported_labels"):
            return self.detector.get_supported_labels()  # type: ignore[attr-defined]
        # Fallback to model names if backend does not implement supported labels
        if hasattr(self.detector, "model") and hasattr(self.detector.model, "names"):
            # Normalize formatting for presentation
            names = []
            for name in self.detector.model.names:  # type: ignore[attr-defined]
                key = str(name).strip().lower().replace("_", "-").replace(" ", "-")
                names.append(key)
            return names
        raise RuntimeError(
            f"Detection backend {self.backend.__class__} does not expose supported labels."
        )
