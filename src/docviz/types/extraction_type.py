import enum

from docviz.lib.detection.labels import CanonicalLabel


class ExtractionType(enum.Enum):
    """
    ExtractionType is an enum that represents the type of content to extract from a document.

    Attributes:
        ALL: Extract all content.
        TABLE: Extract tables.
        TEXT: Extract text.
        FIGURE: Extract figures.
        EQUATION: Extract equations.
        OTHER: Extract other content.
    """

    ALL = "all"
    TABLE = "table"
    TEXT = "text"
    FIGURE = "figure"
    EQUATION = "equation"
    OTHER = "other"

    def __str__(self):
        return self.value

    @classmethod
    def get_all(cls):
        return [t for t in ExtractionType if t != ExtractionType.ALL]

    def to_canonical_label(self) -> str:
        return {
            ExtractionType.TABLE: CanonicalLabel.TABLE.value,
            ExtractionType.TEXT: CanonicalLabel.TEXT.value,
            ExtractionType.FIGURE: CanonicalLabel.PICTURE.value,
            ExtractionType.EQUATION: CanonicalLabel.FORMULA.value,
            ExtractionType.OTHER: CanonicalLabel.OTHER.value,
        }[self]
