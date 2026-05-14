# ADR 0004: LangSmith now, LangFuse switchable later

## Status

Accepted, 2026-05-14.

## Context

The owner wants to see traces for every agent run. LangSmith is the
LangChain-native option: when `LANGCHAIN_TRACING_V2=true` is set, LangChain
auto-registers a tracer and every `.invoke()` produces spans. LangFuse is the
open-source alternative the owner wants to evaluate later.

If the tracing wiring is hardcoded to LangSmith, switching means touching
every `.invoke()` call. If it is abstracted from day one, switching is one
env var.

## Decision

Introduce a single function `tracing.get_callbacks()` that reads the
`TRACING_BACKEND` env var and returns the list of callback handlers to pass
to every `.invoke()` call:

- `langsmith` (default): returns `[]`. LangChain auto-registers the LangSmith
  tracer from `LANGCHAIN_TRACING_V2`.
- `langfuse`: returns `[langfuse.langchain.CallbackHandler()]`. (The legacy
  `langfuse.callback` import path was removed in LangFuse v3.)
- `both`: returns the LangFuse handler on top of LangSmith. Useful for
  comparing the two during migration.
- `none`: returns `[]` and the caller is expected to also unset
  `LANGCHAIN_TRACING_V2`.

The REPL passes `get_callbacks()` to every `.invoke(..., config={"callbacks": ...})`
call. The function is the single point of change when the backend changes.

## Consequences

- LangFuse SDK is a runtime dependency (`pyproject.toml`) so the import in
  `tracing.py` does not fail when the backend is `langsmith`. This is a small
  cost (~2 MB installed) and a worthwhile tradeoff for "switch with one env var".
- The agent code itself is unaware of the backend. Adding a third backend
  (Phoenix, OpenLLMetry, etc.) is one function in `tracing.py` plus a value
  in the `TRACING_BACKEND` enum.
- Tests disable tracing globally (`conftest.py`) so unit tests never reach
  out to an external service.
