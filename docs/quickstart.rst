Quick Start Guide
=================

This guide will help you get started with docviz-python quickly. You'll learn how to install the library and perform basic document extraction operations.

Installation
------------

Install docviz-python using your preferred package manager:

**Using uv (recommended):**

.. code-block:: bash

    uv add docviz-python

**Using pip:**

.. code-block:: bash

    pip install docviz-python

**From source:**

.. code-block:: bash

    git clone https://github.com/privateai-com/docviz.git
    cd docviz
    pip install -e .

Basic Usage
-----------

The simplest way to extract content from a document is to create a :class:`Document` instance and call the extraction method.

Asynchronous Usage
~~~~~~~~~~~~~~~~~~

.. code-block:: python

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

Synchronous Usage
~~~~~~~~~~~~~~~~~

.. code-block:: python

    import docviz

    document = docviz.Document("path/to/your/document.pdf")
    extractions = document.extract_content_sync()
    extractions.save("results", save_format=docviz.SaveFormat.JSON)

Working with URLs
~~~~~~~~~~~~~~~~~

You can also work with documents from URLs:

.. code-block:: python

    import asyncio
    import docviz

    async def main():
        # Create document from URL
        document = await docviz.Document.from_url("https://example.com/document.pdf")
        
        # Extract content
        extractions = await document.extract_content()
        extractions.save("results", save_format=docviz.SaveFormat.JSON)

    asyncio.run(main())

What Gets Extracted
-------------------

By default, docviz extracts the following content types:

* **Text**: All text content from the document
* **Tables**: Tabular data with structure preserved
* **Figures**: Images, charts, and diagrams
* **Equations**: Mathematical expressions

You can customize what gets extracted using the `includes` parameter:

.. code-block:: python

    import docviz

    document = docviz.Document("path/to/document.pdf")

    # Extract only specific types of content
    extractions = document.extract_content_sync(
        includes=[
            docviz.ExtractionType.TABLE,
            docviz.ExtractionType.TEXT,
            docviz.ExtractionType.FIGURE,
        ]
    )

Output Formats
--------------

docviz supports multiple output formats:

* **JSON**: Structured data format
* **CSV**: Comma-separated values
* **Excel**: Microsoft Excel format
* **XML**: Extensible Markup Language format

.. code-block:: python

    import docviz

    document = docviz.Document("path/to/document.pdf")
    extractions = document.extract_content_sync()

    # Save in multiple formats
    extractions.save("results", save_format=[
        docviz.SaveFormat.JSON,
        docviz.SaveFormat.CSV,
        docviz.SaveFormat.EXCEL
    ])

Batch Processing
----------------

Process multiple documents efficiently:

.. code-block:: python

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

Streaming Processing
--------------------

For large documents, use streaming to process page by page:

.. code-block:: python

    import docviz

    document = docviz.Document("path/to/large_document.pdf")

    # Process document in pages to save memory
    async for page_result in document.extract_streaming():
        # Process each page
        page_result.save(f"page_{page_result.page_number}", save_format=docviz.SaveFormat.JSON)

Custom Configuration
--------------------

Configure extraction parameters and LLM settings:

.. code-block:: python

    import os
    import docviz

    document = docviz.Document("path/to/document.pdf")
    
    extractions = document.extract_content_sync(
        extraction_config=docviz.ExtractionConfig(
            page_limit=30,
            zoom_x=2.0,
            zoom_y=2.0
        ),
        llm_config=docviz.LLMConfig(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://api.openai.com/v1",
        )
    )
    
    extractions.save("configured_results", save_format=docviz.SaveFormat.JSON)

Progress Tracking
-----------------

Monitor extraction progress:

.. code-block:: python

    import docviz
    from tqdm import tqdm

    document = docviz.Document("path/to/document.pdf")

    # Extract with progress bar
    with tqdm(total=document.page_count, desc="Extracting content") as pbar:
        extractions = document.extract_content_sync(progress_callback=pbar.update)

    extractions.save("progress_results", save_format=docviz.SaveFormat.JSON)

Next Steps
----------

Now that you have the basics, explore:

* :doc:`user_guide/index` - Detailed usage guide
* :doc:`api/index` - Complete API reference
* :doc:`examples/index` - More examples and use cases

For more advanced features and configurations, see the :doc:`user_guide/index` section.
