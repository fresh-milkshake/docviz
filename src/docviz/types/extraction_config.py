from dataclasses import dataclass, field


@dataclass
class ExtractionConfig:
    """Configuration for document content extraction and processing.

    This configuration class controls the behavior of the document content extraction
    system, which extracts and processes different types of content (text, tables,
    figures, equations) from detected document regions.

    The extraction system handles various aspects of content processing including
    OCR, text extraction, table parsing, and content filtering. This configuration
    allows fine-tuning of the extraction process for optimal results.

    Attributes:
        page_limit (int | None): The maximum number of pages to extract from the document. If None,
            all pages in the document will be processed. Useful for processing large
            documents in parts or for testing with limited page ranges.
        zoom_x (float): The horizontal zoom factor for image processing. Higher values increase
            image resolution for better OCR accuracy but require more memory and
            processing time. Default is 3.0 for good balance of quality and performance.
        zoom_y (float): The vertical zoom factor for image processing. Higher values increase
            image resolution for better OCR accuracy but require more memory and
            processing time. Default is 3.0 for good balance of quality and performance.
        pdf_text_threshold_chars (int): The minimum number of characters required in a PDF
            text element to be considered valid content. Elements with fewer characters
            may be ignored in favor of OCR extraction. Default is 1000 characters.
        labels_to_exclude (list[str]): List of content labels to exclude from extraction. These
            labels correspond to specific content types that should be skipped during
            processing. Common exclusions include headers, footers, and other
            non-content elements.
        prefer_pdf_text (bool): Whether to prefer PDF-embedded text over OCR when both are
            available. When True, the system will use PDF text when it meets quality
            thresholds. When False, OCR will be used even when PDF text is available.
            Default is False for maximum compatibility.

    Example:
        >>> # Basic extraction configuration
        >>> config = ExtractionConfig(
        ...     page_limit=None,  # Process all pages
        ...     zoom_x=3.0,
        ...     zoom_y=3.0,
        ...     pdf_text_threshold_chars=1000,
        ...     labels_to_exclude=["header", "footer"],
        ...     prefer_pdf_text=False
        ... )
        >>>
        >>> # High-quality extraction for small documents
        >>> config = ExtractionConfig(
        ...     page_limit=10,
        ...     zoom_x=4.0,
        ...     zoom_y=4.0,
        ...     pdf_text_threshold_chars=500,
        ...     labels_to_exclude=[],
        ...     prefer_pdf_text=True
        ... )
    """

    page_limit: int | None = None
    zoom_x: float = 3.0
    zoom_y: float = 3.0

    pdf_text_threshold_chars: int = 1000
    labels_to_exclude: list[str] = field(default_factory=list)
    prefer_pdf_text: bool = False
