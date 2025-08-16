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
) -> list[ExtractionResult]:
    return [
        extract_content_sync(document, extraction_config, detection_config, includes)
        for document in documents
    ]


async def extract_content(
    document: "Document",
    extraction_config: ExtractionConfig | None = None,
    detection_config: DetectionConfig | None = None,
    ocr_config: OCRConfig | None = None,
    llm_config: LLMConfig | None = None,
    includes: list[ExtractionType] | None = None,
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

    results = pipeline(
        document_path=document.file_path,
        output_dir=Path("output"),
        detection_config=detection_config,
        extraction_config=extraction_config,
        ocr_config=ocr_config,
        llm_config=llm_config,
        includes=includes,
    )

    return ExtractionResult(entries=[])


def extract_content_sync(
    document: "Document",
    extraction_config: ExtractionConfig | None = None,
    detection_config: DetectionConfig | None = None,
    includes: list[ExtractionType] | None = None,
) -> ExtractionResult:
    return ExtractionResult(entries=[])
