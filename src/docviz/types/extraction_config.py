from dataclasses import dataclass, field


@dataclass
class ExtractionConfig:
    """
    Configuration for extraction.

    Attributes:
        page_limit (int | None): The maximum number of pages to extract.
        zoom_x (float): The zoom factor for the x-axis.
        zoom_y (float): The zoom factor for the y-axis.
    """

    page_limit: int | None = None
    zoom_x: float = 3.0
    zoom_y: float = 3.0

    pdf_text_threshold_chars: int = 1000
    labels_to_exclude: list[str] = field(default_factory=list)
    prefer_pdf_text: bool = False
