import logging
import sys
from pathlib import Path

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "cyberlab.log"


def setup_logger(name: str = "cyberlab", level: int = logging.DEBUG) -> logging.Logger:
    """Return a configured logger. Call once in main, reuse everywhere."""

    logger = logging.getLogger(name)

    # Prevent duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    logger.setLevel(level)

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler — INFO and above
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)

    # File handler — DEBUG and above (full audit trail)
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
