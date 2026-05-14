"""Chain-path tests."""

from __future__ import annotations

from langchain_core.runnables import RunnableSequence
from langchain_core.runnables.base import RunnableBinding

from mathagent.chain import build_chain


def test_chain_returns_float_result() -> None:
    chain = build_chain()
    assert chain.invoke("add 2 and 3") == 5.0


def test_chain_handles_multiplication() -> None:
    chain = build_chain()
    assert chain.invoke("4 times 5") == 20.0


def test_chain_is_an_lcel_runnable_sequence_with_two_steps() -> None:
    # The chain path must stay an LCEL composition (parse | dispatch), not a
    # single RunnableLambda wrapping a multi-step function. The LangChain term
    # "chain" specifically means a RunnableSequence; this test pins the
    # structure so a future refactor cannot silently collapse the two steps
    # back into one.
    #
    # `with_config(run_name="MathChain")` returns a RunnableBinding wrapping
    # the RunnableSequence, so we unwrap one level before checking.
    chain = build_chain()
    assert isinstance(chain, RunnableBinding)
    assert isinstance(chain.bound, RunnableSequence)
    assert len(chain.bound.steps) == 2


def test_chain_carries_a_friendly_run_name_for_traces() -> None:
    # LangSmith / LangFuse read run_name from the Runnable's config to label
    # the trace. Without this, the chain would appear in traces as a generic
    # "RunnableSequence" and be hard to find next to agent and graph runs.
    chain = build_chain()
    # build_chain's declared return type is Runnable[str, float], which does
    # not statically expose `.config`. The runtime is a RunnableBinding that
    # does; getattr keeps mypy strict mode happy.
    config = getattr(chain, "config", {})
    assert config.get("run_name") == "MathChain"
