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

Graceful degradation: when a backend is requested but its keys are missing,
`get_callbacks()` quietly disables that backend (popping LANGCHAIN_TRACING_V2
to stop LangSmith from emitting 401 errors per call, or skipping the LangFuse
handler so the SDK does not log its own "client disabled" warning) and prints
one line to stderr explaining what happened. The agent always runs.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Sequence

from langchain_core.callbacks.base import BaseCallbackHandler


class TracingConfigError(RuntimeError):
    """Raised when the tracing backend is misconfigured."""


def get_callbacks() -> Sequence[BaseCallbackHandler]:
    """Return the callback handlers for the current TRACING_BACKEND value.

    Side effect: when `LANGCHAIN_API_KEY` is missing and `langsmith` or `both`
    is requested, `LANGCHAIN_TRACING_V2` is popped from `os.environ` so the
    LangSmith client does not attempt uploads it cannot authenticate. A
    one-line notice goes to stderr in that case, and again if LangFuse keys
    are missing.
    """
    backend = os.environ.get("TRACING_BACKEND", "langsmith").lower()
    if backend not in ("langsmith", "langfuse", "both", "none"):
        raise TracingConfigError(
            f"Unknown TRACING_BACKEND={backend!r}. "
            "Expected one of: langsmith, langfuse, both, none."
        )

    callbacks: list[BaseCallbackHandler] = []

    if backend in ("langsmith", "both") and not os.environ.get("LANGCHAIN_API_KEY"):
        # Disable the auto-registered LangSmith tracer; with no key it 401s on every call.
        os.environ.pop("LANGCHAIN_TRACING_V2", None)
        print(
            "[tracing] LANGCHAIN_API_KEY not set; LangSmith tracing disabled.",
            file=sys.stderr,
        )

    if backend in ("langfuse", "both"):
        if os.environ.get("LANGFUSE_PUBLIC_KEY") and os.environ.get(
            "LANGFUSE_SECRET_KEY"
        ):
            callbacks.append(_build_langfuse_handler())
        else:
            print(
                "[tracing] LANGFUSE_PUBLIC_KEY/SECRET_KEY not set; "
                "LangFuse tracing disabled.",
                file=sys.stderr,
            )

    return callbacks


def _build_langfuse_handler() -> BaseCallbackHandler:
    """Construct the LangFuse callback handler.

    LangFuse reads its credentials from LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY /
    LANGFUSE_BASE_URL env vars when the handler is instantiated with no arguments.
    (LANGFUSE_HOST is still accepted as a legacy fallback name in v4, but the
    official UI and docs now use LANGFUSE_BASE_URL.)

    Import path note: this is `langfuse.langchain.CallbackHandler`, the LangFuse
    v3+ location. The legacy `langfuse.callback` module was removed in v3. If
    you see older tutorials importing from `langfuse.callback`, that path no
    longer exists on the installed version.
    """
    try:
        from langfuse.langchain import CallbackHandler
    except ImportError as e:
        raise TracingConfigError(
            "langfuse is required when TRACING_BACKEND is 'langfuse' or 'both' "
            "but it is not installed. Run: uv sync"
        ) from e
    return CallbackHandler()


def flush_callbacks(callbacks: Sequence[BaseCallbackHandler]) -> None:
    """Ship any buffered trace events before the process exits.

    LangFuse v3+ buffers events in memory and ships them in batches on a
    background thread. If the process exits before that thread has shipped
    the last batch, the tail of the run is lost. `Langfuse.flush()` forces
    the buffer to be drained and waits for the network round-trip to finish.

    LangSmith's client auto-flushes via its own `atexit` hook, so we only
    flush LangFuse here. The function is a no-op when the callback list
    does not contain a LangFuse handler (e.g. langsmith / none modes).

    Call this once at REPL exit, script end, or container shutdown.
    """
    if not callbacks:
        return
    try:
        from langfuse import get_client
        from langfuse.langchain import CallbackHandler as LangFuseHandler
    except ImportError:
        return
    if any(isinstance(cb, LangFuseHandler) for cb in callbacks):
        get_client().flush()
