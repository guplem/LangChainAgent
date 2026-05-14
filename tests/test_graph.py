"""Graph-path tests.

With the checkpointer enabled, every `.invoke()` requires a
`configurable.thread_id`. Tests pass a fixed one per test so behavior is
deterministic.
"""

from __future__ import annotations

from mathagent.graph import build_graph

_CONFIG = {"configurable": {"thread_id": "test"}}


def test_graph_returns_final_message_with_result() -> None:
    graph = build_graph()
    result = graph.invoke({"messages": [("user", "add 2 and 3")]}, config=_CONFIG)
    messages = result["messages"]
    # The final message is the AIMessage with the final answer.
    final = messages[-1]
    assert "5" in str(final.content)


def test_graph_handles_subtraction() -> None:
    graph = build_graph()
    result = graph.invoke(
        {"messages": [("user", "what is 7 minus 4?")]}, config=_CONFIG
    )
    final = result["messages"][-1]
    assert "3" in str(final.content)


def test_graph_persists_message_history_within_thread() -> None:
    graph = build_graph()
    config = {"configurable": {"thread_id": "persistence-test"}}

    r1 = graph.invoke({"messages": [("user", "add 3 and 5")]}, config=config)
    r2 = graph.invoke({"messages": [("user", "add 4 and 6")]}, config=config)

    assert len(r2["messages"]) > len(r1["messages"]), (
        "second turn should include first turn's history"
    )


def test_graph_multi_turn_follow_up_uses_prior_answer() -> None:
    graph = build_graph()
    config = {"configurable": {"thread_id": "followup-test"}}

    r1 = graph.invoke({"messages": [("user", "add 3 and 5")]}, config=config)
    assert "8" in str(r1["messages"][-1].content)

    r2 = graph.invoke({"messages": [("user", "add 2")]}, config=config)
    assert "10" in str(r2["messages"][-1].content)
