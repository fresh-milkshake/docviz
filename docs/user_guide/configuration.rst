Configuration
=============

This guide covers all configuration options available in docviz-python, including extraction parameters, LLM settings, detection options, and output configurations.

Overview
--------

docviz-python provides several configuration classes to customize the extraction process:

* **ExtractionConfig**: Controls document processing parameters
* **DetectionConfig**: Configures layout detection settings
* **LLMConfig**: Manages Large Language Model integration
* **OCRConfig**: Controls Optical Character Recognition settings

ExtractionConfig
----------------

The `ExtractionConfig` class controls how documents are processed and extracted.

Basic Configuration
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import docviz

    # Default configuration
    config = docviz.ExtractionConfig()

    # Custom configuration
    config = docviz.ExtractionConfig(
        page_limit=20,     # Process only first 20 pages
        zoom_x=2.0,        # 2x horizontal zoom for better quality
        zoom_y=2.0,        # 2x vertical zoom for better quality
    )

Parameters Reference
~~~~~~~~~~~~~~~~~~~~

**Page Processing**

* ``page_limit`` (int, optional): Maximum number of pages to process. Default: None (all pages)
* ``zoom_x`` (float): Horizontal zoom factor for PDF conversion. Default: 3.0
* ``zoom_y`` (float): Vertical zoom factor for PDF conversion. Default: 3.0

**Text Processing**

* ``pdf_text_threshold_chars`` (int): Minimum characters required for PDF text to be considered valid. Default: 1000
* ``labels_to_exclude`` (list[str]): List of content labels to exclude from extraction. Default: []
* ``prefer_pdf_text`` (bool): Whether to prefer PDF-embedded text over OCR. Default: False

Example Configurations
~~~~~~~~~~~~~~~~~~~~~

**High Quality Configuration**

.. code-block:: python

    high_quality = docviz.ExtractionConfig(
        zoom_x=4.0,
        zoom_y=4.0,
        pdf_text_threshold_chars=500,
        prefer_pdf_text=True
    )

**Fast Processing Configuration**

.. code-block:: python

    fast_processing = docviz.ExtractionConfig(
        zoom_x=2.0,
        zoom_y=2.0,
        page_limit=10,
        pdf_text_threshold_chars=2000
    )

**Academic Paper Configuration**

.. code-block:: python

    academic_config = docviz.ExtractionConfig(
        zoom_x=3.5,
        zoom_y=3.5,
        pdf_text_threshold_chars=800,
        labels_to_exclude=["header", "footer"],
        prefer_pdf_text=False
    )

DetectionConfig
---------------

Configure the underlying YOLO model for layout detection.

Basic Configuration
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import docviz
    from docviz.lib.detection.backends import DetectionBackendEnum

    detection_config = docviz.DetectionConfig(
        imagesize=1024,
        confidence=0.5,
        device="cuda",
        layout_detection_backend=DetectionBackendEnum.DOCLAYOUT_YOLO,
        model_path="path/to/custom/model.pt"
    )

Parameters Reference
~~~~~~~~~~~~~~~~~~~

**Required Parameters**

* ``imagesize`` (int): Input image size for the model (e.g., 1024, 2048)
* ``confidence`` (float): Minimum confidence threshold for detections (0.0 to 1.0)
* ``device`` (str): Device for inference ("cpu", "cuda", "mps")
* ``layout_detection_backend`` (DetectionBackendEnum): Detection backend to use
* ``model_path`` (str): Path to the detection model file

Custom Model Usage
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from docviz.lib.detection.backends import DetectionBackendEnum
    
    # Using a custom trained model
    custom_detection = docviz.DetectionConfig(
        imagesize=1280,
        confidence=0.6,
        device="cuda",
        layout_detection_backend=DetectionBackendEnum.DOCLAYOUT_YOLO,
        model_path="/path/to/custom_model.pt"
    )

    document = docviz.Document("document.pdf")
    extractions = document.extract_content_sync(
        detection_config=custom_detection
    )

LLMConfig
---------

Configure Large Language Model integration for content summarization and analysis.

Provider Configuration
~~~~~~~~~~~~~~~~~~~~~

**OpenAI Configuration**

.. code-block:: python

    import os
    import docviz

    openai_config = docviz.LLMConfig(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://api.openai.com/v1"
    )

**Azure OpenAI Configuration**

.. code-block:: python

    azure_config = docviz.LLMConfig(
        model="gpt-4o",
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        base_url=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

**Local Model Configuration**

.. code-block:: python

    local_config = docviz.LLMConfig(
        model="llama2",
        api_key="",
        base_url="http://localhost:11434/v1"
    )

Parameters Reference
~~~~~~~~~~~~~~~~~~~~

**Required Parameters**

* ``model`` (str): Model name (e.g., "gpt-4o-mini", "llama2")
* ``api_key`` (str): API key for the provider (can be empty for local models)
* ``base_url`` (str): Base URL for API endpoints

Usage Examples
~~~~~~~~~~~~~~

**Basic LLM Integration**

.. code-block:: python

    document = docviz.Document("research_paper.pdf")
    
    llm_config = docviz.LLMConfig(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://api.openai.com/v1"
    )
    
    extractions = document.extract_content_sync(
        llm_config=llm_config,
        includes=[docviz.ExtractionType.FIGURE, docviz.ExtractionType.TABLE]
    )

**Custom Prompting**

.. code-block:: python

    # Configure for local model
    local_config = docviz.LLMConfig(
        model="gemma3",
        api_key="",
        base_url="http://localhost:11434/v1"
    )

OCRConfig
---------

Configure Optical Character Recognition for text extraction from images.

Basic Configuration
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import docviz

    ocr_config = docviz.OCRConfig(
        lang="eng",
        chart_labels=["picture", "table", "formula"],
        labels_to_exclude=["header", "footer"]
    )

Parameters Reference
~~~~~~~~~~~~~~~~~~~~

**Required Parameters**

* ``lang`` (str): Language code for OCR (e.g., "eng", "fra", "eng+fra")
* ``chart_labels`` (list[str]): List of content labels to apply OCR to
* ``labels_to_exclude`` (list[str]): List of content labels to exclude from OCR

Advanced Configuration
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Multi-language OCR configuration
    multilang_ocr = docviz.OCRConfig(
        lang="eng+fra+deu",  # Multiple languages
        chart_labels=["picture", "table", "formula", "equation"],
        labels_to_exclude=["header", "footer", "caption"]
    )

Save Configuration
------------------

Configure output formats and file handling.

Output Formats
~~~~~~~~~~~~~~

.. code-block:: python

    import docviz

    # Single format
    extractions.save("output", save_format=docviz.SaveFormat.JSON)

    # Multiple formats
    extractions.save("output", save_format=[
        docviz.SaveFormat.JSON,
        docviz.SaveFormat.CSV,
        docviz.SaveFormat.EXCEL
    ])

Format-Specific Options
~~~~~~~~~~~~~~~~~~~~~~~

**JSON Output**

.. code-block:: python

    extractions.save("output", save_format=docviz.SaveFormat.JSON)

**CSV Output**

.. code-block:: python

    extractions.save("output", save_format=docviz.SaveFormat.CSV)

**Excel Output**

.. code-block:: python

    extractions.save("output", save_format=docviz.SaveFormat.EXCEL)



Configuration Files
-------------------

Use configuration files for complex setups:

**YAML Configuration**

.. code-block:: yaml

    # docviz_config.yaml
    extraction:
      page_limit: 50
      zoom_x: 3.0
      zoom_y: 3.0
      pdf_text_threshold_chars: 1000
      labels_to_exclude: ["header", "footer"]
      prefer_pdf_text: false

    llm:
      model: "gpt-4o-mini"
      base_url: "https://api.openai.com/v1"

    output:
      formats: ["json", "csv"]
      base_path: "output"

**Loading Configuration**

.. code-block:: python

    import yaml
    import docviz

    # Load configuration from file
    with open("docviz_config.yaml", "r") as f:
        config_data = yaml.safe_load(f)

    # Create configuration objects
    extraction_config = docviz.ExtractionConfig(
        page_limit=config_data["extraction"]["page_limit"],
        zoom_x=config_data["extraction"]["zoom_x"],
        zoom_y=config_data["extraction"]["zoom_y"]
    )
    
    llm_config = docviz.LLMConfig(
        model=config_data["llm"]["model"],
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=config_data["llm"]["base_url"]
    )

    # Use in document processing
    document = docviz.Document("document.pdf")
    extractions = document.extract_content_sync(
        extraction_config=extraction_config,
        llm_config=llm_config
    )

Best Practices
--------------

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

1. **Set page limits**: For testing, limit pages to speed up processing
2. **Choose optimal zoom factors**: Balance quality and performance
3. **Use GPU when available**: Set device="cuda" for faster inference
4. **Adjust PDF text threshold**: Lower values prefer OCR, higher values prefer PDF text

Quality vs Speed Trade-offs
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**For High Quality**:
- Zoom: 3.0-4.0
- Detection confidence: 0.7+
- Lower PDF text threshold: 500-800
- Prefer PDF text: True

**For Speed**:
- Zoom: 2.0-2.5
- Detection confidence: 0.3-0.5
- Higher PDF text threshold: 1500+
- Page limit: 10-20

Resource Management
~~~~~~~~~~~~~~~~~~~

1. **Monitor memory usage** with large documents
2. **Use streaming** for very large files
3. **Set appropriate timeouts** for API calls
4. **Cache model weights** for repeated processing

Next Steps
----------

* :doc:`basic_usage` - Basic usage guide
* :doc:`advanced_usage` - Advanced features
* :doc:`output_formats` - Output format details
* :doc:`../api/index` - Complete API reference
