from typing import TYPE_CHECKING

from docviz.types.detection_config import DetectionConfig
from docviz.types.extraction_config import ExtractionConfig
from docviz.types.extraction_result import ExtractionResult
from docviz.types.extraction_type import ExtractionType

if TYPE_CHECKING:
    from .document.document import Document


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
    includes: list[ExtractionType] | None = None,
) -> ExtractionResult:
    return ExtractionResult(entries=[])


def extract_content_sync(
    document: "Document",
    extraction_config: ExtractionConfig | None = None,
    detection_config: DetectionConfig | None = None,
    includes: list[ExtractionType] | None = None,
) -> ExtractionResult:
    return ExtractionResult(entries=[])
