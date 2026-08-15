"""HTTP hardening, SSRF policy, and local abuse-control primitives."""

from __future__ import annotations

import ipaddress
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from threading import RLock
from urllib.parse import urlsplit

SECURITY_HEADERS = {
    "Cache-Control": "no-store, max-age=0",
    "Content-Security-Policy": (
        "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; "
        "form-action 'self'"
    ),
    "Cross-Origin-Opener-Policy": "same-origin",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}


class UnsafeDestinationError(ValueError):
    """Raised before any outbound connection to an unsafe destination."""


@dataclass(frozen=True, slots=True)
class ValidatedDestination:
    """Canonical HTTPS destination after hostname and every address are checked."""

    url: str
    hostname: str
    port: int


@dataclass(frozen=True, slots=True)
class ProductionSecurityConfiguration:
    """Deployment inputs that must exist before production can start."""

    public_origin: str
    managed_configuration_provider: str
    kms_key_resource: str
    edge_rate_limit_enabled: bool

    def validate(self) -> None:
        """Fail closed when TLS, managed keys, or edge controls are absent."""
        if not self.public_origin.startswith("https://"):
            raise ValueError("https_origin_required")
        if not self.managed_configuration_provider or not self.kms_key_resource:
            raise ValueError("managed_key_boundary_required")
        if not self.edge_rate_limit_enabled:
            raise ValueError("edge_rate_limit_required")


def validate_outbound_destination(
    url: str, *, resolved_addresses: tuple[str, ...], allowed_hosts: frozenset[str]
) -> ValidatedDestination:
    """Reject credentials, non-HTTPS, unapproved hosts, and non-global IP addresses."""
    parsed = urlsplit(url)
    hostname = (parsed.hostname or "").rstrip(".").casefold()
    if parsed.scheme != "https" or not hostname or parsed.username or parsed.password:
        raise UnsafeDestinationError("destination_not_allowed")
    if hostname not in allowed_hosts or parsed.fragment:
        raise UnsafeDestinationError("destination_not_allowed")
    if not resolved_addresses:
        raise UnsafeDestinationError("resolution_required")
    try:
        addresses = tuple(ipaddress.ip_address(item) for item in resolved_addresses)
    except ValueError as error:
        raise UnsafeDestinationError("invalid_address") from error
    if any(not address.is_global for address in addresses):
        raise UnsafeDestinationError("non_public_address")
    return ValidatedDestination(url=url, hostname=hostname, port=parsed.port or 443)


class LocalRateLimiter:
    """Bound local bursts; production uses a shared trusted-identity control."""

    def __init__(self, *, limit: int = 200, window_seconds: int = 60) -> None:
        if limit < 1 or window_seconds < 1:
            raise ValueError("invalid_rate_limit")
        self._limit = limit
        self._window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = RLock()

    def allow(self, key: str, *, now: float | None = None) -> bool:
        """Return false after the bounded key exceeds its sliding-window quota."""
        current = time.monotonic() if now is None else now
        with self._lock:
            entries = self._requests[key]
            threshold = current - self._window_seconds
            while entries and entries[0] <= threshold:
                entries.popleft()
            if len(entries) >= self._limit:
                return False
            entries.append(current)
            return True
