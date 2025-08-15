from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import fitz

from docviz.logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class PageAnalysis:
    """Lightweight analysis of a PDF page.

    Attributes:
        page_index: Zero-based page index.
        has_text: Whether the page contains any extractable text.
        image_rects: Image rectangles in page coordinate space (points).
        is_full_page_image: Heuristic flag for scan-like pages (single image occupying most of page and no text).
        page_rect: Full page rectangle in points as a tuple (x0, y0, x1, y1).
    """

    page_index: int
    has_text: bool
    image_rects: list[tuple[float, float, float, float]]
    is_full_page_image: bool
    page_rect: tuple[float, float, float, float]


def _collect_image_rects(page: Any) -> list[tuple[float, float, float, float]]:
    """Collect image rectangles from a page via rawdict blocks.

    Returns rectangles in page coordinate space (points).
    """
    rects: list[tuple[float, float, float, float]] = []
    raw = page.get_text("rawdict")
    for block in raw.get("blocks", []):
        if block.get("type") == 1:
            bbox = block.get("bbox")
            if isinstance(bbox, list | tuple) and len(bbox) == 4:
                x0, y0, x1, y1 = bbox
                rects.append((float(x0), float(y0), float(x1), float(y1)))
    logger.debug(f"Found {len(rects)} image blocks on page")
    return rects


def _has_any_text(page: Any) -> bool:
    """Determine if page contains any textual content."""
    text = page.get_text("text").strip()
    return bool(text)


def _is_scan_like(
    page: Any, image_rects: list[tuple[float, float, float, float]], has_text: bool
) -> bool:
    """Heuristic to detect scan-like pages: no text and one large image covering most of the page area."""
    if has_text:
        return False
    if len(image_rects) != 1:
        return False
    page_rect = page.rect
    page_area = float(page_rect.width * page_rect.height)
    x0, y0, x1, y1 = image_rects[0]
    img_area = float((x1 - x0) * (y1 - y0))
    coverage = img_area / page_area if page_area > 0 else 0.0
    decision = coverage >= 0.9
    logger.debug(f"Scan-like heuristic: coverage={coverage:.3f} -> {'YES' if decision else 'NO'}")
    return decision


def analyze_pdf(pdf_path: str | Path) -> list[PageAnalysis]:
    """Analyze each page to determine text presence and image regions.

    Args:
        pdf_path: Path to PDF.

    Returns:
        List of PageAnalysis, one per page.
    """
    path = str(pdf_path)
    logger.info(f"Starting PDF analysis: {path}")
    results: list[PageAnalysis] = []
    with fitz.open(path) as doc:
        for idx in range(len(doc)):
            page = doc.load_page(idx)
            has_text = _has_any_text(page)
            image_rects = _collect_image_rects(page)
            full_image = _is_scan_like(page, image_rects, has_text)
            rect = page.rect
            page_rect_tuple = (
                float(rect.x0),
                float(rect.y0),
                float(rect.x1),
                float(rect.y1),
            )
            results.append(
                PageAnalysis(
                    page_index=idx,
                    has_text=has_text,
                    image_rects=image_rects,
                    is_full_page_image=full_image,
                    page_rect=page_rect_tuple,
                )
            )
            logger.debug(
                f"Page {idx + 1}: has_text={has_text}, images={len(image_rects)}, full_page_image={full_image}"
            )
    logger.info(f"Analyzed {len(results)} PDF pages for text and image regions")
    return results


def extract_pdf_page_text(pdf_path: str | Path, page_index: int) -> str:
    """Extract raw textual content from a PDF page.

    Args:
        pdf_path: Path to PDF.
        page_index: Zero-based page index.

    Returns:
        Extracted text with surrounding whitespace trimmed.
    """
    with fitz.open(str(pdf_path)) as doc:
        page = doc.load_page(page_index)
        text: str = page.get_text("text")  # type: ignore[attr-defined]
        stripped = text.strip()
        logger.debug(f"Extracted PDF text from page {page_index + 1}: {len(stripped)} characters")
        return stripped


def _rectangles_intersect(
    a: tuple[float, float, float, float], b: tuple[float, float, float, float]
) -> bool:
    """Check if two rectangles in (x0, y0, x1, y1) intersect.

    Rectangles are in the same coordinate space (PDF points).
    """
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return not (ax1 <= bx0 or bx1 <= ax0 or ay1 <= by0 or by1 <= ay0)


def extract_pdf_text_excluding_regions(
    pdf_path: str | Path,
    page_index: int,
    exclude_rects: Iterable[tuple[float, float, float, float]]
    | list[tuple[float, float, float, float]],
) -> str:
    """Extract text from a PDF page while excluding content inside given rectangles.

    Args:
        pdf_path: Path to PDF file.
        page_index: Zero-based page index to extract.
        exclude_rects: Iterable of rectangles to exclude in PDF point coordinates.

    Returns:
        Concatenated text from non-excluded text blocks.
    """
    excludes: list[tuple[float, float, float, float]] = [
        (float(x0), float(y0), float(x1), float(y1)) for (x0, y0, x1, y1) in exclude_rects
    ]

    with fitz.open(str(pdf_path)) as doc:
        page = doc.load_page(page_index)
        raw = page.get_text("rawdict")  # type: ignore[attr-defined]

    kept_blocks = 0
    dropped_blocks = 0
    parts: list[str] = []
    for block in raw.get("blocks", []):
        if block.get("type") != 0:
            # Keep only text blocks
            continue
        bbox = block.get("bbox")
        if not (isinstance(bbox, list | tuple) and len(bbox) == 4):
            continue
        rect = (float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3]))
        if any(_rectangles_intersect(rect, ex) for ex in excludes):
            dropped_blocks += 1
            continue

        # Concatenate spans within lines for this block
        block_text_parts: list[str] = []
        for line in block.get("lines", []):
            line_parts: list[str] = []
            for span in line.get("spans", []):
                text: str = span.get("text", "")
                if text:
                    line_parts.append(text)
            if line_parts:
                block_text_parts.append("".join(line_parts))
        block_text = "\n".join(block_text_parts).strip()
        if block_text:
            kept_blocks += 1
            parts.append(block_text)

    result = "\n\n".join(parts).strip()
    logger.debug(
        f"PDF text extract (page {page_index + 1}): kept={kept_blocks}, dropped={dropped_blocks}, chars={len(result)}"
    )
    return result
