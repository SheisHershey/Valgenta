"""
文档办公工具集

提供办公文档处理相关的工具：
- read_document: 读取本地 docx 文档
- write_document: 将内容写入 docx 文档
- polish_text: AI 润色文本
- summarize_text: AI 总结文本
- translate_text: AI 翻译文本
- check_grammar: AI 语法/用词检查
"""
from langchain_core.tools import tool

from core.docx_processor import read_docx, write_docx
from core.llm import get_llm


@tool
def read_document(file_path: str) -> str:
    """读取本地 Word 文档（.docx）的全部文本内容，包括段落和表格。"""
    return read_docx(file_path)


@tool
def write_document(file_path: str, content: str, title: str = "") -> str:
    """将文本内容写入新的 Word 文档（.docx），返回保存的文件路径。"""
    return write_docx(file_path, content, title=title or None)


@tool
def polish_text(text: str, style: str = "学术") -> str:
    """
    对文本进行润色改写，提升表达质量。
    style 可选：学术、商务、正式、口语、简洁。
    """
    prompt = (
        f"请对以下文本进行润色，使其更加{style}、流畅、专业。"
        f"保持原意不变，直接输出润色后的文本，不要添加解释。\n\n"
        f"原文：\n{text}"
    )
    return get_llm().invoke(prompt).content


@tool
def summarize_text(text: str, max_length: int = 300) -> str:
    """
    对长文本进行摘要总结。
    max_length 控制摘要的大致字数。
    """
    prompt = (
        f"请用不超过{max_length}字总结以下文本的核心内容，"
        f"要求准确、简洁、重点突出。\n\n"
        f"原文：\n{text}"
    )
    return get_llm().invoke(prompt).content


@tool
def translate_text(text: str, target_language: str = "英文") -> str:
    """
    将文本翻译为目标语言。
    target_language 示例：英文、中文、日文。
    """
    prompt = (
        f"请将以下文本翻译为{target_language}，"
        f"要求准确、自然、符合目标语言表达习惯。直接输出译文。\n\n"
        f"原文：\n{text}"
    )
    return get_llm().invoke(prompt).content


@tool
def check_grammar(text: str) -> str:
    """检查文本中的语法错误、用词不当和逻辑问题，并给出修改建议。"""
    prompt = (
        "请检查以下文本的语法、用词和逻辑问题，"
        "逐条列出问题和修改建议，格式为：问题→建议。\n\n"
        f"原文：\n{text}"
    )
    return get_llm().invoke(prompt).content
