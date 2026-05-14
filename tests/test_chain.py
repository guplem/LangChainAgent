"""Chain-path tests."""

from __future__ import annotations

from langchain_core.runnables import RunnableSequence

from mathagent.chain import build_chain


def test_chain_returns_float_result() -> None:
    chain = build_chain()
    assert chain.invoke("add 2 and 3") == 5.0


def test_chain_handles_multiplication() -> None:
    chain = build_chain()
    assert chain.invoke("4 times 5") == 20.0


def test_chain_is_an_lcel_runnable_sequence() -> None:
    # The chain path must stay an LCEL composition (parse | dispatch), not a
    # single RunnableLambda wrapping a multi-step function. The LangChain term
    # "chain" specifically means a RunnableSequence; this test pins that so a
    # future refactor cannot silently collapse the two steps back into one.
    chain = build_chain()
    assert isinstance(chain, RunnableSequence)
