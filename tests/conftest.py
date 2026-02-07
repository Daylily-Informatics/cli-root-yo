"""Shared test fixtures for cli-core-yo."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _reset_runtime():
    """Reset the runtime context between tests."""
    yield
    # Lazy import to avoid circular issues during collection
    try:
        from cli_core_yo import runtime

        runtime._reset()
    except (ImportError, AttributeError):
        pass
