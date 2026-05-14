"""Agent path: langchain.agents.create_agent.

This is the modern, recommended way to build an agent in LangChain 1.x (2026).
`create_agent` is a one-liner that returns a compiled LangGraph state machine.
Under the hood it wires the same loop you would build by hand in `graph.py`,
but you do not see the nodes or edges. Use this in real projects.

Shape of the run:

    {"messages": [("user", "add 2 and 3")]}
      -> model node     (RuleBasedChatModel emits AIMessage with tool_calls)
      -> tools node     (LangGraph runs the tool, appends a ToolMessage)
      -> model node     (RuleBasedChatModel sees ToolMessage, emits final AIMessage)
      -> END
    {"messages": [HumanMessage, AIMessage(tool_call), ToolMessage, AIMessage(final)]}

Compare this to `chain.py` (no loop, no messages) and `graph.py` (the same loop
but visible as nodes and edges so you can see what create_agent abstracts away).

History note: LangChain 0.x used `AgentExecutor` + `create_tool_calling_agent`.
That API is gone in 1.x. If you read older tutorials and see those names, this
function is the replacement.
"""

from __future__ import annotations

from typing import Any

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from mathagent.chat_model import RuleBasedChatModel
from mathagent.tools import ALL_TOOLS


def build_agent() -> Any:
    """Build the agent-path runnable.

    The return value is a compiled state graph (a CompiledStateGraph from
    LangGraph). It accepts `{"messages": [("user", "...")]}` and returns the
    full message history, the same I/O shape as the graph path. We return
    `Any` because the precise generic type CompiledStateGraph[...] is verbose
    and would obscure the teaching value of this file.

    Memory: an `InMemorySaver` checkpointer is attached so every `.invoke()`
    call that shares a `configurable.thread_id` resumes the prior conversation.
    Callers without a thread_id get the original single-turn behavior, but
    LangGraph requires the key to exist; the REPL always passes one.
    """
    return create_agent(RuleBasedChatModel(), tools=ALL_TOOLS, checkpointer=InMemorySaver())
