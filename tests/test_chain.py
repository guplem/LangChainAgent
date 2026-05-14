"""Chain-path tests."""

from __future__ import annotations

from mathagent.chain import build_chain


def test_chain_returns_float_result() -> None:
    chain = build_chain()
    assert chain.invoke("add 2 and 3") == 5.0


def test_chain_handles_multiplication() -> None:
    chain = build_chain()
    assert chain.invoke("4 times 5") == 20.0
