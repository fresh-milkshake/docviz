from pathlib import Path

from ..types.save_format import SaveFormat



class ExtractionEntry:
    pass


class ExtractionResult:
    def __init__(self, entries: list[ExtractionEntry]):
        self.entries = entries

    def save(self, file_path: str | Path, save_format: SaveFormat | list[SaveFormat]):
        pass