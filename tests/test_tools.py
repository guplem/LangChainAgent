"""Tool unit tests. Each `@tool` is also a Runnable, so we test it via `.invoke`."""

from __future__ import annotations

import pytest

from mathagent.tools import ALL_TOOLS, TOOLS_BY_NAME, add, divide, multiply, subtract


def test_all_tools_are_registered_by_name() -> None:
    assert set(TOOLS_BY_NAME) == {"add", "subtract", "multiply", "divide"}
    assert len(ALL_TOOLS) == 4


def test_add() -> None:
    assert add.invoke({"a": 2, "b": 3}) == 5


def test_subtract() -> None:
    assert subtract.invoke({"a": 7, "b": 4}) == 3


def test_multiply() -> None:
    assert multiply.invoke({"a": 6, "b": 9}) == 54


def test_divide() -> None:
    assert divide.invoke({"a": 10, "b": 4}) == 2.5


def test_divide_by_zero_raises() -> None:
    with pytest.raises(ValueError, match="zero"):
        divide.invoke({"a": 1, "b": 0})
