import enum


class ExtractionType(enum.Enum):
    TABLE = "table"
    TEXT = "text"
    FIGURE = "figure"
    EQUATION = "equation"
    CODE = "code"
    REFERENCE = "reference"
    OTHER = "other"

    def __str__(self):
        return self.value

    def get_all(self):
        return list(ExtractionType)
