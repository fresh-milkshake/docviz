Document Class
==============

.. automodule:: docviz.lib.document.class_
   :members:
   :undoc-members:
   :show-inheritance:

Document Class Reference
------------------------

The :class:`Document` class is the main interface for working with documents in docviz-python.

Constructor
-----------

.. autoclass:: docviz.Document
   :members:
   :undoc-members:
   :special-members: __init__

Usage Examples
--------------

Basic Document Creation
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import docviz

    # Create document from local file
    document = docviz.Document("path/to/document.pdf")
    
    # Create document from URL
    document = await docviz.Document.from_url("https://example.com/document.pdf")

Asynchronous Extraction
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import asyncio
    import docviz

    async def extract_document():
        document = docviz.Document("document.pdf")
        extractions = await document.extract_content()
        return extractions

    result = asyncio.run(extract_document())

Synchronous Extraction
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import docviz

    document = docviz.Document("document.pdf")
    extractions = document.extract_content_sync()

Streaming Extraction
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import docviz

    import asyncio
    
    async def process_streaming():
        document = docviz.Document("large_document.pdf")
        
        # Process page by page asynchronously
        async for page_result in document.extract_streaming():
            print(f"Page {page_result.page_number}: {len(page_result.entries)} items")
    
    # Run the async streaming function
    asyncio.run(process_streaming())

