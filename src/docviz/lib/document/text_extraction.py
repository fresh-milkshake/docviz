import numpy as np
import pytesseract

from docviz.logging import get_logger

logger = get_logger(__name__)


def extract_text_from_image(
    image: np.ndarray,
    lang: str = "eng",
    psm: int = 6,
    oem: int = 3,
    extra_config: str | None = None,
) -> str:
    """
    Extract text from an image using Tesseract OCR.

    Args:
        image (np.ndarray): Image to extract text from.
        lang (str): Language(s) for OCR. Defaults to "eng".
        psm (int): Page segmentation mode for Tesseract. Defaults to 6.
        oem (int): OCR Engine mode. Defaults to 3.
        extra_config (Optional[str]): Additional Tesseract config options.

    Returns:
        str: Extracted text from the image.

    Raises:
        FileNotFoundError: If the image cannot be loaded.
    """
    logger.debug(f"Extracting text from image of shape {image.shape}")
    logger.debug(f"OCR settings: lang={lang}, psm={psm}, oem={oem}")

    config = f"--oem {oem} --psm {psm}"
    if extra_config:
        config = f"{config} {extra_config}"

    logger.debug(f"Tesseract config: {config}")
    text = pytesseract.image_to_string(image, lang=lang, config=config)
    result = text.strip()

    logger.debug(f"Extracted {len(result)} characters of text")
    return result
