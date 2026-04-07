# -*- coding: utf-8 -*-
# @Time   : 2026/04/06
# @Author : zip
# @Moto   : Knowledge comes from decomposition
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)

logger = logging.getLogger(__name__)

_singleton_app_config: AppConfig | None = None


def init_app_config(*, config_path: str = "config.yaml", env_path_override: str = ".env"):
    global _singleton_app_config

    _set_dotenv(env_path_override)  # 加载 .env 文件,获得.env 中的所有环境变量

    _config_file = Path(config_path)

    if not _config_file.exists():
        logger.error(f"配置文件不存在: {_config_file}")
        raise FileNotFoundError(f"配置文件不存在: {_config_file}")

    with open(_config_file, encoding="utf-8") as f:
        _raw_data = yaml.safe_load(f) or {}

    _raw_data = _process_dict(_raw_data)  # 若是env 则会覆盖config.yaml
    _singleton_app_config = AppConfig.model_validate(_raw_data)
    logger.info(f"加载配置文件成功: {_singleton_app_config}")


# 直接获取配置
def get_app_config() -> AppConfig:
    global _singleton_app_config
    if _singleton_app_config is None:
        logger.error("请先调用 init_app_config() 初始化配置")
        raise RuntimeError("请先调用 init_app_config() 初始化配置")

    return _singleton_app_config


# ------------------------------ 配置 ------------------------------
class SystemConfig(BaseModel):
    """系统级配置模型"""

    IP_PORT: str = Field("0.0.0.0:2022", description="服务监听的IP和端口")
    WORKERS: int = Field(1, ge=1, le=32, description="服务工作进程数（1-32）")
    TIMEOUT: int = Field(30, ge=1, description="服务超时时间（秒，最小60）")
    NAME: str = Field("vector_service", description="服务名称")
    DESC: str = Field("向量服务", description="服务描述")
    VERSION: str = Field("0.0.1", description="服务版本号")
    DEBUG: bool = Field(default=False, description="调试模式开关")

    @field_validator("IP_PORT")
    @classmethod
    def validate_ip_port(cls, v: str) -> str:
        """校验IP:PORT格式"""
        parts = v.split(":")
        if len(parts) != 2:
            raise ValueError(f"IP_PORT格式错误: {v}，必须是 'ip:port' 格式")
        _, port = parts
        # 简单校验端口范围
        try:
            port_int = int(port)
            if not (0 <= port_int <= 65535):
                raise ValueError(f"端口号 {port} 超出范围（0-65535）")
        except ValueError:
            raise ValueError(f"端口号 {port} 不是有效数字") from None
        return v


class LiteLLMParams(BaseModel):
    """LLM模型的litellm参数模型"""

    model: str = Field(..., description="模型名称（如 openai/Qwen3-235B-A22B）")
    api_base: str = Field(..., description="API基础地址（支持环境变量）")
    api_key: str = Field(..., description="API密钥（支持环境变量）")
    cache: bool = Field(default=False, description="是否启用缓存")
    verbose: bool = Field(default=True, description="是否输出详细日志")
    request_timeout: int = Field(default=600, ge=30, description="请求超时时间（秒）")
    temperature: float = Field(default=0.2, ge=0.0, le=1.0, description="温度系数")
    top_p: float = Field(default=0.2, ge=0.0, le=1.0, description="Top P值")
    top_k: int | None = Field(None, ge=1, description="Top K值")
    max_retries: int = Field(default=2, ge=0, le=10, description="最大重试次数")
    chat_template_kwargs: dict[str, Any] | None = Field(None, description="聊天模板参数")

    @field_validator("api_base", "api_key")
    @classmethod
    def resolve_llm_env_vars(cls, v: str) -> str:
        """解析LLM配置中的环境变量"""
        return os.path.expandvars(v) if v else v


class LiteLLMModelConfig(BaseModel):
    """单个LLM模型配置"""

    model_name: str = Field(..., description="自定义模型名称（如 basic/reasoning）")
    litellm_params: LiteLLMParams = Field(..., description="litellm相关参数")


class LLMConfig(BaseModel):
    """LLM模型配置"""

    default_model_name: str = Field(..., description="默认使用的LLM模型名称")
    model_list: list[LiteLLMModelConfig] = Field(..., description="LLM模型列表")

    @model_validator(mode="after")
    def validate_default_model(self) -> LLMConfig:
        """校验默认模型是否在模型列表中"""
        model_names = [m.model_name for m in self.model_list]
        if self.default_model_name not in model_names:
            raise ValueError(
                f"默认LLM模型 {self.default_model_name} 不在模型列表中，可用模型: {model_names}"
            )
        return self


class AgentNodeHooksConfig(BaseModel):
    """AgentHooks配置模型"""

    truncate_max_length: int = Field(
        default=1024, description="截断最大长度（超过此长度的文本将被截断）"
    )

    enable_timing: bool = Field(default=True, description="是否启用计时功能")


class HookConfig(BaseModel):
    """Hook配置模型"""

    Agent_Node_Hooks: AgentNodeHooksConfig = Field(
        default_factory=AgentNodeHooksConfig, description="AgentHooks配置"
    )


class AppConfig(BaseModel):
    """应用总配置模型（对应整个YAML文件）"""

    SYSTEM: SystemConfig = Field(..., description="系统配置")
    LLM: LLMConfig = Field(..., description="LLM模型配置")
    HOOK: HookConfig = Field(..., description="Hook配置")


# ------------------------------ 配置 ------------------------------
def _replace_env_vars(value: str) -> str:
    """Replace environment variables in string values."""
    if not isinstance(value, str):
        return value
    if value.startswith("$"):
        env_var = value[1:]
        return os.getenv(env_var, value)
    return value


def _process_dict(config: dict[str, Any]) -> dict[str, Any]:
    """Recursively process dictionary to replace environment variables."""
    result = {}
    for key, value in config.items():
        if isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    value[i] = _process_dict(item)
                elif isinstance(item, str):
                    value[i] = _replace_env_vars(item)
            result[key] = value

        if isinstance(value, dict):
            result[key] = _process_dict(value)
        elif isinstance(value, str):
            result[key] = _replace_env_vars(value)
        else:
            result[key] = value
    return result


def _set_dotenv(env_path_override: str = ".env"):
    """
    加载 .env 环境变量文件，支持自定义路径覆盖

    优先级：
    1. 函数入参 env_path_override（最高优先级）
    2. 系统环境变量 ENV_PATH

    Args:
        env_path_override: 自定义 .env 文件路径，优先级高于 ENV_PATH 和默认路径

    Returns:
        bool: 加载成功返回 True，失败返回 False

    Raises:
        无（所有异常捕获并记录日志，保证函数鲁棒性）
    """
    # 1. 确定最终的 .env 文件路径
    try:
        # 优先级：自定义入参 > 系统环境变量 > 默认路径
        final_env_path = env_path_override or os.environ.get("ENV_PATH", ".env")
        # 转换为 Path 对象，提升路径处理兼容性
        final_env_path = Path(final_env_path).resolve()

        # 2. 检查文件是否存在
        if not final_env_path.exists():
            logger.warning(f".env 文件不存在：{final_env_path}，跳过环境变量加载")

        # 3. 检查文件是否为普通文件（避免目录/链接等）
        if not final_env_path.is_file():
            logger.error(f"指定的 .env 路径不是有效文件：{final_env_path}")

        # 4. 加载环境变量
        load_dotenv(
            dotenv_path=final_env_path, override=False
        )  # override=False 避免覆盖已有系统环境变量
        logger.info(f"成功从 {final_env_path} 加载环境变量")

    except Exception as e:
        # 捕获所有异常，避免函数崩溃
        logger.error(f"加载 .env 文件失败：{e!r}", exc_info=True)
