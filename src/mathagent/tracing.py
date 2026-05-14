"""Tracing backend selection.

LangChain emits trace events through a `callbacks` channel. Some backends register
themselves implicitly (LangSmith does this when `LANGCHAIN_TRACING_V2=true`), so
you do not need to pass them. Other backends (like LangFuse) need an explicit
callback handler passed to every `.invoke()` call.

`get_callbacks()` reads the `TRACING_BACKEND` env var and returns the list of
explicit handlers needed for that backend. The REPL passes the result to every
`.invoke(..., config={"callbacks": ...})` call.

Backend values:

  - langsmith (default): no explicit handlers. LangChain auto-registers the
                         LangSmith tracer from env vars. Set LANGCHAIN_TRACING_V2=true.
  - langfuse           : add the LangFuse handler. To stop emitting to LangSmith
                         too, also unset LANGCHAIN_TRACING_V2.
  - both               : add the LangFuse handler on top of LangSmith. Useful when
                         migrating from one backend to the other.
  - none               : empty list. Also unset LANGCHAIN_TRACING_V2 if you want
                         no traces at all.
"""

from __future__ import annotations

import os
from collections.abc import Sequence

from langchain_core.callbacks.base import BaseCallbackHandler


class TracingConfigError(RuntimeError):
    """Raised when the tracing backend is misconfigured."""


def get_callbacks() -> Sequence[BaseCallbackHandler]:
    """Return the callback handlers for the current TRACING_BACKEND value."""
    backend = os.environ.get("TRACING_BACKEND", "langsmith").lower()
    if backend in ("langsmith", "none"):
        return []
    if backend in ("langfuse", "both"):
        return [_build_langfuse_handler()]
    raise TracingConfigError(
        f"Unknown TRACING_BACKEND={backend!r}. Expected one of: langsmith, langfuse, both, none."
    )


def _build_langfuse_handler() -> BaseCallbackHandler:
    """Construct the LangFuse callback handler.

    LangFuse reads its credentials from LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY /
    LANGFUSE_HOST env vars when the handler is instantiated with no arguments.
    """
    try:
        from langfuse.callback import CallbackHandler
    except ImportError as e:
        raise TracingConfigError(
            "langfuse is required when TRACING_BACKEND is 'langfuse' or 'both' "
            "but it is not installed. Run: uv sync"
        ) from e
    return CallbackHandler()
