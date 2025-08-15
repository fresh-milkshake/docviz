import asyncio
from .lib.environment import check_dependencies
from .lib.document.document import Document
from .lib.functions import batch_extract, extract_content, extract_content_sync
from .types import (
    ExtractionConfig,
    DetectionConfig,
    ExtractionResult,
    SaveFormat,
    ExtractionEntry,
    ExtractionType,
)

if asyncio.get_event_loop() is None:
    asyncio.set_event_loop(asyncio.new_event_loop())

loop = asyncio.get_event_loop()
loop.run_until_complete(check_dependencies())

__all__ = [
    "Document",
    "batch_extract",
    "extract_content",
    "extract_content_sync",
    "ExtractionConfig",
    "DetectionConfig",
    "ExtractionResult",
    "SaveFormat",
    "ExtractionEntry",
    "ExtractionType",
]
