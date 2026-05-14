"""Test configuration.

Disables tracing during tests so we never call out to LangSmith / LangFuse from a
unit test. Production code still respects env vars at runtime.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _disable_tracing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LANGCHAIN_TRACING_V2", raising=False)
    monkeypatch.setenv("TRACING_BACKEND", "none")
