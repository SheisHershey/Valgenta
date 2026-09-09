"""
主入口模块 (langchainmain)

本模块是整个 Agent 框架的主入口，演示三种基于 LangChain 的执行通道：

1. 简单 LCEL 通道 (Simple Chain)
   prompt | llm | parser
   适用于单轮问答，无需工具调用的场景。

2. 通用 Agent 通道 (Tool-calling Agent)
   基于 LangGraph 的状态图，LLM 节点 <-> 工具节点 循环执行。

3. 文档办公助手通道 (Document Assistant)
   专注于 Word 文档的阅读、润色、总结、翻译、生成。
"""
from pathlib import Path

from core.chains import build_simple_chain
from core.docx_processor import write_docx
from agent.agent import LangChainAgent
from agent.doc_agent import create_doc_agent
from tools import get_tools


def demo_simple_chain():
    """演示 1：简单 LCEL 问答链"""
    print("=" * 60)
    print("通道一：LCEL 简单问答链 (prompt | llm | parser)")
    print("=" * 60)

    chain = build_simple_chain()
    response = chain.invoke({"question": "什么是Agent？"})
    print(f"提问：什么是Agent？")
    print(f"回答（摘要）：{response[:80]}...")
    print()


def demo_agent_with_tools():
    """演示 2：带工具调用的通用 Agent"""
    print("=" * 60)
    print("通道二：LangGraph Agent (LLM <-> Tools 循环)")
    print("=" * 60)

    tools = get_tools()
    print(f"已加载工具：{[t.name for t in tools]}")

    agent = LangChainAgent(tools=tools)

    answer = agent.run("东京天气怎么样？")
    print(f"提问：东京天气怎么样？")
    print(f"回答：{answer[:100]}")
    print()


def demo_doc_agent():
    """演示 3：文档办公助手"""
    print("=" * 60)
    print("通道三：文档办公助手 (读 docx → 润色 → 写 docx)")
    print("=" * 60)

    # 准备一份样例文档（模拟用户本地的论文草稿）
    sample_dir = Path("output")
    sample_dir.mkdir(exist_ok=True)
    sample_path = sample_dir / "论文草稿.docx"
    draft_content = (
        "人工智能技术的发展\n\n"
        "近年来，人工智能技术发展很快，在很多领域都有应用。"
        "机器学习是人工智能的一个重要分支，它让计算机能够从数据中学习规律。"
        "深度学习作为机器学习的一种方法，在图像识别和自然语言处理方面取得了很好的效果。"
        "总的来说，人工智能将会在未来发挥越来越重要的作用。"
    )
    write_docx(str(sample_path), draft_content, title="人工智能技术的发展")
    print(f"📄 已创建样例文档：{sample_path.resolve()}")

    # 创建文档助手
    agent = create_doc_agent()

    # 场景：读取文档并润色，输出新文档
    instruction = (
        f"请读取文档 {sample_path.resolve()}，"
        f"对内容进行学术风格润色，"
        f"然后将润色后的内容写入 {sample_dir.resolve()}\\论文润色版.docx，"
        f"最后告诉我润色前后的对比要点。"
    )
    print(f"\n💬 用户指令：{instruction[:60]}...\n")

    answer = agent.run(instruction)
    print(f"🤖 助手回复：\n{answer}")
    print()


def main():
    """主函数：依次演示三种通道"""
    print("\n🚀 LangChain Agent Framework 启动\n")

    # 通道一：简单 LCEL 链
    demo_simple_chain()

    # 通道二：通用工具 Agent
    demo_agent_with_tools()

    # 通道三：文档办公助手
    demo_doc_agent()

    print("✅ 所有通道执行完毕")


if __name__ == "__main__":
    main()
