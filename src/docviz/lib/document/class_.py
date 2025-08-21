from collections.abc import AsyncIterator, Callable, Iterator

import fitz  # PyMuPDF

from docviz.lib.document.utils import resolve_path_or_url
from docviz.lib.functions import (
    extract_content,
    extract_content_streaming,
    extract_content_streaming_sync,
    extract_content_sync,
)
from docviz.logging import get_logger
from docviz.types import (
    DetectionConfig,
    ExtractionChunk,
    ExtractionConfig,
    ExtractionResult,
    ExtractionType,
    LLMConfig,
)

logger = get_logger(__name__)


class Document:
    """
    A class representing a document.

    Attributes:
        file_path: The path to the document.
        config: The configuration for the document.

    Methods:
        extract_content: Extract content from the document.
        extract_content_sync: Extract content from the document synchronously.
        extract_streaming: Extract content from the document asynchronously.
        extract_streaming_sync: Extract content from the document synchronously.
        extract_chunked: Extract content from the document in chunks.

    Properties:
        page_count: The number of pages in the document.
        name: The name of the document.

    Class Methods:
        from_url: Create a Document instance from a URL.
    """

    def __init__(
        self,
        file_path: str,
        config: ExtractionConfig | None = None,
        filename: str | None = None,
    ):
        self.file_path = resolve_path_or_url(file_path, filename)
        self.config = config or ExtractionConfig()
        self._page_count = None
        self.name = self.file_path.stem

    @classmethod
    async def from_url(
        cls,
        url: str,
        config: ExtractionConfig | None = None,
        filename: str | None = None,
    ) -> "Document":
        """Create a Document instance from a URL.

        Args:
            url: URL to download the document from
            config: Configuration for extraction
            filename: Optional filename for the downloaded file

        Returns:
            Document instance with the downloaded file
        """
        from docviz.lib.document.utils import resolve_path_or_url_async

        file_path = await resolve_path_or_url_async(url, filename)
        return cls(str(file_path), config)

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
        llm_config: LLMConfig | None = None,
    ) -> ExtractionResult:
        if extraction_config is None:
            extraction_config = self.config
        return await extract_content(
            document=self,
            extraction_config=extraction_config,
            detection_config=detection_config,
            includes=includes,
            progress_callback=progress_callback,
            llm_config=llm_config,
        )

    def extract_content_sync(
        self,
        extraction_config: ExtractionConfig | None = None,
        detection_config: DetectionConfig | None = None,
        includes: list[ExtractionType] | None = None,
        progress_callback: Callable[[int], None] | None = None,
        llm_config: LLMConfig | None = None,
    ) -> ExtractionResult:
        # Use the document's config if no extraction_config is provided
        if extraction_config is None:
            extraction_config = self.config
        return extract_content_sync(
            document=self,
            extraction_config=extraction_config,
            detection_config=detection_config,
            includes=includes,
            progress_callback=progress_callback,
            llm_config=llm_config,
        )

    async def extract_streaming(
        self,
        extraction_config: ExtractionConfig | None = None,
        detection_config: DetectionConfig | None = None,
        includes: list[ExtractionType] | None = None,
        progress_callback: Callable[[int], None] | None = None,
        llm_config: LLMConfig | None = None,
    ) -> AsyncIterator[ExtractionResult]:
        """Extract content page by page for memory-efficient streaming processing.

        Args:
            extraction_config: Configuration for extraction
            detection_config: Configuration for detection
            includes: Types of content to include
            progress_callback: Optional callback for progress tracking
            llm_config: Configuration for LLM

        Yields:
            ExtractionResult: Extraction result for each processed page
        """
        # Use the document's config if no extraction_config is provided
        if extraction_config is None:
            extraction_config = self.config

        async for page_result in extract_content_streaming(
            document=self,
            extraction_config=extraction_config,
            detection_config=detection_config,
            includes=includes,
            progress_callback=progress_callback,
            llm_config=llm_config,
        ):
            yield page_result

    def extract_streaming_sync(
        self,
        extraction_config: ExtractionConfig | None = None,
        detection_config: DetectionConfig | None = None,
        includes: list[ExtractionType] | None = None,
        progress_callback: Callable[[int], None] | None = None,
        llm_config: LLMConfig | None = None,
    ) -> Iterator[ExtractionResult]:
        """Extract content page by page for memory-efficient streaming processing (sync version).

        Args:
            extraction_config: Configuration for extraction
            detection_config: Configuration for detection
            includes: Types of content to include
            progress_callback: Optional callback for progress tracking
            llm_config: Configuration for LLM

        Yields:
            ExtractionResult: Extraction result for each processed page
        """
        if extraction_config is None:
            extraction_config = self.config

        yield from extract_content_streaming_sync(
            document=self,
            extraction_config=extraction_config,
            detection_config=detection_config,
            includes=includes,
            progress_callback=progress_callback,
            llm_config=llm_config,
        )

    def extract_chunked(
        self,
        chunk_size: int = 10,
        extraction_config: ExtractionConfig | None = None,
        detection_config: DetectionConfig | None = None,
        includes: list[ExtractionType] | None = None,
        llm_config: LLMConfig | None = None,
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
            chunk_result = extract_content_sync(
                document=self,
                extraction_config=chunk_config,
                detection_config=detection_config,
                includes=includes,
                llm_config=llm_config,
            )

            yield ExtractionChunk(
                result=chunk_result,
                start_page=start_page,
                end_page=end_page,
            )
