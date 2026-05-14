"""Agent-path tests.

Verify the full tool-calling loop: HumanMessage -> tool_call -> ToolMessage ->
final AIMessage. `create_agent` returns a compiled state graph, so the I/O is
the same shape as the graph path: input `{"messages": [...]}`, output the full
message history.

With the checkpointer enabled, every `.invoke()` requires a
`configurable.thread_id`. Tests pass a fixed one per test so behavior is
deterministic.
"""

from __future__ import annotations

from mathagent.agent import build_agent

_CONFIG = {"configurable": {"thread_id": "test"}}


def test_agent_runs_full_tool_calling_loop() -> None:
    agent = build_agent()
    result = agent.invoke({"messages": [("user", "add 2 and 3")]}, config=_CONFIG)
    final = result["messages"][-1]
    assert "5" in str(final.content)


def test_agent_handles_division() -> None:
    agent = build_agent()
    result = agent.invoke({"messages": [("user", "10 divided by 4")]}, config=_CONFIG)
    final = result["messages"][-1]
    assert "2.5" in str(final.content)


def test_agent_persists_message_history_within_thread() -> None:
    # Same thread_id across calls. The checkpointer should reload prior state,
    # so r2's message list contains turn 1 plus turn 2 (not just turn 2 alone).
    agent = build_agent()
    config = {"configurable": {"thread_id": "persistence-test"}}

    r1 = agent.invoke({"messages": [("user", "add 3 and 5")]}, config=config)
    r2 = agent.invoke({"messages": [("user", "add 4 and 6")]}, config=config)

    assert len(r2["messages"]) > len(r1["messages"]), (
        "second turn should include first turn's history"
    )
