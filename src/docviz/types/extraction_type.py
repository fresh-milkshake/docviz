import enum


class ExtractionType(enum.Enum):
    """
    ExtractionType is an enum that represents the type of content to extract from a document.

    Attributes:
        ALL: Extract all content.
        TABLE: Extract tables.
        TEXT: Extract text.
        FIGURE: Extract figures.
        EQUATION: Extract equations.
        CODE: Extract code.
        OTHER: Extract other content.
    """

    ALL = "all"
    TABLE = "table"
    TEXT = "text"
    FIGURE = "figure"
    EQUATION = "equation"
    CODE = "code"
    OTHER = "other"

    def __str__(self):
        return self.value

    @classmethod
    def get_all(cls):
        return [t for t in ExtractionType if t != ExtractionType.ALL]
