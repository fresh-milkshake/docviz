from typing import Any, Dict, List, Optional, cast
import tempfile
from pathlib import Path
import json
import cv2
import numpy as np

from docviz.logging import get_logger
from docviz.lib.document import (
    pdf_to_png,
    extract_text_from_image,
    analyze_pdf,
    extract_pdf_page_text,
    extract_pdf_text_excluding_regions,
)
from docviz.lib.image import ChartSummarizer
from docviz.lib.image import extract_regions, fill_regions_with_color
from docviz.lib.extraction.utils import filter_detections
from docviz.lib.detection import Detector
from docviz.types import RectangleTuple, RectangleUnion, DetectionResult

logger = get_logger(__name__)


def pipeline(
    document_path: str,
    model_path: str,
    output_dir: str,
    page_limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Full pipeline: convert PDF to PNG, detect charts, extract text, and summarize.

    Args:
        document_path (str): Path to the input PDF document.
        model_path (str): Path to the YOLO model file.
        output_dir (str): Directory to save outputs.
        settings_file (Path): Path to the settings file.

    Returns:
        List[Dict[str, Any]]: List of dicts for each page, each containing a list of elements (charts and text).
    """
    logger.info("Starting document processing pipeline")

    # TODO: Pass settings through function arguments with correct types instead of using global settings
    model_name = settings.vision.provider.model
    base_url = settings.vision.provider.base_url
    api_key = settings.vision.provider.api_key

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Create temporary directory for intermediate data
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        logger.debug(f"Created temporary directory: {temp_path}")

        # Convert PDF to PNG in temporary directory (needed for image regions and OCR fallback)
        logger.info("Converting PDF to PNG images")
        # TODO: Pass settings through function arguments with correct types instead of using global settings
        image_paths = pdf_to_png(
            pdf_path=document_path,
            output_dir=str(temp_path),
            zoom_x=settings.processing.zoom_factor,
            zoom_y=settings.processing.zoom_factor,
        )
        logger.info(f"Converted PDF to {len(image_paths)} PNG images")

        # Optionally analyze PDF pages to detect native text and image regions
        logger.info("Analyzing PDF pages for native text and images")
        try:
            page_analyses = analyze_pdf(document_path)
            logger.info("PDF analysis completed successfully")
        except Exception as exc:
            logger.warning(
                f"PDF analysis failed with error: {exc}. Falling back to OCR-only text extraction."
            )
            page_analyses = [None] * len(image_paths)

        # Initialize models
        logger.info("Initializing detection and summarization models")
        # TODO: Pass settings through function arguments with correct types instead of using global settings
        detector = Detector(
            backend=settings.layout_detection_backend,
            model_path=model_path,
            settings=settings,
        )
        # TODO: Pass settings through function arguments with correct types instead of using global settings
        summarizer = ChartSummarizer(
            model_name=model_name,
            base_url=base_url,
            api_key=api_key or "",
            retries=settings.vision.retries,
            timeout=settings.vision.timeout,
        )
        logger.info("Models initialized successfully")

        # Process each page
        results: List[Dict[str, Any]] = []
        for idx, img_path in enumerate(image_paths):
            img = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
            if img is None:
                logger.error(f"Could not load image at {img_path}")
                raise FileNotFoundError(f"Could not load image at {img_path}")

            if page_limit is not None and idx >= page_limit:
                logger.info(f"Page limit of {page_limit} reached, stopping processing.")
                break

            logger.info(f"Processing page {idx + 1}/{len(image_paths)}")

            # Run layout detection once so we can both (a) exclude regions in PDF text and (b) reuse in processing
            detections = detector.parse_layout(img)

            analysis = page_analyses[idx]
            # TODO: Pass settings through function arguments with correct types instead of using global settings
            prefer_pdf_text = settings.processing.prefer_pdf_text
            fast_text: Optional[str] = None
            if analysis is not None and prefer_pdf_text:
                if analysis.has_text and not analysis.is_full_page_image:
                    # Merge exclusion regions: image regions from analysis + labels_to_exclude regions from detections
                    # TODO: Pass settings through function arguments with correct types instead of using global settings
                    excluded_label_detections = filter_detections(
                        detections, settings.processing.labels_to_exclude
                    )
                    excluded_bboxes = [
                        (
                            float(b[0]),
                            float(b[1]),
                            float(b[2]),
                            float(b[3]),
                        )
                        for b in (
                            detection.bbox for detection in excluded_label_detections
                        )
                    ]
                    combined_excludes = list(analysis.image_rects) + excluded_bboxes

                    if combined_excludes:
                        logger.debug(
                            f"Excluding {len(combined_excludes)} regions from PDF text on page {idx + 1}"
                        )
                        fast_text = extract_pdf_text_excluding_regions(
                            document_path, analysis.page_index, combined_excludes
                        )
                    else:
                        fast_text = extract_pdf_page_text(
                            document_path, analysis.page_index
                        )

                    # TODO: Pass settings through function arguments with correct types instead of using global settings
                    if (
                        fast_text
                        and len(fast_text)
                        < settings.processing.pdf_text_threshold_chars
                    ):
                        fast_text = None
                        logger.debug(
                            f"Discarded short PDF text below threshold; will use OCR for page {idx + 1}"
                        )
                    else:
                        length = 0 if fast_text is None else len(fast_text)
                        logger.info(
                            f"Using PDF-native text for page {idx + 1} (length={length})"
                        )

            # TODO: Pass settings through function arguments with correct types instead of using global settings
            page_result = process_single_page(
                image=img,
                page_number=idx + 1,
                detector=detector,
                summarizer=summarizer,
                ocr_lang=settings.processing.ocr_lang,
                charts_labels=settings.filtration.chart_labels,
                labels_to_exclude_from_ocr=settings.processing.labels_to_exclude,
                pre_extracted_text=fast_text,
                precomputed_detections=detections,
            )
            results.append(page_result)

            with open(Path(output_dir) / f"page_{idx + 1}.json", "w") as f:
                json.dump(page_result, f)

    logger.info("Pipeline completed successfully")
    logger.info(
        f"Processed {len(results)} pages with total elements: {sum(len(page['elements']) for page in results)}"
    )
    return results


def process_single_page(
    image: np.ndarray,
    page_number: int,
    detector: Detector,
    summarizer: ChartSummarizer,
    charts_labels: List[str],
    labels_to_exclude_from_ocr: List[str],
    ocr_lang: str,
    pre_extracted_text: Optional[str] = None,
    precomputed_detections: Optional[List[DetectionResult]] = None,
) -> Dict[str, Any]:
    """
    Process a single page image: detect elements, extract chart and text data.

    Args:
        image (np.ndarray): Image to process.
        detector (Detector): Detector instance for layout detection.
        summarizer (ChartSummarizer): Summarizer for chart elements.
        ocr_lang (str): Language for OCR.
        pre_extracted_text (Optional[str]): Text already extracted from PDF; if present, OCR is skipped.

    Returns:
        Dict[str, Any]: Dictionary containing page number and extracted elements.
    """

    detections = precomputed_detections or detector.parse_layout(image)
    chart_detections = filter_detections(detections, charts_labels)

    chart_elements = process_chart_elements(
        image=image,
        chart_detections=chart_detections,
        page_number=page_number,
        summarizer=summarizer,
    )

    filtered_detections = filter_detections(detections, labels_to_exclude_from_ocr)
    excluded_regions = [detection.bbox for detection in filtered_detections]
    text_elements = process_text_elements(
        image=image,
        excluded_bboxes=excluded_regions,  # type: ignore
        ocr_lang=ocr_lang,
        page_number=page_number,
        pre_extracted_text=pre_extracted_text,
    )

    elements = chart_elements + text_elements

    return {
        "page_number": page_number,
        "elements": elements,
    }


def process_chart_elements(
    image: np.ndarray,
    chart_detections: List[DetectionResult],
    page_number: int,
    summarizer: ChartSummarizer,
    prompt: Optional[str] = None,
    extra_context: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Process chart elements: crop, summarize, and return structured data.

    Args:
        image (np.ndarray): Image to process.
        chart_detections (List[DetectionResult]): Filtered chart detections.
        page_number (int): Current page number.
        summarizer (ChartSummarizer): Chart summarizer instance.
        prompt (Optional[str]): Custom prompt for summarization.
        extra_context (Optional[str]): Extra context for summarization.

    Returns:
        List[Dict[str, Any]]: List of chart elements with summaries.
    """
    logger.info(f"Processing chart elements for page {page_number}")

    if not chart_detections:
        logger.info("No chart detections found, skipping chart processing")
        return []

    extracted_regions = extract_regions(
        image=image,
        regions=[
            cast(RectangleTuple, tuple(detection.bbox))
            for detection in chart_detections
        ],
    )

    if not extracted_regions:
        logger.warning("Failed to extract chart regions")
        return []

    chart_elements: List[Dict[str, Any]] = []
    for idx, (detection, region) in enumerate(zip(chart_detections, extracted_regions)):
        logger.debug(f"Summarizing chart {idx + 1}/{len(extracted_regions)}...")
        summary = summarizer.summarize_charts_from_page(
            image=region,
            prompt=prompt,
            extra_context=extra_context,
        )
        logger.info(
            f"Successfully summarized chart {idx + 1}/{len(extracted_regions)} on page {page_number}"
        )
        chart_elements.append(
            {
                "type": "chart",
                "label": detection.label_name.lower(),
                "summary": summary,
                "bbox": detection.bbox,
            }
        )

    logger.info(f"Successfully processed {len(chart_elements)} chart elements")
    return chart_elements


def process_text_elements(
    image: np.ndarray,
    excluded_bboxes: List[RectangleUnion],
    page_number: int,
    ocr_lang: str,
    pre_extracted_text: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Process text content for a page.

    If ``pre_extracted_text`` is provided, it will be returned directly as a single text
    element that spans the full page. Otherwise, chart regions are masked and OCR is applied.

    Args:
        image (np.ndarray): Page image to extract text from.
        excluded_bboxes (List[RectangleUnion]): Regions to exclude from OCR (e.g., charts).
        page_number (int): Current page number.
        ocr_lang (str): OCR language code.
        pre_extracted_text (Optional[str]): If provided, skip OCR and return this text.

    Returns:
        List[Dict[str, Any]]: List of text elements with extracted content.
    """
    logger.info(f"Processing text elements for page {page_number}")

    # If we already have text from the PDF, just use it and skip OCR
    if pre_extracted_text is not None and pre_extracted_text.strip():
        text = pre_extracted_text.strip()
        height, width = image.shape[:2]
        logger.debug(
            f"Using pre-extracted PDF text for page {page_number} (chars={len(text)})"
        )
        return [
            {
                "type": "text",
                "text": text,
                "bbox": (0, 0, width, height),
            }
        ]

    filled_image = fill_regions_with_color(
        image=image,
        regions=excluded_bboxes,
        color=(255, 255, 255),  # White color
    )

    # Extract text from the entire processed image
    logger.debug("Extracting text from processed image via OCR")
    text = extract_text_from_image(
        image=filled_image,
        lang=ocr_lang,
    )

    text_elements: List[Dict[str, Any]] = []
    if text.strip():
        height, width = filled_image.shape[:2]
        text_elements.append(
            {
                "type": "text",
                "text": text,
                "bbox": (0, 0, width, height),
            }
        )
        logger.info("Successfully extracted text from processed image")
    else:
        logger.info("No text extracted from processed image")

    logger.info(f"Successfully processed {len(text_elements)} text elements")
    return text_elements
