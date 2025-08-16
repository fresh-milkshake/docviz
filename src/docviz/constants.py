import os
from pathlib import Path


def get_docviz_directory() -> Path:
    """Get the docviz configuration directory.

    Returns:
        Path to the docviz directory.
    """
    user_profile = os.getenv("USERPROFILE")
    if not user_profile:
        raise RuntimeError("USERPROFILE environment variable not found")
    return Path(user_profile) / ".docviz"


CONVERSION_MAX_WORKERS = 10

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


TESSERACT_DEFAULT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSERACT_SETUP_URL = "https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe"
TESSERACT_SETUP_FILENAME = "tesseract-ocr-w64-setup-5.5.0.20241111.exe"
BASE_MODELS_URL = "https://github.com/privateai-com/docviz/raw/main/models"
REQUIRED_MODELS = [
    "doclayout_yolo_docstructbench_imgsz1024.pt",
    "yolov12l-doclaynet.pt",
    "yolov12m-doclaynet.pt",
]
MODELS_PATH = get_docviz_directory() / "models"
