# -*- coding: utf-8 -*-
# @Time   : {{ cookiecutter.timestamp }}
# @Author : {{ cookiecutter.author_name }} : {{ cookiecutter.email }}
# @Moto   : Knowledge lies in decomposition
from __future__ import annotations

"""
自定义异常类定义
定义应用中的各种异常类型，包含具体的错误代码和详细信息
AppException 是必备的
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
