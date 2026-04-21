"""Lightweight structured logging helpers."""

from __future__ import annotations

import json
import logging
from typing import Any

from .config import get_settings


class JsonFormatter(logging.Formatter):
    """Render log records as compact JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("trace_id", "session_id", "event_type"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        return json.dumps(payload, ensure_ascii=False)


_configured = False


def configure_logging() -> None:
    """Configure root logging once."""

    global _configured
    if _configured:
        return
    settings = get_settings()
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return configured logger."""

    configure_logging()
    return logging.getLogger(name)
