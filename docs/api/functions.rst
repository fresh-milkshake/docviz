Functions
=========

This section documents the utility functions available in docviz-python.

Batch Extraction
----------------

.. automodule:: docviz.lib.functions
   :members:
   :undoc-members:
   :show-inheritance:

Batch Processing Functions
--------------------------

.. autofunction:: docviz.batch_extract
   :noindex:

Content Extraction Functions
----------------------------

.. autofunction:: docviz.extract_content
   :noindex:

.. autofunction:: docviz.extract_content_sync
   :noindex:

.. autofunction:: docviz.extract_content_streaming
   :noindex:

.. autofunction:: docviz.extract_content_streaming_sync
   :noindex:

Usage Examples
--------------

Batch Processing
~~~~~~~~~~~~~~~~

.. code-block:: python

    import docviz
    from pathlib import Path

    # Process multiple documents
    pdf_directory = Path("data/papers/")
    pdfs = pdf_directory.glob("*.pdf")
    documents = [docviz.Document(str(pdf)) for pdf in pdfs]
    
    # Extract from all documents
    extractions = docviz.batch_extract(documents)
    
    # Save results
    for ext in extractions:
        ext.save(f"output/{ext.document_name}", save_format=docviz.SaveFormat.JSON)

Standalone Extraction
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import docviz

    # Extract content directly
    extractions = docviz.extract_content_sync("document.pdf")
    extractions.save("results", save_format=docviz.SaveFormat.JSON)

Streaming Extraction
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import docviz

    # Stream content extraction
    for page_result in docviz.extract_content_streaming_sync("large_document.pdf"):
        print(f"Page {page_result.page_number}: {len(page_result.entries)} items")
        page_result.save(f"page_{page_result.page_number}", save_format=docviz.SaveFormat.JSON)
