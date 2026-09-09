"""
方向3：论文专项工具

- check_plagiarism: 本地文本相似度查重（基于 n-gram 重叠率）
- academic_search: 调用 arXiv API 搜索学术论文
- format_paper: 按学术论文模板排版 docx（字体/行距/页边距）
"""
import re
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen
import xml.etree.ElementTree as ET

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_LINE_SPACING
from langchain_core.tools import tool


@tool
def check_plagiarism(text1: str, text2: str) -> str:
    """
    对比两段文本的相似度（用于查重）。
    基于字符 n-gram 重叠率计算，返回相似度百分比和重复片段。
    注意：这是本地轻量查重，不能替代专业查重系统。
    """
    def get_ngrams(text, n=4):
        text = re.sub(r"\s+", "", text)
        return set(text[i:i+n] for i in range(len(text) - n + 1))

    ngrams1 = get_ngrams(text1)
    ngrams2 = get_ngrams(text2)

    if not ngrams1 or not ngrams2:
        return "文本过短，无法进行相似度对比。"

    intersection = ngrams1 & ngrams2
    union = ngrams1 | ngrams2
    similarity = len(intersection) / len(union) * 100

    # 找出重复的较长片段
    common_chars = set()
    for ng in intersection:
        common_chars.add(ng)
    # 取最长的公共子串片段展示（简化版）
    repeated = sorted(common_chars, key=len, reverse=True)[:5]

    result = [f"## 查重结果", f"**相似度：{similarity:.1f}%**", ""]
    if similarity > 30:
        result.append("⚠️ 相似度较高，建议修改。")
    elif similarity > 15:
        result.append("⚪ 存在一定重复，可酌情修改。")
    else:
        result.append("✅ 相似度较低。")
    result.append("")
    result.append("**重复片段示例：**")
    for r in repeated:
        result.append(f"- ...{r}...")
    return "\n".join(result)


@tool
def academic_search(query: str, max_results: int = 5) -> str:
    """
    调用 arXiv API 搜索学术论文。
    query: 搜索关键词（建议英文）
    max_results: 返回结果数量
    返回论文标题、作者、摘要和链接。
    """
    url = (
        f"http://export.arxiv.org/api/query?"
        f"search_query=all:{quote(query)}&start=0&max_results={max_results}"
    )
    try:
        with urlopen(url, timeout=15) as resp:
            data = resp.read().decode("utf-8")
    except Exception as e:
        return f"搜索失败：{e}"

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(data)
    entries = root.findall("atom:entry", ns)

    if not entries:
        return f"未找到与 '{query}' 相关的论文。"

    results = [f"## 搜索结果：{query}\n"]
    for i, entry in enumerate(entries, 1):
        title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
        summary = entry.find("atom:summary", ns).text.strip().replace("\n", " ")[:200]
        authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]
        link = entry.find("atom:id", ns).text
        results.append(f"### {i}. {title}")
        results.append(f"**作者**：{', '.join(authors[:3])}{'...' if len(authors) > 3 else ''}")
        results.append(f"**摘要**：{summary}...")
        results.append(f"**链接**：{link}")
        results.append("")
    return "\n".join(results)


@tool
def format_paper(file_path: str, output_path: str = "") -> str:
    """
    按中文学术论文标准排版 Word 文档：
    - 正文：宋体 小四(12pt)，1.5 倍行距，首行缩进 2 字符
    - 标题：黑体
    - 页边距：上下 2.54cm，左右 3.17cm
    file_path: 输入文档路径
    output_path: 输出路径，为空则覆盖原文件
    返回保存的文件路径。
    """
    doc = Document(file_path)

    # 页边距
    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(3.17)
        section.right_margin = Cm(3.17)

    # 遍历段落设置格式
    for para in doc.paragraphs:
        style_name = para.style.name if para.style else ""
        is_heading = re.search(r"(?:Heading|标题)\s*\d", style_name, re.IGNORECASE)

        pf = para.paragraph_format
        if is_heading:
            # 标题：黑体，不加首行缩进
            for run in para.runs:
                run.font.name = "黑体"
                run.font.bold = True
        else:
            # 正文：宋体，1.5倍行距，首行缩进2字符
            pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
            pf.first_line_indent = Cm(0.74)  # 约2字符（小四）
            for run in para.runs:
                run.font.name = "宋体"
                if run.font.size is None or run.font.size < Pt(10):
                    run.font.size = Pt(12)

    save_path = output_path or file_path
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    doc.save(save_path)
    return str(Path(save_path).resolve())
