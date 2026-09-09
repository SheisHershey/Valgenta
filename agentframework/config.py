"""
应用配置模块
使用 pydantic-settings 实现类型安全的配置管理，支持环境变量和 .env 文件
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    全局配置类

    所有配置项均可通过环境变量覆盖，命名规则：
    - 类字段名 -> 环境变量名（自动转大写，支持 .env 文件）
    """

    # LLM 模型配置
    model: str = "sensenova-6.8-flash-lite"
    base_url: str = "https://token.sensenova.cn/v1"
    api_key: str = "sk-YDKSdG8uGeUYTo7TXSdeExW6khDkaQa8"

    # Agent 行为配置
    agent_max_iterations: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


# 全局单例配置实例
settings = Settings()
