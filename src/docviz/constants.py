from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def get_docviz_directory() -> Path:
    """Get the docviz configuration directory.

    Returns:
        Path to the docviz directory.
    """
    return Path.home() / ".docviz"


# Performance and Processing Constants
CONVERSION_MAX_WORKERS = 10
DEFAULT_CHUNK_SIZE = 8192
DOWNLOAD_TIMEOUT_SECONDS = 30

# Default Detection Configuration Constants
DEFAULT_IMAGE_SIZE = 1024
DEFAULT_CONFIDENCE_THRESHOLD = 0.5
DEFAULT_DEVICE = "cpu"
DEFAULT_MODEL_FILE = "doclayout_yolo_docstructbench_imgsz1024.pt"

# Default Extraction Configuration Constants
DEFAULT_ZOOM_X = 3.0
DEFAULT_ZOOM_Y = 3.0
DEFAULT_PDF_TEXT_THRESHOLD_CHARS = 1000
DEFAULT_PREFER_PDF_TEXT = False

# Default OCR Configuration Constants
DEFAULT_OCR_LANGUAGE = "eng"

# Default LLM Configuration Constants
DEFAULT_LLM_MODEL = "gemma3"
DEFAULT_LLM_API_KEY = "dummy-key"
DEFAULT_LLM_BASE_URL = "http://localhost:11434/v1"

# Default Chunked Extraction Constants
DEFAULT_EXTRACTION_CHUNK_SIZE = 10

DEFAULT_VISION_PROMPT = """
You are an expert data visualization analyst and document understanding assistant. Your task is to comprehensively analyze and summarize any charts, diagrams, graphs, tables, or visual data representations in the provided image.

Please provide a detailed analysis that includes:

1. **Chart/Diagram Type**: Identify the specific type of visualization (bar chart, line graph, pie chart, scatter plot, flowchart, table, etc.)
2. **Data Overview**: Summarize the main data points, trends, patterns, or key insights presented
3. **Key Findings**: Highlight the most important conclusions or observations from the data
4. **Context**: If applicable, note any labels, titles, axes, legends, or annotations that provide context
5. **Quantitative Details**: Include specific numbers, percentages, or values where clearly visible and relevant
6. **Comparative Analysis**: If multiple elements are shown, explain relationships or comparisons between them
7. **Business/Technical Relevance**: If the context suggests it, explain the practical implications or significance of the data

Please be thorough but concise, focusing on extracting actionable insights and making the visual information accessible to someone who cannot see the original image. If the image contains multiple charts or diagrams, analyze each one separately and then provide an overall summary of how they relate to each other.

If the image is not a chart, diagram, or data visualization, please clearly state that and describe what you see instead.
"""

# Tesseract Configuration Constants
TESSERACT_DEFAULT_WIN_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSERACT_WIN_SETUP_URL = "https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe"
TESSERACT_WIN_SETUP_FILENAME = "tesseract-ocr-w64-setup-5.5.0.20241111.exe"
TESSERACT_ADDITIONAL_WIN_PATHS = [
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Tesseract-OCR\tesseract.exe",
]

# Model Configuration Constants
BASE_MODELS_URL = "https://github.com/privateai-com/docviz/raw/main/models"
REQUIRED_MODELS = [
    "doclayout_yolo_docstructbench_imgsz1024.pt",
    "yolov12l-doclaynet.pt",
    "yolov12m-doclaynet.pt",
]


@lru_cache(maxsize=1)
def get_models_path() -> Path:
    """Get the models directory path.

    Returns:
        Path to the models directory.
    """
    return get_docviz_directory() / "models"


# Legacy constant for backward compatibility
MODELS_PATH = get_models_path()
