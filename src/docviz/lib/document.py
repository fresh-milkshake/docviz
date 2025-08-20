from collections.abc import Callable, Iterator
from pathlib import Path

import fitz  # PyMuPDF

from docviz.lib.functions import extract_content, extract_content_sync
from docviz.logging import get_logger
from docviz.types import (
    DetectionConfig,
    ExtractionChunk,
    ExtractionConfig,
    ExtractionResult,
    ExtractionType,
)

logger = get_logger(__name__)


class Document:
    def __init__(
        self,
        file_path: str,
        config: ExtractionConfig | None = None,
    ):
        self.file_path = Path(file_path)
        self.config = config or ExtractionConfig()
        if not self.file_path.exists():
            raise FileNotFoundError(f"File {self.file_path} does not exist")

        # Cache the page count for performance
        self._page_count = None

    @property
    def page_count(self) -> int:
        """Get the number of pages in the document."""
        if self._page_count is None:
            try:
                with fitz.open(self.file_path) as doc:
                    self._page_count = doc.page_count
            except Exception as e:
                logger.warning(f"Could not determine page count for {self.file_path}: {e}")
                self._page_count = 0
        return self._page_count

    async def extract_content(
        self,
        extraction_config: ExtractionConfig | None = None,
        detection_config: DetectionConfig | None = None,
        includes: list[ExtractionType] | None = None,
        progress_callback: Callable[[int], None] | None = None,
    ) -> ExtractionResult:
        # Use the document's config if no extraction_config is provided
        if extraction_config is None:
            extraction_config = self.config
        return await extract_content(
            self, extraction_config, detection_config, includes, progress_callback
        )

    def extract_content_sync(
        self,
        extraction_config: ExtractionConfig | None = None,
        detection_config: DetectionConfig | None = None,
        includes: list[ExtractionType] | None = None,
        progress_callback: Callable[[int], None] | None = None,
    ) -> ExtractionResult:
        # Use the document's config if no extraction_config is provided
        if extraction_config is None:
            extraction_config = self.config
        return extract_content_sync(
            self, extraction_config, detection_config, includes, progress_callback
        )

    def extract_streaming(
        self,
        chunk_size: int = 10,
        extraction_config: ExtractionConfig | None = None,
        detection_config: DetectionConfig | None = None,
        includes: list[ExtractionType] | None = None,
    ) -> Iterator[ExtractionChunk]:
        """Extract content in chunks for memory-efficient processing.

        Args:
            chunk_size (int): Number of pages to process in each chunk.
            extraction_config (ExtractionConfig | None): Configuration for extraction.
            detection_config (DetectionConfig | None): Configuration for detection.
            includes (list[ExtractionType] | None): Types of content to include.

        Yields:
            ExtractionChunk: Chunks of extraction results.
        """
        total_pages = self.page_count
        if total_pages == 0:
            return

        # Use the document's config if no extraction_config is provided
        if extraction_config is None:
            extraction_config = self.config

        for start_page in range(1, total_pages + 1, chunk_size):
            end_page = min(start_page + chunk_size - 1, total_pages)

            # Create a modified config for this chunk
            chunk_config = ExtractionConfig(
                page_limit=end_page - start_page + 1,
                zoom_x=extraction_config.zoom_x,
                zoom_y=extraction_config.zoom_y,
                pdf_text_threshold_chars=extraction_config.pdf_text_threshold_chars,
                labels_to_exclude=extraction_config.labels_to_exclude,
                prefer_pdf_text=extraction_config.prefer_pdf_text,
            )

            # Extract content for this chunk
            chunk_result = extract_content_sync(self, chunk_config, detection_config, includes)

            yield ExtractionChunk(
                result=chunk_result,
                start_page=start_page,
                end_page=end_page,
            )
