# -*- coding: utf-8 -*-
# @Time   : {{ cookiecutter.timestamp }}
# @Author : {{ cookiecutter.author_name }} : {{ cookiecutter.email }}
# @Moto   : Knowledge comes from decomposition
from __future__ import annotations

"""

## 对外路由，不可存在任何的处理逻辑（处理逻辑请由service负责），纯粹路由管理

import logging

from fastapi import APIRouter, WebSocket

from src.chat_bot.services.chat_bot_service import chat_bot_service, chat_bot_service_ws

from .schema import SuperAgentRequest, SuperAgentResponse

logger = logging.getLogger(__name__)


# Define the router
chat_with_llm_router = APIRouter(tags=["VECTOR SERVER"])


@chat_with_llm_router.post("/v1", response_model=SuperAgentResponse)
async def chat_with_llm(request: SuperAgentRequest):
    return await chat_bot_service(request)


@chat_with_llm_router.websocket("/ws")
async def chat_with_llm_ws(websocket: WebSocket):
    return await chat_bot_service_ws(websocket)
"""
