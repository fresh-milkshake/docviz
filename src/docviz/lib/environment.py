import os
import subprocess
from pathlib import Path
import requests
from tqdm import tqdm
import asyncio

from ..logging import get_logger


logger = get_logger(__name__)


async def download(url: str, path: Path):
    """Download a file from a URL to a local path.

    Args:
        url (str): The URL of the file to download.
        path (Path): The local path to save the file.
    """
    logger.debug(f"Starting download from {url} to {path}")
    try:
        response = requests.get(url, stream=True)
        total = int(response.headers.get("content-length", 0))
        chunk_size = 1024
        with (
            open(path, "wb") as f,
            tqdm(
                desc=f"Downloading {path.name}",
                total=total,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar,
        ):
            for data in response.iter_content(chunk_size=chunk_size):
                size = f.write(data)
                bar.update(size)
        logger.info(f"Download completed: {path}")
    except Exception as e:
        logger.error(f"Failed to download {url} to {path}: {e}")
        raise


async def download_models(appdata_models: Path):
    """Download models from https://github.com/privateai-com/docviz/tree/main/models"""
    base_url = "https://github.com/privateai-com/docviz/raw/main/models"
    logger.debug(f"Checking for models in {appdata_models}")
    for model in appdata_models.iterdir():
        if model.is_dir():
            logger.debug(f"Skipping directory {model}")
            continue
        logger.debug(f"Downloading model {model.name} from {base_url}/{model.name}")
        await download(f"{base_url}/{model.name}", appdata_models / model.name)


async def check_dependencies():
    docviz_dir = Path(os.getenv("USERPROFILE")) / ".docviz"  # type: ignore
    logger.debug(f"Checking dependencies. Using docviz directory: {docviz_dir}")

    # pytesseract
    try:
        import pytesseract

        logger.debug("Setting pytesseract command path.")
        pytesseract.pytesseract.tesseract_cmd = (
            "C:\\Program Files\\Tesseract-OCR\\tesseract.esxe"
        )
        logger.debug("Testing pytesseract installation with a sample image.")
        pytesseract.image_to_string(r"D:\code\projects\docviz\examples\data\image.png")
        logger.debug("pytesseract is installed and working.")
    except pytesseract.pytesseract.TesseractNotFoundError:
        logger.error("pytesseract is not installed. Downloading setup...")
        tesseract_setup = docviz_dir / "tesseract-ocr-w64-setup-5.5.0.20241111.exe"
        if not tesseract_setup.exists():
            logger.debug(f"Downloading Tesseract setup to {tesseract_setup}")
            await download(
                "https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe",
                tesseract_setup,
            )
        else:
            logger.info(f"Tesseract setup: {tesseract_setup}")
        logger.debug(f"Running Tesseract setup: {tesseract_setup}")
        logger.info(
            "Please, go through the installation process. After installation setup will be automatically removed."
        )
        subprocess.run(["cmd", "/c", "start", tesseract_setup.as_posix()], shell=True)
        logger.debug("Waiting 10 seconds for Tesseract setup to complete...")
        await asyncio.sleep(1)
        logger.debug(f"Removing Tesseract setup file: {tesseract_setup}")
        tesseract_setup.unlink()
        logger.error("Tesseract installation required. Exiting.")
        exit(1)
    except KeyboardInterrupt:
        logger.error("Keyboard interrupt. Exiting...")
        exit(1)
    except ImportError:
        logger.error(
            "pytesseract is not installed. Please install it using `pip install pytesseract`."
        )
        exit(1)
    except Exception as e:
        logger.exception(f"Unexpected exception during pytesseract check: {e}")

    models = [
        "doclayout_yolo_docstructbench_imgsz1024.pt",
        "yolov12l-doclaynet.pt",
        "yolov12m-doclaynet.pt",
    ]
    appdata_models = docviz_dir / "models"
    logger.debug(f"Ensuring models directory exists: {appdata_models}")
    appdata_models.mkdir(parents=True, exist_ok=True)
    for model in models:
        model_path = appdata_models / model
        if not model_path.exists():
            logger.debug(f"Model {model} not found. Downloading...")
            await download(
                f"https://github.com/privateai-com/docviz/raw/main/models/{model}",
                model_path,
            )
        else:
            logger.debug(f"Model {model} already exists at {model_path}")
