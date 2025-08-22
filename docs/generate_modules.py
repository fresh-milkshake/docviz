"""
Script to generate module documentation for docviz-python.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def generate_modules_rst():
    """Generate the modules.rst file for Sphinx."""

    modules_content = """Modules
=======

.. toctree::
   :maxdepth: 4

"""

    # Add main modules
    modules = [
        "docviz",
        "docviz.lib",
        "docviz.types",
        "docviz.cli",
        "docviz.lib.document",
        "docviz.lib.functions",
    ]

    for module in modules:
        modules_content += f"   modules/{module}\n"

    # Write the modules.rst file
    modules_file = Path(__file__).parent / "api" / "modules.rst"
    modules_file.write_text(modules_content)

    # Create individual module files
    modules_dir = Path(__file__).parent / "api" / "modules"
    modules_dir.mkdir(exist_ok=True)

    for module in modules:
        module_file = modules_dir / f"{module}.rst"
        module_content = f"""{module}
{"=" * len(module)}

.. automodule:: {module}
   :members:
   :undoc-members:
   :show-inheritance:
"""
        module_file.write_text(module_content)


if __name__ == "__main__":
    generate_modules_rst()
    print("Module documentation generated successfully!")
