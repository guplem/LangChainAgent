# LangChainAgent

A reference LangChain agent that does math without using an LLM. Built so a
Python developer who is new to agents can read it on a single afternoon and
walk away with the concepts that real complex agents are made of.

The same question (`add 2 and 3`) runs through three different LangChain
shapes (**chain**, **agent**, **graph**) so you can see each shape, compare
the trace each one produces in LangSmith, and pick the right one when you
build your next agent.

## Why this project exists

LangChain has a lot of moving parts: tools, runnables, callbacks, tracing,
agent loops, state graphs. Tutorials usually bundle them with a real LLM,
which adds API keys, token costs, and non-determinism. This repo strips the
LLM out so the only thing you have to learn is the infrastructure.

## Concepts in one page

If any of these are new, read this section before the code.

- **Tool**: a Python function the agent can call. Decorated with `@tool`.
  The function's docstring and type hints become a schema the agent reads.
  See `src/mathagent/tools.py`.
- **Runnable**: LangChain's universal interface. Anything that has
  `.invoke()`, `.batch()`, and `.stream()` is a Runnable. Tools, chat models,
  chains, agents, and graphs are all Runnables, which is why you can compose
  them.
- **Chat model**: a Runnable whose input is a list of messages and whose
  output is an `AIMessage`. In a real agent, this is the LLM. Here we
  substitute `RuleBasedChatModel`, see `src/mathagent/chat_model.py`.
- **Tool call**: a structured field on an `AIMessage` that says "call tool
  X with arguments Y". When a chat model emits one, the agent loop runs
  the tool and feeds the result back as a `ToolMessage`.
- **Agent loop**: chat model -> tool -> chat model -> ... until the chat
  model returns a normal `AIMessage` with no tool calls. That last message
  is the final answer.
- **Callback / tracing**: every Runnable run produces events (started,
  ended, errored, child started). LangSmith and LangFuse listen to these
  events to draw the trace tree you see in their UI. See
  `src/mathagent/tracing.py`.
- **State graph**: LangGraph's model of an agent. Nodes do things, edges
  decide what to do next. `create_agent` builds one under the hood; you can
  also build one by hand (see `src/mathagent/graph.py`).

## The three routing paths

Each path takes the same input (a math question), uses the same tools, and
produces the same answer. What differs is the LangChain machinery wrapped
around the tool call. The REPL asks you to pick a mode at start.

### chain (`src/mathagent/chain.py`)

A `RunnableLambda` that calls the parser, looks up the tool, and invokes it.
No agent loop, no messages. The simplest LangChain pattern. Use it when the
control flow is fully deterministic and you do not need multi-step reasoning.

**Conversation: single-turn only.** A chain is a pure function. It has no
state and no notion of "previous turn". Use the agent or graph path if you
want follow-ups.

### agent (`src/mathagent/agent.py`)

`langchain.agents.create_agent`, the modern one-liner. Wraps the rule-based
chat model and the tools into a compiled state graph that runs the full agent
loop. This is the recommended pattern for new agents in LangChain 1.x.

**Conversation: multi-turn.** Calls sharing a `configurable.thread_id`
resume the prior conversation (via an `InMemorySaver` checkpointer). With
the context-aware parser, follow-ups like `"add 2"` after `"add 3 and 5 -> 8"`
become `8 + 2 = 10`. See ADR 0007.

*History note:* tutorials from 2023-2024 use `AgentExecutor` and
`create_tool_calling_agent`. Those names were removed in LangChain 1.x.
`create_agent` is their replacement.

### graph (`src/mathagent/graph.py`)

An **explicit** LangGraph `StateGraph` with `model` and `tools` nodes, a
state schema, and conditional edges. Same standard LangGraph primitives
`create_agent` uses internally, but composed by hand so every node, edge,
and routing decision is visible in source. Educational: it builds the same
loop `create_agent` builds for you. Use this lower-level form when
`create_agent`'s defaults are not enough (custom routing, multiple models,
parallel branches).

**Conversation: multi-turn.** Same memory model as the agent path: a
`thread_id` in the config keys into an `InMemorySaver` checkpointer.

## Tracing

By default the project sends traces to **LangSmith**. Switching to
**LangFuse** (or both at once) is one env var. See ADR 0004 for the design
and `src/mathagent/tracing.py` for the wiring.

`TRACING_BACKEND` controls which handlers are attached:

| Value | What it does |
|---|---|
| `langsmith` (default) | Relies on `LANGCHAIN_TRACING_V2=true`. LangChain auto-registers its tracer. |
| `langfuse` | Adds the LangFuse callback handler. Reads `LANGFUSE_*` env vars. |
| `both` | LangFuse on top of LangSmith. Useful when migrating. |
| `none` | No callbacks. Also unset `LANGCHAIN_TRACING_V2` for full silence. |

### Flushing on exit

LangFuse v3+ buffers trace events in memory and ships them in batches on a
background thread. A short-lived process (REPL, script, CI job) can exit
before that thread has sent the last batch, which drops the tail of the
run. The REPL calls `tracing.flush_callbacks(callbacks)` in a `finally`
block so every exit path flushes once. If you import the library and call
the runnables yourself, call `flush_callbacks` on shutdown too. It is a
no-op for `langsmith` / `none` (LangSmith auto-flushes via `atexit`).

## Quick start

### 1. Install uv (one-time per machine)

uv is the package manager. Follow the official install for your OS:
<https://docs.astral.sh/uv/getting-started/installation/>.

### 2. Install dependencies

uv creates the virtual environment for you. No `python -m venv` step needed.

```bash
uv sync
```

> The first run downloads LangChain, LangGraph, LangSmith, LangFuse and dev
> tools (pytest, ruff, mypy) into a local `.venv` directory.

No manual activation needed; `uv run` handles it. To activate anyway:
`source .venv/bin/activate` (bash/zsh) or `.venv\Scripts\Activate.ps1`
(PowerShell). `deactivate` undoes it.

### 3. Fill in your secret keys

The repo ships a `.env` file with public, non-secret defaults
(`LANGCHAIN_TRACING_V2`, `LANGCHAIN_PROJECT`, `TRACING_BACKEND`,
`LANGFUSE_HOST`). You do not need to edit it. Secrets live in a separate
`.env.local` file that is gitignored.

Copy the secrets template:

**macOS / Linux (bash, zsh):**
```bash
cp .env.local.example .env.local
```

**Windows (PowerShell):**
```powershell
Copy-Item .env.local.example .env.local
```

Open `.env.local` and fill the keys for the backend you want to use:

- **LangSmith** (the default backend). Get a key at
  <https://smith.langchain.com/> -> *Settings* -> *API Keys* -> *Create API
  Key*. Paste it into `LANGCHAIN_API_KEY`.
- **LangFuse** (only if you set `TRACING_BACKEND=langfuse` or `both` in
  `.env`). Sign up at <https://cloud.langfuse.com/> (or self-host), open
  your project -> *Settings* -> *API Keys* -> *Create new API keys*. Paste
  the public and secret keys into `LANGFUSE_PUBLIC_KEY` and
  `LANGFUSE_SECRET_KEY`. If you use the US region or a self-hosted
  instance, also override `LANGFUSE_HOST` here (the value in `.env.local`
  wins over `.env`).

You can leave LangFuse blank if you only want LangSmith.

### 4. Load both env files into your shell

The REPL reads `os.environ` directly; nothing auto-loads `.env` files. Run
this in the **same terminal session** that you will use to start the REPL.
Source `.env` first (defaults), then `.env.local` (your secrets, which
override anything in `.env` when names collide):

**macOS / Linux (bash, zsh):**
```bash
set -a && source .env && source .env.local && set +a
```

**Windows (PowerShell):**
```powershell
Get-ChildItem .env, .env.local | ForEach-Object {
  Get-Content $_ | ForEach-Object {
    if ($_ -match '^\s*([^#=]+)=(.*)$') { Set-Item "env:$($matches[1].Trim())" $matches[2].Trim() }
  }
}
```

Verify the key was loaded:

**macOS / Linux:**
```bash
echo $LANGCHAIN_API_KEY
```

**Windows (PowerShell):**
```powershell
echo $env:LANGCHAIN_API_KEY
```

You should see your key printed. A blank line means the load step did not
run in this terminal.

### 5. Run the REPL

```bash
uv run python -m mathagent
```

You will be asked for a mode, then prompted for math questions. Try the same
question in each mode and compare traces in the LangSmith UI.

Example session:

```
MathAgent REPL
Three modes, three LangChain shapes that share the same tools:
  chain  -> RunnableLambda composition. Deterministic, no loop.
  agent  -> create_agent (LangGraph under the hood). Modern agent path.
  graph  -> Explicit LangGraph state machine. Educational.

mode> agent

Ready (agent mode). Ask a math question. Type 'quit' to exit.

> add 2 and 3
5.0
> what is 10 divided by 4?
2.5
> quit
```

## Development

```bash
uv run pytest          # run tests
uv run ruff check .    # lint
uv run ruff format .   # format
uv run mypy src tests  # type-check
```

The project follows TDD: write a failing test, then code. See `tests/` for
working examples of every layer.

## Features

- Four math tools (`add`, `subtract`, `multiply`, `divide`) defined via the
  `@tool` decorator.
- A simple free-form parser that maps human phrasings to tool calls.
- Three runnable shapes that share the tools and the parser.
- LangSmith tracing on by default; LangFuse switchable via `TRACING_BACKEND`.
- Strict typing (mypy strict) and lint/format (ruff).

## Project layout

```
src/mathagent/
  __init__.py        # public API: build_chain, build_agent, build_graph
  __main__.py        # python -m mathagent entry
  repl.py            # interactive prompt loop
  tools.py           # @tool definitions
  parser.py          # text -> (tool name, args)
  chat_model.py      # RuleBasedChatModel: BaseChatModel subclass with no LLM
  chain.py           # chain path
  agent.py           # agent path (create_agent)
  graph.py           # graph path (explicit StateGraph)
  tracing.py         # TRACING_BACKEND -> callback handlers
tests/               # one file per source module
adr/                 # design decisions, see ADR index below
```

## Design decisions (ADRs)

The "why" behind each choice lives in `adr/`:

- [ADR 0001](adr/0001-python-and-uv.md): Python 3.12 with uv
- [ADR 0002](adr/0002-langchain-without-llm.md): LangChain without an LLM
- [ADR 0003](adr/0003-three-routing-paths.md): Three routing paths
- [ADR 0004](adr/0004-tracing-langsmith-then-langfuse.md): LangSmith now, LangFuse switchable
- [ADR 0005](adr/0005-repl-entry-point.md): REPL as the entry point
- [ADR 0006](adr/0006-pytest-and-tdd.md): pytest with TDD

## Troubleshooting

**`ImportError: cannot import name 'AgentExecutor' from 'langchain.agents'`**
You are on LangChain 1.x. `AgentExecutor` was removed; use `create_agent`
from `langchain.agents` instead. See ADR 0003.

**Traces are not showing up in LangSmith.**
Check that `LANGCHAIN_TRACING_V2=true` is set in the same shell that runs
`uv run python -m mathagent`. Verify with `echo $env:LANGCHAIN_API_KEY`
(PowerShell) or `echo $LANGCHAIN_API_KEY` (bash). Check
`LANGCHAIN_PROJECT` if you do not see them in your default project.

**`langfuse` is not installed.**
Run `uv sync` again. langfuse is a runtime dependency in `pyproject.toml`.
