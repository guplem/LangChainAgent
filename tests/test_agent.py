"""Agent-path tests.

Verify the full tool-calling loop: HumanMessage -> tool_call -> ToolMessage ->
final AIMessage. `create_agent` returns a compiled state graph, so the I/O is
the same shape as the graph path: input `{"messages": [...]}`, output the full
message history.
"""

from __future__ import annotations

from mathagent.agent import build_agent


def test_agent_runs_full_tool_calling_loop() -> None:
    agent = build_agent()
    result = agent.invoke({"messages": [("user", "add 2 and 3")]})
    final = result["messages"][-1]
    assert "5" in str(final.content)


def test_agent_handles_division() -> None:
    agent = build_agent()
    result = agent.invoke({"messages": [("user", "10 divided by 4")]})
    final = result["messages"][-1]
    assert "2.5" in str(final.content)
