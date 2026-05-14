"""Math tools.

A LangChain `tool` is a function the agent can call. The `@tool` decorator wraps
a plain Python function and exposes it through LangChain's tool-calling protocol:

  - the function's name becomes the tool's name
  - the docstring becomes the description (this is what a real LLM would read
    to decide which tool to call)
  - the type hints become the argument schema (Pydantic generates it)

All three routing paths in this project (chain / agent / graph) call the same
tool objects defined here, which is the whole point of the `@tool` abstraction:
the tools do not know who called them.
"""

from langchain_core.tools import tool


@tool
def add(a: float, b: float) -> float:
    """Add two numbers. Returns a + b."""
    return a + b


@tool
def subtract(a: float, b: float) -> float:
    """Subtract b from a. Returns a - b."""
    return a - b


@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers. Returns a * b."""
    return a * b


@tool
def divide(a: float, b: float) -> float:
    """Divide a by b. Returns a / b. Raises ValueError when b is zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


# Single source of truth used by every router. Order is irrelevant; lookup is by name.
ALL_TOOLS = [add, subtract, multiply, divide]
TOOLS_BY_NAME = {t.name: t for t in ALL_TOOLS}
