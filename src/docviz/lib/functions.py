from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

from docviz.constants import MODELS_PATH
from docviz.lib.detection.backends import DetectionBackendEnum
from docviz.lib.detection.labels import CanonicalLabel
from docviz.lib.extraction import pipeline
from docviz.types import (
    DetectionConfig,
    ExtractionConfig,
    ExtractionResult,
    ExtractionType,
    LLMConfig,
    OCRConfig,
)

if TYPE_CHECKING:
    from .document import Document


def batch_extract(
    documents: list["Document"],
    extraction_config: ExtractionConfig | None = None,
    detection_config: DetectionConfig | None = None,
    includes: list[ExtractionType] | None = None,
    progress_callback: Callable[[int], None] | None = None,
) -> list[ExtractionResult]:
    """Extract content from multiple documents in batch.

    Args:
        documents: List of Document objects to process.
        extraction_config: Configuration for extraction.
        detection_config: Configuration for detection.
        includes: Types of content to include.
        progress_callback: Optional callback for progress tracking.

    Returns:
        List of ExtractionResult objects.
    """
    results = []
    for i, document in enumerate(documents):
        result = extract_content_sync(
            document, extraction_config, detection_config, includes, progress_callback
        )
        results.append(result)
        if progress_callback:
            progress_callback(i + 1)
    return results


async def extract_content(
    document: "Document",
    extraction_config: ExtractionConfig | None = None,
    detection_config: DetectionConfig | None = None,
    includes: list[ExtractionType] | None = None,
    progress_callback: Callable[[int], None] | None = None,
    ocr_config: OCRConfig | None = None,
    llm_config: LLMConfig | None = None,
) -> ExtractionResult:
    if extraction_config is None:
        extraction_config = ExtractionConfig()
    if detection_config is None:
        detection_config = DetectionConfig(
            imagesize=1024,
            confidence=0.5,
            device="cpu",
            layout_detection_backend=DetectionBackendEnum.DOCLAYOUT_YOLO,
            model_path=str(MODELS_PATH / "doclayout_yolo_docstructbench_imgsz1024.pt"),
        )
    if ocr_config is None:
        ocr_config = OCRConfig(
            lang="eng",
            chart_labels=[
                CanonicalLabel.PICTURE.value,
                CanonicalLabel.TABLE.value,
                CanonicalLabel.FORMULA.value,
            ],
            labels_to_exclude=[
                CanonicalLabel.OTHER.value,
                CanonicalLabel.PAGE_FOOTER.value,
                CanonicalLabel.PAGE_HEADER.value,
                CanonicalLabel.FOOTNOTE.value,
            ],
        )
    if llm_config is None:
        llm_config = LLMConfig(
            model="gemma3",
            api_key="dummy-key",
            base_url="http://localhost:11434/v1",
        )
    if includes is None:
        includes = ExtractionType.get_all()

    # Handle ExtractionType.ALL
    if ExtractionType.ALL in includes:
        includes = ExtractionType.get_all()

    # TODO: Implement actual async pipeline
    # For now, call the sync version
    return extract_content_sync(
        document,
        extraction_config,
        detection_config,
        includes,
        progress_callback,
        ocr_config,
        llm_config,
    )


def extract_content_sync(
    document: "Document",
    extraction_config: ExtractionConfig | None = None,
    detection_config: DetectionConfig | None = None,
    includes: list[ExtractionType] | None = None,
    progress_callback: Callable[[int], None] | None = None,
    ocr_config: OCRConfig | None = None,
    llm_config: LLMConfig | None = None,
) -> ExtractionResult:
    """Synchronous version of extract_content.

    Args:
        document: Document to extract content from.
        extraction_config: Configuration for extraction.
        detection_config: Configuration for detection.
        includes: Types of content to include.
        progress_callback: Optional callback for progress tracking.
        ocr_config: Configuration for OCR.
        llm_config: Configuration for LLM.

    Returns:
        ExtractionResult containing extracted content.
    """
    if extraction_config is None:
        extraction_config = ExtractionConfig()
    if detection_config is None:
        detection_config = DetectionConfig(
            imagesize=1024,
            confidence=0.5,
            device="cpu",
            layout_detection_backend=DetectionBackendEnum.DOCLAYOUT_YOLO,
            model_path=str(MODELS_PATH / "doclayout_yolo_docstructbench_imgsz1024.pt"),
        )
    if ocr_config is None:
        ocr_config = OCRConfig(
            lang="eng",
            chart_labels=[
                CanonicalLabel.PICTURE.value,
                CanonicalLabel.TABLE.value,
                CanonicalLabel.FORMULA.value,
            ],
            labels_to_exclude=[
                CanonicalLabel.OTHER.value,
                CanonicalLabel.PAGE_FOOTER.value,
                CanonicalLabel.PAGE_HEADER.value,
                CanonicalLabel.FOOTNOTE.value,
            ],
        )
    if llm_config is None:
        llm_config = LLMConfig(
            model="gemma3",
            api_key="dummy-key",
            base_url="http://localhost:11434/v1",
        )
    if includes is None:
        includes = ExtractionType.get_all()

    # Handle ExtractionType.ALL
    if ExtractionType.ALL in includes:
        includes = ExtractionType.get_all()

    # TODO: Replace with actual pipeline call when ready
    # For now, return empty result as placeholder
    try:
        _results = pipeline(
            document_path=document.file_path,
            output_dir=Path("output"),
            detection_config=detection_config,
            extraction_config=extraction_config,
            ocr_config=ocr_config,
            llm_config=llm_config,
            includes=includes,
        )

        # TODO: Convert pipeline results to ExtractionResult
        # This is a placeholder - actual implementation depends on pipeline return format
        return ExtractionResult(entries=[])

    except Exception as e:
        # Log error and return empty result for now
        print(f"Pipeline execution failed: {e}")
        return ExtractionResult(entries=[])
