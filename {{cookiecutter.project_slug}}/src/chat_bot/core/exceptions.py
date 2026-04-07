# -*- coding: utf-8 -*-
# @Time   : 2026/04/06
# @Author : zip
# @Moto   : Knowledge comes from decomposition
from __future__ import annotations

"""
自定义异常类定义
定义应用中的各种异常类型，包含具体的错误代码和详细信息
"""


class AppException(Exception):
    """应用异常基类"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
        self.exc_name = "AppException"
        self.code = 500

    def __str__(self) -> str:
        return f"[code={self.code}]|[exc_name={self.exc_name}]:{self.message}"


class LLMContextExceededError(AppException):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

        self.exc_name = "LLM_ContextExceeded_ERROR"
        self.code = 501


class LLMBadRequestError(AppException):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

        self.exc_name = "LLM_BadRequest_ERROR"
        self.code = 502


class LLMExceptionError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
        self.exc_name = "LLM_Exception_ERROR"
        self.code = 503


class ChatExceptionError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
        self.exc_name = "Cha_Exception_ERROR"
        self.code = 504
