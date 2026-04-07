# -*- coding: utf-8 -*-
# @Time   : {{ cookiecutter.timestamp }}
# @Author : {{ cookiecutter.author_name }} : {{ cookiecutter.email }}
# @Moto   : Knowledge comes from decomposition
import asyncio
import json

import requests
import websockets

request_data = {
    "trace_id": "123",
    "context": {"thread_id": "Nova", "model": "deepseek", "agent": "chat"},
    "state": {
        "messages": [
            {
                "type": "human",
                "content": "中国的首都在哪？",  #
            },
        ],
    },
    "stream": True,
}


async def chat_client():

    # 使用 httpx 异步客户端发送请求
    result = requests.post("http://0.0.0.0:2022/chat_with_llm/v1", data=request_data, timeout=600.0)
    print(result.json())


asyncio.run(chat_client())

"""
curl -X POST http://0.0.0.0:2022/chat_with_llm/v1 -H "Content-Type: application/json" -d '{"trace_id": "123", "context": {"thread_id": "Nova", "model": "deepseek", "agent": "chat"}, "state": {"messages": [{"type": "human", "content": "中国的首都在哪？"}]}, "stream": true}'

"""


async def chat_websocket():
    token = 1234
    async with websockets.connect(f"ws://0.0.0.0:2021/agent/ws?token={token}") as websocket:
        # 发送请求（JSON 字符串）
        await websocket.send(json.dumps(request_data))

        # 接收响应（流式则循环接收）
        print("=== 开始接收响应 ===")
        while True:
            try:
                response_json = await websocket.recv()
                # 解析为字典，便于查看
                response = json.loads(response_json)
                print(f"code: {response['code']} | data: {response['data']}")

                # 流式场景：判断是否完成
                if (
                    response["code"] == 0
                    and response["data"].get("event_info")
                    and response["data"].get("event_name") == "on_chain_end"
                    and response["data"]["event_info"].get("node_name") == "LangGraph"
                ):
                    print("=== 流式响应接收完成 ===")
                    break

            except websockets.exceptions.ConnectionClosed:
                print("连接已关闭")
                break


# asyncio.run(chat_websocket())
