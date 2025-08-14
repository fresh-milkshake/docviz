"""Shared helpers placeholder for cross-backend labeling.

Aliasing is handled per-backend for flexibility and richer context.
This module remains for potential shared utilities in the future.
"""

from enum import Enum


class CanonicalLabel(Enum):
    """
    Canonical label for document layout detection.

    Attributes:
        TITLE (str): Title of the document.
        TEXT (str): Text of the document.
        SECTION_HEADER (str): Section header of the document.
        LIST_ITEM (str): List item of the document.
        CAPTION (str): Caption of the document.
        PICTURE (str): Picture of the document.
        PICTURE_CAPTION (str): Picture caption of the document.
        TABLE (str): Table of the document.
        TABLE_CAPTION (str): Table caption of the document.
        TABLE_FOOTNOTE (str): Table footnote of the document.
        FORMULA (str): Formula of the document.
        FORMULA_CAPTION (str): Formula caption of the document.
        PAGE_HEADER (str): Page header of the document.
        PAGE_FOOTER (str): Page footer of the document.
        FOOTNOTE (str): Footnote of the document.
        OTHER (str): Other of the document.
    """

    # Titles and text
    TITLE = "title"
    TEXT = "text"
    SECTION_HEADER = "section_header"
    LIST_ITEM = "list_item"

    # Figures and captions
    CAPTION = "caption"
    PICTURE = "picture"
    PICTURE_CAPTION = "picture_caption"

    # Tables and related
    TABLE = "table"
    TABLE_CAPTION = "table_caption"
    TABLE_FOOTNOTE = "table_footnote"

    # Formulae
    FORMULA = "formula"
    FORMULA_CAPTION = "formula_caption"

    # Page elements
    PAGE_HEADER = "page_header"
    PAGE_FOOTER = "page_footer"

    # Miscellaneous
    FOOTNOTE = "footnote"
    OTHER = "other"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def get_all_labels(cls) -> list[str]:
        return [label.value for label in cls]

    @classmethod
    def validate_label(cls, label: str) -> bool:
        return label in cls.get_all_labels()


if __name__ == "__main__":
    print(CanonicalLabel.get_all_labels())
    print(CanonicalLabel.validate_label("title"))
    print(CanonicalLabel.validate_label("other"))
    print(CanonicalLabel.validate_label("unknown"))
