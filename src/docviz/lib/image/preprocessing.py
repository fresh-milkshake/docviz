import numpy as np
from PIL import Image, ImageDraw

from docviz.logging import get_logger
from docviz.types import Color, RectangleTuple, RectangleUnion

logger = get_logger(__name__)


def fill_regions_with_color(
    image: np.ndarray,
    regions: list[RectangleUnion],
    color: Color = (255, 255, 255),
) -> np.ndarray:
    """
    Fill specified rectangular regions in an image with a solid color.

    Args:
        image: Image to fill regions in.
        regions: List of rectangles (x1, y1, x2, y2) to fill.
        color: RGB color tuple to fill the regions with.
    """
    try:
        img = Image.fromarray(image)
        draw = ImageDraw.Draw(img)
        for rect in regions:
            draw.rectangle(rect, fill=color)
        logger.info(f"Filled {len(regions)} regions in '{image.shape}'.")
        return np.array(img)
    except Exception as exc:
        logger.error(f"Failed to fill regions in image '{image.shape}': {exc}")
        raise


def extract_regions(
    image: np.ndarray,
    regions: list[RectangleTuple],
) -> list[np.ndarray]:
    """
    Extract specified rectangular regions from an image and save each as a separate file.

    Args:
        image: Image to extract regions from.
        regions: List of rectangles (x1, y1, x2, y2) to extract.

    Returns:
        List of numpy arrays representing the extracted regions.
    """
    try:
        img = Image.fromarray(image)
        logger.info(f"Extracted {len(regions)} regions from '{image.shape}'.")
        return [np.array(img.crop(rect)) for rect in regions]
    except Exception as exc:
        logger.error(f"Failed to extract regions from image '{image.shape}': {exc}")
        return []
