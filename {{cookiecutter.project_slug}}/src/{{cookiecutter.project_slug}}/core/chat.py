# -*- coding: utf-8 -*-
# @Time   : {{ cookiecutter.timestamp }}
# @Author : {{ cookiecutter.author_name }} : {{ cookiecutter.email }}
# @Moto   : Knowledge comes from decomposition
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

"""
注意当你的对象需要实例化调用时，请采用函数式操作

"""
_singleton_chat: ChatWithLLM | None = None


def get_chat_with_llm() -> ChatWithLLM:
    global _singleton_chat
    if _singleton_chat is None:
        _singleton_chat = ChatWithLLM()
    return _singleton_chat


class ChatWithLLM:
    def __init__(self):
        self.compile_graph = None

    def get_compile_graph(self):
        if self.compile_graph:
            return self.compile_graph
        else:
            return self._compile_graph()

    def _creat_node(self, node_name="chat"):
        pass

    def _compile_graph(self):
        pass
