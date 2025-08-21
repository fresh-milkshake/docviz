> [!Caution]
> This project is in active development. The API is subject to change and breaking changes may occur. Package may not work until first stable release (1.0.0).


<div align="left">
  <img src="https://raw.githubusercontent.com/privateai-com/docviz/refs/heads/main/assets/header_long.svg" alt="docviz" width="100%">
  
  [![python](https://img.shields.io/badge/python-3.10+-141414.svg?logo=python&logoColor=white)](https://www.python.org/)
  [![version](https://img.shields.io/pypi/v/docviz-python?color=141414&label=version&logo=pypi&logoColor=white)](https://pypi.org/project/docviz-python/)
  [![License](https://img.shields.io/badge/License-MIT-141414.svg?logo=open-source-initiative&logoColor=white)](https://github.com/privateai-com/docviz/blob/main/LICENSE)
  [![Ruff](https://img.shields.io/badge/linter-ruff-141414.svg?logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)
  [![uv](https://img.shields.io/badge/package_manager-uv-141414.svg?logo=uv&logoColor=white)](https://docs.astral.sh/uv/)
</div>


## Overview

**Extract content from documents easily with Python.**

- Extract from PDFs (other formats are coming soon)
- Streaming extraction for large documents and real-time results
- Process one or many files using batch extraction
- Choose what to extract (tables, text, images, etc.)
- Export results to JSON, CSV, Excel and [others](https://github.com/privateai-com/docviz/blob/main/src/docviz/types/save_format.py#L4)
- Simple and flexible API with high configurability

## 📦 Installation

- Using [uv](https://docs.astral.sh/uv/):

    ```bash
    uv add docviz-python
    ```

    Upgrading from previous version:

    ```bash
    uv pip install docviz-python --upgrade
    ```

- Using pip:

    ```bash
    pip install docviz-python --upgrade
    ```

- Directly from source:

    ```bash
    git clone https://github.com/privateai-com/docviz.git
    cd docviz
    pip install -e .
    ```

## Quick Start

### Basic Usage

```python
import asyncio
import docviz

async def main():
    # Create a document instance (can be a local file or a URL)
    document = docviz.Document("path/to/your/document.pdf")
    
    # Extract all content asynchronously
    extractions = await document.extract_content()
    
    # Save results (file name without extension, it will be inherited from chosen format)
    extractions.save("results", save_format=docviz.SaveFormat.JSON)

asyncio.run(main())
```

### Synchronous Usage

```python
import docviz

document = docviz.Document("path/to/your/document.pdf")
extractions = document.extract_content_sync()
extractions.save("results", save_format=docviz.SaveFormat.JSON)
```

## Code Examples

### Batch Processing

```python
import docviz
from pathlib import Path

# Process all PDF files in a directory
pdf_directory = Path("data/papers/")
output_dir = Path("output/")
output_dir.mkdir(exist_ok=True)

pdfs = pdf_directory.glob("*.pdf")
documents = [docviz.Document(str(pdf)) for pdf in pdfs]
extractions = docviz.batch_extract(documents)

for ext in extractions:
    ext.save(output_dir, save_format=[docviz.SaveFormat.JSON, docviz.SaveFormat.CSV])
```

### Selective Extraction

```python
import docviz

document = docviz.Document("path/to/document.pdf")

# Extract only specific types of content
extractions = document.extract_content(
    includes=[
        docviz.ExtractionType.TABLE,
        docviz.ExtractionType.TEXT,
        docviz.ExtractionType.FIGURE,
        docviz.ExtractionType.EQUATION,
    ]
)

extractions.save("selective_results", save_format=docviz.SaveFormat.JSON)
```

### Custom Configuration

```python
import docviz

document = docviz.Document("path/to/document.pdf")
extractions = document.extract_content(
    extraction_config=docviz.ExtractionConfig(page_limit=30),
    llm_config=LLMConfig(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://api.openai.com/v1",
    )
)
extractions.save("configured_results", save_format=docviz.SaveFormat.JSON)
```

### Streaming Processing

```python
import docviz

document = docviz.Document("path/to/large_document.pdf")

# Process document in pages to save memory
for page_result in document.extract_streaming():
    # Process each page
    page_result.save(f"page_{page_result.page_number}", save_format=docviz.SaveFormat.JSON)
```

### Progress Tracking

```python
import docviz
from tqdm import tqdm

document = docviz.Document("path/to/document.pdf")

# Extract with progress bar
with tqdm(total=document.page_count, desc="Extracting content") as pbar:
    extractions = document.extract_content(progress_callback=pbar.update)

extractions.save("progress_results", save_format=docviz.SaveFormat.JSON)
```

## Docs

TODO: create docs static site

### Examples

- [Basic Usage](https://github.com/privateai-com/docviz/blob/main/src/example_usage.py) with 3 different approaches: simple, passing url to document, streaming example and custom configuration using OpenAI key.

## 📝 Contributing

TODO: WIP

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.