"""Configuration caching module for improved performance.

This module provides cached factory functions for creating default configurations,
reducing object creation overhead and improving performance.
"""

from functools import lru_cache

from docviz.constants import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    DEFAULT_DEVICE,
    DEFAULT_IMAGE_SIZE,
    DEFAULT_LLM_API_KEY,
    DEFAULT_LLM_BASE_URL,
    DEFAULT_LLM_MODEL,
    DEFAULT_MODEL_FILE,
    DEFAULT_OCR_LANGUAGE,
    DEFAULT_PDF_TEXT_THRESHOLD_CHARS,
    DEFAULT_PREFER_PDF_TEXT,
    DEFAULT_ZOOM_X,
    DEFAULT_ZOOM_Y,
    get_models_path,
)
from docviz.lib.detection.backends import DetectionBackendEnum
from docviz.lib.detection.labels import CanonicalLabel
from docviz.types import DetectionConfig, ExtractionConfig, LLMConfig, OCRConfig


@lru_cache(maxsize=4)
def get_default_detection_config(
    imagesize: int = DEFAULT_IMAGE_SIZE,
    confidence: float = DEFAULT_CONFIDENCE_THRESHOLD,
    device: str = DEFAULT_DEVICE,
    model_file: str = DEFAULT_MODEL_FILE,
) -> DetectionConfig:
    """Get a cached default detection configuration.

    Args:
        imagesize: Image size for detection
        confidence: Confidence threshold for detection
        device: Device to use for detection
        model_file: Model file name to use

    Returns:
        Cached DetectionConfig instance
    """
    return DetectionConfig(
        imagesize=imagesize,
        confidence=confidence,
        device=device,
        layout_detection_backend=DetectionBackendEnum.DOCLAYOUT_YOLO,
        model_path=str(get_models_path() / model_file),
    )


@lru_cache(maxsize=4)
def get_default_extraction_config(
    zoom_x: float = DEFAULT_ZOOM_X,
    zoom_y: float = DEFAULT_ZOOM_Y,
    pdf_text_threshold_chars: int = DEFAULT_PDF_TEXT_THRESHOLD_CHARS,
    prefer_pdf_text: bool = DEFAULT_PREFER_PDF_TEXT,
) -> ExtractionConfig:
    """Get a cached default extraction configuration.

    Args:
        zoom_x: Horizontal zoom factor
        zoom_y: Vertical zoom factor
        pdf_text_threshold_chars: PDF text threshold
        prefer_pdf_text: Whether to prefer PDF text

    Returns:
        Cached ExtractionConfig instance
    """
    return ExtractionConfig(
        page_limit=None,
        zoom_x=zoom_x,
        zoom_y=zoom_y,
        pdf_text_threshold_chars=pdf_text_threshold_chars,
        labels_to_exclude=[],
        prefer_pdf_text=prefer_pdf_text,
    )


@lru_cache(maxsize=4)
def get_default_ocr_config(
    lang: str = DEFAULT_OCR_LANGUAGE,
    include_formulas: bool = True,
) -> OCRConfig:
    """Get a cached default OCR configuration.

    Args:
        lang: OCR language
        include_formulas: Whether to include formulas in chart labels

    Returns:
        Cached OCRConfig instance
    """
    chart_labels = [
        CanonicalLabel.PICTURE.value,
        CanonicalLabel.TABLE.value,
    ]
    if include_formulas:
        chart_labels.append(CanonicalLabel.FORMULA.value)

    return OCRConfig(
        lang=lang,
        chart_labels=chart_labels,
        labels_to_exclude=[
            CanonicalLabel.OTHER.value,
            CanonicalLabel.PAGE_FOOTER.value,
            CanonicalLabel.PAGE_HEADER.value,
            CanonicalLabel.FOOTNOTE.value,
        ],
    )


@lru_cache(maxsize=4)
def get_default_llm_config(
    model: str = DEFAULT_LLM_MODEL,
    api_key: str = DEFAULT_LLM_API_KEY,
    base_url: str = DEFAULT_LLM_BASE_URL,
) -> LLMConfig:
    """Get a cached default LLM configuration.

    Args:
        model: LLM model name
        api_key: API key for LLM
        base_url: Base URL for LLM API

    Returns:
        Cached LLMConfig instance
    """
    return LLMConfig(
        model=model,
        api_key=api_key,
        base_url=base_url,
    )


def clear_config_cache() -> None:
    """Clear all configuration caches.

    This function should be called if configuration constants are updated
    during runtime and cached configurations need to be refreshed.
    """
    get_default_detection_config.cache_clear()
    get_default_extraction_config.cache_clear()
    get_default_ocr_config.cache_clear()
    get_default_llm_config.cache_clear()
