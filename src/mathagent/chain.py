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

Single-turn only. A chain is a pure function with no message list and no
state primitive, so follow-ups like "add 2" after a previous "add 3 and 5"
do not work here -- the parser would reject the lone "2" because the chain
has no way to know about the prior answer. If you need conversation memory,
use the agent or graph path (both compile to a LangGraph state machine
with an InMemorySaver checkpointer keyed by thread_id; see ADR 0007).
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
