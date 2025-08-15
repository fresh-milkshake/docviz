
import numpy as np
from ultralytics import YOLO

from docviz.lib.detection.backends.base import BaseDetectionBackend
from docviz.lib.detection.deduplication import remove_duplicates_nms
from docviz.lib.detection.labels import CanonicalLabel
from docviz.logging import get_logger
from docviz.types import DetectionConfig, DetectionResult

logger = get_logger(__name__)


class YoloDoclaynetBackend(BaseDetectionBackend):
    """
    Detector for running YOLO detection and returning detection results.

    Attributes:
        model_path (str): Path to the YOLO model file.
    """

    def __init__(
        self,
        model_path: str,
        _: DetectionConfig,
    ) -> None:
        """
        Initialize the Detector with a YOLO model.

        Args:
            model_path (str): Path to the YOLO model file.
        """
        logger.info(f"Initializing YoloDoclaynetBackend with model: {model_path}")
        self.model_path = model_path
        self.model = YOLO(self.model_path)
        logger.info("YoloDoclaynetBackend initialized successfully")

    def detect(
        self,
        image: np.ndarray,
    ) -> list[DetectionResult]:
        """
        Run detection on an image and return detection results.

        Args:
            image (np.ndarray): Image to detect objects in.

        Returns:
            List[DetectionResult]: List of detection results.

        Raises:
            FileNotFoundError: If the image cannot be loaded.
        """
        logger.debug(f"Running layout detection on shape: {image.shape}")

        result = self.model(image)[0]
        height, width = image.shape[:2]

        detections: list[DetectionResult] = []
        for label, box, conf in zip(
            result.boxes.cls.tolist(),
            result.boxes.xyxyn.tolist(),
            result.boxes.conf.tolist(), strict=False,
        ):
            label_idx = int(label)
            bbox = [
                float(box[0]) * width,
                float(box[1]) * height,
                float(box[2]) * width,
                float(box[3]) * height,
            ]
            confidence = float(conf)
            unified_label_name = self.normalize_label(result.names[label_idx])
            detection = DetectionResult(
                label=label_idx,
                label_name=unified_label_name,
                bbox=bbox,
                confidence=confidence,
            )
            detections.append(detection)
            logger.debug(f"Detection: {detection.label_name} at {bbox} (conf: {confidence:.3f})")

        logger.info(f"Layout detection completed: {len(detections)} objects found")

        count_before = len(detections)
        detections = remove_duplicates_nms(detections)
        count_after = len(detections)
        logger.info(f"Removed {count_before - count_after} duplicates")

        return detections

    # {0: 'Caption',
    #  1: 'Footnote',
    #  10: 'Title',
    #  2: 'Formula',
    #  3: 'List-item',
    #  4: 'Page-footer',
    #  5: 'Page-header',
    #  6: 'Picture',
    #  7: 'Section-header',
    #  8: 'Table',
    #  9: 'Text'}

    _ALIASES: dict[str, CanonicalLabel] = {
        "caption": CanonicalLabel.CAPTION,
        "footnote": CanonicalLabel.FOOTNOTE,
        "title": CanonicalLabel.TITLE,
        "formula": CanonicalLabel.FORMULA,
        "list-item": CanonicalLabel.LIST_ITEM,
        "page-footer": CanonicalLabel.PAGE_FOOTER,
        "page-header": CanonicalLabel.PAGE_HEADER,
        "picture": CanonicalLabel.PICTURE,
        "section-header": CanonicalLabel.SECTION_HEADER,
        "table": CanonicalLabel.TABLE,
        "text": CanonicalLabel.TEXT,
    }

    @classmethod
    def normalize_label(cls, raw_label: str) -> str:
        key = raw_label.strip().lower().replace("-", "_")
        if key in cls._ALIASES:
            return cls._ALIASES[key].value
        return key

    @classmethod
    def get_supported_labels(cls) -> list[str]:
        return [i.value for i in cls._ALIASES.values()]

    @classmethod
    def get_original_labels(cls) -> list[str]:
        return list(cls._ALIASES.keys())
