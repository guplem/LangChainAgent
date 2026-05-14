# ADR 0002: A LangChain agent without an LLM

## Status

Accepted, 2026-05-14.

## Context

The owner wants a reference project to learn LangChain infrastructure (tools,
runnables, callbacks, tracing, agent loops, graphs) without the cost or noise
of calling a real LLM. Math is the chosen domain: every operation has a
deterministic answer, so failures are easy to spot.

The challenge: in a normal agent, the LLM is the decision-maker. Take it away
and something has to play that role.

## Decision

Substitute the LLM with two deterministic components:

1. A **parser** (`parser.py`) that maps free-form math text to a tool name and
   arguments. This is the "brain" the LLM would normally provide.
2. A **rule-based chat model** (`chat_model.py`) that implements the
   `BaseChatModel` interface and emits fake `AIMessage` objects with tool
   calls, using the parser. From LangChain's point of view, this is a chat
   model that supports tool calling: it is invoked with a message list and
   returns an `AIMessage`.

Everything else (tools, AgentExecutor / `create_agent`, LangGraph state,
callbacks, tracing) is the real LangChain machinery, unchanged.

## Consequences

- We exercise the full LangChain agent loop end to end (HumanMessage ->
  tool_call -> ToolMessage -> final AIMessage) with no LLM token spend.
- LangSmith traces look real and have the same shape they would with an LLM,
  which is the main pedagogical payoff.
- The "intelligence" of the agent is the parser. Edge cases that an LLM would
  handle gracefully (typos, ambiguous phrasing, math word problems) fail here.
  This is by design: the parser is not the focus.
- When the owner adds a real LLM later, the only file that needs to change is
  `chat_model.py` -> swap `RuleBasedChatModel` for a real `ChatAnthropic` or
  `ChatOpenAI`. The agent, graph, tools, and tracing all stay the same.
