from dataclasses import dataclass
from pathlib import Path

from .extraction_result import ExtractionResult
from .save_format import SaveFormat


@dataclass
class ExtractionChunk:
    """Represents a chunk of extraction results from streaming processing.

    Attributes:
        result (ExtractionResult): The extraction results for this chunk.
        page_range (str): The page range this chunk covers (e.g., "1-10").
        start_page (int): The starting page number (1-indexed).
        end_page (int): The ending page number (1-indexed).
    """

    result: ExtractionResult
    start_page: int
    end_page: int

    @property
    def page_range(self) -> str:
        """Get the page range as a string."""
        if self.start_page == self.end_page:
            return str(self.start_page)
        return f"{self.start_page}-{self.end_page}"

    def save(self, file_path: str | Path, save_format: SaveFormat | list[SaveFormat]):
        """Save the chunk results to a file.

        Args:
            file_path (str | Path): The path to save the file.
            save_format (SaveFormat | list[SaveFormat]): The format(s) to save in.
        """
        self.result.save(file_path, save_format)
