"""mathagent: a LangChain reference agent for math operations without an LLM.

The package exposes three "router" implementations that share the same tools:

  - build_chain  : RunnableLambda composition (deterministic; "chain" pattern).
  - build_agent  : AgentExecutor + custom rule-based chat model ("agent" pattern, legacy).
  - build_graph  : LangGraph create_react_agent ("graph" pattern, modern).

All three produce LangSmith traces so you can compare their shapes.
"""

from mathagent.agent import build_agent
from mathagent.chain import build_chain
from mathagent.graph import build_graph

__all__ = ["build_agent", "build_chain", "build_graph"]
