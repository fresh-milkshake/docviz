"""
Build script for docviz-python documentation.
"""

import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    try:
        subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Error: {e.stderr}")
        return False


def main():
    """Main build function."""
    docs_dir = Path(__file__).parent

    print("Building docviz-python documentation...")
    print("=" * 50)

    # Check if we're in the right directory
    if not (docs_dir / "conf.py").exists():
        print("Error: conf.py not found. Make sure you're running this from the docs directory.")
        sys.exit(1)

    # Generate module documentation
    print("Generating module documentation...")
    if not run_command("python generate_modules.py", "Generating modules"):
        print("Failed to generate module documentation.")
        sys.exit(1)

    print("Removing old build directory...")
    if (docs_dir / "_build").exists():
        shutil.rmtree(docs_dir / "_build")
    else:
        print("No old build directory found.")

    # Build HTML documentation
    print("Building HTML documentation...")
    if not run_command("uv run sphinx-build -b html . _build/html", "Building HTML"):
        print("Failed to build HTML documentation.")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("Documentation build completed successfully!")
    print(f"HTML documentation is available in: {docs_dir / '_build' / 'html' / 'index.html'}")
    print("\nTo serve the documentation locally, run:")
    print("  python -m http.server --directory _build/html 8000")


if __name__ == "__main__":
    main()
