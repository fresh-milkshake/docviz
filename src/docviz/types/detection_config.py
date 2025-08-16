from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from docviz.lib.detection import DetectionBackendEnum


@dataclass
class DetectionConfig:
    """
    Configuration for detection.

    Attributes:
        imagesize (int): The size of the image to detect.
        confidence (float): The confidence threshold for the detection.
        device (str): The device to use for the detection.
    """

    imagesize: int
    confidence: float
    device: str

    layout_detection_backend: "DetectionBackendEnum"
    model_path: str
