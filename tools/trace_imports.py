"""
Import tracing CLI tool.

This tool allows you to trace and monitor import operations in Python modules,
helping identify slow imports and import failures.
"""

import argparse
import sys
import time
from collections.abc import Callable
from typing import Any

original_import: Callable[..., Any] = None  # type: ignore
start_time: float = 0.0
import_times: dict[str, float] = {}


def traced_import(name: str, globals=None, locals=None, fromlist=(), level: int = 0):
    """
    Wrapper for the built-in import function that traces import operations.

    :param name: Module name to import
    :param globals: Global namespace
    :param locals: Local namespace
    :param fromlist: List of names to import from the module
    :param level: Import level (0 for absolute imports)
    :return: Imported module
    """
    import_start = time.time()
    print(f"[{time.time() - start_time:.3f}s] Importing: {name}")

    try:
        result = original_import(name, globals, locals, fromlist, level)
        import_end = time.time()
        import_duration = import_end - import_start

        import_times[name] = import_duration

        if import_duration > 0.1:
            print(
                f"[{time.time() - start_time:.3f}s] ⚠️  SLOW IMPORT: {name} took {import_duration:.3f}s"
            )

        return result
    except Exception as e:
        print(f"[{time.time() - start_time:.3f}s] ❌ Failed to import {name}: {e}")
        raise


def setup_import_tracing() -> None:
    """Set up import tracing by replacing the built-in import function."""
    global original_import, start_time
    original_import = __builtins__.__import__
    start_time = time.time()
    __builtins__.__import__ = traced_import


def display_import_summary() -> None:
    """
    Display a summary table of the slowest imports sorted by duration.
    """
    if not import_times:
        print("\n📊 No import timing data collected.")
        return

    sorted_imports = sorted(import_times.items(), key=lambda x: x[1])

    significant_imports = [(name, duration) for name, duration in sorted_imports if duration > 0.01]

    if not significant_imports:
        print("\nAll imports completed in under 0.01 seconds.")
        return

    print("\n" + "=" * 80)
    print("IMPORT TIMING SUMMARY (sorted by duration)")
    print("=" * 80)
    print(f"{'Rank':<4} {'Duration (s)':<12} {'Module':<64}")
    print("-" * 80)

    for i, (name, duration) in enumerate(significant_imports[-20:], 1):
        display_name = name if len(name) <= 62 else "..." + name[-59:]
        print(f"{i:<4} {duration:<12.3f} {display_name:<64}")

    if len(significant_imports) > 20:
        print(f"... and {len(significant_imports) - 20} more imports")

    total_imports = len(import_times)
    slow_imports = len([d for d in import_times.values() if d > 0.1])
    total_time = sum(import_times.values())

    print("-" * 80)
    print("📈 Statistics:")
    print(f"   • Total imports: {total_imports}")
    print(f"   • Slow imports (>0.1s): {slow_imports}")
    print(f"   • Total import time: {total_time:.3f}s")
    print(f"   • Average import time: {total_time / total_imports:.3f}s")
    print("=" * 80)


def trace_module_imports(module_name: str, verbose: bool = False) -> None:
    """
    Trace imports for a specific module.

    :param module_name: Name of the module to trace imports for
    :param verbose: Whether to enable verbose output
    """
    if verbose:
        print(f"Tracing imports for module: {module_name}")

    print(f"[{time.time() - start_time:.3f}s] Starting import tracing for: {module_name}")

    try:
        __import__(module_name)
        print(f"[{time.time() - start_time:.3f}s] Successfully imported: {module_name}")
    except Exception as e:
        print(f"[{time.time() - start_time:.3f}s] ❌ Failed to import {module_name}: {e}")
        if verbose:
            import traceback

            traceback.print_exc()


def main() -> int:
    """
    Main CLI entry point.

    :return: Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="Trace Python module imports to identify slow imports and failures",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s start_bot                    
  %(prog)s agent.pipeline.search        
  %(prog)s --verbose shared.database    
  %(prog)s --help                       
        """,
    )

    parser.add_argument("module", help="Name of the module to trace imports for")

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output with full tracebacks",
    )

    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    args = parser.parse_args()

    setup_import_tracing()

    try:
        trace_module_imports(args.module, args.verbose)

        display_import_summary()

        return 0
    except KeyboardInterrupt:
        print("\n[INFO] Import tracing interrupted by user")
        display_import_summary()
        return 1
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        display_import_summary()
        return 1


if __name__ == "__main__":
    sys.exit(main())
