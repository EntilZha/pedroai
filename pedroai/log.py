import logging

from rich.logging import RichHandler

logging.basicConfig(
    format="%(message)s",
    level=logging.INFO,
    handlers=[RichHandler(rich_tracebacks=True)],
)


def get_logger(name: str):
    return logging.getLogger(name)
