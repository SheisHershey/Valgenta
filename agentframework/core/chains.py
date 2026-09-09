"""
LCEL 链（通道）模块

LCEL (LangChain Expression Language) 通过管道符 | 将多个 Runnable 组件
串联成一条数据处理流水线。这条流水线就是 LangChain 中的"通道"：

    prompt  -->  llm  -->  parser
    (输入)     (推理)     (解析输出)

数据从左到右流过每个节点，每个节点接收上一个节点的输出并产生新的输出，
最终形成一条可组合、可观测、可调试的执行通道。
"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSerializable

from core.llm import get_llm
from core.prompts import get_teacher_prompt


def build_simple_chain() -> RunnableSerializable:
    """
    构建基础问答链（对应 langchainmain 中的原始示例）

    通道结构：
        ChatPromptTemplate -> ChatOpenAI -> StrOutputParser

    工作流程：
        1. prompt 接收 {"question": "..."} 生成 ChatPromptValue
        2. llm 接收提示词消息列表，调用模型生成 AIMessage
        3. parser 从 AIMessage 中提取纯文本字符串

    Returns:
        RunnableSerializable: 可直接 .invoke() 的 LCEL 链
    """
    prompt = get_teacher_prompt()
    llm = get_llm()
    parser = StrOutputParser()

    # 使用 | 运算符组合通道：每个组件都是 Runnable，| 会返回 RunnableSequence
    chain = prompt | llm | parser
    return chain
