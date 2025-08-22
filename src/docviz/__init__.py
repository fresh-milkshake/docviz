import asyncio
import threading

from .constants import get_docviz_directory
from .environment import check_dependencies
from .lib.document.class_ import Document
from .lib.functions import (
    batch_extract,
    extract_content,
    extract_content_streaming,
    extract_content_streaming_sync,
    extract_content_sync,
)
from .types import (
    DetectionConfig,
    ExtractionChunk,
    ExtractionConfig,
    ExtractionEntry,
    ExtractionResult,
    ExtractionType,
    LLMConfig,
    OCRConfig,
    SaveFormat,
)

__DEPENDENCIES_CHECKED = False
__DEPENDENCIES_LOCK = threading.Lock()


def _check_dependencies_once():
    """
    Ensure dependencies are checked only once in a thread-safe and process-safe manner.

    This function is called automatically on module import to verify that all required
    dependencies (models, libraries, etc.) are available before document processing.
    This prevents runtime errors and provides early feedback about missing dependencies.

    A global variable tracks whether dependencies have been checked in the current thread.
    For process-level safety, a lock file at ~/.docviz/dependencies_checked.lock prevents
    multiple processes from performing the check simultaneously. Double-checked locking
    is used to minimize unnecessary locking and improve performance. If no asyncio event
    loop is available, one is created before running the dependency check.

    Raises:
        Exception: If any required dependency is missing or the dependency check fails.
            The specific exception type depends on what dependency is missing (e.g.,
            FileNotFoundError for missing models, ImportError for missing packages).
    """
    global __DEPENDENCIES_CHECKED

    # Use a lock file to ensure this runs only once across processes
    lock_file = get_docviz_directory() / "dependencies_checked.lock"
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
    "OCRConfig",
    "SaveFormat",
    "batch_extract",
    "extract_content",
    "extract_content_streaming",
    "extract_content_streaming_sync",
    "extract_content_sync",
]
