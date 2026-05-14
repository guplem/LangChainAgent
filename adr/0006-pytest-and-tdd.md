# ADR 0006: pytest with a TDD workflow

## Status

Accepted, 2026-05-14.

## Context

The owner wants strict test discipline to build the habit before working on
production agents. pytest is the standard choice in Python.

## Decision

- Use **pytest** with `pytest-cov` for coverage.
- Follow **TDD**: every new feature starts as a failing test. The CLAUDE.md
  front-loads the rule and routes test execution through the `test-runner`
  agent so it is hard to forget.
- Tests live under `tests/` and import the package via `pythonpath = ["src"]`
  in `pyproject.toml`.
- A `conftest.py` autouse fixture disables tracing during tests so unit tests
  never call LangSmith or LangFuse.

## Consequences

- Adding a new tool, a new routing path, or a new tracing backend is preceded
  by a test. The test file becomes a worked example of the public API and
  doubles as documentation.
- CI (when added) can run `uv run pytest` as the canonical check.
- The TDD rule is enforced by convention, not by tooling. The user can opt out
  per-task, but the default is "test first".
