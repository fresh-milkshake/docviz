import asyncio
import os
import subprocess
import sys
from pathlib import Path

import requests
from tqdm import tqdm

from docviz.logging import get_logger

logger = get_logger(__name__)

# Constants
TESSERACT_DEFAULT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSERACT_SETUP_URL = "https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe"
TESSERACT_SETUP_FILENAME = "tesseract-ocr-w64-setup-5.5.0.20241111.exe"
BASE_MODELS_URL = "https://github.com/privateai-com/docviz/raw/main/models"
REQUIRED_MODELS = [
    "doclayout_yolo_docstructbench_imgsz1024.pt",
    "yolov12l-doclaynet.pt",
    "yolov12m-doclaynet.pt",
]


async def download_file(url: str, path: Path, chunk_size: int = 8192) -> None:
    """Download a file from a URL to a local path with progress bar.

    Args:
        url: The URL of the file to download.
        path: The local path to save the file.
        chunk_size: Size of chunks to download at once.

    Raises:
        requests.RequestException: If download fails.
        OSError: If file cannot be written.
    """
    logger.debug(f"Starting download from {url} to {path}")

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        with (
            open(path, "wb") as file,
            tqdm(
                desc=f"Downloading {path.name}",
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as progress_bar,
        ):
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    file.write(chunk)
                    progress_bar.update(len(chunk))

        logger.info(f"Download completed: {path}")

    except requests.RequestException as e:
        logger.error(f"Failed to download {url}: {e}")
        raise
    except OSError as e:
        logger.error(f"Failed to write file {path}: {e}")
        raise


def get_docviz_directory() -> Path:
    """Get the docviz configuration directory.

    Returns:
        Path to the docviz directory.
    """
    user_profile = os.getenv("USERPROFILE")
    if not user_profile:
        raise RuntimeError("USERPROFILE environment variable not found")
    return Path(user_profile) / ".docviz"


def find_tesseract_executable() -> str | None:
    """Find the Tesseract executable on the system.

    Returns:
        Path to tesseract executable if found, None otherwise.
    """
    # Common installation paths
    possible_paths = [
        TESSERACT_DEFAULT_PATH,
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Tesseract-OCR\tesseract.exe",
    ]

    # Check if tesseract is in PATH
    try:
        result = subprocess.run(
            ["tesseract", "--version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return "tesseract"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Check common installation paths
    for path in possible_paths:
        if Path(path).exists():
            return path

    return None


async def install_tesseract(docviz_dir: Path) -> None:
    """Download and install Tesseract OCR.

    Args:
        docviz_dir: Directory to store the installer.
    """
    logger.info("Tesseract not found. Starting installation process...")

    setup_path = docviz_dir / TESSERACT_SETUP_FILENAME

    try:
        if not setup_path.exists():
            logger.info("Downloading Tesseract installer...")
            await download_file(TESSERACT_SETUP_URL, setup_path)

        logger.info("Launching Tesseract installer...")
        logger.info(
            "Please complete the installation process. The installer will be removed automatically."
        )

        # Launch installer
        subprocess.Popen(["cmd", "/c", "start", setup_path.as_posix()], shell=True)

        # Wait a bit for installer to start
        await asyncio.sleep(2)

        # Clean up installer
        if setup_path.exists():
            setup_path.unlink()
            logger.debug("Installer file removed")

        logger.error("Tesseract installation required. Please restart after installation.")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Failed to install Tesseract: {e}")
        if setup_path.exists():
            setup_path.unlink()
        raise


def test_tesseract_installation() -> None:
    """Test if Tesseract is properly installed and working.

    Raises:
        RuntimeError: If Tesseract is not working properly.
    """
    try:
        import pytesseract

        # Find tesseract executable
        tesseract_path = find_tesseract_executable()
        if not tesseract_path:
            raise RuntimeError("Tesseract executable not found")

        # Set the path
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

        # Test with a simple image if available
        test_image_path = (
            Path(__file__).parent.parent.parent.parent / "examples" / "data" / "image.png"
        )
        if test_image_path.exists():
            logger.debug("Testing Tesseract with sample image...")
            result = pytesseract.image_to_string(str(test_image_path))
            logger.debug(f"Tesseract test successful. Extracted text length: {len(result)}")
        else:
            logger.debug("No test image found, skipping Tesseract test")

    except ImportError as e:
        raise RuntimeError(
            "pytesseract is not installed. Please install it using 'pip install pytesseract'"
        ) from e
    except Exception as e:
        raise RuntimeError(f"Tesseract test failed: {e}") from e


async def ensure_models_available(models_dir: Path) -> None:
    """Ensure all required models are downloaded and available.

    Args:
        models_dir: Directory to store models.
    """
    logger.debug(f"Checking models in {models_dir}")

    # Create models directory if it doesn't exist
    models_dir.mkdir(parents=True, exist_ok=True)

    # Check and download missing models
    missing_models = []
    for model_name in REQUIRED_MODELS:
        model_path = models_dir / model_name
        if not model_path.exists():
            missing_models.append(model_name)
        else:
            logger.debug(f"Model {model_name} already exists")

    # Download missing models
    if missing_models:
        logger.info(f"Downloading {len(missing_models)} missing models...")
        for model_name in missing_models:
            model_url = f"{BASE_MODELS_URL}/{model_name}"
            model_path = models_dir / model_name
            logger.info(f"Downloading {model_name}...")
            await download_file(model_url, model_path)
    else:
        logger.info("All required models are already available")


async def check_dependencies() -> None:
    """Check and ensure all dependencies are available.

    This function:
    1. Checks if Tesseract OCR is installed and working
    2. Downloads and installs Tesseract if needed
    3. Ensures all required models are downloaded
    """
    logger.info("Checking dependencies...")

    try:
        # Get docviz directory
        docviz_dir = get_docviz_directory()
        logger.debug(f"Using docviz directory: {docviz_dir}")

        # Check Tesseract installation
        try:
            test_tesseract_installation()
            logger.info("Tesseract OCR is properly installed and working")
        except RuntimeError as e:
            logger.warning(f"Tesseract issue: {e}")
            await install_tesseract(docviz_dir)

        # Ensure models are available
        models_dir = docviz_dir / "models"
        await ensure_models_available(models_dir)

        logger.info("All dependencies are ready")

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to check dependencies: {e}")
        raise
