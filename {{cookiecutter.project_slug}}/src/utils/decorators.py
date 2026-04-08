# -*- coding: utf-8 -*-
# @Time   : {{ cookiecutter.timestamp }}
# @Author : {{ cookiecutter.author_name }} : {{ cookiecutter.email }}
# @Moto   : Knowledge lies in decomposition
from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import Any

from .common import truncate_if_too_long

"""
装饰器：方便零侵入实现包装
"""


logger = logging.getLogger(__name__)


# 计算函数运行时间，并加入超时控制
def monitor_timer(
    trace_id_param="trace_id",
    timeout: float = 5.0,
    timeout_return: Any = None,
):
    """
    计算函数运行时间
    """

    def _decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            _trace_id = ""
            if len(args) > 0 and hasattr(args[0], trace_id_param):
                _trace_id = getattr(args[0], trace_id_param, "")

            start = time.perf_counter()
            result = await func(*args, **kwargs)
            end = time.perf_counter()
            logger.info(f"| [耗时][{func.__name__}] | _trace_id: {_trace_id}: {end - start:.4f}s")
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            _trace_id = ""
            if len(args) > 0 and hasattr(args[0], trace_id_param):
                _trace_id = getattr(args[0], trace_id_param, "")

            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            logger.info(f"| [耗时][{func.__name__}] | _trace_id: {_trace_id}: {end - start:.4f}s")
            return result

        # 自动判断同步/异步
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    def _decorator_limit_timeout(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            _trace_id = ""
            if len(args) > 0 and hasattr(args[0], trace_id_param):
                _trace_id = getattr(args[0], trace_id_param, "")

            start = time.perf_counter()
            try:
                # 异步函数 + 超时控制
                result = await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            except TimeoutError:
                end = time.perf_counter()
                logger.error(
                    f"| [超时][{func.__name__}] | trace_id: {_trace_id} | 超时{timeout}s | 耗时: {end - start:.4f}s"
                )
                return timeout_return

            end = time.perf_counter()
            logger.info(f"| [耗时][{func.__name__}] | _trace_id: {_trace_id}: {end - start:.4f}s")
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            _trace_id = ""
            if len(args) > 0 and hasattr(args[0], trace_id_param):
                _trace_id = getattr(args[0], trace_id_param, "")

            start = time.perf_counter()
            executor = ThreadPoolExecutor(max_workers=1)

            def run_func():
                return func(*args, **kwargs)

            future = executor.submit(run_func)
            try:
                result = future.result(timeout=timeout)
            except TimeoutError:
                end = time.perf_counter()
                logger.error(
                    f"| [超时][{func.__name__}] | trace_id: {_trace_id} | 超时{timeout}s | 耗时: {end - start:.4f}s"
                )
                executor.shutdown(wait=False, cancel_futures=True)
                return timeout_return
            end = time.perf_counter()
            logger.info(
                f"| [耗时][{func.__name__}] | trace_id: {_trace_id} | 耗时: {end - start:.4f}s"
            )
            executor.shutdown(wait=False)
            return result

        # 自动判断同步/异步
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    if timeout_return:
        return _decorator_limit_timeout
    else:
        return _decorator


# 记录请求和响应
def monitor_request_response(trace_id_param="trace_id"):
    """
    记录请求和响应
    """

    def _decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            _trace_id = ""
            _req = ""
            if len(args) > 0 and hasattr(args[0], trace_id_param):
                _trace_id = getattr(args[0], trace_id_param, "")
                _req = truncate_if_too_long(args[0])

            logger.info(f"| [接收请求][{func.__name__}] | _trace_id: {_trace_id}: {_req}")
            result = await func(*args, **kwargs)
            logger.info(
                f"| [返回结果][{func.__name__}] | _trace_id: {_trace_id}: {truncate_if_too_long(result)}"
            )
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            _trace_id = ""
            _req = ""
            if len(args) > 0 and hasattr(args[0], trace_id_param):
                _trace_id = getattr(args[0], trace_id_param, "")
                _req = truncate_if_too_long(args[0])

            logger.info(f"| [接收请求][{func.__name__}] | _trace_id: {_trace_id}: {_req}")
            result = func(*args, **kwargs)
            logger.info(
                f"| [返回结果][{func.__name__}] | _trace_id: {_trace_id}: {truncate_if_too_long(result)}"
            )
            return truncate_if_too_long(result)

        # 自动判断同步/异步
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return _decorator
