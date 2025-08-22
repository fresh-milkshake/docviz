Basic Usage
===========

This guide covers the fundamental concepts and basic operations in docviz-python.

Core Concepts
-------------

Document Class
~~~~~~~~~~~~~

The :class:`Document` class is the main interface for working with documents. It represents a single document file and provides methods for content extraction.

.. code-block:: python

    import docviz
    
    # Create a document instance
    document = docviz.Document("path/to/document.pdf")
    
    # Get document information
    print(f"Document name: {document.name}")
    print(f"Page count: {document.page_count}")

Extraction Types
~~~~~~~~~~~~~~~~

docviz can extract different types of content from documents:

* **TEXT**: Plain text content
* **TABLE**: Tabular data with structure
* **FIGURE**: Images, charts, and diagrams
* **EQUATION**: Mathematical expressions


Extraction Results
~~~~~~~~~~~~~~~~~~

The extraction process returns an :class:`ExtractionResult` object containing:

* **entries**: List of extracted content items (ExtractionEntry objects)
* **page_number**: Number of pages processed

Each ExtractionEntry contains:

* **text**: The extracted text content
* **class_**: The type of content (table, text, figure, etc.)
* **confidence**: Confidence score for the detection
* **bbox**: Bounding box coordinates [x1, y1, x2, y2]
* **page_number**: Page number where the content was found


.. note::

    The ``bbox`` (bounding box) field is only meaningful for content types that represent images, figures, or other visual elements. For text and tables, the ``bbox`` will be the size of the page.


Basic Operations
----------------

Simple Extraction
~~~~~~~~~~~~~~~~

Extract all content from a document:

.. code-block:: python

    import docviz
    
    # Create document and extract content
    document = docviz.Document("sample.pdf")
    extractions = document.extract_content_sync()
    
    # Print summary
    print(f"Extracted {len(extractions.entries)} items")

Saving Results
~~~~~~~~~~~~~

Save extraction results in various formats:

.. code-block:: python

    import docviz
    
    document = docviz.Document("sample.pdf")
    extractions = document.extract_content_sync()
    
    # Save as JSON
    extractions.save("results", save_format=docviz.SaveFormat.JSON)
    
    # Save as CSV
    extractions.save("results", save_format=docviz.SaveFormat.CSV)
    
    # Save in multiple formats
    extractions.save("results", save_format=[
        docviz.SaveFormat.JSON,
        docviz.SaveFormat.CSV,
        docviz.SaveFormat.EXCEL
    ])

Selective Extraction
~~~~~~~~~~~~~~~~~~~~

Extract only specific types of content:

.. code-block:: python

    import docviz
    
    document = docviz.Document("sample.pdf")
    
    # Extract only tables and text
    extractions = document.extract_content_sync(
        includes=[
            docviz.ExtractionType.TABLE,
            docviz.ExtractionType.TEXT,
        ]
    )
    
    # Extract everything except figures
    extractions = document.extract_content_sync(
        includes=[
            docviz.ExtractionType.TABLE,
            docviz.ExtractionType.TEXT,
            docviz.ExtractionType.EQUATION,
            docviz.ExtractionType.OTHER,
        ]
    )

Working with URLs
-----------------

Load documents from URLs:

.. code-block:: python

    import asyncio
    import docviz
    
    async def load_from_url():
        # Create document from URL
        document = await docviz.Document.from_url(
            "https://example.com/document.pdf"
        )
        
        # Extract content
        extractions = await document.extract_content()
        extractions.save("url_results", save_format=docviz.SaveFormat.JSON)
        
        return extractions
    
    # Run the async function
    result = asyncio.run(load_from_url())

Asynchronous vs Synchronous
---------------------------

docviz supports both synchronous and asynchronous operations:

Synchronous Usage
~~~~~~~~~~~~~~~~

.. code-block:: python

    import docviz
    
    # Simple synchronous extraction
    document = docviz.Document("sample.pdf")
    extractions = document.extract_content_sync()
    extractions.save("results", save_format=docviz.SaveFormat.JSON)

Asynchronous Usage
~~~~~~~~~~~~~~~~~

.. code-block:: python

    import asyncio
    import docviz
    
    async def extract_async():
        document = docviz.Document("sample.pdf")
        extractions = await document.extract_content()
        extractions.save("results", save_format=docviz.SaveFormat.JSON)
        return extractions
    
    # Run async function
    result = asyncio.run(extract_async())

Error Handling
--------------

Handle common errors gracefully:

.. code-block:: python

    import docviz
    from pathlib import Path
    
    def safe_extract(file_path: str):
        try:
            # Check if file exists
            if not Path(file_path).exists():
                print(f"File not found: {file_path}")
                return None
            
            # Create document and extract
            document = docviz.Document(file_path)
            extractions = document.extract_content_sync()
            
            # Save results
            extractions.save("output", save_format=docviz.SaveFormat.JSON)
            return extractions
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None
    
    # Use the safe extraction function
    result = safe_extract("sample.pdf")
    if result:
        print(f"Successfully extracted {len(result.entries)} items")

Progress Tracking
-----------------

Monitor extraction progress:

.. code-block:: python

    import docviz
    from tqdm import tqdm
    
    document = docviz.Document("large_document.pdf")
    
    # Create progress bar
    with tqdm(total=document.page_count, desc="Extracting") as pbar:
        extractions = document.extract_content_sync(
            progress_callback=pbar.update
        )
    
    extractions.save("progress_results", save_format=docviz.SaveFormat.JSON)

Working with Results
--------------------    

Access and process extraction results:

.. code-block:: python

    import docviz
    
    document = docviz.Document("sample.pdf")
    extractions = document.extract_content_sync()
    
    # Iterate through extracted items
    for entry in extractions.entries:
        print(f"Type: {entry.class_}")
        print(f"Page: {entry.page_number}")
        print(f"Content: {entry.text[:100]}...")
        print(f"Confidence: {entry.confidence:.2f}")
        print("---")
    
    # Filter by content type
    tables = [entry for entry in extractions.entries 
              if entry.class_ == "table"]
    
    text_items = [entry for entry in extractions.entries 
                  if entry.class_ == "text"]
    
    print(f"Found {len(tables)} tables and {len(text_items)} text items")

Next Steps
----------

Now that you understand the basics, explore:

* :doc:`advanced_usage` - Advanced features and configurations
* :doc:`configuration` - Detailed configuration options
* :doc:`../api/index` - Complete API reference
* :doc:`../examples/index` - More examples and use cases
