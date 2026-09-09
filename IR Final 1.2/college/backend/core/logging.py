# ==============================================================================
# InsightRural — Structured Logging Configuration
# ==============================================================================
# Replaces all print() statements with structured, contextual logging.
# Provides JSON-formatted logs in production and human-readable in development.
#
# Usage:
#   from core.logging import get_logger
#   logger = get_logger("MyModule")
#   logger.info("Processing request", extra={"rank": 5000, "category": "GM"})
# ==============================================================================

import logging
import sys
from typing import Optional

from core.config import settings


# ── Log Format ────────────────────────────────────────────────────────────────

DETAILED_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s"
)

SIMPLE_FORMAT = "%(levelname)-8s | %(name)s | %(message)s"


# ── Module-level Logger Cache ─────────────────────────────────────────────────

_configured = False


def setup_logging(
    level: Optional[str] = None,
    json_output: bool = False,
) -> None:
    """
    Configure application-wide logging. Call once at startup.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR). Defaults to
               INFO in production, DEBUG if settings.DEBUG is True.
        json_output: If True, format logs as JSON (for cloud ingestion).
    """
    global _configured
    if _configured:
        return

    log_level = level or ("DEBUG" if settings.DEBUG else "INFO")

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove any existing handlers to prevent duplicate output
    root_logger.handlers.clear()

    # Ensure stdout/stderr use UTF-8 on all platforms
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    if json_output:
        # JSON format for production/cloud deployment
        handler.setFormatter(_JsonFormatter())
    else:
        # Human-readable format for development
        handler.setFormatter(logging.Formatter(DETAILED_FORMAT, datefmt="%H:%M:%S"))

    root_logger.addHandler(handler)

    # Suppress noisy third-party loggers
    for noisy in ("httpx", "httpcore", "chromadb", "urllib3", "asyncio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger. Ensures logging is set up first.

    Args:
        name: Logger name (typically module or class name).

    Returns:
        Configured logging.Logger instance.
    """
    if not _configured:
        setup_logging()
    return logging.getLogger(name)


# ── JSON Formatter ────────────────────────────────────────────────────────────

class _JsonFormatter(logging.Formatter):
    """Simple JSON log formatter for production environments."""

    def format(self, record: logging.LogRecord) -> str:
        import json
        from datetime import datetime, timezone

        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include extra fields if present
        if hasattr(record, "rank"):
            log_entry["rank"] = record.rank
        if hasattr(record, "category"):
            log_entry["category"] = record.category
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "elapsed_ms"):
            log_entry["elapsed_ms"] = record.elapsed_ms

        # Include exception info
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = {
                "type": type(record.exc_info[1]).__name__,
                "message": str(record.exc_info[1]),
            }

        return json.dumps(log_entry, default=str)
