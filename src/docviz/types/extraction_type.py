import enum

from docviz.lib.detection.labels import CanonicalLabel


class ExtractionType(enum.Enum):
    """Enumeration of content types that can be extracted from documents.

    This enum defines the different types of content that can be extracted and
    processed from documents. Each type corresponds to a specific category of
    document content with its own processing requirements and characteristics.

    The enum provides utility methods for working with extraction types, including
    getting all types (excluding the special ALL type) and converting to canonical
    label names used by the detection system.

    Attributes:
        ALL: Special value indicating all content types should be extracted.
            This is a convenience option that expands to all individual types.
        TABLE: Tabular data and structured information organized in rows and columns.
            Includes data tables, comparison tables, and other tabular formats.
        TEXT: Regular text content including paragraphs, headings, lists, and
            other textual elements. This is the most common content type.
        FIGURE: Visual elements including charts, graphs, diagrams, images, and
            other graphical content. Also includes charts and visualizations.
        EQUATION: Mathematical expressions, formulas, and equations. Includes
            both inline and block mathematical content.
        OTHER: Miscellaneous content that doesn't fit into other categories.
            May include special elements, annotations, or unrecognized content.

    Example:
        >>> # Extract all content types
        >>> types = [ExtractionType.ALL]
        >>> 
        >>> # Extract specific content types
        >>> types = [ExtractionType.TABLE, ExtractionType.TEXT]
        >>> 
        >>> # Get all individual types (excluding ALL)
        >>> all_types = ExtractionType.get_all()
        >>> 
        >>> # Convert to canonical label
        >>> label = ExtractionType.TABLE.to_canonical_label()
        >>> print(label)  # "table"
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
        """Convert the extraction type to a canonical label.

        This method maps the extraction type to a canonical label used by the detection system.
        The canonical label is a string representation of the extraction type that is used
        to identify the type of content in the document.

        Returns:
            str: The canonical label for the extraction type.
        """
        return {
            ExtractionType.TABLE: CanonicalLabel.TABLE.value,
            ExtractionType.TEXT: CanonicalLabel.TEXT.value,
            ExtractionType.FIGURE: CanonicalLabel.PICTURE.value,
            ExtractionType.EQUATION: CanonicalLabel.FORMULA.value,
            ExtractionType.OTHER: CanonicalLabel.OTHER.value,
        }[self]
