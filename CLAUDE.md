# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

LangChainAgent is a reference LangChain 1.x project written in Python 3.12. It exposes the same math agent through three routing patterns (chain, agent, graph) so the reader can compare LangChain shapes side by side. There is no LLM: the parser plus a custom `BaseChatModel` substitute for one, so the full agent loop runs deterministically while still producing real LangSmith / LangFuse traces.

## Mandatory agent delegations

Before writing code that adds or changes a feature, invoke the **pattern-scout** agent to find similar existing implementations in this repo and report the conventions used.

Before changes that touch architectural areas described in ADRs (routing paths, tracing wiring, REPL, tool layer, chat-model substitution), invoke the **adr-checker** agent to check that the change does not contradict an existing decision. After significant changes, invoke it again to record a new ADR if a decision has shifted.

After writing or modifying code, invoke the **test-runner** agent to execute `uv run pytest` and report failures.

After changes that affect documented content (README sections, ADRs, code-level docstrings that the README references), invoke the **docs-checker** agent to find drift.

When the user's request is broad or exploratory ("how should we approach X?", "what would it take to add Y?"), ask whether to run `/research-agents`. Do not start coding before that decision.

## Living Document

| Discovery | Where to write |
|---|---|
| Cross-project preference or pattern | `~/.claude/CLAUDE.md` |
| Project-specific constraint, gotcha, or pattern | This file |
| Design decision with rationale | A new ADR in `adr/` |
| Wrong or outdated instruction | Correct it in place |

Persist rules when the user says "every time", "always", or "never". Use the narrowest scope that fits.

## Documentation Structure

| File | Audience | Contains |
|---|---|---|
| `README.md` | Humans getting started | Project description, concepts, quick start, troubleshooting, ADR index. |
| `CLAUDE.md` (this file) | AI agents writing code | Architecture map, patterns, gotchas, agent procedures. |
| `adr/NNNN-*.md` | Both | Design decisions with context, decision, consequences. |

No content is duplicated. If you find yourself writing the same thing twice, one of the files is wrong: pick the right home and link from the other.

## Development Commands

| Task | Command | Notes |
|---|---|---|
| Install / sync deps | `uv sync` | Creates `.venv` and installs everything including dev tools. |
| Run REPL | `uv run python -m mathagent` | Asks for mode (chain / agent / graph). |
| Run tests | `uv run pytest` | Tracing is disabled in tests via `conftest.py`. |
| Lint | `uv run ruff check .` | Selected rules: E, F, I, UP, B, SIM. |
| Format | `uv run ruff format .` | Re-run after edits before commit. |
| Type-check | `uv run mypy src tests` | Strict mode. |

## Architecture

```
src/mathagent/
  __init__.py     # Public API: build_chain, build_agent, build_graph
  __main__.py     # python -m mathagent entry
  repl.py         # Interactive prompt loop
  tools.py        # @tool definitions, ALL_TOOLS, TOOLS_BY_NAME
  parser.py       # text -> (tool_name, args). Plays the role of the LLM.
  chat_model.py   # RuleBasedChatModel: BaseChatModel subclass that calls the parser
  chain.py        # Chain path (RunnableLambda)
  agent.py        # Agent path (langchain.agents.create_agent)
  graph.py        # Graph path (explicit StateGraph + ToolNode)
  tracing.py      # TRACING_BACKEND env var -> list of callback handlers
```

The three paths share:

- `tools.py` (the `@tool` functions and the lookup map)
- `parser.py` (the text-to-tool-call translation)
- `chat_model.py` (the LLM substitute, used by agent and graph paths)
- `tracing.py` (the backend selector)

What differs per path:

- **chain**: calls the parser directly inside a `RunnableLambda`. No messages, no loop.
- **agent**: passes the rule-based chat model to `create_agent`. Returns a compiled state graph that runs the full tool-calling loop. I/O is `{"messages": [...]}`.
- **graph**: builds a `StateGraph` with `model` and `tools` nodes, conditional edges, and a state schema using `add_messages`. Same I/O shape as the agent path. Educational: it exposes what `create_agent` builds for you.

See ADR 0003 for the why.

## Test-Driven Development

This project follows TDD. Add a failing test before adding code.

- Tests live under `tests/`, one file per source module.
- `tests/conftest.py` autouse-fixture disables tracing during tests (`TRACING_BACKEND=none`, unset `LANGCHAIN_TRACING_V2`). Never call out to LangSmith or LangFuse from a unit test.
- Run via the test-runner agent or `uv run pytest`.

When you add a tool, write `test_tools.py::test_<name>` first. When you add a routing path or a tracing backend, write the corresponding test before the wiring.

## Key Patterns and Gotchas

**Tools are LangChain Runnables.** Call them via `.invoke({"a": ..., "b": ...})`, not as plain Python functions. The decorator returns a `BaseTool`, not a function. Plain calls (`add(2, 3)`) still work because the decorator is callable, but inside the agent and graph paths every call goes through `.invoke`.

**`RuleBasedChatModel.bind_tools` is a no-op.** Real chat models attach a tool schema so the LLM knows what to emit. Our parser already knows every tool by name, so we return `self`. If you add tool-validation logic later, this is the place.

**`create_agent` is the LangChain 1.x successor to `AgentExecutor`.** Older tutorials use `AgentExecutor` + `create_tool_calling_agent`. Those names were removed in 1.x. Do not reintroduce them: use `create_agent` from `langchain.agents`. See ADR 0003.

**`langgraph.prebuilt.create_react_agent` is deprecated in favor of `create_agent`.** Same loop, the langchain package is now the canonical entry. The graph path in this repo uses `StateGraph` directly, not `create_react_agent`, to stay forward-compatible.

**Agent and graph share I/O shape; chain does not.** Both `build_agent()` and `build_graph()` accept `{"messages": [("user", "...")]}` and return `{"messages": [...]}`. `build_chain()` accepts a plain string and returns a float. The REPL handles this dispatch in `_prepare_input` and `_format_output`.

**Tracing handlers are passed per-call, not registered globally.** Every `.invoke()` call in the REPL passes `config={"callbacks": get_callbacks()}`. LangSmith is the exception: it registers its tracer globally via `LANGCHAIN_TRACING_V2=true` and does not need an explicit handler. See ADR 0004.

**Tests disable tracing globally.** Adding a test that needs tracing should override the `conftest.py` fixture explicitly and document why in the test docstring.

**Add a new tool:** the `/add-tool` slash command automates this. Manually: define `@tool def newop(...)` in `tools.py`, add it to `ALL_TOOLS`, teach the parser its keywords, then add tests in `tests/test_tools.py` and `tests/test_parser.py`. The chain, agent, and graph paths pick up the new tool automatically because they pull from `ALL_TOOLS` / `TOOLS_BY_NAME`.

## Architecture Decision Records (ADRs)

Format: `NNNN-short-descriptive-title.md` under `adr/`. Each ADR has Context, Decision, Consequences. Status is one of Accepted, Superseded, Deprecated.

Index:

| ADR | Title |
|---|---|
| [0001](adr/0001-python-and-uv.md) | Python 3.12 with uv as the package manager |
| [0002](adr/0002-langchain-without-llm.md) | A LangChain agent without an LLM |
| [0003](adr/0003-three-routing-paths.md) | Three routing paths (chain, agent, graph) |
| [0004](adr/0004-tracing-langsmith-then-langfuse.md) | LangSmith now, LangFuse switchable later |
| [0005](adr/0005-repl-entry-point.md) | REPL as the primary entry point |
| [0006](adr/0006-pytest-and-tdd.md) | pytest with a TDD workflow |

Create a new ADR when a change introduces a new component, a new external dependency, or alters how an existing concept works (routing, tracing, state representation, public API). Do not create an ADR for routine bug fixes, refactors, or test additions.

## GitHub Issues, PRs, and Other Artifacts

- Always self-assign PRs: `--assignee @me`.
- Always link PRs to the relevant issue with `Closes #N` in the PR body.
- Always add the `waiting-for-human-check` label to PRs and to non-trivial issues. If the label does not exist, create it first:
  ```bash
  gh label create "waiting-for-human-check" --color "fbca04" --description "Needs a human to review before merging or progressing" || true
  ```

## Self-Updating Rules

Add a rule to this file only when:
- A user instruction includes "every time", "always", or "never".
- A non-obvious behavior bit a real change (silent failure, framework quirk, dependency surprise).
- A pattern is followed three times and is worth codifying.

Do not add rules that just describe what the code already shows. Read the code first.

## Deployment

The project is not deployed as a service. It runs locally via `uv run python -m mathagent`. The only "deployment" artifact is the LangSmith / LangFuse traces produced when env vars are set, which appear in the corresponding web UI under the project name configured in `LANGCHAIN_PROJECT` or LangFuse's project.
