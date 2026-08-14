"""Privacy-safe logging and tracing foundations."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Protocol

from opentelemetry import trace

if TYPE_CHECKING:
    from careerpilot_core import TelemetryEvent

LOGGER_NAME = "careerpilot.api"


class ContentCaptureMode(StrEnum):
    NO_CONTENT = "NO_CONTENT"


@dataclass(frozen=True, slots=True)
class ExporterConfiguration:
    """Describe an exporter without credentials, clients, or network side effects."""

    destination: str
    enabled: bool = False
    content_capture: ContentCaptureMode = ContentCaptureMode.NO_CONTENT

    def __post_init__(self) -> None:
        if self.enabled:
            raise ValueError("telemetry_export_requires_separate_approval")


class TelemetryExporter(Protocol):
    def export(self, event: TelemetryEvent) -> None: ...


class DisabledTelemetryExporter:
    """Make disabled export attempts visible instead of silently dropping them."""

    def __init__(self, configuration: ExporterConfiguration) -> None:
        self.configuration = configuration

    def export(self, event: TelemetryEvent) -> None:
        del event
        raise RuntimeError(
            f"telemetry_export_disabled:{self.configuration.destination}"
        )


def telemetry_json(event: TelemetryEvent) -> str:
    """Serialize only the already validated content-free telemetry schema."""
    payload = asdict(event)
    payload["kind"] = event.kind.value
    payload["attributes"] = dict(event.attributes)
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)


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
