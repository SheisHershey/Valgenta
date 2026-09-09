"""
提示词模板模块
使用 LangChain 的 ChatPromptTemplate 定义可复用的提示词
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def get_teacher_prompt() -> ChatPromptTemplate:
    """
    AI 老师场景的提示词模板（对应 langchainmain 中的原始示例）

    Returns:
        ChatPromptTemplate: 包含 system 和 human 消息的模板
    """
    return ChatPromptTemplate.from_template(
        """
你是一个AI老师。

请回答下面的问题：

{question}

"""
    )


def get_agent_prompt() -> ChatPromptTemplate:
    """
    Agent 场景的提示词模板，支持工具调用

    使用 MessagesPlaceholder 占位符，允许动态插入：
    - chat_history: 历史对话消息
    - agent_scratchpad: Agent 的中间思考过程（工具调用 + 工具结果）

    Returns:
        ChatPromptTemplate: Agent 专用的多消息模板
    """
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是一个智能助手，可以使用工具来帮助用户解决问题。"
                "当需要查询外部信息时，请调用合适的工具。",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
