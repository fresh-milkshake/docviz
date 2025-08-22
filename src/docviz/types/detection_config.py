from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from docviz.lib.detection import DetectionBackendEnum


@dataclass
class DetectionConfig:
    """Configuration for document layout detection and analysis.

    This configuration class controls the behavior of the document layout detection
    system, which identifies and locates different content types (text, tables,
    figures, equations) within document pages.

    The detection system uses computer vision models to analyze document images and
    identify regions of interest. This configuration allows fine-tuning of the
    detection process for optimal performance and accuracy.

    Attributes:
        imagesize (int): The size of the image to process for detection. Larger images
            generally provide better accuracy but require more computational resources.
            Common values are 512, 1024, or 2048. Default is typically 1024.
        confidence (float): The confidence threshold for detection results. Only detections
            with confidence scores above this threshold are included in results.
            Range: 0.0 to 1.0. Higher values are more selective but may miss valid
            content. Lower values include more content but may include false positives.
        device (str): The computing device to use for detection. Options include "cpu",
            "cuda", "mps" (Apple Silicon), or specific device identifiers like
            "cuda:0". Use "cpu" for compatibility, "cuda" for NVIDIA GPUs.
        layout_detection_backend (DetectionBackendEnum): The detection backend to use. Different backends
            may use different models or algorithms for layout detection. Options
            include various YOLO-based models and other detection frameworks.
        model_path (str): Path to the detection model file. This should point to a valid
            model file compatible with the specified backend. The model file contains
            the trained weights and architecture for the detection system.

    Example:
        >>> # Basic CPU configuration
        >>> config = DetectionConfig(
        ...     imagesize=1024,
        ...     confidence=0.5,
        ...     device="cpu",
        ...     layout_detection_backend=DetectionBackendEnum.DOCLAYOUT_YOLO,
        ...     model_path="/path/to/model.pt"
        ... )
        >>>
        >>> # High-accuracy GPU configuration
        >>> config = DetectionConfig(
        ...     imagesize=2048,
        ...     confidence=0.7,
        ...     device="cuda",
        ...     layout_detection_backend=DetectionBackendEnum.DOCLAYOUT_YOLO,
        ...     model_path="/path/to/model.pt"
        ... )
    """

    imagesize: int
    confidence: float
    device: str

    layout_detection_backend: "DetectionBackendEnum"
    model_path: str
