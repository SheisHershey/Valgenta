"""
文档办公智能体

基于通用 LangChainAgent，配置文档办公专用的工具集和系统提示词，
专注于论文/办公文档的阅读、润色、总结、翻译、生成等场景。
"""
from agent.agent import LangChainAgent

# 基础文档工具
from tools.document import (
    read_document,
    write_document,
    polish_text,
    summarize_text,
    translate_text,
    check_grammar,
)

# 方向1：文档结构增强
from tools.structure import (
    extract_outline,
    format_reference,
    generate_toc,
)

# 方向2：表格与数据
from tools.data import (
    read_table,
    create_chart,
    excel_summary,
)

# 方向3：论文专项
from tools.paper import (
    check_plagiarism,
    academic_search,
    format_paper,
)

# 方向4：多格式支持
from tools.format import (
    convert_format,
    read_pdf,
)

# 方向5：流程自动化
from tools.automation import (
    batch_process,
    compare_versions,
    email_draft,
)

# 方向6：知识管理（RAG）
from tools.knowledge import (
    build_knowledge_base,
    search_knowledge_base,
    extract_keywords,
)


# 文档办公场景的系统提示词
DOC_SYSTEM_PROMPT = """\
你是一位专业的办公文档与论文写作助手，擅长处理 Word 文档、PDF、Excel 等办公文件。

你拥有以下能力，请按需调用对应工具：

【文档读写】
- read_document: 读取本地 .docx 文档内容
- write_document: 将内容写入新的 .docx 文档
- read_pdf: 读取 PDF 文档内容
- convert_format: 文档格式转换（docx→md/txt）

【内容处理】
- polish_text: 润色改写文本（学术/商务/正式/口语/简洁）
- summarize_text: 摘要总结
- translate_text: 翻译文本
- check_grammar: 语法/用词检查

【文档结构】
- extract_outline: 提取文档大纲
- generate_toc: 生成目录
- format_reference: 格式化参考文献

【表格与数据】
- read_table: 读取 docx 中的表格
- create_chart: 生成图表（柱状/折线/饼图）
- excel_summary: 分析 Excel 数据

【论文专项】
- check_plagiarism: 文本相似度查重
- academic_search: 搜索学术论文（arXiv）
- format_paper: 按学术论文模板排版

【流程自动化】
- batch_process: 批量处理文件夹中的 docx
- compare_versions: 对比两个版本文档差异
- email_draft: 生成商务邮件草稿

【知识管理 RAG】
- build_knowledge_base: 构建知识库（加载文件夹文档→向量化→存储）
- search_knowledge_base: 从知识库语义检索相关内容
- extract_keywords: 从文档提取关键词/标签

工作原则：
- 用户提到本地文件时，先读取内容再处理
- 处理后如需保存，调用 write_document 或对应工具生成新文件
- 回答简洁专业，先告知将执行的操作，再给出结果
"""


def create_doc_agent() -> LangChainAgent:
    """
    创建文档办公智能体（含全部 6 大方向、共 23 个工具）

    Returns:
        LangChainAgent: 配置好文档工具和系统提示词的智能体
    """
    doc_tools = [
        # 基础
        read_document, write_document, polish_text,
        summarize_text, translate_text, check_grammar,
        # 方向1
        extract_outline, format_reference, generate_toc,
        # 方向2
        read_table, create_chart, excel_summary,
        # 方向3
        check_plagiarism, academic_search, format_paper,
        # 方向4
        convert_format, read_pdf,
        # 方向5
        batch_process, compare_versions, email_draft,
        # 方向6
        build_knowledge_base, search_knowledge_base, extract_keywords,
    ]
    return LangChainAgent(
        tools=doc_tools,
        system_prompt=DOC_SYSTEM_PROMPT,
    )
