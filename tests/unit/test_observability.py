"""Tests for the privacy-safe structured log formatter."""

from __future__ import annotations

import json
import logging

from careerpilot_api.observability import JsonFormatter


def test_json_formatter_emits_allow_list_without_record_arguments() -> None:
    record = logging.LogRecord(
        name="careerpilot.api",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request_completed",
        args=(),
        exc_info=None,
    )
    record.correlation_id = "correlation-001"
    record.path = "/api/v1/profiles"
    record.profile_content = "private synthetic profile content"

    payload = json.loads(JsonFormatter().format(record))

    assert payload["event"] == "request_completed"
    assert payload["correlation_id"] == "correlation-001"
    assert "profile_content" not in payload
    assert "private synthetic profile content" not in json.dumps(payload)
