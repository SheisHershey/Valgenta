"""
LangChain Agent 封装

基于 langchain.agents.create_agent 构建工具调用型智能体。
create_agent 内部编译为 LangGraph 的 CompiledStateGraph，
消息状态通过 Channel（add_messages 归约器）在节点间传递。
"""
from typing import List, Optional

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool

from core.llm import get_llm


class LangChainAgent:
    """
    工具调用型 Agent 的工程化封装

    职责：
    - 接收 LLM 模型和工具列表
    - 构建 LangGraph 状态图（create_agent）
    - 提供 run() 方法执行对话
    """

    def __init__(
        self,
        tools: Optional[List[BaseTool]] = None,
        system_prompt: Optional[str] = None,
    ):
        """
        Args:
            tools: 可供 Agent 调用的工具列表
            system_prompt: 系统提示词，定义 Agent 角色和行为
        """
        self.tools = tools or []
        self.system_prompt = system_prompt or (
            "你是一个智能助手，可以使用工具来帮助用户解决问题。"
            "当需要查询外部信息时，请调用合适的工具。"
        )
        # 编译生成 LangGraph 状态图（内部使用 Channel 管理 messages）
        self._graph = create_agent(
            model=get_llm(),
            tools=self.tools,
            system_prompt=self.system_prompt,
        )

    def run(self, user_input: str) -> str:
        """
        执行一次 Agent 对话

        Args:
            user_input: 用户输入文本

        Returns:
            str: Agent 的最终回答文本
        """
        # 构造初始状态：messages 通道接收一条 HumanMessage
        initial_state = {"messages": [HumanMessage(content=user_input)]}

        # 调用状态图，LangGraph 会在 LLM 节点和工具节点之间循环，
        # 每次循环通过 messages channel 累积对话历史
        result = self._graph.invoke(initial_state)

        # 从最终状态的 messages 通道中取出最后一条 AI 消息
        messages = result["messages"]
        return messages[-1].content
