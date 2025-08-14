import numpy as np
from pathlib import Path
from typing import Any

import cv2

from docviz.logging import get_logger
from docviz.types import DetectionResult

logger = get_logger(__name__)


def _generate_vibrant_colors(n: int) -> list[tuple[int, int, int]]:
    """
    Generate n visually distinct pale CMYK-like BGR colors.

    This uses low saturation and high value in HSV to achieve a soft, print-like palette.

    Args:
        n (int): Number of colors to generate.

    Returns:
        list[tuple[int, int, int]]: List of pale BGR color tuples.
    """
    if n <= 0:
        return []
    # Low saturation, high value for pastel/pale colors
    hsvs = [(int(i * 180 / n), 80, 240) for i in range(n)]
    colors = [
        cv2.cvtColor(np.uint8([[[h, s, v]]]), cv2.COLOR_HSV2BGR)[0, 0]  # type: ignore
        for h, s, v in hsvs
    ]  # type: ignore
    # Slightly blend with white to soften further
    blended: list[tuple[int, int, int]] = []
    for bgr in colors:
        b, g, r = int(bgr[0]), int(bgr[1]), int(bgr[2])
        b = int(round(0.8 * b + 0.2 * 255))
        g = int(round(0.8 * g + 0.2 * 255))
        r = int(round(0.8 * r + 0.2 * 255))
        blended.append((b, g, r))
    return blended


def _make_pale_color(bgr: tuple[int, int, int]) -> tuple[int, int, int]:
    """Convert an arbitrary BGR color to a pale CMYK-like tone.

    The function reduces saturation, increases value, and blends slightly with white.

    Args:
        bgr (tuple[int, int, int]): Input BGR color.

    Returns:
        tuple[int, int, int]: Pale BGR color.
    """
    color_arr = np.array([[[bgr[0], bgr[1], bgr[2]]]], dtype=np.uint8)
    hsv = cv2.cvtColor(color_arr, cv2.COLOR_BGR2HSV)[0, 0]  # type: ignore
    h, s, v = int(hsv[0]), int(hsv[1]), int(hsv[2])
    s = min(s, 80)
    v = max(v, 240)
    pale_bgr = cv2.cvtColor(np.uint8([[[h, s, v]]]), cv2.COLOR_HSV2BGR)[0, 0]  # type: ignore
    b, g, r = int(pale_bgr[0]), int(pale_bgr[1]), int(pale_bgr[2])
    # Soft blend with white for a print-like feel
    b = int(round(0.85 * b + 0.15 * 255))
    g = int(round(0.85 * g + 0.15 * 255))
    r = int(round(0.85 * r + 0.15 * 255))
    return (b, g, r)


class FileAnnotator:
    """
    Annotates an image with bounding boxes and labels using configurable drawing options.
    Each label is assigned a unique vibrant color.
    """

    def __init__(
        self,
        image_path: Path,
        detections: list[DetectionResult],
        line_width: int = 2,
        font_size: float = 2,
        font_thickness: int = 2,
        font_family: int = cv2.FONT_HERSHEY_SIMPLEX,
        line_type: int = cv2.LINE_AA,
        line_color: tuple[int, int, int] | None = None,
        sort_by_y: bool = True,
    ) -> None:
        """
        Initialize the Annotator.

        Args:
            image_path (Path): Path to the input image.
            detections (list[DetectionResult]): List of detection results to annotate.
            line_width (int, optional): Width of the bounding box lines.
            font_size (float, optional): Font size for labels.
            font_thickness (int, optional): Thickness of label text.
            font_family (int, optional): OpenCV font family constant.
            line_type (int, optional): OpenCV line type.
            line_color (tuple[int, int, int], optional): Default color for bounding box (BGR).
        """
        self.image_path = image_path
        self.detections = detections
        self.line_width = line_width
        self.font_size = font_size
        self.font_thickness = font_thickness  # * max(1, int(round(font_size)))
        self.font_family = font_family
        self.line_type = line_type
        self.line_color = line_color
        self.sort_by_y = sort_by_y
        self.label_colors = self._assign_label_colors()

    def _assign_label_colors(self) -> dict[Any, tuple[int, int, int]]:
        """
        Assign a unique vibrant color to each label in the detections.

        Returns:
            dict[Any, tuple[int, int, int]]: Mapping from label to BGR color.
        """
        labels: list[str] = []
        for det in self.detections:
            label = getattr(det, "label_name", str(det.label))
            if label not in labels:
                labels.append(label)
        colors = _generate_vibrant_colors(len(labels))
        return {label: color for label, color in zip(labels, colors)}

    def annotate(self) -> np.ndarray:
        """
        Annotate the image with bounding boxes and labels, each with a unique vibrant color.

        Returns:
            np.ndarray: Annotated image as a numpy array.

        Raises:
            FileNotFoundError: If the image cannot be loaded.
        """
        image = cv2.imread(str(self.image_path), cv2.IMREAD_COLOR)
        if image is None:
            raise FileNotFoundError(f"Could not load image at {self.image_path}")

        for detection in self.detections:
            x1, y1, x2, y2 = map(int, detection.bbox)
            label = getattr(detection, "label_name", str(detection.label))
            base_color: tuple[int, int, int] = self.line_color or self.label_colors.get(
                label, (0, 0, 0)
            )
            color = _make_pale_color(base_color)

            cv2.rectangle(
                image,
                (x1, y1),
                (x2, y2),
                color,
                self.line_width,
                self.line_type,
            )
            text_size, baseline = cv2.getTextSize(
                label,
                self.font_family,
                self.font_size,
                self.font_thickness,
            )
            text_width, text_height = text_size
            # text_x, text_y = x1, max(y1 - 5, text_height + 2)
            text_x, text_y = x1, max(y1 - self.line_width, text_height + 2)
            # print("max(y1 - 5, text_height + 2)")
            # print(f"max({y1} - 5, {text_height} + 2) = {max(y1 - 5, text_height + 2)}")

            cv2.rectangle(
                image,
                (text_x - self.line_width, text_y - text_height - baseline),
                (text_x + text_width, text_y),
                color,
                thickness=-1,
            )
            cv2.putText(
                image,
                label,
                (text_x, text_y),
                self.font_family,
                self.font_size,
                (0, 0, 0),
                self.font_thickness,
                self.line_type,
            )

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image


class NumpyAnnotator:
    """
    Annotates an image with bounding boxes and labels using configurable drawing options.
    Each label is assigned a unique vibrant color.
    """

    def __init__(
        self,
        image: np.ndarray,
        detections: list[DetectionResult],
        line_width: int = 2,
        font_size: float = 2,
        font_thickness: int = 2,
        font_family: int = cv2.FONT_HERSHEY_SIMPLEX,
        line_type: int = cv2.LINE_AA,
        line_color: tuple[int, int, int] | None = None,
        sort_by_y: bool = True,
    ) -> None:
        """
        Initialize the Annotator.

        Args:
            image_path (Path): Path to the input image.
            detections (list[DetectionResult]): List of detection results to annotate.
            line_width (int, optional): Width of the bounding box lines.
            font_size (float, optional): Font size for labels.
            font_thickness (int, optional): Thickness of label text.
            font_family (int, optional): OpenCV font family constant.
            line_type (int, optional): OpenCV line type.
            line_color (tuple[int, int, int], optional): Default color for bounding box (BGR).
        """
        self.image = image
        self.detections = detections
        self.line_width = line_width
        self.font_size = font_size
        self.font_thickness = font_thickness  # * max(1, int(round(font_size)))
        self.font_family = font_family
        self.line_type = line_type
        self.line_color = line_color
        self.sort_by_y = sort_by_y
        self.label_colors = self._assign_label_colors()

    def _assign_label_colors(self) -> dict[Any, tuple[int, int, int]]:
        """
        Assign a unique vibrant color to each label in the detections.

        Returns:
            dict[Any, tuple[int, int, int]]: Mapping from label to BGR color.
        """
        labels: list[str] = []
        for det in self.detections:
            label = getattr(det, "label_name", str(det.label))
            if label not in labels:
                labels.append(label)
        colors = _generate_vibrant_colors(len(labels))
        return {label: color for label, color in zip(labels, colors)}

    def annotate(self) -> np.ndarray:
        """
        Draws bounding boxes and labels on the image for each detection.

        Returns:
            Annotated image as a numpy ndarray.
        """
        annotated_image = self.image.copy()
        for detection in self.detections:
            x1, y1, x2, y2 = map(int, detection.bbox)
            label = getattr(detection, "label_name", str(detection.label))
            base_color: tuple[int, int, int] = self.line_color or self.label_colors.get(
                label, (0, 0, 0)
            )
            color = _make_pale_color(base_color)

            cv2.rectangle(
                annotated_image,
                (x1, y1),
                (x2, y2),
                color,
                self.line_width,
                self.line_type,
            )
            text_size, baseline = cv2.getTextSize(
                label,
                self.font_family,
                self.font_size,
                self.font_thickness,
            )
            text_width, text_height = text_size
            text_x, text_y = x1, max(y1 - self.line_width, text_height + 2)

            cv2.rectangle(
                annotated_image,
                (text_x - self.line_width, text_y - text_height - baseline),
                (text_x + text_width, text_y),
                color,
                thickness=-1,
            )
            cv2.putText(
                annotated_image,
                label,
                (text_x, text_y),
                self.font_family,
                self.font_size,
                (0, 0, 0),
                self.font_thickness,
                self.line_type,
            )

        return annotated_image
