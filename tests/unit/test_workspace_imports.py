"""Smoke tests for the Phase 1 Python workspace packages."""

import careerpilot_api
import careerpilot_core


def test_core_package_is_importable() -> None:
    """Prove the framework-independent core package is discoverable."""
    assert careerpilot_core.__doc__


def test_api_package_is_importable() -> None:
    """Prove the HTTP adapter package is discoverable without starting a server."""
    assert careerpilot_api.__doc__
