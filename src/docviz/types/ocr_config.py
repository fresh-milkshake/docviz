from dataclasses import dataclass


@dataclass
class OCRConfig:
    """
    Configuration for OCR.

    Attributes:
        lang (str): The language to use for OCR.
        chart_labels (list[str]): The labels to use for chart OCR.
        labels_to_exclude (list[str]): The labels to exclude from OCR.
    """

    lang: str
    chart_labels: list[str]
    labels_to_exclude: list[str]
