# ADR 0001: Python 3.12 with uv as the package manager

## Status

Accepted, 2026-05-14.

## Context

The project is a reference LangChain agent. The owner is comfortable in Python
and wants to use this codebase as a base for future agent work. The tooling
should be modern (so the patterns transfer to new projects) but not exotic
(so a junior dev can read it on day one).

## Decision

- Use **Python 3.12**, pinned via `.python-version`.
- Use **uv** for environment management, dependency resolution, and command
  execution. The project layout is the standard `pyproject.toml` + `src/`
  layout uv expects, with a `[dependency-groups]` section for dev tools.

## Consequences

- Setup is one command: `uv sync` creates `.venv`, installs everything, and
  builds the local package. No `python -m venv`, no `pip install -e .`.
- Running code and tests goes through `uv run ...`, which auto-activates the
  venv. No manual `source .venv/bin/activate` or `.venv\Scripts\Activate.ps1`
  is needed.
- Python 3.12 is well-supported by LangChain 1.x, LangGraph 1.x, LangSmith,
  and LangFuse. 3.13 was rejected because some ML/agent libraries still lag.
- New contributors must have uv installed. The README links to install
  instructions for each platform.
