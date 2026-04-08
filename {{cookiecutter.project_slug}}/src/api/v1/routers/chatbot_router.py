# -*- coding: utf-8 -*-
# @Time   : {{ cookiecutter.timestamp }}
# @Author : {{ cookiecutter.author_name }} : {{ cookiecutter.email }}
# @Moto   : Knowledge comes from decomposition
from __future__ import annotations

import logging

from fastapi import APIRouter, WebSocket

from src.api.v1.schemas.chatbot_schema import SuperAgentRequest, SuperAgentResponse
from src.services.chatbot_service import chatbot_service, chatbot_service_ws

logger = logging.getLogger(__name__)


# Define the router
chat_router = APIRouter(prefix="/chat", tags=["CHATBOT SERVER"])


@chat_router.post("/v1", response_model=SuperAgentResponse)
async def chat_with_llm(request: SuperAgentRequest):
    return await chatbot_service(request)


@chat_router.websocket("/ws")
async def chat_with_llm_ws(websocket: WebSocket):
    return await chatbot_service_ws(websocket)
