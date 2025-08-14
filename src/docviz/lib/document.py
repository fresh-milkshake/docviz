from pathlib import Path

from ..types import (
    ExtractionConfig,
    DetectionConfig,
    ExtractionResult,
    ExtractionType,
)
from ..lib.functions import extract_content, extract_content_sync


class Document:
    def __init__(
        self,
        file_path: str,
    ):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File {self.file_path} does not exist")

    async def extract_content(
        self,
        extraction_config: ExtractionConfig | None = None,
        detection_config: DetectionConfig | None = None,
        includes: list[ExtractionType] | None = None,
    ) -> ExtractionResult:
        return await extract_content(self, extraction_config, detection_config)

    def extract_content_sync(
        self,
        extraction_config: ExtractionConfig | None = None,
        detection_config: DetectionConfig | None = None,
        includes: list[ExtractionType] | None = None,
    ) -> ExtractionResult:
        return extract_content_sync(self, extraction_config, detection_config)
