"""
Word 文档处理模块

封装 python-docx，提供文档读写的工程化能力：
- 读取 docx 全文（段落 + 表格）
- 将文本写入新的 docx 文件
- 保留基本段落结构
"""
from pathlib import Path
from typing import Optional

from docx import Document
from docx.shared import Pt


def read_docx(file_path: str) -> str:
    """
    读取 Word 文档全文内容

    依次提取所有段落和表格中的文本，按出现顺序拼接。

    Args:
        file_path: docx 文件路径

    Returns:
        str: 文档纯文本内容，段落间以换行分隔

    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 文件不是 .docx 格式
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    if path.suffix.lower() != ".docx":
        raise ValueError(f"仅支持 .docx 格式，当前文件: {path.suffix}")

    doc = Document(str(path))
    parts: list[str] = []

    # 提取段落
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            parts.append(text)

    # 提取表格
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(
                cell.text.strip() for cell in row.cells if cell.text.strip()
            )
            if row_text:
                parts.append(row_text)

    return "\n".join(parts)


def write_docx(file_path: str, content: str, title: Optional[str] = None) -> str:
    """
    将文本内容写入新的 Word 文档

    Args:
        file_path: 输出 docx 文件路径
        content: 文本内容，以换行符分段
        title: 可选的文档标题（加粗放大）

    Returns:
        str: 实际写入的文件绝对路径
    """
    doc = Document()

    # 设置默认字体
    style = doc.styles["Normal"]
    font = style.font
    font.name = "宋体"
    font.size = Pt(12)

    # 写入标题
    if title:
        heading = doc.add_heading(title, level=1)
        for run in heading.runs:
            run.font.size = Pt(18)

    # 按换行分段写入
    for line in content.split("\n"):
        line = line.strip()
        if line:
            doc.add_paragraph(line)
        else:
            doc.add_paragraph("")

    # 确保输出目录存在
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(file_path))
    return str(Path(file_path).resolve())
