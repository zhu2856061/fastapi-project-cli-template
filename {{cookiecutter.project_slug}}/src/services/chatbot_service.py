# -*- coding: utf-8 -*-
# @Time   : {{ cookiecutter.timestamp }}
# @Author : {{ cookiecutter.author_name }} : {{ cookiecutter.email }}
# @Moto   : Knowledge lies in decomposition
from __future__ import annotations

import logging
from typing import cast

from fastapi import WebSocket, WebSocketDisconnect
from langchain_core.runnables.config import RunnableConfig

from src.api.v1.schemas.chatbot_schema import SuperAgentRequest, SuperAgentResponse
from src.core.chatbot.chat import get_chat_with_llm
from src.core.chatbot.constants import VALID_TOKENS
from src.core.chatbot.exceptions import ChatExceptionError
from src.utils.decorators import monitor_request_response, monitor_timer

logger = logging.getLogger(__name__)


@monitor_timer(
    trace_id_param="trace_id", timeout=120, timeout_return={"code": 504, "message": "请求超时"}
)
@monitor_request_response(trace_id_param="trace_id")
async def chatbot_service(request: SuperAgentRequest) -> SuperAgentResponse:
    """Generate embeddings for a list of texts."""
    try:
        if not request.state:
            return SuperAgentResponse(code=-1, message="Input state cannot be empty")

        # 获取 thread_id
        thread_id = request.context.get("thread_id")
        if not thread_id:
            logger.error("herror: thread_id is required", exc_info=True)
            return SuperAgentResponse(code=-1, message="thread_id is required")

        # 创建 config
        config = request.context.get("config", {"recursion_limit": 100})
        assert isinstance(config, dict)
        config.update({"configurable": {"thread_id": thread_id}})

        result = (
            await get_chat_with_llm()
            .get_compile_graph()
            .ainvoke(
                input=request.state,
                config=RunnableConfig(**config),
                context=request.context,
            )
        )

        result = cast(dict, result)

        return SuperAgentResponse(code=result.get("code", 0), data=result.get("data", {}))

    except ChatExceptionError as e:
        return SuperAgentResponse(code=e.code, message=e.message)


_active_connections: list[WebSocket] = []


async def chatbot_service_ws(websocket: WebSocket):
    """Generate embeddings for a list of texts."""

    token = websocket.query_params.get("token")
    if not token or token not in VALID_TOKENS:
        await websocket.close(code=1008)
        raise WebSocketDisconnect(code=1008)

    # 1. 接受客户端连接
    await websocket.accept()
    # 将连接加入活跃列表（可选）
    _active_connections.append(websocket)
    try:
        while True:
            _data = await websocket.receive_text()
            _request = SuperAgentRequest.model_validate_json(_data)
            _result = await chatbot_service(_request)
            await websocket.send_text(cast(SuperAgentResponse, _result).model_dump_json())

    except WebSocketDisconnect:
        logger.info("客户端主动断开连接")
    except Exception as e:
        logger.error(f"处理过程中发生异常: {e}")
    finally:
        # 确保无论因为什么原因退出，都清理资源
        if websocket in _active_connections:
            _active_connections.remove(websocket)
