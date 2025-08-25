"""Model caching module for improved performance.

This module provides cached model loading to avoid reloading heavy model files
multiple times, significantly improving performance for repeated operations.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any

from docviz.logging import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=4)
def load_doclayout_yolo_model(model_path: str) -> Any:
    """Load and cache a DoclayoutYolo model.

    Args:
        model_path: Path to the model file

    Returns:
        Loaded model instance

    Raises:
        ImportError: If doclayout_yolo is not available
        FileNotFoundError: If model file does not exist
    """
    try:
        from doclayout_yolo import YOLOv10
    except ImportError as e:
        logger.error("doclayout_yolo package not found")
        raise ImportError("doclayout_yolo package is required") from e

    model_file = Path(model_path)
    if not model_file.exists():
        logger.error(f"Model file not found: {model_path}")
        raise FileNotFoundError(f"Model file not found: {model_path}")

    logger.info(f"Loading DoclayoutYolo model: {model_path}")
    model = YOLOv10(model_path)
    logger.info(f"Successfully loaded model: {model_path}")

    return model


@lru_cache(maxsize=4)
def load_ultralytics_model(model_path: str) -> Any:
    """Load and cache an Ultralytics YOLO model.

    Args:
        model_path: Path to the model file

    Returns:
        Loaded model instance

    Raises:
        ImportError: If ultralytics is not available
        FileNotFoundError: If model file does not exist
    """
    try:
        from ultralytics import YOLO
    except ImportError as e:
        logger.error("ultralytics package not found")
        raise ImportError("ultralytics package is required") from e

    model_file = Path(model_path)
    if not model_file.exists():
        logger.error(f"Model file not found: {model_path}")
        raise FileNotFoundError(f"Model file not found: {model_path}")

    logger.info(f"Loading Ultralytics model: {model_path}")
    model = YOLO(model_path)
    logger.info(f"Successfully loaded model: {model_path}")

    return model


def clear_model_cache() -> None:
    """Clear all cached models.

    This function should be called to free memory or when model files
    have been updated and need to be reloaded.
    """
    logger.info("Clearing model cache")
    load_doclayout_yolo_model.cache_clear()
    load_ultralytics_model.cache_clear()
    logger.info("Model cache cleared")


def get_model_cache_info() -> dict[str, Any]:
    """Get information about cached models.

    Returns:
        Dictionary containing cache statistics
    """
    return {
        "doclayout_yolo_cache": load_doclayout_yolo_model.cache_info(),
        "ultralytics_cache": load_ultralytics_model.cache_info(),
    }
