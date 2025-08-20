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
    """Validate that the file path exists."""
    if value is None:
        return value

    path = Path(value)
    if not path.exists():
        raise click.BadParameter(f"File does not exist: {value}")

    if not path.is_file():
        raise click.BadParameter(f"Path is not a file: {value}")

    return str(path)


def validate_output_format(ctx, param, value):
    """Validate output format."""
    if value is None:
        return SaveFormat.JSON

    try:
        return SaveFormat(value.lower())
    except ValueError as e:
        raise click.BadParameter(
            f"Invalid format. Choose from: {', '.join([f.value for f in SaveFormat])}"
        ) from e


def validate_extraction_types(ctx, param, value):
    """Validate extraction types."""
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
@click.version_option(version="0.4.0", prog_name="docviz")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def cli(verbose):
    """DocViz CLI - Extract and analyze content from documents."""
    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")


@cli.command()
@click.argument("file_path", callback=validate_file_path)
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
    """Extract content from a single document."""
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

    info_table.add_row("Version", "0.4.0")
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
