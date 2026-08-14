"""Strict HTTP contracts for tenant-scoped in-app notifications."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from careerpilot_api.contracts import StrictContract
from careerpilot_core import NotificationCategory  # noqa: TC001


class NotificationPreferenceRequest(StrictContract):
    enabled_categories: Annotated[list[NotificationCategory], Field(max_length=3)]


class NotificationPreferenceResponse(StrictContract):
    enabled_categories: list[NotificationCategory]


class NotificationResponse(StrictContract):
    notification_id: str
    event_id: str
    category: NotificationCategory
    subject_ref: str
    message_key: str
    created_at: str
    read_at: str | None
