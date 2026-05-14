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

A `RunnableLambda` that calls the parser and invokes the matching tool. No
LLM, no message list, no loop. This is the "chain" pattern in LangChain
terminology: deterministic composition of Runnables.

### 2. Agent (`agent.py`)

`langchain.agents.create_agent`. A one-liner that returns a compiled LangGraph
state machine. This is the modern, recommended path in LangChain 1.x (2026).
The previous API, `AgentExecutor` + `create_tool_calling_agent`, was removed
in 1.x. If you see those names in older tutorials, this is the replacement.

### 3. Custom graph (`graph.py`)

A hand-built `StateGraph` with a `model` node, a `tools` node, a state schema,
and explicit conditional edges. Builds the same loop that `create_agent` would
generate, but exposes every component. Educational only -- for production use
the agent path.

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
