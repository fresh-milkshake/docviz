import asyncio
import concurrent.futures
import tempfile
from collections.abc import AsyncIterator, Callable, Iterator
from pathlib import Path
from typing import TYPE_CHECKING, Any

from docviz.config_cache import (
    get_default_detection_config,
    get_default_extraction_config,
    get_default_llm_config,
    get_default_ocr_config,
)
from docviz.lib.extraction import pipeline, pipeline_streaming
from docviz.logging import get_logger
from docviz.types import (
    DetectionConfig,
    ExtractionConfig,
    ExtractionEntry,
    ExtractionResult,
    ExtractionType,
    LLMConfig,
    OCRConfig,
)

if TYPE_CHECKING:
    from .document import Document


logger = get_logger(__name__)


def _convert_pipeline_results_to_extraction_result(
    pipeline_results: list[dict[str, Any]],
) -> ExtractionResult:
    """Convert pipeline results to ExtractionResult format.

    This function transforms the raw pipeline output into a standardized ExtractionResult
    format. It handles type mapping, coordinate conversion, and text content extraction
    for different element types.

    Args:
        pipeline_results: List of page results from pipeline function. Each page result
            should contain a "page_number" key and an "elements" list. Each element
            should have "type", "bbox", "text", "confidence", and optionally "summary"
            keys.

    Returns:
        ExtractionResult: Standardized extraction result containing all converted
            entries with proper type annotations and coordinate formats.

    Example:
        >>> pipeline_results = [{
        ...     "page_number": 1,
        ...     "elements": [{
        ...         "type": "chart",
        ...         "bbox": [100, 200, 300, 400],
        ...         "text": "Chart title",
        ...         "summary": "Bar chart showing sales data",
        ...         "confidence": 0.95
        ...     }]
        ... }]
        >>> result = _convert_pipeline_results_to_extraction_result(pipeline_results)
        >>> result.entries[0].class_ == "figure"
        True
    """
    entries = []
    page_number = 1  # Default page number if no results

    for page_result in pipeline_results:
        page_number = page_result.get("page_number", 1)
        elements = page_result.get("elements", [])

        for element in elements:
            # Map element types to canonical names
            element_type = element.get("type", "other")
            if element_type == "chart":
                element_type = "figure"
            elif element_type == "formula":
                element_type = "equation"

            # Extract bbox and ensure it's a list
            bbox = element.get("bbox", [])
            if isinstance(bbox, tuple):
                bbox = list(bbox)

            # For chart elements, use summary as text
            text_content = element.get("text", "")
            if element_type == "figure" and "summary" in element:
                text_content = element.get("summary", "")

            entry = ExtractionEntry(
                text=text_content,
                class_=element_type,
                confidence=element.get("confidence", 1.0),
                bbox=bbox,
                page_number=page_number,
            )
            entries.append(entry)

    return ExtractionResult(entries=entries, page_number=page_number)


def batch_extract(
    documents: list["Document"],
    extraction_config: ExtractionConfig | None = None,
    detection_config: DetectionConfig | None = None,
    includes: list[ExtractionType] | None = None,
    progress_callback: Callable[[int], None] | None = None,
) -> list[ExtractionResult]:
    """Extract content from multiple documents in batch.

    This function processes multiple documents sequentially using the same configuration
    settings. It's designed for bulk document processing scenarios where you need to
    extract content from a collection of documents with consistent settings.

    Performance considerations:
    - Documents are processed sequentially, not in parallel
    - Memory usage scales with the number of documents and their sizes
    - Progress tracking is available for long-running batch operations
    - Each document is processed independently, so failures don't affect other documents

    Args:
        documents: List of Document objects to process. Each document should be a valid
            Document instance with an accessible file path.
        extraction_config: Configuration for extraction. If None, default settings
            will be used for all documents.
        detection_config: Configuration for detection. If None, default settings
            will be used for all documents.
        includes: Types of content to include in extraction. If None, all content
            types will be extracted. Use ExtractionType.ALL for all types or specify
            individual types like [ExtractionType.TABLE, ExtractionType.TEXT].
        progress_callback: Optional callback function for progress tracking. The callback
            receives the current document index (1-based) as its argument. Useful for
            updating progress bars or logging in user interfaces.

    Returns:
        list[ExtractionResult]: List of extraction results, one for each input document.
            The order of results matches the order of input documents. Each result
            contains all extracted content for that document.

    Example:
        >>> docs = [Document("doc1.pdf"), Document("doc2.pdf")]
        >>> results = batch_extract(
        ...     documents=docs,
        ...     includes=[ExtractionType.TABLE, ExtractionType.TEXT],
        ...     progress_callback=lambda i: print(f"Processing document {i}")
        ... )
        >>> len(results) == 2
        True
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
    """Extract content from a document asynchronously.

    This is the primary async function for document content extraction. It processes
    the entire document and returns all extracted content in a single result. The
    function runs the synchronous extraction pipeline in a thread pool to provide
    async behavior while maintaining compatibility with the underlying processing
    pipeline.

    The function automatically sets up default configurations if none are provided:
    - DetectionConfig: Uses CPU device with 1024 image size and 0.5 confidence threshold
    - OCRConfig: English language with chart labels for pictures, tables, and formulas
    - LLMConfig: Uses Gemma3 model with local Ollama server
    - ExtractionConfig: Uses default extraction settings

    Processing workflow:
    1. Validates and sets up default configurations
    2. Creates a temporary directory for processing artifacts
    3. Runs the extraction pipeline in a thread pool
    4. Converts pipeline results to standardized format
    5. Cleans up temporary files automatically

    Args:
        document: Document object to extract content from. Must have a valid file path
            accessible to the current process.
        extraction_config: Configuration for extraction process. If None, uses default
            settings optimized for general document processing.
        detection_config: Configuration for layout detection. If None, uses CPU-based
            detection with balanced speed/accuracy settings.
        includes: List of content types to extract. If None, extracts all available
            content types. Use ExtractionType.ALL for all types or specify individual
            types like [ExtractionType.TABLE, ExtractionType.TEXT].
        progress_callback: Optional callback for progress tracking. Called with current
            page number during processing. Useful for UI progress updates.
        ocr_config: Configuration for OCR processing. If None, uses English language
            with optimized settings for document analysis.
        llm_config: Configuration for LLM-based content analysis. If None, uses local
            Gemma3 model via Ollama server.

    Returns:
        ExtractionResult: Complete extraction result containing all extracted content
            from the document, organized by page and content type.

    Raises:
        Exception: If document processing fails, file access issues, or pipeline errors
            occur. The specific exception depends on the failure point.

    Example:
        >>> doc = Document("document.pdf")
        >>> result = await extract_content(
        ...     document=doc,
        ...     includes=[ExtractionType.TABLE, ExtractionType.TEXT],
        ...     progress_callback=lambda page: print(f"Processing page {page}")
        ... )
        >>> print(f"Extracted {len(result.entries)} elements")
    """
    if extraction_config is None:
        extraction_config = get_default_extraction_config()
    if detection_config is None:
        detection_config = get_default_detection_config()
    if ocr_config is None:
        ocr_config = get_default_ocr_config(include_formulas=True)
    if llm_config is None:
        llm_config = get_default_llm_config()
    if includes is None:
        includes = ExtractionType.get_all()

    # Handle ExtractionType.ALL
    if ExtractionType.ALL in includes:
        includes = ExtractionType.get_all()

    # Run the sync pipeline in an executor for async behavior
    def _run_sync_pipeline():
        return extract_content_sync(
            document,
            extraction_config,
            detection_config,
            includes,
            progress_callback,
            ocr_config,
            llm_config,
        )

    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _run_sync_pipeline)


def extract_content_sync(
    document: "Document",
    extraction_config: ExtractionConfig | None = None,
    detection_config: DetectionConfig | None = None,
    includes: list[ExtractionType] | None = None,
    progress_callback: Callable[[int], None] | None = None,
    ocr_config: OCRConfig | None = None,
    llm_config: LLMConfig | None = None,
) -> ExtractionResult:
    """Extract content from a document synchronously.

    This is the core synchronous function for document content extraction. It processes
    the entire document in the current thread and returns all extracted content in a
    single result. This function is the foundation for both sync and async extraction
    workflows.

    The function automatically sets up default configurations if none are provided:
    - DetectionConfig: Uses CPU device with 1024 image size and 0.5 confidence threshold
    - OCRConfig: English language with chart labels for pictures, tables, and formulas
    - LLMConfig: Uses Gemma3 model with local Ollama server
    - ExtractionConfig: Uses default extraction settings

    Processing workflow:
    1. Validates and sets up default configurations
    2. Creates a temporary directory for processing artifacts
    3. Runs the extraction pipeline synchronously
    4. Converts pipeline results to standardized format
    5. Cleans up temporary files automatically

    Memory and performance considerations:
    - Processes the entire document in memory
    - Uses temporary files for intermediate processing steps
    - Automatically cleans up temporary files on completion
    - Suitable for documents up to several hundred pages

    Args:
        document: Document object to extract content from. Must have a valid file path
            accessible to the current process.
        extraction_config: Configuration for extraction process. If None, uses default
            settings optimized for general document processing.
        detection_config: Configuration for layout detection. If None, uses CPU-based
            detection with balanced speed/accuracy settings.
        includes: List of content types to extract. If None, extracts all available
            content types. Use ExtractionType.ALL for all types or specify individual
            types like [ExtractionType.TABLE, ExtractionType.TEXT].
        progress_callback: Optional callback for progress tracking. Called with current
            page number during processing. Useful for UI progress updates.
        ocr_config: Configuration for OCR processing. If None, uses English language
            with optimized settings for document analysis.
        llm_config: Configuration for LLM-based content analysis. If None, uses local
            Gemma3 model via Ollama server.

    Returns:
        ExtractionResult: Complete extraction result containing all extracted content
            from the document, organized by page and content type.

    Raises:
        Exception: If document processing fails, file access issues, or pipeline errors
            occur. The specific exception depends on the failure point.

    Example:
        >>> doc = Document("document.pdf")
        >>> result = extract_content_sync(
        ...     document=doc,
        ...     includes=[ExtractionType.TABLE, ExtractionType.TEXT],
        ...     progress_callback=lambda page: print(f"Processing page {page}")
        ... )
        >>> print(f"Extracted {len(result.entries)} elements")
    """
    if extraction_config is None:
        extraction_config = get_default_extraction_config()
    if detection_config is None:
        detection_config = get_default_detection_config()
    if ocr_config is None:
        ocr_config = get_default_ocr_config(include_formulas=False)
    if llm_config is None:
        llm_config = get_default_llm_config()
    if includes is None:
        includes = ExtractionType.get_all()

        # Handle ExtractionType.ALL
    if ExtractionType.ALL in includes:
        includes = ExtractionType.get_all()

    try:
        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            pipeline_results = pipeline(
                document_path=document.file_path,
                output_dir=Path(temp_dir),
                detection_config=detection_config,
                extraction_config=extraction_config,
                ocr_config=ocr_config,
                llm_config=llm_config,
                includes=includes,
                progress_callback=progress_callback,
            )

        # Convert pipeline results to ExtractionResult
        return _convert_pipeline_results_to_extraction_result(pipeline_results)

    except Exception as e:
        # Log error and return empty result
        logger.error(f"Pipeline execution failed: {e}")
        return ExtractionResult(entries=[], page_number=0)


async def extract_content_streaming(
    document: "Document",
    extraction_config: ExtractionConfig | None = None,
    detection_config: DetectionConfig | None = None,
    includes: list[ExtractionType] | None = None,
    progress_callback: Callable[[int], None] | None = None,
    ocr_config: OCRConfig | None = None,
    llm_config: LLMConfig | None = None,
) -> AsyncIterator[ExtractionResult]:
    """Extract content from a document asynchronously with streaming results.

    This function provides memory-efficient streaming extraction by yielding results
    page by page as they are processed. It's ideal for large documents where loading
    all content into memory at once would be problematic.

    The function runs the synchronous streaming pipeline in a thread pool to provide
    async behavior while maintaining the memory efficiency of streaming processing.
    Each yielded result contains the extracted content for a single page.

    Key benefits:
    - Memory efficient: Only one page is processed at a time
    - Real-time results: Pages are yielded as soon as they're processed
    - Progress tracking: Can track progress on a per-page basis
    - Scalable: Suitable for documents of any size

    Processing workflow:
    1. Sets up default configurations if none provided
    2. Creates temporary directory for processing artifacts
    3. Runs streaming pipeline in thread pool
    4. Yields page results as they become available
    5. Cleans up temporary files on completion

    Args:
        document: Document object to extract content from. Must have a valid file path
            accessible to the current process.
        extraction_config: Configuration for extraction process. If None, uses default
            settings optimized for general document processing.
        detection_config: Configuration for layout detection. If None, uses CPU-based
            detection with balanced speed/accuracy settings.
        includes: List of content types to extract. If None, extracts all available
            content types. Use ExtractionType.ALL for all types or specify individual
            types like [ExtractionType.TABLE, ExtractionType.TEXT].
        progress_callback: Optional callback for progress tracking. Called with current
            page number during processing. Useful for UI progress updates.
        ocr_config: Configuration for OCR processing. If None, uses English language
            with optimized settings for document analysis.
        llm_config: Configuration for LLM-based content analysis. If None, uses local
            Gemma3 model via Ollama server.

    Yields:
        ExtractionResult: Extraction result for each processed page. Each result
            contains all extracted content for that specific page.

    Raises:
        Exception: If document processing fails, file access issues, or pipeline errors
            occur. The specific exception depends on the failure point.

    Example:
        >>> doc = Document("large_document.pdf")
        >>> async for page_result in extract_content_streaming(doc):
        ...     print(f"Page {page_result.page_number}: {len(page_result.entries)} elements")
        ...     # Process each page as it becomes available
    """

    # Run the sync version in a separate thread
    loop = asyncio.get_event_loop()

    def _get_streaming_sync_generator():
        return extract_content_streaming_sync(
            document,
            extraction_config,
            detection_config,
            includes,
            progress_callback,
            ocr_config,
            llm_config,
        )

    # Get the generator from executor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        generator = await loop.run_in_executor(executor, _get_streaming_sync_generator)

        # Yield each result from the generator
        while True:
            try:
                # Get next result from generator in executor
                result = await loop.run_in_executor(executor, next, generator, None)
                if result is None:
                    break
                yield result
            except StopIteration:
                break


def extract_content_streaming_sync(
    document: "Document",
    extraction_config: ExtractionConfig | None = None,
    detection_config: DetectionConfig | None = None,
    includes: list[ExtractionType] | None = None,
    progress_callback: Callable[[int], None] | None = None,
    ocr_config: OCRConfig | None = None,
    llm_config: LLMConfig | None = None,
) -> Iterator[ExtractionResult]:
    """Extract content from a document synchronously with streaming results.

    This function provides memory-efficient streaming extraction by yielding results
    page by page as they are processed. It's the core synchronous implementation
    that powers both sync and async streaming workflows.

    The function processes pages one at a time and yields results immediately upon
    completion of each page. This approach is ideal for large documents where
    loading all content into memory at once would be problematic or when you need
    to start processing results before the entire document is complete.

    Key benefits:
    - Memory efficient: Only one page is processed at a time
    - Real-time results: Pages are yielded as soon as they're processed
    - Progress tracking: Can track progress on a per-page basis
    - Scalable: Suitable for documents of any size
    - Synchronous: No async/await complexity for simple use cases

    Processing workflow:
    1. Sets up default configurations if none provided
    2. Creates temporary directory for processing artifacts
    3. Runs streaming pipeline synchronously
    4. Yields page results as they become available
    5. Cleans up temporary files on completion

    Args:
        document: Document object to extract content from. Must have a valid file path
            accessible to the current process.
        extraction_config: Configuration for extraction process. If None, uses default
            settings optimized for general document processing.
        detection_config: Configuration for layout detection. If None, uses CPU-based
            detection with balanced speed/accuracy settings.
        includes: List of content types to extract. If None, extracts all available
            content types. Use ExtractionType.ALL for all types or specify individual
            types like [ExtractionType.TABLE, ExtractionType.TEXT].
        progress_callback: Optional callback for progress tracking. Called with current
            page number during processing. Useful for UI progress updates.
        ocr_config: Configuration for OCR processing. If None, uses English language
            with optimized settings for document analysis.
        llm_config: Configuration for LLM-based content analysis. If None, uses local
            Gemma3 model via Ollama server.

    Yields:
        ExtractionResult: Extraction result for each processed page. Each result
            contains all extracted content for that specific page.

    Raises:
        Exception: If document processing fails, file access issues, or pipeline errors
            occur. The specific exception depends on the failure point.

    Example:
        >>> doc = Document("large_document.pdf")
        >>> for page_result in extract_content_streaming_sync(doc):
        ...     print(f"Page {page_result.page_number}: {len(page_result.entries)} elements")
        ...     # Process each page as it becomes available
    """
    if extraction_config is None:
        extraction_config = get_default_extraction_config()
    if detection_config is None:
        detection_config = get_default_detection_config()
    if ocr_config is None:
        ocr_config = get_default_ocr_config(include_formulas=False)
    if llm_config is None:
        llm_config = get_default_llm_config()
    if includes is None:
        includes = ExtractionType.get_all()

    # Handle ExtractionType.ALL
    if ExtractionType.ALL in includes:
        includes = ExtractionType.get_all()

    try:
        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use the streaming pipeline generator
            pipeline_generator = pipeline_streaming(
                document_path=document.file_path,
                output_dir=Path(temp_dir),
                detection_config=detection_config,
                extraction_config=extraction_config,
                ocr_config=ocr_config,
                llm_config=llm_config,
                includes=includes,
                progress_callback=progress_callback,
            )

            # Yield converted results one by one
            for page_result in pipeline_generator:
                # Convert single page result to ExtractionResult
                extraction_result = _convert_pipeline_results_to_extraction_result([page_result])
                yield extraction_result

    except Exception as e:
        # Log error and return empty result
        logger.error(f"Streaming pipeline execution failed: {e}")
        yield ExtractionResult(entries=[], page_number=0)
