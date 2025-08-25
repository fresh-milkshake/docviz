import sys
from subprocess import CalledProcessError, run


def main(target: str | None = None) -> None:
    """Run quality checks (ruff, pyright) on a target path.

    :param target: Optional directory or file to check. Defaults to ``"."`` if not provided.
    :returns: ``None``.
    :raises subprocess.CalledProcessError: If any subprocess fails.
    """
    check_target = target or "."
    commands: list[list[str]] = [
        [
            "uv",
            "run",
            "ruff",
            "check",
            check_target,
            "--fix",
            "--unsafe-fixes",
        ],
        [
            "uv",
            "run",
            "ruff",
            "format",
            check_target,
        ],
        [
            "uv",
            "run",
            "pyright",
            check_target,
        ],
    ]
    try:
        for command in commands:
            run(command, check=True)
    except CalledProcessError as exc:
        print(f"Process failed with exit code {exc.returncode}")
        raise


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    main(arg)
