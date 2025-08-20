import asyncio

from .environment import check_dependencies
from .lib.document import Document
from .lib.functions import batch_extract, extract_content, extract_content_sync
from .types import (
    DetectionConfig,
    ExtractionChunk,
    ExtractionConfig,
    ExtractionEntry,
    ExtractionResult,
    ExtractionType,
    SaveFormat,
)

__DEPENDENCIES_CHECKED = False


if not __DEPENDENCIES_CHECKED:
    if asyncio.get_event_loop() is None:
        asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        check_dependencies()
    )  # TODO: find a way to run this only once, even if the user runs the script multiple times or in a different process using multiprocessing
    __DEPENDENCIES_CHECKED = True

__all__ = [
    "DetectionConfig",
    "Document",
    "ExtractionChunk",
    "ExtractionConfig",
    "ExtractionEntry",
    "ExtractionResult",
    "ExtractionType",
    "SaveFormat",
    "batch_extract",
    "extract_content",
    "extract_content_sync",
]
