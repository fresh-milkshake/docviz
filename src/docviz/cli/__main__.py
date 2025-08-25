#!/usr/bin/env python3
"""
DocViz CLI - Command line interface for document analysis and extraction.
"""

import json
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

from docviz import Document, ExtractionType, SaveFormat
from docviz.constants import MODELS_PATH
from docviz.lib.detection.backends import DetectionBackendEnum
from docviz.lib.functions import batch_extract
from docviz.types import DetectionConfig, ExtractionConfig

console = Console()


def print_banner():
    """Print the DocViz banner."""
    banner_text = Text("DocViz CLI", style="bold blue")
    subtitle = Text("Document Analysis and Extraction Tool", style="dim")

    panel = Panel(f"{banner_text}\n{subtitle}", border_style="blue", padding=(1, 2))
    console.print(panel)


def validate_file_path(ctx, param, value):
    """Validate that the file path exists or is a valid URL.

    This function validates input file paths for the CLI, supporting both local file
    paths and URLs. It performs existence checks for local files and URL format
    validation for remote resources.

    The function handles various input scenarios:
    - Local file paths: Validates file existence and type
    - URLs: Validates URL format without checking accessibility
    - None values: Returns as-is for optional parameters
    - Invalid paths: Raises descriptive error messages

    Args:
        ctx: Click context object (unused but required by Click callback signature).
        param: Click parameter object (unused but required by Click callback signature).
        value: The file path or URL string to validate. Can be None for optional
            parameters.

    Returns:
        str: The validated file path or URL. Returns the original value if it's a
            valid local file path or URL, or None if the input was None.

    Raises:
        click.BadParameter: If the file path is invalid, the file doesn't exist,
            or the path is not a regular file (e.g., it's a directory).

    Example:
        >>> # Valid local file
        >>> validate_file_path(None, None, "document.pdf")
        "document.pdf"
        >>>
        >>> # Valid URL
        >>> validate_file_path(None, None, "https://example.com/doc.pdf")
        "https://example.com/doc.pdf"
        >>>
        >>> # Invalid file (raises BadParameter)
        >>> validate_file_path(None, None, "nonexistent.pdf")
        # Raises: click.BadParameter: File does not exist: nonexistent.pdf
    """
    if value is None:
        return value

    # Check if it's a URL
    from docviz.lib.document.utils import is_url

    if is_url(value):
        return value

    # Check if it's a local file
    path = Path(value)
    if not path.exists():
        raise click.BadParameter(f"File does not exist: {value}")

    if not path.is_file():
        raise click.BadParameter(f"Path is not a file: {value}")

    return str(path)


def validate_output_format(ctx, param, value):
    """Validate and normalize output format specification.

    This function validates output format strings for the CLI, converting them to
    proper SaveFormat enum values. It handles case-insensitive format names and
    provides helpful error messages for invalid formats.

    The function supports all formats defined in the SaveFormat enum:
    - JSON: Structured data in JSON format
    - CSV: Comma-separated values format
    - Excel: Microsoft Excel format (.xlsx)
    - XML: Extensible Markup Language format

    Args:
        ctx: Click context object (unused but required by Click callback signature).
        param: Click parameter object (unused but required by Click callback signature).
        value: The output format string to validate. Can be None, in which case
            JSON format is used as the default.

    Returns:
        SaveFormat: The validated output format enum value. Returns SaveFormat.JSON
            if the input is None.

    Raises:
        click.BadParameter: If the format string is not a valid SaveFormat value.
            The error message includes a list of all valid format options.

    Example:
        >>> # Valid formats (case-insensitive)
        >>> validate_output_format(None, None, "json")
        <SaveFormat.JSON: 'json'>
        >>> validate_output_format(None, None, "CSV")
        <SaveFormat.CSV: 'csv'>
        >>>
        >>> # None returns default format
        >>> validate_output_format(None, None, None)
        <SaveFormat.JSON: 'json'>
        >>>
        >>> # Invalid format (raises BadParameter)
        >>> validate_output_format(None, None, "invalid")
        # Raises: click.BadParameter: Invalid format. Choose from: json, csv, excel, xml
    """
    if value is None:
        return SaveFormat.JSON

    try:
        return SaveFormat(value.lower())
    except ValueError as e:
        raise click.BadParameter(
            f"Invalid format. Choose from: {', '.join([f.value for f in SaveFormat])}"
        ) from e


def validate_extraction_types(ctx, param, value):
    """Validate and normalize extraction type specifications.

    This function validates extraction type strings for the CLI, converting them to
    proper ExtractionType enum values. It handles case-insensitive type names and
    provides special handling for the "all" type which expands to all available types.

    The function supports all extraction types defined in the ExtractionType enum:
    - all: Special value that expands to all individual types
    - table: Tabular data and structured information
    - text: Regular text content including paragraphs and headings
    - figure: Visual elements including charts, graphs, and images
    - equation: Mathematical expressions and formulas
    - other: Miscellaneous content not fitting other categories

    Args:
        ctx: Click context object (unused but required by Click callback signature).
        param: Click parameter object (unused but required by Click callback signature).
        value: The extraction type strings to validate. Can be None, in which case
            [ExtractionType.ALL] is used as the default. Can be a single string or
            a tuple of strings for multiple types.

    Returns:
        list[ExtractionType]: List of validated extraction type enum values. Returns
            [ExtractionType.ALL] if the input is None or if "all" is specified.

    Raises:
        click.BadParameter: If any extraction type string is not a valid ExtractionType
            value. The error message includes a list of all valid type options.

    Example:
        >>> # Single type
        >>> validate_extraction_types(None, None, ("table",))
        [<ExtractionType.TABLE: 'table'>]
        >>>
        >>> # Multiple types
        >>> validate_extraction_types(None, None, ("table", "text"))
        [<ExtractionType.TABLE: 'table'>, <ExtractionType.TEXT: 'text'>]
        >>>
        >>> # All types (special handling)
        >>> validate_extraction_types(None, None, ("all",))
        [<ExtractionType.ALL: 'all'>]
        >>>
        >>> # None returns default
        >>> validate_extraction_types(None, None, None)
        [<ExtractionType.ALL: 'all'>]
        >>>
        >>> # Invalid type (raises BadParameter)
        >>> validate_extraction_types(None, None, ("invalid",))
        # Raises: click.BadParameter: Invalid extraction type 'invalid'. Choose from: all, table, text, figure, equation, other
    """
    if value is None:
        return [ExtractionType.ALL]

    types = []
    for v in value:
        try:
            if v.lower() == "all":
                return [ExtractionType.ALL]
            types.append(ExtractionType(v.lower()))
        except ValueError as e:
            valid_types = [t.value for t in ExtractionType]
            raise click.BadParameter(
                f"Invalid extraction type '{v}'. Choose from: {', '.join(valid_types)}"
            ) from e

    return types


@click.group()
@click.version_option(version="0.7.0", prog_name="docviz")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def cli(verbose):
    """DocViz CLI - Extract and analyze content from documents."""
    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")


@cli.command()
@click.argument("file_path", callback=validate_file_path, help="Path to document file or URL")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option(
    "--format", "-f", callback=validate_output_format, help="Output format (json, csv, excel, xml)"
)
@click.option(
    "--types",
    "-t",
    multiple=True,
    callback=validate_extraction_types,
    help="Extraction types to include",
)
@click.option("--confidence", type=float, default=0.5, help="Detection confidence threshold")
@click.option("--device", default="cpu", help="Device to use for detection (cpu, cuda)")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def extract(file_path, output, format, types, confidence, device, verbose):
    """Extract content from a single document (local file or URL)."""
    print_banner()

    with console.status("[bold green]Processing document...", spinner="dots"):
        try:
            # Create document
            document = Document(file_path)

            # Create configurations
            detection_config = DetectionConfig(
                imagesize=1024,
                confidence=confidence,
                device=device,
                layout_detection_backend=DetectionBackendEnum.DOCLAYOUT_YOLO,
                model_path=str(MODELS_PATH / "doclayout_yolo_docstructbench_imgsz1024.pt"),
            )

            extraction_config = ExtractionConfig()

            # Extract content
            result = document.extract_content_sync(
                extraction_config=extraction_config,
                detection_config=detection_config,
                includes=types,
            )

            # Display results
            display_extraction_results(result, document.file_path.name)

            # Save to file if output specified
            if output:
                save_results(result, output, format)
                console.print(f"\n[green]Results saved to: {output}[/green]")

        except Exception as e:
            console.print(f"[red]Error processing document: {e}[/red]")
            raise click.Abort() from e


@cli.command()
@click.argument("input_dir", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--output", "-o", type=click.Path(), help="Output directory")
@click.option(
    "--format", "-f", callback=validate_output_format, help="Output format (json, csv, excel, xml)"
)
@click.option(
    "--types",
    "-t",
    multiple=True,
    callback=validate_extraction_types,
    help="Extraction types to include",
)
@click.option("--confidence", type=float, default=0.5, help="Detection confidence threshold")
@click.option("--device", default="cpu", help="Device to use for detection (cpu, cuda)")
@click.option("--pattern", default="*.pdf", help="File pattern to match")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def batch(input_dir, output, format, types, confidence, device, pattern, verbose):
    """Extract content from multiple documents in a directory."""
    print_banner()

    input_path = Path(input_dir)
    files = list(input_path.glob(pattern))

    if not files:
        console.print(
            f"[yellow]No files found matching pattern '{pattern}' in {input_dir}[/yellow]"
        )
        return

    console.print(f"[blue]Found {len(files)} files to process[/blue]")

    # Create documents
    documents = []
    for file_path in files:
        try:
            doc = Document(str(file_path))
            documents.append(doc)
        except Exception as e:
            console.print(f"[red]Error loading {file_path}: {e}[/red]")

    if not documents:
        console.print("[red]No valid documents found[/red]")
        return

    # Create configurations
    detection_config = DetectionConfig(
        imagesize=1024,
        confidence=confidence,
        device=device,
        layout_detection_backend=DetectionBackendEnum.DOCLAYOUT_YOLO,
        model_path=str(MODELS_PATH / "doclayout_yolo_docstructbench_imgsz1024.pt"),
    )

    extraction_config = ExtractionConfig()

    # Process documents with progress bar
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Processing documents...", total=len(documents))

        def progress_callback(current):
            progress.update(task, completed=current)

        try:
            results = batch_extract(
                documents,
                extraction_config=extraction_config,
                detection_config=detection_config,
                includes=types,
                progress_callback=progress_callback,
            )

            # Display summary
            display_batch_summary(results, [doc.file_path.name for doc in documents])

            # Save results if output specified
            if output:
                save_batch_results(
                    results, output, format, [doc.file_path.name for doc in documents]
                )
                console.print(f"\n[green]Results saved to: {output}[/green]")

        except Exception as e:
            console.print(f"[red]Error during batch processing: {e}[/red]")
            raise click.Abort() from e


@cli.command()
def info():
    """Show information about DocViz and available options."""
    print_banner()

    # System info
    info_table = Table(title="DocViz Information", show_header=False)
    info_table.add_column("Property", style="cyan")
    info_table.add_column("Value", style="white")

    info_table.add_row("Version", "0.7.0")
    info_table.add_row("Python", ">=3.10")
    info_table.add_row("License", "MIT")

    console.print(info_table)

    # Available extraction types
    types_table = Table(title="Available Extraction Types")
    types_table.add_column("Type", style="cyan")
    types_table.add_column("Description", style="white")

    for ext_type in ExtractionType:
        types_table.add_row(ext_type.value, f"Extract {ext_type.value} content")

    console.print(types_table)

    # Available output formats
    formats_table = Table(title="Available Output Formats")
    formats_table.add_column("Format", style="cyan")
    formats_table.add_column("Description", style="white")

    for save_format in SaveFormat:
        formats_table.add_row(save_format.value, f"Save as {save_format.value.upper()}")

    console.print(formats_table)


def display_extraction_results(result, filename):
    """Display extraction results in a table."""
    if not result.entries:
        console.print(f"[yellow]No content extracted from {filename}[/yellow]")
        return

    # Group entries by type
    by_type = {}
    for entry in result.entries:
        if entry.class_ not in by_type:
            by_type[entry.class_] = []
        by_type[entry.class_].append(entry)

    # Create summary table
    summary_table = Table(title=f"Extraction Results: {filename}")
    summary_table.add_column("Type", style="cyan")
    summary_table.add_column("Count", style="green")
    summary_table.add_column("Pages", style="yellow")

    for content_type, entries in by_type.items():
        pages = {entry.page_number for entry in entries}
        summary_table.add_row(
            content_type,
            str(len(entries)),
            f"{min(pages)}-{max(pages)}" if len(pages) > 1 else str(next(iter(pages))),
        )

    console.print(summary_table)

    # Show sample content
    console.print("\n[bold]Sample Content:[/bold]")
    for content_type, entries in by_type.items():
        if entries:
            sample = entries[0]
            console.print(f"[cyan]{content_type.upper()}:[/cyan]")
            console.print(
                f"  Page {sample.page_number}: {sample.text[:100]}{'...' if len(sample.text) > 100 else ''}"
            )
            console.print()


def display_batch_summary(results, filenames):
    """Display batch processing summary."""
    summary_table = Table(title="Batch Processing Summary")
    summary_table.add_column("File", style="cyan")
    summary_table.add_column("Entries", style="green")
    summary_table.add_column("Types", style="yellow")

    total_entries = 0
    for result, filename in zip(results, filenames, strict=False):
        entry_count = len(result.entries)
        total_entries += entry_count

        types = {entry.class_ for entry in result.entries}
        types_str = ", ".join(sorted(types)) if types else "None"

        summary_table.add_row(filename, str(entry_count), types_str)

    console.print(summary_table)
    console.print(f"\n[bold green]Total entries extracted: {total_entries}[/bold green]")


def save_results(result, output_path, format):
    """Save extraction results to file."""
    output_path = Path(output_path)

    if format == SaveFormat.JSON:
        data = {
            "entries": [
                {
                    "text": entry.text,
                    "class": entry.class_,
                    "confidence": entry.confidence,
                    "bbox": entry.bbox,
                    "page_number": entry.page_number,
                }
                for entry in result.entries
            ]
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    elif format == SaveFormat.CSV:
        import csv

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["text", "class", "confidence", "bbox", "page_number"])
            for entry in result.entries:
                writer.writerow(
                    [entry.text, entry.class_, entry.confidence, str(entry.bbox), entry.page_number]
                )

    elif format == SaveFormat.EXCEL:
        try:
            import pandas as pd

            data = []
            for entry in result.entries:
                data.append(
                    {
                        "text": entry.text,
                        "class": entry.class_,
                        "confidence": entry.confidence,
                        "bbox": str(entry.bbox),
                        "page_number": entry.page_number,
                    }
                )
            dataframe = pd.DataFrame(data)
            dataframe.to_excel(output_path, index=False)
        except ImportError as e:
            console.print(
                "[red]pandas is required for Excel export. Install with: pip install pandas[/red]"
            )
            raise click.Abort() from e

    elif format == SaveFormat.XML:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write("<extraction_results>\n")
            for entry in result.entries:
                f.write(
                    f'  <entry class="{entry.class_}" page="{entry.page_number}" confidence="{entry.confidence}">\n'
                )
                f.write(f"    <text>{entry.text}</text>\n")
                f.write("  </entry>\n")
            f.write("</extraction_results>\n")


def save_batch_results(results, output_path, format, filenames):
    """Save batch results to files."""
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    for result, filename in zip(results, filenames, strict=False):
        base_name = Path(filename).stem
        file_output = output_path / f"{base_name}.{format.value}"
        save_results(result, file_output, format)


if __name__ == "__main__":
    cli()
