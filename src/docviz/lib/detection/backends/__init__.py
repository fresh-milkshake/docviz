from enum import Enum

from .doclayout_yolo import DoclayoutYoloBackend
from .yolo_doclaynet import YoloDoclaynetBackend


class DetectionBackendEnum(Enum):
    DOCLAYOUT_YOLO = "doclayout_yolo"
    YOLO_DOCLAYNET = "yolo_doclaynet"


__all__ = ["DoclayoutYoloBackend", "YoloDoclaynetBackend", "DetectionBackendEnum"]
