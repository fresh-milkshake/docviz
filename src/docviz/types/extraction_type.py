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

    @classmethod
    def get_all(cls):
        return list(ExtractionType)
