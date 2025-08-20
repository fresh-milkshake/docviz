import csv
import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from docviz.logging import get_logger
from docviz.types.save_format import SaveFormat

logger = get_logger(__name__)


@dataclass
class ExtractionEntry:
    """Extraction entry.

    Attributes:
        text (str): The text of the entry.
        class_ (str): The class of the entry.
        confidence (float): The confidence of the entry.
        bbox (list[float]): The bounding box of the entry.
        page_number (int): The page number of the entry.
    """

    text: str
    class_: str
    confidence: float = field(default=-1.0)
    bbox: list[float] = field(default_factory=list)
    page_number: int = field(default=-1)


class ExtractionResult:
    def __init__(self, entries: list[ExtractionEntry]):
        self.entries = entries

    def to_json(self, file_path: str | Path):
        """Save the extraction result to a JSON file.

        Args:
            file_path (str | Path): The path to the file to save the result to without extension.
        """
        with open(f"{file_path}.json", "w") as f:
            json.dump(self.entries, f, indent=4)

    def to_csv(self, file_path: str | Path):
        """Save the extraction result to a CSV file.

        Args:
            file_path (str | Path): The path to the file to save the result to without extension.
        """
        with open(f"{file_path}.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(self.entries[0].__dict__.keys())
            for entry in self.entries:
                writer.writerow(entry.__dict__.values())

    def to_excel(self, file_path: str | Path):
        """Save the extraction result to an Excel file.

        Args:
            file_path (str | Path): The path to the file to save the result to without extension.
        """

        dataframe = pd.DataFrame(self.entries)
        dataframe.to_excel(f"{file_path}.xlsx", index=False)

    def to_xml(self, file_path: str | Path):
        """Save the extraction result to an XML file.

        Args:
            file_path (str | Path): The path to the file to save the result to without extension.
        """
        root = ET.Element("ExtractionResults")
        for entry in self.entries:
            entry_elem = ET.SubElement(root, "ExtractionEntry")
            for key, value in entry.__dict__.items():
                child = ET.SubElement(entry_elem, key)
                child.text = str(value)

        tree = ET.ElementTree(root)
        tree.write(f"{file_path}.xml", encoding="utf-8", xml_declaration=True)

    def save(self, file_path: str | Path, save_format: SaveFormat | list[SaveFormat]):
        """Save the extraction result to a file.

        Args:
            file_path (str | Path): The path to the file to save the result to without extension.
            save_format (SaveFormat | list[SaveFormat]): The format to save the result in.

        Raises:
            ValueError: If provided save format is not presented in SaveFormat enum.
        """

        if isinstance(save_format, SaveFormat):
            save_format = [save_format]

        for format in save_format:
            if format == SaveFormat.JSON:
                self.to_json(file_path)
            elif format == SaveFormat.CSV:
                self.to_csv(file_path)
            elif format == SaveFormat.EXCEL:
                self.to_excel(file_path)
            elif format == SaveFormat.XML:
                self.to_xml(file_path)
            else:
                raise ValueError(f"Unsupported save format: {format}")

        logger.info(f"Saving extraction result to {file_path}")

    def to_dict(self) -> dict:
        """Convert the extraction result to a dictionary.

        Returns:
            dict: Dictionary representation of the extraction result.
        """
        return {
            "entries": [
                {
                    "text": entry.text,
                    "class": entry.class_,
                    "confidence": entry.confidence,
                    "bbox": entry.bbox,
                    "page_number": entry.page_number,
                }
                for entry in self.entries
            ]
        }

    def to_dataframe(self) -> pd.DataFrame:
        """Convert the extraction result to a pandas DataFrame.

        Returns:
            pd.DataFrame: DataFrame representation of the extraction result.
        """
        data = []
        for entry in self.entries:
            data.append(
                {
                    "text": entry.text,
                    "type": entry.class_,  # Using 'type' instead of 'class' for DataFrame
                    "confidence": entry.confidence,
                    "bbox": entry.bbox,
                    "page_number": entry.page_number,
                }
            )
        return pd.DataFrame(data)
