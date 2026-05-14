"""Tracing-config tests."""

from __future__ import annotations

import pytest

from mathagent.tracing import TracingConfigError, get_callbacks


def test_default_is_langsmith_and_returns_no_handlers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRACING_BACKEND", "langsmith")
    assert list(get_callbacks()) == []


def test_none_returns_no_handlers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRACING_BACKEND", "none")
    assert list(get_callbacks()) == []


def test_unknown_backend_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRACING_BACKEND", "bogus")
    with pytest.raises(TracingConfigError, match="Unknown TRACING_BACKEND"):
        get_callbacks()
