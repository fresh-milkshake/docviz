from .document.document import Document
from ..types.extraction_config import ExtractionConfig
from ..types.detection_config import DetectionConfig
from ..types.extraction_result import ExtractionResult
from ..types.extraction_type import ExtractionType


def batch_extract(
    documents: list[Document],
    extraction_config: ExtractionConfig | None = None,
    detection_config: DetectionConfig | None = None,
    includes: list[ExtractionType] | None = None,
) -> list[ExtractionResult]:
    return [
        extract_content_sync(document, extraction_config, detection_config, includes)
        for document in documents
    ]


async def extract_content(
    document: Document,
    extraction_config: ExtractionConfig | None = None,
    detection_config: DetectionConfig | None = None,
    includes: list[ExtractionType] | None = None,
) -> ExtractionResult:
    return ExtractionResult(entries=[])


def extract_content_sync(
    document: Document,
    extraction_config: ExtractionConfig | None = None,
    detection_config: DetectionConfig | None = None,
    includes: list[ExtractionType] | None = None,
) -> ExtractionResult:
    return ExtractionResult(entries=[])
