Basic Examples
===============

This section provides simple examples to get you started with docviz-python.

Simple Document Extraction
-------------------------

Extract all content from a PDF document:

.. code-block:: python

    import asyncio
    import docviz

    async def extract_simple():
        # Create document instance
        document = docviz.Document("sample.pdf")
        
        # Extract all content
        extractions = await document.extract_content()
        
        # Save results
        extractions.save("output", save_format=docviz.SaveFormat.JSON)
        
        print(f"Extracted {len(extractions.entries)} items")
        return extractions

    # Run the extraction
    result = asyncio.run(extract_simple())

Synchronous Extraction
---------------------

Use synchronous extraction for simpler scripts:

.. code-block:: python

    import docviz

    # Create document and extract content
    document = docviz.Document("sample.pdf")
    extractions = document.extract_content_sync()
    
    # Save in multiple formats
    extractions.save("output", save_format=[
        docviz.SaveFormat.JSON,
        docviz.SaveFormat.CSV
    ])

Working with URLs
----------------

Extract content from documents hosted online:

.. code-block:: python

    import asyncio
    import docviz

    async def extract_from_url():
        # Create document from URL
        document = await docviz.Document.from_url(
            "https://example.com/document.pdf"
        )
        
        # Extract content
        extractions = await document.extract_content()
        extractions.save("url_output", save_format=docviz.SaveFormat.JSON)
        
        return extractions

    result = asyncio.run(extract_from_url())

Selective Extraction
--------------------

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
    
    extractions.save("selective_output", save_format=docviz.SaveFormat.JSON)

Batch Processing
----------------

Process multiple documents at once:

.. code-block:: python

    import docviz
    from pathlib import Path

    # Find all PDF files in a directory
    pdf_dir = Path("documents/")
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    # Create document instances
    documents = [docviz.Document(str(pdf)) for pdf in pdf_files]
    
    # Process all documents
    extractions = docviz.batch_extract(documents)
    
    # Save results
    for i, ext in enumerate(extractions):
        filename = pdf_files[i].stem
        ext.save(f"batch_output/{filename}", save_format=docviz.SaveFormat.JSON)

Streaming Processing
--------------------

Process large documents page by page:

.. code-block:: python

    import asyncio
    import docviz

    async def process_streaming():
        document = docviz.Document("large_document.pdf")
        
        # Process each page separately
        async for page_result in document.extract_streaming():
            print(f"Processing page {page_result.page_number}")
            
            # Save each page result
            page_result.save(
                f"streaming_output/page_{page_result.page_number}",
                save_format=docviz.SaveFormat.JSON
            )
    
    # Run the streaming process
    asyncio.run(process_streaming())

Progress Tracking
----------------

Monitor extraction progress:

.. code-block:: python

    import docviz
    from tqdm import tqdm

    document = docviz.Document("sample.pdf")
    
    # Create progress bar
    with tqdm(total=document.page_count, desc="Extracting") as pbar:
        extractions = document.extract_content_sync(
            progress_callback=pbar.update
        )
    
    extractions.save("progress_output", save_format=docviz.SaveFormat.JSON)

Custom Configuration
--------------------

Configure extraction parameters:

.. code-block:: python

    import docviz

    document = docviz.Document("sample.pdf")
    
    # Configure extraction
    extractions = document.extract_content_sync(
        extraction_config=docviz.ExtractionConfig(
            page_limit=10,      # Process only first 10 pages
            zoom_x=2.0,         # Zoom factor for X axis
            zoom_y=2.0,         # Zoom factor for Y axis
        ),
        includes=[
            docviz.ExtractionType.TABLE,
            docviz.ExtractionType.TEXT,
        ]
    )
    
    extractions.save("configured_output", save_format=docviz.SaveFormat.JSON)

Output Format Examples
-----------------------

Save results in different formats:

.. code-block:: python

    import docviz

    document = docviz.Document("sample.pdf")
    extractions = document.extract_content_sync()
    
    # Save as JSON (structured data)
    extractions.save("output", save_format=docviz.SaveFormat.JSON)
    
    # Save as CSV (tabular data)
    extractions.save("output", save_format=docviz.SaveFormat.CSV)
    
    # Save as Excel (multiple sheets)
    extractions.save("output", save_format=docviz.SaveFormat.EXCEL)
    
    # Save as XML (structured markup)
    extractions.save("output", save_format=docviz.SaveFormat.XML)

Error Handling
--------------

Handle common errors gracefully:

.. code-block:: python

    import docviz
    from pathlib import Path

    def safe_extract(file_path: str):
        try:
            document = docviz.Document(file_path)
            extractions = document.extract_content_sync()
            extractions.save("output", save_format=docviz.SaveFormat.JSON)
            return True
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return False
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False

    # Process multiple files safely
    files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
    results = [safe_extract(f) for f in files]
    print(f"Successfully processed {sum(results)} out of {len(files)} files")
