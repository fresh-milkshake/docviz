from logging import getLogger


def get_logger(name: str):
    """
    Get a logger instance for a specific module.

    Args:
        name: Module name (usually __name__)

    Returns:
        Logger instance configured for the module
    """
    return getLogger(name=name)
