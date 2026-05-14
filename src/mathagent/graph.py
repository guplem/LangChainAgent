"""Graph path: a hand-built LangGraph state machine.

This path exists purely for learning. `create_agent` in `agent.py` builds the
same loop in one line; here we build it explicitly so you can see the nodes,
the edges, the state schema, and the routing decision. Every concept that is
hidden by `create_agent` is visible here.

The state of the graph is a message list. Two nodes update it:

  - `model`: calls our RuleBasedChatModel on the current message list and
             appends whatever AIMessage it returns.
  - `tools`: a `ToolNode` from langgraph that looks at the most recent
             AIMessage, runs each tool_call, and appends one ToolMessage per call.

The routing is also explicit:

  - START -> model
  - model -> tools  if the last AIMessage has tool_calls
            -> END    otherwise
  - tools -> model  always (loop back so the model sees the tool result)

Compare the trace this produces in LangSmith to the trace from `agent.py`. They
should be very similar in shape, because `create_agent` builds essentially this
graph for you.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Annotated, Any, TypedDict

from langchain_core.messages import AIMessage, AnyMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from mathagent.chat_model import RuleBasedChatModel
from mathagent.tools import ALL_TOOLS


class GraphState(TypedDict):
    """The single piece of state the graph tracks.

    `add_messages` is a reducer: when a node returns `{"messages": [m]}`, the
    framework appends `m` to the existing list instead of replacing it.
    """

    messages: Annotated[Sequence[AnyMessage], add_messages]


def _call_model(state: GraphState) -> dict[str, list[AnyMessage]]:
    """Run the chat model on the current message list, append its reply."""
    llm = RuleBasedChatModel()
    reply = llm.invoke(state["messages"])
    return {"messages": [reply]}


def _should_continue(state: GraphState) -> str:
    """If the model wants to call a tool, route to `tools`. Else END."""
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return END


def build_graph() -> Any:
    """Build the graph-path runnable.

    Returns a compiled state graph. Invoke it with:
        graph.invoke({"messages": [("user", "add 2 and 3")]})

    We return `Any` because the precise generic type (CompiledStateGraph[...])
    is verbose and would obscure the teaching value of this file.
    """
    tool_node = ToolNode(ALL_TOOLS)

    builder = StateGraph(GraphState)
    builder.add_node("model", _call_model)
    builder.add_node("tools", tool_node)
    builder.add_edge(START, "model")
    builder.add_conditional_edges("model", _should_continue, {"tools": "tools", END: END})
    builder.add_edge("tools", "model")
    return builder.compile()
