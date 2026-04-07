# -*- coding: utf-8 -*-
# @Time   : {{ cookiecutter.timestamp }}
# @Author : {{ cookiecutter.author_name }} : {{ cookiecutter.email }}
# @Moto   : Knowledge comes from decomposition
from __future__ import annotations

import os

import yaml


# 使用下划线开头的变量名，Gunicorn 会忽略它们
def _load_config():
    config_path = os.getenv("CONFIG_PATH", "config.yaml")
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


_data = _load_config()
_system_config = _data["SYSTEM"]

# --- Gunicorn 核心配置 ---
# 这些变量名是 Gunicorn 识别的，必须保持原样
bind = _system_config["IP_PORT"]
workers = _system_config["WORKERS"]
timeout = _system_config["TIMEOUT"]
worker_class = "uvicorn.workers.UvicornWorker"

# 日志配置
accesslog = None
errorlog = None
loglevel = "info"
