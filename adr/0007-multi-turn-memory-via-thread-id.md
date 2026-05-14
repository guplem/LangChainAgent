# ADR 0007: Multi-turn memory via LangGraph checkpointer + thread_id

## Status

Accepted, 2026-05-14.

## Context

The first version of the agent and graph paths were stateless: every
`.invoke()` started with a fresh message list, so the chat model could not
see prior turns. For a math agent this is acceptable on its own, but the
project's goal is to be a reference for real complex agents. Real agents
hold conversations, so the reference must demonstrate the standard pattern.

The chain path is excluded by design (chains are pure functions; memory is an
anti-pattern there).

## Decision

Attach an `InMemorySaver` checkpointer to the compiled graph in both routing
paths:

- `agent.py`: `create_agent(model, tools=ALL_TOOLS, checkpointer=InMemorySaver())`
- `graph.py`: `builder.compile(checkpointer=InMemorySaver())`

Each `.invoke()` must include a `configurable.thread_id`. LangGraph uses the
thread_id as the key to load prior state at the start of the call and save
the new state at the end.

The REPL generates a fresh `uuid4().hex` per session and threads it through
every call. A new `reset` command in the REPL regenerates the thread_id so a
user can clear the conversation without restarting the process.

## Consequences

- Calls without a `configurable.thread_id` raise. The REPL always passes one,
  and tests pass a fixed string. Library users must do the same.
- `InMemorySaver` keeps state inside the compiled graph object, in process
  memory. State is lost on process exit, which is fine for the REPL. Real
  production agents would use a persistent checkpointer (SQLite, Postgres,
  Redis); swapping one in is a one-line change.
- Each `thread_id` is an isolated conversation. A library caller can run
  multiple parallel conversations against the same `build_agent()` instance
  by giving each a distinct thread_id.
- Chain path remains stateless on purpose. Its docstring states this; the
  README's "The three routing paths" section names it as the single-turn
  path so a reader does not look for memory there.
- Wiring memory only enables LangGraph to remember; it does not make the
  rule-based parser context-aware. The parser change that lets
  "add 2" follow "add 3 and 5" is the subject of a separate change in
  `parser.py` and `chat_model.py`.
