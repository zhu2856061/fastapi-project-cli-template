# -*- coding: utf-8 -*-
# @Time   : {{ cookiecutter.timestamp }}
# @Author : {{ cookiecutter.author_name }} : {{ cookiecutter.email }}
# @Moto   : Knowledge comes from decomposition
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.v1.routers.chatbot_router import chat_router
from src.config.app_config import init_app_config
from src.config.logging_config import init_app_logging
from src.exceptions.app_exception import AppException

# --- Logging Configuration ---
init_app_logging(json_logs=os.getenv("WORK_ENV", "dev") == "prod")

logger = logging.getLogger(__name__)


# --- Config Configuration ---
init_app_config(
    config_path=os.getenv("CONFIG_PATH", "config.yaml"),
    env_path_override=os.getenv("ENV_PATH", ".env"),
)

# --- Self Initialization ---


# --- load resources and cleanup resources ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """定义 FastAPI 生命周期事件"""
    # 启动时加载分词器和模型
    logger.info("加载资源")
    yield
    # 关闭时清理资源
    logger.info("清理资源")


# --- FastAPI App ---
app = FastAPI(
    title="Service",
    description="一个通用的模型服务",
    version="1.0.0",
    lifespan=lifespan,
)

# --- Add CORS middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# --- Health Check ---
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# --- Include The Router ---
app.include_router(chat_router)


# ==============================================
# 【1】捕获：请求参数校验错误 422
# ==============================================
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # 这里返回你统一的格式
    return JSONResponse(
        status_code=422,  # 你也可以改成 -1
        content={"code": 422, "message": f"请求参数错误:{exc!r}"},
    )


# ==============================================
# 【2】捕获：FastAPI 内部抛出的 HTTP 异常（400/401/403/404/500）
# ==============================================
# 使用 StarletteHTTPException，因为它能捕获更底层的异常
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={
                "code": 404,
                "message": f"路由没找到，当前请求路径: {request.url.path}",
                "detail": str(exc.detail),
            },
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": f"{exc!r}"},
    )


# ==============================================
# 【3】捕获：捕获：你自己的业务异常 AppException
# ==============================================
@app.exception_handler(AppException)
async def handler_app_exception(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.code,
        content={"code": exc.code, "message": f"{exc!r}"},
    )


# ==============================================
# 【4】兜底：捕获所有 未知/系统/代码BUG 异常（终极兜底）
# ==============================================
@app.exception_handler(Exception)
async def handler_global_exception(request: Request, exc: Exception):
    return JSONResponse(
        status_code=-1,
        content={"code": -1, "message": f"{exc!r}"},
    )


"""
gunicorn -k uvicorn.workers.UvicornWorker main:app -w 4 -b 0.0.0.0:2022
"""
