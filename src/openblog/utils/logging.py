"""Logging configuration for OpenBlog."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import TextIO


def configure_logging(
    level: int | str = logging.INFO,
    log_file: str | Path | None = None,
    format_string: str | None = None,
    verbose: bool = False,
    debug: bool = False,
) -> logging.Logger:
    """Configure logging for OpenBlog.

    Args:
        level: Logging level (int or string like 'DEBUG').
        log_file: Optional file path for logging.
        format_string: Custom format string.
        verbose: Enable verbose output (INFO level).
        debug: Enable debug output (DEBUG level).

    Returns:
        Configured root logger for openblog.
    """
    # Determine log level
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    elif isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    # Default format
    if format_string is None:
        if debug:
            format_string = (
                "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
            )
        else:
            format_string = "%(asctime)s | %(levelname)-8s | %(message)s"

    # Create formatter
    formatter = logging.Formatter(format_string, datefmt="%H:%M:%S")

    # Get the openblog logger
    logger = logging.getLogger("openblog")
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Don't propagate to root logger
    logger.propagate = False

    return logger


class RichHandler(logging.Handler):
    """Custom logging handler using Rich for pretty output.

    Only used when Rich is available and terminal is interactive.
    """

    def __init__(
        self,
        stream: TextIO | None = None,
        show_time: bool = True,
        show_path: bool = False,
    ) -> None:
        """Initialize the Rich handler.

        Args:
            stream: Output stream.
            show_time: Show timestamp.
            show_path: Show file path.
        """
        super().__init__()
        self.stream = stream or sys.stdout
        self.show_time = show_time
        self.show_path = show_path

        try:
            from rich.console import Console

            self.console = Console(file=self.stream, force_terminal=True)
            self.rich_available = True
        except ImportError:
            self.rich_available = False

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record.

        Args:
            record: Log record to emit.
        """
        if not self.rich_available:
            return

        try:
            msg = self.format(record)

            # Color based on level
            style = {
                logging.DEBUG: "dim",
                logging.INFO: "blue",
                logging.WARNING: "yellow",
                logging.ERROR: "red bold",
                logging.CRITICAL: "red bold reverse",
            }.get(record.levelno, "")

            self.console.print(msg, style=style)

        except Exception:
            self.handleError(record)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the openblog namespace.

    Args:
        name: Logger name (will be prefixed with 'openblog.').

    Returns:
        Logger instance.
    """
    if not name.startswith("openblog."):
        name = f"openblog.{name}"
    return logging.getLogger(name)
