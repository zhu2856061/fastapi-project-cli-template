# -*- coding: utf-8 -*-
# @Time   : {{ cookiecutter.timestamp }}
# @Author : {{ cookiecutter.author_name }} : {{ cookiecutter.email }}
# @Moto   : Knowledge comes from decomposition
from __future__ import annotations

import logging
from typing import cast

from fastapi import WebSocket, WebSocketDisconnect
from langchain_core.runnables.config import RunnableConfig

from src.chat_bot.api.v1.schema import SuperAgentRequest, SuperAgentResponse
from src.chat_bot.core.chat import get_chat_with_llm
from src.chat_bot.core.constants import VALID_TOKENS
from src.chat_bot.core.exceptions import ChatExceptionError
from src.chat_bot.utils.decorators import monitor_request_response, monitor_timer

logger = logging.getLogger(__name__)


@monitor_timer(
    trace_id_param="trace_id", timeout=120, timeout_return={"code": 504, "message": "请求超时"}
)
@monitor_request_response(trace_id_param="trace_id")
async def chat_bot_service(request: SuperAgentRequest) -> SuperAgentResponse:
    """Generate embeddings for a list of texts."""
    pass


_active_connections: list[WebSocket] = []


async def chat_bot_service_ws(websocket: WebSocket):
    """Generate embeddings for a list of texts."""

    pass
