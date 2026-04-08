# -*- coding: utf-8 -*-
# @Time   : {{ cookiecutter.timestamp }}
# @Author : {{ cookiecutter.author_name }} : {{ cookiecutter.email }}
# @Moto   : Knowledge lies in decomposition
from __future__ import annotations

import logging
import logging.config
import os
import re
from configparser import RawConfigParser
from datetime import datetime
from pathlib import Path

import structlog
from structlog.stdlib import ProcessorFormatter


def _custom_timestamper(_, __, event_dict):
    """自定义时间格式处理器"""
    now = datetime.now()  # 获取当前本地时间
    # 输出格式: 2026-04-06 22:15:30.456 | 1744025730
    readable_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    timestamp = int(now.timestamp())
    # 组合成你要的格式
    event_dict["timestamp"] = f"{readable_time} | {timestamp}"
    return event_dict


def _configure_structlog(use_json: bool, log_level: str) -> None:
    """structlog 核心配置"""
    shared_processors = [
        structlog.contextvars.merge_contextvars,  # 支持请求上下文（request_id 等）
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        # structlog.processors.TimeStamper(fmt="iso", utc=True),
        _custom_timestamper,  # 使用自定义的时间处理器代替 TimeStamper
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    # 选择渲染器
    if use_json:
        renderer = structlog.processors.JSONRenderer(ensure_ascii=False, indent=4, sort_keys=True)
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    # 配置 structlog
    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,  # 关键桥接点
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # --- 关键步骤：统一配置现有 Handler 的 Formatter ---
    # 这会强制让所有通过 logging.getLogger 打印的内容也经过 structlog 的处理器
    formatter = ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=shared_processors,
    )

    root_logger = logging.getLogger()
    for handler in logging.getLogger().handlers:
        handler.setFormatter(formatter)

    root_logger.setLevel(log_level)


def _get_log_file_paths_from_ini(ini_path: str) -> list[Path]:
    """从 logging.ini 中自动提取所有日志文件路径"""
    parser = RawConfigParser()
    parser.read(ini_path, encoding="utf-8")

    log_paths = []
    # 正则匹配 FileHandler 路径
    pattern = re.compile(r"[^']+'([^']+)'")

    for section in parser.sections():
        if not section.startswith("handler_"):
            continue
        if "args" not in parser[section]:
            continue

        args = parser[section]["args"].strip()
        match = pattern.search(args)
        if match:
            log_path = match.group(1).strip()
            if log_path.endswith(".log"):
                log_paths.append(Path(log_path))

    return log_paths


def init_app_logging(*, json_logs=True, log_level: str = "INFO") -> None:
    """
    配置结构化日志
    json_logs=True 时输出纯 JSON（生产环境）
    json_logs=False 时输出彩色控制台日志（开发环境）
    """
    # 1. 先加载 logging.ini（配置 handlers、levels 等）
    ini_path = os.getenv("LOGGING_PATH", "logging.ini")
    ini_path = Path(ini_path).resolve()

    # 2. 自动解析所有日志文件路径 → 创建目录（核心）
    log_paths = _get_log_file_paths_from_ini(str(ini_path))
    for log_path in log_paths:
        if not log_path.is_absolute():
            log_path = Path.cwd() / log_path
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # 3. 加载 logging 配置
    logging.config.fileConfig(str(ini_path), disable_existing_loggers=False)

    # 4. 配置 structlog（核心：根据环境切换 renderer）
    _configure_structlog(json_logs, log_level)

    # 初始化日志
    structlog.get_logger("chatbot").info(
        "日志系统初始化完成",
        environment="development" if not json_logs else "production",
        log_format="json" if json_logs else "console",
        log_files=[str(p) for p in log_paths],
    )
