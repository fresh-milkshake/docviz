from typing import List
from pathlib import Path

import numpy as np
import cv2

from docviz.types import DetectionResult


def filter_detections(
    detections: List[DetectionResult],
    labels_to_include: List[str] = [],
    labels_to_exclude: List[str] = [],
) -> List[DetectionResult]:
    """
    Filter detections to only include elements with specified labels.

    Args:
        detections (List[DetectionResult]): List of all detections.
        labels (List[str]): List of lowercased labels to filter by.

    Returns:
        List[DetectionResult]: Filtered list containing only detections with specified labels.
    """

    if labels_to_include:
        detections = [
            det for det in detections if det.label_name.lower() in labels_to_include
        ]
    if labels_to_exclude:
        detections = [
            det for det in detections if det.label_name.lower() not in labels_to_exclude
        ]
    return detections


def load_rgb_image(image_path: Path) -> np.ndarray:
    """
    Load an image from the given path and convert it to RGB format.

    Args:
        image_path (Path): Path to the image file.

    Returns:
        np.ndarray: Image in RGB format.
    """
    image_bgr: np.ndarray | None = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise FileNotFoundError(f"Image not found at {image_path}")
    image_rgb: np.ndarray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    return image_rgb
