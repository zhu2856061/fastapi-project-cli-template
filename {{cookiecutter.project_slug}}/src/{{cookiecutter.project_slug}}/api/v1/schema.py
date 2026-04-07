# -*- coding: utf-8 -*-
# @Time   : {{ cookiecutter.timestamp }}
# @Author : {{ cookiecutter.author_name }} : {{ cookiecutter.email }}
# @Moto   : Knowledge comes from decomposition
from __future__ import annotations

"""

## 该部分为统一的schema 管理

from typing import Annotated, NotRequired

from langgraph.graph.message import (
    AnyMessage,
    add_messages,
)
from pydantic import BaseModel, Field

# from langgraph.types import Overwrite 很重要
from typing_extensions import TypedDict


class SuperState(TypedDict):

    code: NotRequired[int | None]  # 判断状态 0 正常 1 异常
    err_message: NotRequired[str | None]  # 错误信息

    # messages: Annotated[list[AnyMessage], add_messages]  # 核心交互信息
    messages: NotRequired[Annotated[list[AnyMessage], add_messages]]  # 核心交互信息

    user_guidance: NotRequired[dict | None]  # 用户反馈信息
    data: NotRequired[dict | None]  # 核心结果信息存储
    human_in_loop_node: NotRequired[str | None]  # 人类反馈的节点
    todos: NotRequired[list | None]  # 任务列表todo-list
    sandbox_id: NotRequired[str | None]  # 沙盒id, local: 本地


class SuperContext(TypedDict):

    thread_id: str
    agent: str
    is_human_in_loop: NotRequired[bool]
    task_dir: NotRequired[str | None]
    model: NotRequired[str | None]
    models: NotRequired[dict | None]
    config: NotRequired[dict | None]


# Pydantic models
class SuperAgentRequest(BaseModel):
    trace_id: str = Field("default", description="the trace_id")
    context: SuperContext = Field(..., description="the context runtime dict")
    state: SuperState = Field(..., description="the input messages of the task")
    stream: bool = Field(True, description="whether to stream the response")


class SuperAgentResponse(BaseModel):
    code: int = Field(default=0, description="code ID")
    message: str = Field(default="ok", description="error message")
    data: dict = Field(default={}, description="data")

"""
