"""Graph-path tests."""

from __future__ import annotations

from mathagent.graph import build_graph


def test_graph_returns_final_message_with_result() -> None:
    graph = build_graph()
    result = graph.invoke({"messages": [("user", "add 2 and 3")]})
    messages = result["messages"]
    # The final message is the AIMessage with the final answer.
    final = messages[-1]
    assert "5" in str(final.content)


def test_graph_handles_subtraction() -> None:
    graph = build_graph()
    result = graph.invoke({"messages": [("user", "what is 7 minus 4?")]})
    final = result["messages"][-1]
    assert "3" in str(final.content)
