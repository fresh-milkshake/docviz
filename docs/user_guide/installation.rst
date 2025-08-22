Installation Guide
==================

This guide covers how to install docviz-python and its dependencies.

System Requirements
------------------

* Python 3.10 or higher
* Operating System: Windows, macOS, or Linux
* Memory: At least 4GB RAM (8GB recommended)
* Storage: At least 2GB free space

Package Manager Installation
----------------------------

Using uv (Recommended)
~~~~~~~~~~~~~~~~~~~~~~

`uv` is a fast Python package installer and resolver. It's the recommended way to install docviz-python:

.. code-block:: bash

    # Install uv if you haven't already
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Install docviz-python
    uv add docviz-python

    # Or add to an existing project
    uv add docviz-python --project

Using pip
~~~~~~~~~

Standard pip installation:

.. code-block:: bash

    pip install docviz-python

    # Upgrade to latest version
    pip install docviz-python --upgrade



From Source
-----------

Clone the repository and install in development mode:

.. code-block:: bash

    git clone https://github.com/privateai-com/docviz.git
    cd docviz
    pip install -e .

Optional Dependencies
---------------------

Install additional dependencies for specific features:

Development Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Using uv
    uv add docviz-python[dev]

    # Using pip
    pip install docviz-python[dev]

Showcase Dependencies
~~~~~~~~~~~~~~~~~~~~~

For Jupyter notebooks and visualization examples:

.. code-block:: bash

    # Using uv
    uv add docviz-python[showcase]

    # Using pip
    pip install docviz-python[showcase]

CLI Dependencies
~~~~~~~~~~~~~~~~

For command-line interface features:

.. code-block:: bash

    # Using uv
    uv add docviz-python[cli]

    # Using pip
    pip install docviz-python[cli]

External Dependencies
---------------------

docviz-python uses several external tools that may need to be installed separately:

Tesseract OCR
~~~~~~~~~~~~~

Required for text extraction from images:

**Ubuntu/Debian:**

.. code-block:: bash

    sudo apt-get install tesseract-ocr

**macOS:**

.. code-block:: bash

    brew install tesseract

**Windows:**

Download and install from `https://github.com/UB-Mannheim/tesseract/wiki`

**Verify installation:**

.. code-block:: bash

    tesseract --version

Verification
------------

Test that the installation was successful:

.. code-block:: python

    import docviz

    # Test basic functionality
    document = docviz.Document("test.pdf")
    print(f"Document loaded: {document.name}")
    print(f"Document has {document.page_count} pages")

Common Installation Issues
--------------------------

Permission Errors
~~~~~~~~~~~~~~~~

If you encounter permission errors, try:

.. code-block:: bash

    # Use user installation
    pip install --user docviz-python

    # Or use a virtual environment
    python -m venv docviz_env
    source docviz_env/bin/activate  # On Windows: docviz_env\Scripts\activate
    pip install docviz-python

Missing Dependencies
~~~~~~~~~~~~~~~~~~~~

If you get import errors for dependencies:

.. code-block:: bash

    # Reinstall with all dependencies
    pip install --force-reinstall docviz-python

Tesseract Not Found
~~~~~~~~~~~~~~~~~~~

If Tesseract is not found, ensure it's in your system PATH or specify the path:

.. code-block:: python

    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows example

Next Steps
----------

After successful installation, proceed to:

* :doc:`../quickstart` - Quick start guide
* :doc:`basic_usage` - Basic usage tutorial
* :doc:`../api/index` - API reference
