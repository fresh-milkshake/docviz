from dataclasses import dataclass
from typing import List


@dataclass
class DetectionResult:
    """
    Data class representing a single detection result.
    Kept for backward compatibility.

    Attributes:
        label (int): The class index of the detected object.
        label_name (str): The class name of the detected object.
        bbox (List[float]): Bounding box coordinates in pixel values [x1, y1, x2, y2].
        confidence (float): Confidence score of the detection.
    """

    label: int
    label_name: str
    bbox: List[float]
    confidence: float
