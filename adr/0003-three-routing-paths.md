# ADR 0003: Three routing paths (chain, agent, graph)

## Status

Accepted, 2026-05-14.

## Context

LangChain offers more than one way to call tools. As a reference project, this
codebase should show the patterns the owner will see in real code and
tutorials, with enough contrast that picking between them later is informed.

## Decision

Implement three routing paths that share the same tools and the same parser.
The REPL asks the user to pick a mode at start, and the chosen mode controls
which LangChain shape runs.

### 1. Chain (`chain.py`)

An **LCEL pipeline**: two `RunnableLambda` steps composed with `|` as
`parse | dispatch`. The result is a `RunnableSequence`, the canonical
LangChain 1.x form of "a chain". No LLM, no message list, no loop -- just
deterministic composition of Runnables.

The earlier draft of this path wrapped a single `_route(text)` function in
one `RunnableLambda`. That worked but obscured the canonical `|` idiom and
made the "chain" label loose, since a single Runnable is not a chain by the
strict 1.x definition. The LCEL form was chosen so the file teaches the
single most common LangChain composition pattern.

### 2. Agent (`agent.py`)

`langchain.agents.create_agent`. A one-liner that returns a compiled LangGraph
state machine. This is the modern, recommended path in LangChain 1.x (2026).
The previous API, `AgentExecutor` + `create_tool_calling_agent`, was removed
in 1.x. If you see those names in older tutorials, this is the replacement.

### 3. Custom graph (`graph.py`)

An explicit `StateGraph` with a `model` node, a `tools` node, a state schema,
and conditional edges. Uses the same standard LangGraph primitives as
`create_agent` (`StateGraph`, `add_messages`, `ToolNode`), but composes them
by hand so every component is visible. Educational: for production, use the
agent path.

## Consequences

- The same math question runs through three different runnable shapes. The
  user can compare LangSmith traces side by side to see what each pattern
  produces. The chain has one span; agent and graph each have several.
- Code duplication is minimal because tools and the parser are shared.
- The "agent" and "graph" paths use the same I/O shape
  (`{"messages": [("user", "...")]}`) because `create_agent` is itself a
  LangGraph compilation. The chain path uses a plain string for input.
- When the owner moves on to real complex agents, they should default to the
  agent path. The graph path is useful when `create_agent`'s defaults are not
  enough (custom routing, multiple model nodes, parallel branches).
