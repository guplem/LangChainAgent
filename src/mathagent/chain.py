"""Chain path: deterministic Runnable composition.

A "chain" in LangChain is a Runnable that does a fixed sequence of steps. There
is no LLM in the loop and no decision-making at run time besides what the code
explicitly says.

Shape of this chain:

    input: str
      -> parse_math_request   (picks tool name and args)
      -> route_to_tool        (looks up the @tool and calls .invoke(args))
      -> output: float

Compare this to `agent.py` and `graph.py` which wrap the same call in an agent
loop. The chain path is the simplest and cheapest, but it has no scratchpad,
no multi-step reasoning, and no "thinking" step the LLM would normally do.
"""

from __future__ import annotations

from langchain_core.runnables import Runnable, RunnableLambda

from mathagent.parser import parse_math_request
from mathagent.tools import TOOLS_BY_NAME


def _route(text: str) -> float:
    """Parse the input, look up the tool, invoke it."""
    tool_name, args = parse_math_request(text)
    tool = TOOLS_BY_NAME[tool_name]
    # tool.invoke is the standard Runnable interface for any @tool. It returns
    # the raw function return value (float here) when no LangChain wrapping is needed.
    result = tool.invoke(args)
    return float(result)


def build_chain() -> Runnable[str, float]:
    """Build the chain-path runnable.

    Wrapping `_route` in RunnableLambda is what turns a plain function into a
    LangChain Runnable, so it gets `.invoke`, `.batch`, `.stream`, callbacks,
    and tracing for free.
    """
    return RunnableLambda(_route, name="MathChain")
