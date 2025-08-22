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
    """A class representing a document for content extraction and analysis.

    The Document class is the primary interface for working with documents in DocViz.
    It provides methods for extracting various types of content (text, tables, figures,
    equations) from PDF documents and other supported formats.

    The class handles document loading, validation, and provides both synchronous and
    asynchronous extraction methods. It supports streaming extraction for memory-efficient
    processing of large documents and chunked extraction for batch processing scenarios.

    Attributes:
        file_path: Path object representing the document file location. Automatically
            resolved from input string (local path or URL).
        config: ExtractionConfig instance containing default extraction settings.
            Used when no specific config is provided to extraction methods.
        name: String name of the document, derived from the file stem.

    Methods:
        extract_content: Extract all content from the document asynchronously.
        extract_content_sync: Extract all content from the document synchronously.
        extract_streaming: Extract content page by page asynchronously.
        extract_streaming_sync: Extract content page by page synchronously.
        extract_chunked: Extract content in configurable page chunks.

    Properties:
        page_count: The total number of pages in the document. Lazy-loaded on first
            access using PyMuPDF.

    Class Methods:
        from_url: Create a Document instance from a URL, downloading the file first.

    Example:
        >>> # Create document from local file
        >>> doc = Document("document.pdf")
        >>> print(f"Document has {doc.page_count} pages")
        >>> 
        >>> # Extract all content
        >>> result = await doc.extract_content()
        >>> print(f"Extracted {len(result.entries)} elements")
        >>> 
        >>> # Extract specific content types
        >>> tables_only = await doc.extract_content(
        ...     includes=[ExtractionType.TABLE]
        ... )
        >>> 
        >>> # Stream processing for large documents
        >>> async for page_result in doc.extract_streaming():
        ...     print(f"Page {page_result.page_number}: {len(page_result.entries)} elements")
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

        This class method downloads a document from a URL and creates a Document instance
        for it. The downloaded file is saved to a temporary location and managed by the
        Document instance.

        The method supports various URL schemes (http, https, ftp, etc.) and automatically
        handles file naming. If no filename is provided, it attempts to extract one from
        the URL or uses a default name.

        Args:
            url: URL to download the document from. Must be a valid URL pointing to
                a downloadable document file (PDF, etc.).
            config: Configuration for extraction. If None, uses default extraction
                settings. This config will be used as the default for all extraction
                methods on this document.
            filename: Optional filename for the downloaded file. If None, the filename
                will be extracted from the URL or a default name will be used.

        Returns:
            Document: Document instance with the downloaded file ready for extraction.

        Raises:
            Exception: If the URL is invalid, the file cannot be downloaded, or the
                downloaded file is not a valid document format.

        Example:
            >>> # Download document from URL
            >>> doc = await Document.from_url(
            ...     "https://example.com/document.pdf",
            ...     filename="my_document.pdf"
            ... )
            >>> 
            >>> # Extract content from downloaded document
            >>> result = await doc.extract_content()
            >>> print(f"Extracted {len(result.entries)} elements")
        """
        from docviz.lib.document.utils import resolve_path_or_url_async

        file_path = await resolve_path_or_url_async(url, filename)
        return cls(str(file_path), config)

    @property
    def page_count(self) -> int:
        """Get the total number of pages in the document.

        This property provides lazy loading of the page count. The page count is only
        calculated when first accessed, and then cached for subsequent accesses. This
        approach avoids unnecessary file operations when the page count isn't needed.

        The method uses PyMuPDF (fitz) to open the document and count pages. If the
        document cannot be opened or the page count cannot be determined, it returns
        0 and logs a warning.

        Returns:
            int: The total number of pages in the document. Returns 0 if the page
                count cannot be determined.

        Raises:
            No explicit exceptions are raised, but warnings may be logged if the
                document cannot be opened or processed.

        Example:
            >>> doc = Document("document.pdf")
            >>> print(f"Document has {doc.page_count} pages")
            >>> # The page count is now cached and won't be recalculated
            >>> print(f"Still has {doc.page_count} pages")
        """
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
        """Extract all content from the document asynchronously.

        This method extracts all content from the document in a single operation and
        returns a complete ExtractionResult containing all extracted elements. It's
        the primary async method for document content extraction.

        The method uses the document's default configuration if no extraction_config
        is provided, allowing for document-specific default settings while still
        supporting per-extraction customization.

        Processing characteristics:
        - Processes the entire document at once
        - Returns complete results in a single ExtractionResult
        - Uses document's default config if no config provided
        - Supports all content types (text, tables, figures, equations)
        - Provides progress tracking capabilities

        Args:
            extraction_config: Configuration for extraction process. If None, uses
                the document's default configuration (self.config).
            detection_config: Configuration for layout detection. If None, uses
                default detection settings optimized for general document processing.
            includes: List of content types to extract. If None, extracts all
                available content types. Use ExtractionType.ALL for all types or
                specify individual types like [ExtractionType.TABLE, ExtractionType.TEXT].
            progress_callback: Optional callback for progress tracking. Called with
                current page number during processing. Useful for UI progress updates.
            llm_config: Configuration for LLM-based content analysis. If None, uses
                default LLM settings for content enhancement and analysis.

        Returns:
            ExtractionResult: Complete extraction result containing all extracted
                content from the document, organized by page and content type.

        Raises:
            Exception: If document processing fails, file access issues, or pipeline
                errors occur. The specific exception depends on the failure point.

        Example:
            >>> doc = Document("document.pdf")
            >>> # Extract all content using document's default config
            >>> result = await doc.extract_content()
            >>> print(f"Extracted {len(result.entries)} elements")
            >>> 
            >>> # Extract specific content types with custom config
            >>> tables_only = await doc.extract_content(
            ...     includes=[ExtractionType.TABLE],
            ...     progress_callback=lambda page: print(f"Processing page {page}")
            ... )
        """
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

        This method provides memory-efficient streaming extraction by yielding results
        page by page as they are processed. It's ideal for large documents where
        loading all content into memory at once would be problematic.

        The method processes pages sequentially and yields each page's results as soon
        as processing is complete. This allows for real-time processing and reduces
        memory usage compared to loading all results at once.

        Key benefits:
        - Memory efficient: Only one page is processed at a time
        - Real-time results: Pages are yielded as soon as they're processed
        - Progress tracking: Can track progress on a per-page basis
        - Scalable: Suitable for documents of any size
        - Configurable: Uses document's default config if no config provided

        Args:
            extraction_config: Configuration for extraction process. If None, uses
                the document's default configuration (self.config).
            detection_config: Configuration for layout detection. If None, uses
                default detection settings optimized for general document processing.
            includes: List of content types to extract. If None, extracts all
                available content types. Use ExtractionType.ALL for all types or
                specify individual types like [ExtractionType.TABLE, ExtractionType.TEXT].
            progress_callback: Optional callback for progress tracking. Called with
                current page number during processing. Useful for UI progress updates.
            llm_config: Configuration for LLM-based content analysis. If None, uses
                default LLM settings for content enhancement and analysis.

        Yields:
            ExtractionResult: Extraction result for each processed page. Each result
                contains all extracted content for that specific page.

        Raises:
            Exception: If document processing fails, file access issues, or pipeline
                errors occur. The specific exception depends on the failure point.

        Example:
            >>> doc = Document("large_document.pdf")
            >>> # Process pages as they become available
            >>> async for page_result in doc.extract_streaming():
            ...     print(f"Page {page_result.page_number}: {len(page_result.entries)} elements")
            ...     # Process each page immediately
            ...     for entry in page_result.entries:
            ...         if entry.class_ == "table":
            ...             print(f"Found table: {entry.text[:50]}...")
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

        This method processes the document in configurable page chunks, providing
        a balance between memory efficiency and processing efficiency. It's useful
        for large documents where you want to process multiple pages at once but
        still maintain reasonable memory usage.

        The method divides the document into chunks of specified size and processes
        each chunk as a separate extraction operation. This approach allows for
        better memory management while still providing batch processing benefits.

        Chunking strategy:
        - Divides document into chunks of chunk_size pages
        - Processes each chunk independently
        - Returns ExtractionChunk objects with chunk metadata
        - Maintains page numbering across chunks

        Args:
            chunk_size: Number of pages to process in each chunk. Default is 10 pages.
                Larger chunks use more memory but may be more efficient for processing.
            extraction_config: Configuration for extraction process. If None, uses
                the document's default configuration (self.config).
            detection_config: Configuration for layout detection. If None, uses
                default detection settings optimized for general document processing.
            includes: List of content types to extract. If None, extracts all
                available content types. Use ExtractionType.ALL for all types or
                specify individual types like [ExtractionType.TABLE, ExtractionType.TEXT].
            llm_config: Configuration for LLM-based content analysis. If None, uses
                default LLM settings for content enhancement and analysis.

        Yields:
            ExtractionChunk: Chunks of extraction results. Each chunk contains:
                - result: ExtractionResult for the chunk's pages
                - start_page: First page number in the chunk
                - end_page: Last page number in the chunk

        Raises:
            Exception: If document processing fails, file access issues, or pipeline
                errors occur. The specific exception depends on the failure point.

        Example:
            >>> doc = Document("large_document.pdf")
            >>> # Process document in 5-page chunks
            >>> for chunk in doc.extract_chunked(chunk_size=5):
            ...     print(f"Chunk {chunk.start_page}-{chunk.end_page}: {len(chunk.result.entries)} elements")
            ...     # Process each chunk
            ...     for entry in chunk.result.entries:
            ...         if entry.class_ == "table":
            ...             print(f"Table on page {entry.page_number}")
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
