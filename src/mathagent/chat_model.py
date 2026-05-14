"""Rule-based chat model.

This is the substitute for an LLM. LangChain's AgentExecutor and LangGraph's
create_react_agent both expect a chat model that supports tool calling. They
send a list of messages and expect back an `AIMessage` that either:

  - contains `tool_calls` (telling the executor to run a tool), or
  - has plain content (signalling the final answer).

`RuleBasedChatModel` fakes that contract:

  - When the last message is a HumanMessage, it parses the text with
    `parser.parse_math_request` and emits a fake AIMessage carrying a tool_call.
  - When the last message is a ToolMessage (the result of running a tool), it
    emits an AIMessage whose content is that result. This is the final answer
    and the agent loop terminates.

The result is that the entire agent loop (`HumanMessage -> tool_call -> ToolMessage
-> final answer`) runs end to end using real LangChain machinery, real
LangSmith spans, real callbacks. Only the "brain" is replaced by a parser.
"""

from __future__ import annotations

from typing import Any

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import Runnable

from mathagent.parser import parse_math_request


class RuleBasedChatModel(BaseChatModel):
    """A BaseChatModel that calls the parser instead of an LLM."""

    @property
    def _llm_type(self) -> str:
        return "rule-based-fake"

    def bind_tools(
        self,
        tools: Any,
        **kwargs: Any,
    ) -> Runnable[Any, Any]:
        """No-op tool binding.

        Real chat models use this to attach a tool schema to every request so
        the LLM knows what tools exist. Our parser knows every tool by name
        already, so we just return self. We ignore the BaseChatModel override
        check because matching its deeply-nested Runnable type signature would
        bury the teaching value of this file.
        """
        return self

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        last = messages[-1]

        if isinstance(last, ToolMessage):
            # Tool produced a result. Use it as the final answer and end the loop.
            answer = AIMessage(content=str(last.content))
            return ChatResult(generations=[ChatGeneration(message=answer)])

        # First turn: a human asked something. Parse and emit a tool call.
        text = last.content if isinstance(last.content, str) else str(last.content)
        tool_name, args = parse_math_request(text)
        ai = AIMessage(
            content="",
            tool_calls=[
                {
                    "name": tool_name,
                    "args": args,
                    "id": "call_1",
                    "type": "tool_call",
                }
            ],
        )
        return ChatResult(generations=[ChatGeneration(message=ai)])
