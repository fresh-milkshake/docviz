Output Formats
==============

This guide covers the various output formats supported by docviz-python and how to use them effectively for different use cases.

Supported Formats
-----------------

docviz-python supports the following output formats:

* **JSON**: Structured data format with full metadata
* **CSV**: Tabular format for spreadsheet applications
* **Excel**: Microsoft Excel format with multiple sheets
* **XML**: Extensible markup language format

Each format has different strengths and is suitable for different use cases and downstream processing needs.

JSON Format
-----------

JSON is the most comprehensive format, preserving all metadata and structure information.

Basic Usage
~~~~~~~~~~~

.. code-block:: python

    import docviz

    document = docviz.Document("document.pdf")
    extractions = document.extract_content_sync()

    # Save as JSON
    extractions.save("results", save_format=docviz.SaveFormat.JSON)

JSON Structure
~~~~~~~~~~~~~

The JSON output contains the following structure:

.. code-block:: json

    {
        "entries": [
            {
                "text": "This is extracted text content...",
                "class": "text",
                "confidence": 0.95,
                "bbox": [100, 200, 500, 250],
                "page_number": 1
            },
            {
                "text": "| Column 1 | Column 2 | Column 3 |\n|----------|----------|----------|",
                "class": "table",
                "confidence": 0.88,
                "bbox": [50, 300, 550, 450],
                "page_number": 1
            }
        ]
    }

JSON Processing
~~~~~~~~~~~~~~~

.. code-block:: python

    # Access JSON data programmatically
    result_dict = extractions.to_dict()
    
    # Filter entries by type
    text_entries = [
        entry for entry in result_dict["entries"]
        if entry["class"] == "text"
    ]
    
    # Print structure information
    print(f"Total entries: {len(result_dict['entries'])}")
    for entry in result_dict["entries"]:
        print(f"Page {entry['page_number']}: {entry['class']} (confidence: {entry['confidence']:.2f})")

Filtering JSON Content
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Save only specific content types
    filtered_entries = [
        entry for entry in extractions.entries
        if entry.class_ in ["table", "figure"]
    ]
    
    filtered_extractions = docviz.ExtractionResult(
        entries=filtered_entries,
        page_number=extractions.page_number
    )

    filtered_extractions.save(
        "tables_and_figures",
        save_format=docviz.SaveFormat.JSON
    )

CSV Format
----------

CSV format provides a tabular view of extracted content, suitable for analysis in spreadsheet applications.

Basic Usage
~~~~~~~~~~~

.. code-block:: python

    import docviz

    document = docviz.Document("document.pdf")
    extractions = document.extract_content_sync()

    # Save as CSV
    extractions.save("results", save_format=docviz.SaveFormat.CSV)

CSV Structure
~~~~~~~~~~~~~

The CSV output contains the following columns:

.. csv-table:: CSV Output Columns
    :header: "Column", "Description", "Example"
    :widths: 20, 40, 40

    "page_number", "Page where content was found", "1"
    "class", "Type of content", "text, table, figure, equation"
    "text", "Extracted text content", "This is the extracted text..."
    "confidence", "Detection confidence score", "0.95"
    "bbox", "Bounding box coordinates [x1, y1, x2, y2]", "[100, 200, 500, 250]"

Working with CSV Data
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # After saving as CSV, you can read it with pandas
    import pandas as pd
    
    # Read the generated CSV
    df = pd.read_csv("results.csv")
    
    # Analyze the data
    print(f"Total entries: {len(df)}")
    print(f"Content types: {df['class_'].unique()}")
    print(f"Average confidence: {df['confidence'].mean():.2f}")

Filtering CSV Content
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Save only high-confidence extractions
    high_confidence = [
        entry for entry in extractions.entries
        if entry.confidence > 0.8
    ]

    # Create filtered result
    filtered_result = docviz.ExtractionResult(
        entries=high_confidence,
        page_number=extractions.page_number
    )

    filtered_result.save("high_confidence", save_format=docviz.SaveFormat.CSV)

Excel Format
------------

Excel format provides rich formatting options and supports multiple sheets for organized data presentation.

Basic Usage
~~~~~~~~~~~

.. code-block:: python

    import docviz

    document = docviz.Document("document.pdf")
    extractions = document.extract_content_sync()

    # Save as Excel
    extractions.save("results", save_format=docviz.SaveFormat.EXCEL)

Excel Structure
~~~~~~~~~~~~~~~

The Excel output creates a single sheet with all extraction data in tabular format, similar to CSV but with Excel formatting capabilities.

Working with Excel Data
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # After saving as Excel, you can read it with pandas
    import pandas as pd
    
    # Read the generated Excel file
    df = pd.read_excel("results.xlsx")
    
    # Analyze the data
    print(f"Total entries: {len(df)}")
    print(f"Content types: {df['class_'].unique()}")
    
    # Create pivot table
    pivot = df.pivot_table(
        values='confidence',
        index='class_',
        aggfunc=['count', 'mean']
    )
    print(pivot)

XML Format
----------

XML format provides structured markup suitable for integration with other systems.

Basic Usage
~~~~~~~~~~~

.. code-block:: python

    import docviz

    document = docviz.Document("document.pdf")
    extractions = document.extract_content_sync()

    # Save as XML
    extractions.save("results", save_format=docviz.SaveFormat.XML)

XML Structure
~~~~~~~~~~~~~

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <ExtractionResults>
        <ExtractionEntry>
            <text>This is extracted text content...</text>
            <class_>text</class_>
            <confidence>0.95</confidence>
            <bbox>[100, 200, 500, 250]</bbox>
            <page_number>1</page_number>
        </ExtractionEntry>
        <ExtractionEntry>
            <text>| Column 1 | Column 2 | Column 3 |</text>
            <class_>table</class_>
            <confidence>0.88</confidence>
            <bbox>[50, 300, 550, 450]</bbox>
            <page_number>1</page_number>
        </ExtractionEntry>
    </ExtractionResults>

Working with XML Data
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Parse the generated XML file
    import xml.etree.ElementTree as ET
    
    tree = ET.parse("results.xml")
    root = tree.getroot()
    
    # Extract data from XML
    for entry in root.findall('ExtractionEntry'):
        text = entry.find('text').text
        class_ = entry.find('class_').text
        confidence = float(entry.find('confidence').text)
        page_number = int(entry.find('page_number').text)
        
        print(f"Page {page_number}: {class_} (confidence: {confidence:.2f})")

Multiple Format Output
----------------------

Save extraction results in multiple formats simultaneously:

Basic Multi-Format
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import docviz

    document = docviz.Document("document.pdf")
    extractions = document.extract_content_sync()

    # Save in multiple formats
    extractions.save("results", save_format=[
        docviz.SaveFormat.JSON,
        docviz.SaveFormat.CSV,
        docviz.SaveFormat.EXCEL
    ])

This creates:
- ``results.json``
- ``results.csv``
- ``results.xlsx``

Format-Specific Output
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Different content for different formats
    base_name = "document_extractions"

    # Full data as JSON
    extractions.save(f"{base_name}_full", save_format=docviz.SaveFormat.JSON)

    # Tables only as Excel
    tables_only = docviz.ExtractionResult(
        entries=[e for e in extractions.entries if e.class_ == "table"],
        page_number=extractions.page_number
    )
    tables_only.save(f"{base_name}_tables", save_format=docviz.SaveFormat.EXCEL)

    # Summary as CSV
    summary_data = [
        entry for entry in extractions.entries
        if entry.confidence > 0.7
    ]
    summary_result = docviz.ExtractionResult(
        entries=summary_data,
        page_number=extractions.page_number
    )
    summary_result.save(f"{base_name}_summary", save_format=docviz.SaveFormat.CSV)

Custom Output Processing
------------------------

Post-Process Extraction Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import pandas as pd
    import json
    from pathlib import Path

    def create_analysis_report(extractions, output_dir):
        """Create comprehensive analysis report."""
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Extract statistics
        stats = {
            "total_entries": len(extractions.entries),
            "pages_processed": extractions.page_number,
            "content_types": {},
            "average_confidence": 0,
            "high_confidence_count": 0
        }
        
        # Calculate statistics
        for entry in extractions.entries:
            content_type = entry.class_
            stats["content_types"][content_type] = stats["content_types"].get(content_type, 0) + 1
            stats["average_confidence"] += entry.confidence
            if entry.confidence > 0.8:
                stats["high_confidence_count"] += 1
        
        stats["average_confidence"] /= len(extractions.entries)
        
        # Save statistics
        with open(output_path / "statistics.json", "w") as f:
            json.dump(stats, f, indent=2)
        
        # Create detailed DataFrame
        detailed_data = []
        for entry in extractions.entries:
            detailed_data.append({
                "page": entry.page_number,
                "type": entry.class_,
                "confidence": entry.confidence,
                "text_length": len(entry.text),
                "bbox_area": (entry.bbox[2] - entry.bbox[0]) * (entry.bbox[3] - entry.bbox[1]),
                "preview": entry.text[:50] + "..." if len(entry.text) > 50 else entry.text
            })
        
        df = pd.DataFrame(detailed_data)
        
        # Save detailed analysis
        df.to_excel(output_path / "detailed_analysis.xlsx", index=False)
        df.to_csv(output_path / "detailed_analysis.csv", index=False)
        
        # Create pivot tables
        pivot_by_type = df.pivot_table(
            values=['confidence', 'text_length'],
            index='type',
            aggfunc=['mean', 'count']
        )
        pivot_by_type.to_excel(output_path / "analysis_by_type.xlsx")
        
        pivot_by_page = df.pivot_table(
            values=['confidence', 'text_length'],
            index='page',
            columns='type',
            aggfunc=['mean', 'count'],
            fill_value=0
        )
        pivot_by_page.to_excel(output_path / "analysis_by_page.xlsx")

    # Usage
    document = docviz.Document("document.pdf")
    extractions = document.extract_content_sync()
    create_analysis_report(extractions, "analysis_output")

Format Conversion Utilities
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def convert_formats(input_json_path, output_formats):
        """Convert existing JSON results to other formats."""
        
        # Load JSON data
        with open(input_json_path, 'r') as f:
            data = json.load(f)
        
        # Reconstruct ExtractionResult
        entries = []
        for entry_data in data['entries']:
            entry = docviz.ExtractionEntry(
                text=entry_data['text'],
                class_=entry_data['class'],
                confidence=entry_data['confidence'],
                bbox=entry_data['bbox'],
                page_number=entry_data['page_number']
            )
            entries.append(entry)
        
        extractions = docviz.ExtractionResult(
            entries=entries,
            page_number=data.get('page_number', len(entries))
        )
        
        # Save in requested formats
        base_name = Path(input_json_path).stem
        extractions.save(base_name, save_format=output_formats)

    # Usage
    convert_formats(
        "existing_results.json",
        [docviz.SaveFormat.CSV, docviz.SaveFormat.EXCEL]
    )




Next Steps
----------

* :doc:`basic_usage` - Basic usage guide
* :doc:`advanced_usage` - Advanced features
* :doc:`configuration` - Configuration options
* :doc:`../api/index` - Complete API reference
