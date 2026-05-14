"""Interactive REPL.

Asks for a routing mode (chain / agent / graph), builds the matching runnable,
and loops on user input. Each call is invoked with the configured tracing
callbacks so every question produces a trace.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from langchain_core.runnables import Runnable

from mathagent.agent import build_agent
from mathagent.chain import build_chain
from mathagent.graph import build_graph
from mathagent.tracing import get_callbacks

_MODES: dict[str, Callable[[], Runnable[Any, Any]]] = {
    "chain": build_chain,
    "agent": build_agent,
    "graph": build_graph,
}


def _ask_mode() -> str:
    print("MathAgent REPL")
    print("Three modes, three LangChain shapes that share the same tools:")
    print("  chain  -> RunnableLambda composition. Deterministic, no loop.")
    print("  agent  -> AgentExecutor + tool-calling chat model. Legacy agent loop.")
    print("  graph  -> LangGraph create_react_agent. Modern agent path.")
    print()
    while True:
        choice = input("mode> ").strip().lower()
        if choice in _MODES:
            return choice
        print(f"Unknown mode {choice!r}. Choose: {', '.join(_MODES)}.")


def _prepare_input(mode: str, text: str) -> Any:
    """Each path expects a different input shape. Convert here."""
    if mode == "chain":
        return text
    # Both agent (create_agent) and graph (hand-built) take the same shape:
    # a messages list, since both compile to a LangGraph state machine.
    return {"messages": [("user", text)]}


def _format_output(mode: str, result: Any) -> str:
    if mode == "chain":
        return str(result)
    # Agent and graph both return a state dict with the full message history.
    last_message = result["messages"][-1]
    return str(getattr(last_message, "content", last_message))


def run() -> None:
    mode = _ask_mode()
    runnable = _MODES[mode]()
    callbacks = list(get_callbacks())
    print(f"\nReady ({mode} mode). Ask a math question. Type 'quit' to exit.\n")
    while True:
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not text:
            continue
        if text.lower() in {"quit", "exit"}:
            return
        try:
            payload = _prepare_input(mode, text)
            result = runnable.invoke(payload, config={"callbacks": callbacks})
            print(_format_output(mode, result))
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")
