"""
LLM 模型模块
基于 langchain_openai.ChatOpenAI 构建可复用的聊天模型实例
"""
from functools import lru_cache

from langchain_openai import ChatOpenAI

from config import settings


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    """
    获取 ChatOpenAI 单例实例

    使用 lru_cache 保证整个应用生命周期内只创建一次模型连接，
    避免重复初始化带来的性能开销。

    Returns:
        ChatOpenAI: 配置好的 LangChain 聊天模型实例
    """
    return ChatOpenAI(
        model=settings.model,
        base_url=settings.base_url,
        api_key=settings.api_key,
        temperature=0.7,
    )
