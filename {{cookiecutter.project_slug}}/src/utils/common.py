# -*- coding: utf-8 -*-
# @Time   : {{ cookiecutter.timestamp }}
# @Author : {{ cookiecutter.author_name }} : {{ cookiecutter.email }}
# @Moto   : Knowledge lies in decomposition
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


# 截断结果
def truncate_if_too_long(result: list[Any] | Any) -> list[str] | str:
    TOOL_RESULT_TOKEN_LIMIT = 100
    TRUNCATION_GUIDANCE = "... [结果太长被截断]"

    """Truncate list or string result if it exceeds token limit (rough estimate: 4 chars/token)."""
    if isinstance(result, list):
        result = [str(item) for item in result]
        total_chars = sum(len(item) for item in result)
        if total_chars > TOOL_RESULT_TOKEN_LIMIT * 4:
            return [
                *result[: len(result) * TOOL_RESULT_TOKEN_LIMIT * 4 // total_chars],
                TRUNCATION_GUIDANCE,
            ]
        return result
    # string
    result = str(result)
    if len(result) > TOOL_RESULT_TOKEN_LIMIT * 4:
        return result[: TOOL_RESULT_TOKEN_LIMIT * 4] + "\n" + TRUNCATION_GUIDANCE
    return result
