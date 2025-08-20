import asyncio
import concurrent.futures
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from docviz.environment import download_file
from docviz.logging import get_logger

logger = get_logger(__name__)


def is_url(path_or_url: str) -> bool:
    """Check if the given string is a URL.

    Args:
        path_or_url: String to check

    Returns:
        True if the string is a URL, False otherwise
    """
    try:
        result = urlparse(path_or_url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def get_filename_from_url(url: str) -> str:
    """Extract filename from URL.

    Args:
        url: URL to extract filename from

    Returns:
        Filename extracted from URL
    """
    parsed = urlparse(url)
    path = parsed.path
    filename = path.split("/")[-1]

    # If no filename in path, try to get it from content-disposition header
    if not filename or "." not in filename:
        filename = "downloaded_file.pdf"  # Default fallback

    return filename


async def download_to_temp(url: str, filename: str | None = None) -> Path:
    """Download a file from URL to a temporary directory.

    Args:
        url: URL to download from
        filename: Optional filename to use (if None, will be extracted from URL)

    Returns:
        Path to the downloaded file

    Raises:
        requests.RequestException: If download fails
        OSError: If file cannot be written
    """
    if filename is None:
        filename = get_filename_from_url(url)

    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp(prefix="docviz_"))
    file_path = temp_dir / filename

    logger.info(f"Downloading {url} to temporary file: {file_path}")

    try:
        await download_file(url, file_path)
        return file_path
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        # Clean up temporary directory on error
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def download_to_temp_sync(url: str, filename: str | None = None) -> Path:
    """Synchronous version of download_to_temp.

    Args:
        url: URL to download from
        filename: Optional filename to use (if None, will be extracted from URL)

    Returns:
        Path to the downloaded file
    """
    try:
        asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(lambda: asyncio.run(download_to_temp(url, filename)))
            return future.result()
    except RuntimeError:
        return asyncio.run(download_to_temp(url, filename))


def resolve_path_or_url(path_or_url: str, filename: str | None = None) -> Path:
    """Resolve a path or URL to a local file path.

    If the input is a URL, it will be downloaded to a temporary location.
    If the input is a local path, it will be returned as is.

    Args:
        path_or_url: Local file path or URL
        filename: Optional filename for downloaded files

    Returns:
        Path to the local file

    Raises:
        FileNotFoundError: If local file doesn't exist
        requests.RequestException: If download fails
        OSError: If file cannot be written
    """
    if is_url(path_or_url):
        return download_to_temp_sync(path_or_url, filename)
    else:
        path = Path(path_or_url)
        if not path.exists():
            raise FileNotFoundError(f"File {path} does not exist")
        return path


async def resolve_path_or_url_async(path_or_url: str, filename: str | None = None) -> Path:
    """Async version of resolve_path_or_url.

    Args:
        path_or_url: Local file path or URL
        filename: Optional filename for downloaded files

    Returns:
        Path to the local file
    """
    if is_url(path_or_url):
        return await download_to_temp(path_or_url, filename)
    else:
        path = Path(path_or_url)
        if not path.exists():
            raise FileNotFoundError(f"File {path} does not exist")
        return path
