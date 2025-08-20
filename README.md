> [!Caution]
> This project is in active development. The API is subject to change and breaking changes may occur. Package may not work until first stable release (1.0.0).


<div align="left">
  <img src="https://raw.githubusercontent.com/fresh-milkshake/docviz/refs/heads/main/assets/header_long.svg" alt="docviz" width="100%">
  
  [![python](https://img.shields.io/badge/python-3.10+-141414.svg?logo=python&logoColor=white)](https://www.python.org/)
  [![version](https://img.shields.io/pypi/v/docviz-python?color=141414&label=version&logo=pypi&logoColor=white)](https://pypi.org/project/docviz-python/)
  [![License](https://img.shields.io/badge/License-MIT-141414.svg?logo=open-source-initiative&logoColor=white)](https://github.com/fresh-milkshake/docviz/blob/main/LICENSE)
  [![Ruff](https://img.shields.io/badge/linter-ruff-141414.svg?logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)
  [![uv](https://img.shields.io/badge/package_manager-uv-141414.svg?logo=uv&logoColor=white)](https://docs.astral.sh/uv/)
</div>


## Overview

**Extract content from documents easily with Python.**

- Extract from PDFs and other formats
- Process one or many files
- Choose what to extract (tables, text, etc.)
- Export results to JSON, CSV, Excel
- Simple and flexible API

## 📦 Installation

```bash
pip install docviz-python
```

## Quick Start

### Basic Usage

```python
import asyncio
import docviz

async def main():
    # Create a document instance
    document = docviz.Document("path/to/your/document.pdf")
    
    # Extract all content
    extractions = await document.extract_content()
    
    # Save results
    extractions.save("results", save_format=docviz.SaveFormat.JSON)

asyncio.run(main())
```

### Synchronous Usage

```python
import docviz

document = docviz.Document("path/to/your/document.pdf")
extractions = document.extract_content_sync()
extractions.save("results.json", save_format=docviz.SaveFormat.JSON)
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

extractions.save("selective_results.json", save_format=docviz.SaveFormat.JSON)
```

### Custom Configuration

```python
import docviz

# Configure extraction settings
config = docviz.ExtractionConfig(
    extraction_type=docviz.ExtractionType.ALL,
    extraction_config=docviz.ExtractionConfig(
        extraction_type=docviz.ExtractionType.ALL,
    ),
)

document = docviz.Document("path/to/document.pdf", config=config)
extractions = document.extract_content()
extractions.save("configured_results.json", save_format=docviz.SaveFormat.JSON)
```

### Streaming Processing

```python
import docviz

document = docviz.Document("path/to/large_document.pdf")

# Process document in chunks to save memory
for chunk in document.extract_streaming(chunk_size=10):
    # Process each chunk (10 pages at a time)
    chunk.save(f"chunk_{chunk.page_range}.json", save_format=docviz.SaveFormat.JSON)
```

### Progress Tracking

```python
import docviz
from tqdm import tqdm

document = docviz.Document("path/to/document.pdf")

# Extract with progress bar
with tqdm(total=document.page_count, desc="Extracting content") as pbar:
    extractions = document.extract_content(progress_callback=pbar.update)

extractions.save("progress_results.json", save_format=docviz.SaveFormat.JSON)
```

### Data Analysis Integration

```python
import docviz
import pandas as pd

document = docviz.Document("path/to/document.pdf")
extractions = document.extract_content()

# Convert to pandas DataFrame for analysis
df = extractions.to_dataframe()

# Basic analysis
print(f"Total tables extracted: {len(df[df['type'] == 'table'])}")
print(f"Total figures extracted: {len(df[df['type'] == 'figure'])}")

# Save as Excel with multiple sheets
with pd.ExcelWriter("analysis_results.xlsx") as writer:
    df.to_excel(writer, sheet_name="All_Content", index=False)
    
    # Separate sheets by content type
    for content_type in df["type"].unique():
        type_df = df[df["type"] == content_type]
        type_df.to_excel(writer, sheet_name=f"{content_type.capitalize()}", index=False)
```

## 🔧 API Reference

### Core Classes

#### `Document`
Main class for document processing.

```python
document = docviz.Document(
    file_path: str,
    config: Optional[ExtractionConfig] = None
)
```

#### `ExtractionConfig`
Configuration for content extraction.

```python
config = docviz.ExtractionConfig(
    extraction_type: ExtractionType = ExtractionType.ALL,
    # Additional configuration options
)
```

#### `ExtractionType`
Enumeration of extractable content types:
- `TEXT` - Plain text content
- `TABLE` - Tabular data
- `FIGURE` - Images and figures
- `EQUATION` - Mathematical equations
- `ALL` - All content types

#### `SaveFormat`
Supported output formats:
- `JSON` - JavaScript Object Notation
- `CSV` - Comma-separated values
- `EXCEL` - Microsoft Excel format


## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.