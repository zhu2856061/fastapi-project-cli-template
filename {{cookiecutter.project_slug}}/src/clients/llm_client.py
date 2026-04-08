# -*- coding: utf-8 -*-
# @Time   : {{ cookiecutter.timestamp }}
# @Author : {{ cookiecutter.author_name }} : {{ cookiecutter.email }}
# @Moto   : Knowledge lies in decomposition
from __future__ import annotations

import logging
import time
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage
from langchain_litellm import ChatLiteLLM, ChatLiteLLMRouter
from litellm import BadRequestError, ContextWindowExceededError, Router  # type: ignore
from pydantic import BaseModel

from src.config.app_config import LLMConfig, get_app_config
from src.core.chatbot.exceptions import (
    LLMBadRequestError,
    LLMContextExceededError,
    LLMExceptionError,
)

logger = logging.getLogger(__name__)

_singleton_llm_provider: LLMSProvider | None = None


# 直接获取配置
def get_llm_provider() -> LLMSProvider:
    global _singleton_llm_provider
    if _singleton_llm_provider is None:
        logger.warning("初始化 llm_provider 配置")
        _singleton_llm_provider = LLMSProvider(get_app_config().LLM)
        return _singleton_llm_provider

    return _singleton_llm_provider


class LLMSProvider:
    """
    LLM 模型提供者，提供两个方法：

    1. get_llm_by_type(llm_type: str) -> BaseChatModel

    2. llm_wrap_hooks(
        thread_id: str,
        node_name: str,
        messages: list,
        model_name: str,
        *,
        tools: list | None = None,
        structured_output: Any = None,
        **invoke_kwargs,
    ) -> LLM 调用包装器
    """

    def __init__(self, llm_config: LLMConfig):
        self.llm_config = llm_config
        # 配置来源：格式参考 litellm.Router 要求
        self.llm_instance_cache: dict[str, ChatLiteLLM] = {}
        self._init_llm_instance_cache()

    def _init_llm_instance_cache(self):
        # 初始化 LiteLLM 路由实例：支持多模型路由、故障转移、负载均衡
        _model_list = [_.model_dump() for _ in self.llm_config.model_list]
        _litellm_router = Router(model_list=_model_list)
        for _instance in self.llm_config.model_list:
            _name = _instance.model_name
            _is_cache = _instance.litellm_params.cache
            llm = ChatLiteLLMRouter(router=_litellm_router, model_name=_name)

            self.llm_instance_cache[_name] = llm

    def get_llm_by_type(self, llm_type: str) -> ChatLiteLLM:
        if llm_type in self.llm_instance_cache:
            return self.llm_instance_cache[llm_type]
        raise ValueError(f"未找到 LLM 实例（类型：{llm_type}）")

    # 重装
    async def llm_wrap_hooks(
        self,
        thread_id: str,
        node_name: str,
        messages: list,
        model_name: str,
        *,
        tools: list | None = None,
        structured_output: Any = None,
        **invoke_kwargs,
    ) -> AIMessage:
        """LLM 调用包装器（实现 LLM 前 + LLM 后 日志跟踪）
        thread_id: 线程 ID
        node_name: 节点名称
        messages: 输入消息
        model_name: 模型名称
        tools: 工具列表
        structured_output: 结构化输出定义
        invoke_kwargs: 调用参数
        """
        await self.before_llm(thread_id, node_name, messages)

        try:
            start = time.perf_counter()
            if tools:
                model = self.get_llm_by_type(model_name).bind_tools(tools)
            elif structured_output:
                model = self.get_llm_by_type(model_name).with_structured_output(structured_output)
            else:
                model = self.get_llm_by_type(model_name)

            response: AIMessage = await model.ainvoke(messages, **invoke_kwargs)  # type: ignore

            elapsed = time.perf_counter() - start
            await self.after_llm(thread_id, node_name, response, elapsed)

            # 可选：在这里记录总耗时、token 等
            return response

        except ContextWindowExceededError as e:
            await self.on_error(thread_id, node_name, e)
            raise LLMContextExceededError(e.message) from None

        except BadRequestError as e:
            await self.on_error(thread_id, node_name, e)
            raise LLMBadRequestError(e.message) from None

        except Exception as e:
            await self.on_error(thread_id, node_name, e)
            raise LLMExceptionError(str(e)) from None

    @staticmethod
    async def before_llm(thread_id: str, node_name: str, messages: list[BaseMessage]):
        msg_count = len(messages)
        last_content = f"{messages[-1].content[:80]}..." if messages else ""
        message = f"[LLM Call] -> messages: {msg_count} | last: {last_content}"

        logger.info(f"[thread_id={thread_id}] | [node={node_name}], message={message}")
        # 可扩展：prompt 注入、敏感词过滤、修改 messages、动态调整 temperature 等

    @staticmethod
    async def after_llm(thread_id: str, node_name: str, response: Any, elapsed: float):
        tool_calls = 0

        if isinstance(response, AIMessage):
            _result = response.content
            tool_calls = len(response.tool_calls) if hasattr(response, "tool_calls") else 0

        elif isinstance(response, BaseModel):
            _result = response.model_dump()
        else:
            _result = response
        _result = str(_result)

        content_preview = f"{_result[:80]}..." if _result else ""

        usage = getattr(response, "usage_metadata", None)
        tokens_str = (
            f" in:{usage.get('input_tokens', '?')} out:{usage.get('output_tokens', '?')}"
            if usage
            else ""
        )
        message = f"[LLM Returned: {elapsed:.3f}s] <- tools:{tool_calls} | tokens:{tokens_str} | response:{content_preview}"

        logger.info(f"[thread_id={thread_id}] | [node={node_name}], message={message}")
        # 可扩展：输出校验、PII 脱敏、自动总结等

    @staticmethod
    async def on_error(thread_id: str, node_name: str, exc: Exception):
        logger.info(f"[thread_id={thread_id}] | [node={node_name}], exc={exc!r}")
        # 可扩展：统一错误上报、转成 AIMessage 错误回复
