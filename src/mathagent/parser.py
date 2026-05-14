"""Free-form input parser.

This is the part of the system that, in a real agent, would be done by an LLM.
Because this project removes the LLM, the parser plays that role: it reads a
human sentence and decides which tool to call and with which arguments.

All three routing paths use this parser:

  - chain path : the chain calls `parse_math_request` directly to dispatch the tool.
  - agent path : the rule-based chat model in `chat_model.py` calls the parser
                 and wraps the result in a fake AIMessage with tool_calls.
  - graph path : same as the agent path, since LangGraph's `create_react_agent`
                 uses the same chat-model interface.

The parser is intentionally small. It is not the focus of the project; it exists
so the three router shapes can be compared on equal footing.
"""

from __future__ import annotations

import re

# Keyword -> tool name. The first keyword found in the input wins. Order matters
# only when keywords overlap (none do today).
_OPERATION_KEYWORDS: dict[str, str] = {
    # add
    "add": "add",
    "plus": "add",
    "sum": "add",
    "+": "add",
    # subtract
    "subtract": "subtract",
    "minus": "subtract",
    "-": "subtract",
    # multiply
    "multiply": "multiply",
    "times": "multiply",
    "*": "multiply",
    "x": "multiply",
    # divide
    "divide": "divide",
    "divided": "divide",
    "over": "divide",
    "/": "divide",
}

# Captures integers and decimals, with optional sign. Used to pull the two operands.
_NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")


class ParseError(ValueError):
    """Raised when the parser cannot extract a tool name and two operands."""


def parse_math_request(text: str) -> tuple[str, dict[str, float]]:
    """Parse a free-form math question.

    Returns (tool_name, args) where args is the dict passed to the tool's
    `.invoke()` call. The tool name is one of: add, subtract, multiply, divide.

    Examples:
        >>> parse_math_request("add 2 and 3")
        ('add', {'a': 2.0, 'b': 3.0})
        >>> parse_math_request("what is 7 minus 4?")
        ('subtract', {'a': 7.0, 'b': 4.0})
        >>> parse_math_request("6 * 9")
        ('multiply', {'a': 6.0, 'b': 9.0})

    Raises ParseError if no operation keyword is found or if fewer than two
    numbers are present.
    """
    lowered = text.lower()
    tool_name: str | None = None
    for keyword, name in _OPERATION_KEYWORDS.items():
        if keyword in lowered:
            tool_name = name
            break
    if tool_name is None:
        raise ParseError(
            f"Could not detect a math operation in {text!r}. "
            f"Known keywords: {sorted(_OPERATION_KEYWORDS)}."
        )

    numbers = [float(m) for m in _NUMBER_RE.findall(text)]
    if len(numbers) < 2:
        raise ParseError(f"Need two numbers in {text!r}, found {len(numbers)}.")

    return tool_name, {"a": numbers[0], "b": numbers[1]}
