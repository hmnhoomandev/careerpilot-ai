"""Privacy-safe logging and tracing foundations."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

from opentelemetry import trace

LOGGER_NAME = "careerpilot.api"


class JsonFormatter(logging.Formatter):
    """Encode allow-listed log metadata as one JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }
        for field in (
            "correlation_id",
            "duration_ms",
            "method",
            "path",
            "status_code",
        ):
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        return json.dumps(payload, separators=(",", ":"), sort_keys=True)


def configure_logging() -> logging.Logger:
    """Configure the application logger once without capturing request bodies."""
    logger = logging.getLogger(LOGGER_NAME)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def get_tracer() -> trace.Tracer:
    """Return the vendor-neutral tracer; export remains disabled by default."""
    return trace.get_tracer("careerpilot.api")
