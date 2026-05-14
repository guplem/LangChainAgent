"""Chain path: an LCEL pipeline composed with `|`.

LCEL is the **LangChain Expression Language**: a way to compose Runnables
with the `|` operator, borrowed from Unix pipes. `a | b` produces a new
Runnable (a `RunnableSequence`) that first invokes `a`, then feeds its
output into `b`. This is the canonical "chain" pattern in LangChain 1.x;
every real tutorial uses it (`prompt | model | parser` is the classic
shape).

Shape of this chain:

    input: str
      -> parse     (RunnableLambda wrapping parse_math_request)
                   str -> (tool_name, args)
      -> dispatch  (RunnableLambda wrapping _dispatch)
                   (tool_name, args) -> float
      -> output: float

Each step is its own named Runnable, so each one produces a span in the
LangSmith trace. Compare this to `agent.py` and `graph.py` which wrap the
same call in an agent loop with multiple message turns. The chain path is
the simplest and cheapest, but it has no scratchpad, no multi-step
reasoning, and no "thinking" step the LLM would normally do.

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


def _dispatch(parsed: tuple[str, dict[str, float]]) -> float:
    """Run the tool named by the parser with the parsed arguments."""
    tool_name, args = parsed
    return float(TOOLS_BY_NAME[tool_name].invoke(args))


def build_chain() -> Runnable[str, float]:
    """Build the chain-path runnable as an LCEL pipeline.

    Returns `parse | dispatch`, a `RunnableSequence` of two named
    `RunnableLambda` steps. Each step appears as its own span in the
    LangSmith trace.
    """
    parse = RunnableLambda(parse_math_request, name="parse")
    dispatch = RunnableLambda(_dispatch, name="dispatch")
    return parse | dispatch
