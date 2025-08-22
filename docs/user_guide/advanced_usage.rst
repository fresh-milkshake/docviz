Advanced Usage
==============

This guide covers advanced features and configurations for docviz-python, including batch processing, streaming, custom configurations, and performance optimization.

Batch Processing
----------------

Processing Multiple Documents
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Process multiple documents efficiently using the batch processing functionality:

.. code-block:: python

    import docviz
    from pathlib import Path

    # Define input and output directories
    input_dir = Path("data/documents/")
    output_dir = Path("output/")
    output_dir.mkdir(exist_ok=True)

    # Get all PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    
    # Create document instances
    documents = [docviz.Document(str(pdf)) for pdf in pdf_files]
    
    # Batch extract content
    results = docviz.batch_extract(documents)
    
    # Save results
    for i, result in enumerate(results):
        filename = pdf_files[i].stem
        result.save(output_dir / filename, save_format=docviz.SaveFormat.JSON)

Parallel Processing
~~~~~~~~~~~~~~~~~~

Use async processing for better performance with multiple documents:

.. code-block:: python

    import asyncio
    import docviz
    from pathlib import Path

    async def process_document(doc_path: Path) -> docviz.ExtractionResult:
        """Process a single document asynchronously."""
        document = docviz.Document(str(doc_path))
        return await document.extract_content()

    async def batch_process_async(doc_paths: list[Path]) -> list[docviz.ExtractionResult]:
        """Process multiple documents concurrently."""
        tasks = [process_document(path) for path in doc_paths]
        return await asyncio.gather(*tasks)

    # Usage
    async def main():
        input_dir = Path("data/documents/")
        pdf_files = list(input_dir.glob("*.pdf"))
        
        results = await batch_process_async(pdf_files)
        
        # Save results
        for pdf_file, result in zip(pdf_files, results):
            result.save(f"output/{pdf_file.stem}", save_format=docviz.SaveFormat.JSON)

    asyncio.run(main())

Streaming Processing
--------------------

For Large Documents
~~~~~~~~~~~~~~~~~~~

Process large documents page by page to manage memory usage:

.. code-block:: python

    import docviz

    async def stream_large_document(doc_path: str):
        """Stream process a large document."""
        document = docviz.Document(doc_path)
        
        print(f"Processing {document.page_count} pages...")
        
        all_results = []
        async for page_result in document.extract_streaming():
            print(f"Processed page {page_result.page_number}")
            
            # Process page result immediately
            page_result.save(
                f"page_{page_result.page_number:03d}",
                save_format=docviz.SaveFormat.JSON
            )
            
            # Optionally collect all results
            all_results.append(page_result)
        
        return all_results

Custom Progress Tracking
~~~~~~~~~~~~~~~~~~~~~~~~

Monitor extraction progress with custom callbacks:

.. code-block:: python

    import docviz
    from tqdm import tqdm

    def create_progress_callback():
        """Create a progress callback function."""
        pbar = tqdm(desc="Extracting content", unit="page")
        
        def update_progress(page_num: int):
            pbar.update(1)
            pbar.set_postfix(page=page_num)
        
        return update_progress, pbar

    # Usage
    document = docviz.Document("large_document.pdf")
    progress_callback, pbar = create_progress_callback()
    
    pbar.total = document.page_count
    
    try:
        extractions = document.extract_content_sync(
            progress_callback=progress_callback
        )
        extractions.save("results", save_format=docviz.SaveFormat.JSON)
    finally:
        pbar.close()

Advanced Configuration
----------------------

Custom Extraction Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~

Configure the extraction pipeline for specific use cases:

.. code-block:: python

    import docviz

    # High-quality extraction configuration
    high_quality_config = docviz.ExtractionConfig(
        page_limit=50,           # Process up to 50 pages
        zoom_x=3.0,              # Higher resolution for better OCR
        zoom_y=3.0,
    )

    # Fast extraction configuration
    fast_config = docviz.ExtractionConfig(
        page_limit=10,
        zoom_x=1.5,
        zoom_y=1.5,
    )

    document = docviz.Document("document.pdf")
    
    # Use high-quality config for important documents
    extractions = document.extract_content_sync(
        extraction_config=high_quality_config
    )

LLM Integration
~~~~~~~~~~~~~~

Configure different LLM providers and models:

.. code-block:: python

    import os
    import docviz

    # OpenAI configuration
    openai_config = docviz.LLMConfig(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://api.openai.com/v1",
    )

    # Azure OpenAI configuration
    azure_config = docviz.LLMConfig(
        model="gpt-4o",
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )

    # Custom configuration for summarization
    document = docviz.Document("research_paper.pdf")
    extractions = document.extract_content_sync(
        llm_config=openai_config,
        includes=[docviz.ExtractionType.TEXT, docviz.ExtractionType.FIGURE]
    )

Content Filtering and Processing
-------------------------------

Selective Extraction
~~~~~~~~~~~~~~~~~~~

Extract only specific types of content:

.. code-block:: python

    import docviz

    document = docviz.Document("document.pdf")

    # Extract only tables and figures
    tables_and_figures = document.extract_content_sync(
        includes=[
            docviz.ExtractionType.TABLE,
            docviz.ExtractionType.FIGURE
        ]
    )

Post-Processing Results
~~~~~~~~~~~~~~~~~~~~~~

Filter and process extraction results:

.. code-block:: python

    import docviz

    document = docviz.Document("document.pdf")
    extractions = document.extract_content_sync()

    # Filter by confidence score
    high_confidence_results = [
        entry for entry in extractions.entries
        if entry.confidence > 0.8
    ]

    # Filter by content type and page range
    first_page_tables = [
        entry for entry in extractions.entries
        if entry.class_ == "table" and entry.page_number == 1
    ]

    # Filter by content length
    substantial_text = [
        entry for entry in extractions.entries
        if entry.class_ == "text" and len(entry.text) > 100
    ]

Performance Optimization
-----------------------

Memory Management
~~~~~~~~~~~~~~~~

Optimize memory usage for large document processing:

.. code-block:: python

    import docviz
    import gc

    def process_large_dataset(document_paths: list[str]):
        """Process large dataset with memory optimization."""
        
        for doc_path in document_paths:
            print(f"Processing {doc_path}...")
            
            # Process document
            document = docviz.Document(doc_path)
            extractions = document.extract_content_sync()
            
            # Save immediately
            filename = Path(doc_path).stem
            extractions.save(f"output/{filename}", save_format=docviz.SaveFormat.JSON)
            
            # Clean up memory
            del document, extractions
            gc.collect()

Caching Results
~~~~~~~~~~~~~~

Cache extraction results to avoid reprocessing:

.. code-block:: python

    import docviz
    import pickle
    from pathlib import Path

    def get_cached_extraction(doc_path: str, cache_dir: str = "cache"):
        """Get cached extraction result or create new one."""
        cache_path = Path(cache_dir) / f"{Path(doc_path).stem}.pkl"
        cache_path.parent.mkdir(exist_ok=True)
        
        if cache_path.exists():
            print(f"Loading cached result for {doc_path}")
            with open(cache_path, "rb") as f:
                return pickle.load(f)
        
        print(f"Processing {doc_path}")
        document = docviz.Document(doc_path)
        extractions = document.extract_content_sync()
        
        # Cache the result
        with open(cache_path, "wb") as f:
            pickle.dump(extractions, f)
        
        return extractions

Error Handling and Retry Logic
------------------------------

Robust Document Processing
~~~~~~~~~~~~~~~~~~~~~~~~~~

Handle errors gracefully during batch processing:

.. code-block:: python

    import docviz
    import logging
    from pathlib import Path

    def robust_batch_process(document_paths: list[str]):
        """Process documents with error handling."""
        results = {}
        errors = {}
        
        for doc_path in document_paths:
            try:
                document = docviz.Document(doc_path)
                extractions = document.extract_content_sync()
                
                # Save successful result
                filename = Path(doc_path).stem
                extractions.save(f"output/{filename}", save_format=docviz.SaveFormat.JSON)
                results[doc_path] = "success"
                
            except Exception as e:
                logging.error(f"Failed to process {doc_path}: {e}")
                errors[doc_path] = str(e)
        
        return results, errors

Retry with Exponential Backoff
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Implement retry logic for network-dependent operations:

.. code-block:: python

    import asyncio
    import docviz
    from typing import Optional

    async def extract_with_retry(
        document: docviz.Document,
        max_retries: int = 3,
        base_delay: float = 1.0
    ) -> Optional[docviz.ExtractionResult]:
        """Extract content with exponential backoff retry."""
        
        for attempt in range(max_retries):
            try:
                return await document.extract_content()
                
            except Exception as e:
                if attempt == max_retries - 1:
                    logging.error(f"Failed after {max_retries} attempts: {e}")
                    raise
                
                delay = base_delay * (2 ** attempt)
                logging.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                await asyncio.sleep(delay)
        
        return None

Next Steps
----------

For more advanced configurations and customization options, see:

* :doc:`configuration` - Detailed configuration reference
* :doc:`../api/index` - Complete API documentation
* :doc:`../examples/index` - More examples and use cases
