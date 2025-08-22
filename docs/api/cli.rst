Command Line Interface
======================

docviz-python provides a command-line interface for document extraction.

Basic Usage
-----------

.. code-block:: bash

    # Extract content from a single document
    docviz extract document.pdf

    # Extract with specific output format
    docviz extract document.pdf --format json --output results.json

    # Extract from multiple documents in a directory
    docviz batch input_directory/ --output output_directory/

    # Extract specific content types
    docviz extract document.pdf --types table --types text

Command Reference
-----------------

Extract Command
~~~~~~~~~~~~~~~

Extract content from a single document.

.. code-block:: bash

    docviz extract [OPTIONS] FILE_PATH

    Options:

        --output, -o PATH          Output file path
        --format, -f TEXT          Output format (json, csv, excel, xml)
        --types, -t TEXT           Content types to extract (all, table, text, figure, equation, other)
        --confidence FLOAT         Detection confidence threshold (default: 0.5)
        --device TEXT              Device to use for detection (cpu, cuda)
        --verbose, -v              Enable verbose output
        --help                     Show help message

Batch Command
~~~~~~~~~~~~~

Extract content from multiple documents in a directory.

.. code-block:: bash

    docviz batch [OPTIONS] INPUT_DIR

    Options:

        --output, -o PATH          Output directory
        --format, -f TEXT          Output format (json, csv, excel, xml)
        --types, -t TEXT           Content types to extract (all, table, text, figure, equation, other)
        --confidence FLOAT         Detection confidence threshold (default: 0.5)
        --device TEXT              Device to use for detection (cpu, cuda)
        --pattern TEXT             File pattern to match (default: *.pdf)
        --verbose, -v              Enable verbose output
        --help                     Show help message

Info Command
~~~~~~~~~~~~

Show information about DocViz and available options.

.. code-block:: bash

    docviz info

Examples
--------

Basic Extraction
~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Extract all content from a PDF
    docviz extract document.pdf

    # Save as JSON with specific output file
    docviz extract document.pdf --format json --output results.json

    # Save as CSV
    docviz extract document.pdf --format csv --output results.csv

Selective Extraction
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Extract only tables and text
    docviz extract document.pdf --types table --types text

    # Extract all content types (default)
    docviz extract document.pdf --types all

Batch Processing
~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Process all PDFs in a directory
    docviz batch input_directory/ --output results/

    # Process with specific pattern
    docviz batch input_directory/ --output results/ --pattern "*.pdf"

Custom Configuration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Use GPU for faster processing
    docviz extract document.pdf --device cuda

    # Set confidence threshold
    docviz extract document.pdf --confidence 0.7

Output Formats
-------------

JSON Format
~~~~~~~~~~~

.. code-block:: bash

    docviz extract document.pdf --format json

Produces a JSON file with structured extraction results.

CSV Format
~~~~~~~~~~

.. code-block:: bash

    docviz extract document.pdf --format csv

Produces a CSV file with tabular data.

Excel Format
~~~~~~~~~~~~

.. code-block:: bash

    docviz extract document.pdf --format excel

Produces an Excel file (.xlsx) with extraction results.

XML Format
~~~~~~~~~~

.. code-block:: bash

    docviz extract document.pdf --format xml

Produces an XML file with structured extraction results.

Environment Variables
---------------------

You can set environment variables for configuration:

.. code-block:: bash

    # Set API key for LLM integration (if used in processing)
    export OPENAI_API_KEY="your-api-key-here"

Error Handling
--------------

The CLI provides informative error messages for common issues:

* File not found
* Invalid file format
* Missing dependencies
* API authentication errors
* Memory issues with large documents

Verbose Output
--------------

Enable verbose output for debugging:

.. code-block:: bash

    docviz extract document.pdf --verbose

This will show:
* Processing progress
* Detailed error messages
* Configuration information
* Performance metrics
