# ADR 0005: REPL as the primary entry point

## Status

Accepted, 2026-05-14.

## Context

The agent needs a way to be invoked so the owner can run questions through it
and inspect the traces. Three options were considered: a CLI built with Typer,
a plain script + REPL, and a library-only package.

## Decision

Ship the project as a Python module with `python -m mathagent` as the entry
point. The module starts an interactive REPL that:

1. Prints a one-paragraph description of each routing mode.
2. Asks for a mode (chain / agent / graph).
3. Builds the matching runnable once.
4. Loops on user input, invoking the runnable with tracing callbacks each turn.

A `mathagent` console script is also registered in `pyproject.toml` so the
command works on PATH after `uv sync`, but `python -m mathagent` is the
documented form.

## Consequences

- One process per mode. To compare modes, the owner exits the REPL and starts
  it again with a new mode. This is intentional: it keeps the per-invocation
  cost (model build, tool binding) out of the per-turn loop.
- No CLI framework dependency. The REPL is ~70 lines of stdlib + LangChain.
  This keeps the reference compact.
- No batch mode and no file input. If the owner wants to script questions,
  they can import `build_chain` / `build_agent` / `build_graph` from
  `mathagent` and call them directly. The library surface is small and stable.
