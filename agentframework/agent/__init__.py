"""
agent 包：基于 LangChain 的智能体

- LangChainAgent: 通用工具调用型 Agent
- create_doc_agent: 文档办公专用 Agent 工厂函数
"""
from agent.agent import LangChainAgent
from agent.doc_agent import create_doc_agent

__all__ = ["LangChainAgent", "create_doc_agent"]
