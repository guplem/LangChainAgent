"""Parser tests."""

from __future__ import annotations

import pytest

from mathagent.parser import ParseError, parse_math_request


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("add 2 and 3", ("add", {"a": 2.0, "b": 3.0})),
        ("what is 7 minus 4?", ("subtract", {"a": 7.0, "b": 4.0})),
        ("6 * 9", ("multiply", {"a": 6.0, "b": 9.0})),
        ("12 divided by 4", ("divide", {"a": 12.0, "b": 4.0})),
        ("sum of 1.5 and 2.5", ("add", {"a": 1.5, "b": 2.5})),
        ("100 - 25", ("subtract", {"a": 100.0, "b": 25.0})),
    ],
)
def test_parses_known_phrasings(text: str, expected: tuple[str, dict[str, float]]) -> None:
    assert parse_math_request(text) == expected


def test_raises_when_no_operation_keyword() -> None:
    with pytest.raises(ParseError, match="math operation"):
        parse_math_request("hello world 1 2")


def test_raises_when_fewer_than_two_numbers() -> None:
    with pytest.raises(ParseError, match="two numbers"):
        parse_math_request("add 5")


@pytest.mark.parametrize(
    ("text", "prior", "expected"),
    [
        ("add 2", 8.0, ("add", {"a": 8.0, "b": 2.0})),
        ("subtract 3", 10.0, ("subtract", {"a": 10.0, "b": 3.0})),
        ("times 4", 6.0, ("multiply", {"a": 6.0, "b": 4.0})),
        ("divided by 2", 20.0, ("divide", {"a": 20.0, "b": 2.0})),
    ],
)
def test_one_number_input_uses_prior_answer(
    text: str, prior: float, expected: tuple[str, dict[str, float]]
) -> None:
    assert parse_math_request(text, prior_answer=prior) == expected


def test_one_number_without_prior_still_raises() -> None:
    with pytest.raises(ParseError, match="prior answer"):
        parse_math_request("add 5", prior_answer=None)
