Contributing to docviz-python
=============================

Thank you for your interest in contributing to docviz-python! This document provides guidelines and information for contributors.

Getting Started
---------------

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a virtual environment** using uv
4. **Install dependencies** in development mode

.. code-block:: bash

    # Fork and clone
    git clone https://github.com/YOUR_USERNAME/docviz.git
    cd docviz
    
    # Create virtual environment and install
    uv venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    uv pip install -e ".[dev]"

Development Setup
------------------

Install development dependencies:

.. code-block:: bash

    # Install all development dependencies
    uv pip install -e ".[dev,showcase,cli]"

    # Install pre-commit hooks
    pre-commit install

Code Style
----------

docviz-python follows strict coding standards:

* **Type hints**: All functions must have type hints
* **Docstrings**: Use Google-style docstrings
* **Formatting**: Use ruff for formatting and linting
* **Line length**: Maximum 100 characters
* **Naming**: snake_case for functions, PascalCase for classes

Example of proper code style:

.. code-block:: python

    def extract_content(
        document_path: str,
        config: ExtractionConfig | None = None,
    ) -> ExtractionResult:
        """
        Extract content from a document.

        Args:
            document_path: Path to the document file
            config: Optional extraction configuration

        Returns:
            ExtractionResult containing extracted content

        Raises:
            FileNotFoundError: If document file doesn't exist
            ValueError: If document format is not supported
        """
        if not Path(document_path).exists():
            raise FileNotFoundError(f"Document not found: {document_path}")
        
        # Implementation here
        return result

Running Tests
-------------

Run the test suite:

.. code-block:: bash

    # Run all tests
    uv run pytest

    # Run with coverage
    uv run pytest --cov=docviz

    # Run specific test file
    uv run pytest tests/test_document.py

    # Run with verbose output
    uv run pytest -v

Code Quality Checks
-------------------

Run quality checks:

.. code-block:: bash

    # Run ruff linter
    uv run ruff check .

    # Run ruff formatter
    uv run ruff format .

    # Run type checking
    uv run pyright

    # Run all quality checks
    uv run python tools/quality-check.py src/

Making Changes
---------------

1. **Create a feature branch**:
   .. code-block:: bash

       git checkout -b feature/your-feature-name

2. **Make your changes** following the coding standards

3. **Add tests** for new functionality

4. **Update documentation** if needed

5. **Run quality checks**:
   .. code-block:: bash

       uv run python tools/quality-check.py src/

6. **Commit your changes** with a descriptive message:
   .. code-block:: bash

       git commit -m "feat: add new extraction feature"

7. **Push to your fork**:
   .. code-block:: bash

       git push origin feature/your-feature-name

8. **Create a pull request** on GitHub

Commit Message Format
---------------------

Use conventional commit messages:

* `feat:` - New features
* `fix:` - Bug fixes
* `docs:` - Documentation changes
* `style:` - Code style changes
* `refactor:` - Code refactoring
* `test:` - Test additions or changes
* `chore:` - Maintenance tasks

Examples:
.. code-block:: bash

    feat: add support for Excel output format
    fix: resolve memory leak in batch processing
    docs: update installation instructions
    test: add tests for URL document loading

Pull Request Guidelines
-----------------------

1. **Title**: Clear and descriptive
2. **Description**: Explain what the PR does and why
3. **Tests**: Include tests for new functionality
4. **Documentation**: Update docs if needed
5. **Quality**: All quality checks must pass

Example PR description:

.. code-block:: markdown

    ## Description
    
    Adds support for extracting equations from PDF documents using OCR.
    
    ## Changes
    
    - Add equation detection using Tesseract OCR
    - Add ExtractionType.EQUATION enum value
    - Update Document class to handle equation extraction
    - Add tests for equation extraction
    
    ## Testing
    
    - [x] Added unit tests for equation extraction
    - [x] Added integration tests with sample PDFs
    - [x] All existing tests pass
    
    ## Documentation
    
    - [x] Updated API documentation
    - [x] Added examples for equation extraction

Issue Reporting
---------------

When reporting issues, please include:

1. **Environment**: Python version, OS, docviz version
2. **Reproduction**: Steps to reproduce the issue
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Error messages**: Full error traceback
6. **Sample files**: If applicable, provide sample documents

Example issue:

.. code-block:: markdown

    ## Environment
    
    - Python: 3.11.0
    - OS: Ubuntu 22.04
    - docviz-python: 0.7.0
    
    ## Issue
    
    When extracting tables from PDFs with complex layouts, some table cells are missing.
    
    ## Steps to Reproduce
    
    1. Load a PDF with complex table layout
    2. Extract content with `includes=[ExtractionType.TABLE]`
    3. Check the extracted table data
    
    ## Expected Behavior
    
    All table cells should be extracted correctly.
    
    ## Actual Behavior
    
    Some cells in the middle of tables are empty or missing.
    
    ## Error Messages
    
    No errors, but incomplete data extraction.

Documentation
-------------

When contributing documentation:

1. **Use RST format** for Sphinx documentation
2. **Include code examples** that work
3. **Update API docs** for new features
4. **Add type hints** in docstrings
5. **Test documentation** builds correctly

Building Documentation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Install documentation dependencies
    uv pip install sphinx sphinx-rtd-theme sphinx-copybutton

    # Build documentation
    cd docs
    make html

    # View documentation
    open _build/html/index.html

Release Process
---------------

For maintainers, the release process involves:

1. **Update version** in `pyproject.toml`
2. **Update changelog** with new features/fixes
3. **Create release tag** on GitHub
4. **Build and publish** to PyPI

.. code-block:: bash

    # Update version
    # Edit pyproject.toml
    
    # Build package
    uv build
    
    # Publish to PyPI
    uv publish

Getting Help
------------

* **GitHub Issues**: For bug reports and feature requests
* **GitHub Discussions**: For questions and general discussion
* **Documentation**: Check the docs for usage examples

Thank you for contributing to docviz-python!
