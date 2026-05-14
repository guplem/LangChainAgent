"""Tracing-config tests."""

from __future__ import annotations

import pytest

from mathagent.tracing import TracingConfigError, flush_callbacks, get_callbacks


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


def test_flush_callbacks_is_noop_on_empty_list() -> None:
    # langsmith / none modes return [] from get_callbacks(). Flushing must
    # not raise when there is nothing LangFuse-shaped to drain.
    flush_callbacks([])


def test_flush_callbacks_is_noop_when_no_langfuse_handler() -> None:
    # If we hand it a non-LangFuse callback, flush_callbacks should do nothing.
    # Using a bare LangSmith-shaped sentinel object that is NOT a LangFuse
    # handler proves the isinstance gate works.
    from langchain_core.callbacks.base import BaseCallbackHandler

    class _Dummy(BaseCallbackHandler):
        pass

    flush_callbacks([_Dummy()])
