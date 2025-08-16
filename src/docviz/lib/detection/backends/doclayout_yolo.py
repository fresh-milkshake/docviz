import numpy as np
from doclayout_yolo import YOLOv10
from doclayout_yolo.engine.results import Results

from docviz.lib.detection.backends.base import BaseDetectionBackend
from docviz.lib.detection.deduplication import remove_duplicates_nms
from docviz.lib.detection.labels import CanonicalLabel
from docviz.logging import get_logger
from docviz.types import DetectionConfig, DetectionResult

logger = get_logger(__name__)


class DoclayoutYoloBackend(BaseDetectionBackend):
    """
    Backend for document layout detection using YOLOv10 from doclayout_yolo.

    Attributes:
        model (YOLOv10): The loaded YOLOv10 model for detection.
    """

    def __init__(self, model_path: str, settings: DetectionConfig) -> None:
        """
        Initialize the DoclayoutYoloBackend with a YOLOv10 model.

        Args:
            model_path (str): Path to the YOLOv10 model file.
        """
        logger.info(f"Initializing DoclayoutYoloBackend with model: {model_path}")
        self.model = YOLOv10(model_path)
        logger.info("DoclayoutYoloBackend initialized successfully")

        self.imgsz = settings.imagesize
        self.conf = settings.confidence
        self.device = settings.device

    def detect(
        self,
        image: np.ndarray,
    ) -> list[DetectionResult]:
        """
        Run document layout detection on an image.

        Args:
            image (np.ndarray): Image to detect objects in.
            imgsz (int, optional): Prediction image size. Defaults to 1024.
            conf (float, optional): Confidence threshold. Defaults to 0.7.
            device (str, optional): Device to use for inference (e.g., 'cuda:0' or 'cpu'). Defaults to "cpu".

        Returns:
            List[DetectionResult]: List of detection results.
        """
        logger.debug(f"Running layout detection on shape: {image.shape}")

        results: list[Results] = self.model.predict(
            image,
            imgsz=self.imgsz,
            conf=self.conf,
            device=self.device,
        )

        detections: list[DetectionResult] = []
        for result in results:
            if hasattr(result, "boxes") and result.boxes is not None:
                boxes = result.boxes
                height, width = result.orig_shape

            if not (hasattr(boxes, "cls") and hasattr(boxes, "conf") and hasattr(boxes, "xyxyn")):
                continue

            for label, box, conf in zip(
                boxes.cls.tolist(),
                boxes.xyxyn.tolist(),
                boxes.conf.tolist(),
                strict=False,
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
                logger.debug(
                    f"Detection: {detection.label_name} at {bbox} (conf: {confidence:.3f})"
                )

        logger.info(f"Layout detection completed: {len(detections)} objects found")

        count_before = len(detections)
        detections = remove_duplicates_nms(detections)
        count_after = len(detections)
        logger.info(f"Removed {count_before - count_after} duplicates")

        return detections

    # {0: 'title',
    #  1: 'plain text',
    #  2: 'abandon',
    #  3: 'figure',
    #  4: 'figure_caption',
    #  5: 'table',
    #  6: 'table_caption',
    #  7: 'table_footnote',
    #  8: 'isolate_formula',
    #  9: 'formula_caption'}

    _ALIASES: dict[str, CanonicalLabel] = {
        "title": CanonicalLabel.TITLE,
        "plain text": CanonicalLabel.TEXT,
        "figure": CanonicalLabel.PICTURE,
        "figure_caption": CanonicalLabel.PICTURE_CAPTION,
        "table_caption": CanonicalLabel.TABLE_CAPTION,
        "formula_caption": CanonicalLabel.FORMULA_CAPTION,
        "table": CanonicalLabel.TABLE,
        "table_footnote": CanonicalLabel.TABLE_FOOTNOTE,
        "isolate_formula": CanonicalLabel.FORMULA,
        "abandon": CanonicalLabel.OTHER,
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
