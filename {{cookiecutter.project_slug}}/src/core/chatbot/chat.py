# -*- coding: utf-8 -*-
# @Time   : {{ cookiecutter.timestamp }}
# @Author : {{ cookiecutter.author_name }} : {{ cookiecutter.email }}
# @Moto   : Knowledge lies in decomposition
from __future__ import annotations

import logging

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, StateGraph
from langgraph.runtime import Runtime
from langgraph.types import Command

from src.api.v1.schemas.chatbot_schema import SuperContext, SuperState
from src.clients.llm_client import get_llm_provider
from src.middleware.super_agent_hooks import get_super_agent_hook

logger = logging.getLogger(__name__)

_singleton_chat: ChatWithLLM | None = None


def get_chat_with_llm() -> ChatWithLLM:
    global _singleton_chat
    if _singleton_chat is None:
        _singleton_chat = ChatWithLLM()
    return _singleton_chat


class ChatWithLLM:
    def __init__(self):
        self.compile_graph = None

    def get_compile_graph(self):
        if self.compile_graph:
            return self.compile_graph
        else:
            return self._compile_graph()

    def _creat_node(self, node_name="chat"):
        _hook = get_super_agent_hook()

        @_hook.node_with_hooks(node_name=node_name)
        async def _node(state: SuperState, runtime: Runtime[SuperContext]):
            # 获取运行时变量
            _thread_id = runtime.context.get("thread_id", "default")
            _model_name = runtime.context.get("model", "basic")
            _config = runtime.context.get("config", {})

            # 创建工作目录
            # _task_dir = runtime.context.get("task_dir", CONF.SYSTEM.task_dir)
            # _work_dir = os.path.join(cast(str, _task_dir), _thread_id)
            # os.makedirs(_work_dir, exist_ok=True)

            # 获取状态变量
            _code = state.get("code", 0)
            if _code != 0:
                return Command(goto="__end__")

            _messages = state.get("messages")
            if not _messages:
                return Command(
                    goto="__end__",
                    update={"code": -1, "messages": [AIMessage(content="No messages")]},
                )

            # 模型执行中
            response = await get_llm_provider().llm_wrap_hooks(
                _thread_id,
                node_name,
                _messages,
                _model_name,
                **_config,  # type: ignore
            )
            # 模型执行后
            # 去掉冗余信息
            response.additional_kwargs = {}
            response.response_metadata = {}

            return Command(
                update={"messages": [response], "data": {"result": response.content}},
            )

        return _node

    def _compile_graph(self):
        _chat_node = self._creat_node("chat")
        # chat graph
        _agent = StateGraph(SuperState, context_schema=SuperContext)
        _agent.add_node("chat", _chat_node)
        _agent.add_edge(START, "chat")

        checkpointer = InMemorySaver()
        self.compile_graph = _agent.compile(checkpointer=checkpointer)
        return self.compile_graph
