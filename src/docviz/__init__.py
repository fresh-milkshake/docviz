import asyncio
import threading
from pathlib import Path

from .environment import check_dependencies
from .lib.document.class_ import Document
from .lib.functions import batch_extract, extract_content, extract_content_sync
from .types import (
    DetectionConfig,
    ExtractionChunk,
    ExtractionConfig,
    ExtractionEntry,
    ExtractionResult,
    ExtractionType,
    LLMConfig,
    SaveFormat,
)

__DEPENDENCIES_CHECKED = False
__DEPENDENCIES_LOCK = threading.Lock()


def _check_dependencies_once():
    """
    Ensure dependencies are checked only once in a thread-safe and process-safe manner.

    This function is invoked on import to guarantee that dependency checks are performed
    a single time per user environment, even if multiple threads or processes are involved.
    A lock file in the user's home directory prevents redundant checks across processes.

    Raises:
        Exception: If the dependencies check fails.
    """
    global __DEPENDENCIES_CHECKED

    # Use a lock file to ensure this runs only once across processes
    lock_file = Path.home() / ".docviz" / "dependencies_checked.lock"
    lock_file.parent.mkdir(exist_ok=True)

    # Check if already verified in this session or globally
    if __DEPENDENCIES_CHECKED or lock_file.exists():
        return

    with __DEPENDENCIES_LOCK:
        # Double-check pattern
        if __DEPENDENCIES_CHECKED or lock_file.exists():
            return

        try:
            if asyncio.get_event_loop() is None:
                asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()
            loop.run_until_complete(check_dependencies())

            # Mark as checked
            __DEPENDENCIES_CHECKED = True
            lock_file.touch()

        except Exception as e:
            # If dependencies check fails, don't mark as checked
            # so it will retry next time
            raise e


# Check dependencies on import
_check_dependencies_once()

__all__ = [
    "DetectionConfig",
    "Document",
    "ExtractionChunk",
    "ExtractionConfig",
    "ExtractionEntry",
    "ExtractionResult",
    "ExtractionType",
    "LLMConfig",
    "SaveFormat",
    "batch_extract",
    "extract_content",
    "extract_content_sync",
]
