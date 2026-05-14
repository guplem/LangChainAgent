"""Tracing-config tests."""

from __future__ import annotations

import os

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


def test_langsmith_pops_tracing_v2_when_no_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # User wants LangSmith and turned on LANGCHAIN_TRACING_V2 but never filled
    # the API key. get_callbacks should pop the V2 flag so the LangSmith client
    # does not try to upload (and 401 noisily) on every call.
    monkeypatch.setenv("TRACING_BACKEND", "langsmith")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "true")
    monkeypatch.delenv("LANGCHAIN_API_KEY", raising=False)

    assert list(get_callbacks()) == []
    assert "LANGCHAIN_TRACING_V2" not in os.environ


def test_langfuse_skipped_when_keys_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRACING_BACKEND", "langfuse")
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)

    assert list(get_callbacks()) == []


def test_langfuse_handler_built_when_keys_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from langfuse.langchain import CallbackHandler as LangFuseHandler

    monkeypatch.setenv("TRACING_BACKEND", "langfuse")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-test")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-test")

    callbacks = list(get_callbacks())
    assert len(callbacks) == 1
    assert isinstance(callbacks[0], LangFuseHandler)


def test_both_with_no_keys_returns_empty_and_disables_langsmith(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TRACING_BACKEND", "both")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "true")
    monkeypatch.delenv("LANGCHAIN_API_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)

    assert list(get_callbacks()) == []
    assert "LANGCHAIN_TRACING_V2" not in os.environ
