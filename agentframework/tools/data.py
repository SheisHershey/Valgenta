"""
方向2：表格与数据工具

- read_table: 精确读取 docx 中指定表格，返回结构化文本
- create_chart: 根据数据生成柱状/折线/饼图图片
- excel_summary: 读取 Excel 并生成数据分析报告
"""
from pathlib import Path
from typing import List

import matplotlib
matplotlib.use("Agg")  # 无界面后端
import matplotlib.pyplot as plt

# 设置中文字体（Windows 优先使用微软雅黑/黑体）
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
matplotlib.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

from docx import Document
from langchain_core.tools import tool

from core.llm import get_llm


@tool
def read_table(file_path: str, table_index: int = 0) -> str:
    """
    读取 Word 文档中指定的表格（从 0 开始编号）。
    返回表格的行列结构文本。
    """
    doc = Document(file_path)
    if table_index >= len(doc.tables):
        return f"文档中只有 {len(doc.tables)} 个表格，无法读取第 {table_index} 个。"

    table = doc.tables[table_index]
    rows: List[str] = []
    for i, row in enumerate(table.rows):
        cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
        if i == 0:
            rows.append("| " + " | ".join(cells) + " |")
            rows.append("|" + "|".join(["---"] * len(cells)) + "|")
        else:
            rows.append("| " + " | ".join(cells) + " |")
    return f"### 表格 {table_index}\n" + "\n".join(rows)


@tool
def create_chart(
    title: str,
    labels: str,
    values: str,
    chart_type: str = "bar",
    output_path: str = "output/chart.png",
) -> str:
    """
    根据数据生成图表图片。
    labels: 横轴标签，用逗号分隔，如 "一季度,二季度,三季度,四季度"
    values: 数值，用逗号分隔，如 "100,200,150,300"
    chart_type: bar（柱状）/ line（折线）/ pie（饼图）
    output_path: 图片保存路径
    返回保存的图片路径。
    """
    label_list = [x.strip() for x in labels.split(",")]
    try:
        value_list = [float(x.strip()) for x in values.split(",")]
    except ValueError:
        return "错误：values 必须是逗号分隔的数字。"

    if len(label_list) != len(value_list):
        return f"错误：标签数量({len(label_list)})与数值数量({len(value_list)})不匹配。"

    fig, ax = plt.subplots(figsize=(8, 5))

    if chart_type == "bar":
        ax.bar(label_list, value_list, color="#4C72B0")
    elif chart_type == "line":
        ax.plot(label_list, value_list, marker="o", color="#4C72B0")
    elif chart_type == "pie":
        ax.pie(value_list, labels=label_list, autopct="%1.1f%%")
        ax.axis("equal")
    else:
        return f"不支持的图表类型: {chart_type}，可选 bar/line/pie。"

    ax.set_title(title)
    fig.tight_layout()

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return str(Path(output_path).resolve())


@tool
def excel_summary(file_path: str, sheet_name: str = "") -> str:
    """
    读取 Excel 文件并生成数据分析报告。
    sheet_name: 工作表名称，为空则读取第一个工作表。
    """
    from openpyxl import load_workbook

    wb = load_workbook(file_path, read_only=True, data_only=True)
    ws = wb[sheet_name] if sheet_name else wb.active

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return "Excel 文件为空。"

    # 取前 50 行用于分析（避免 token 过多）
    sample_rows = rows[:50]
    header = [str(c) if c is not None else "" for c in sample_rows[0]]
    data_preview = []
    for row in sample_rows[1:11]:
        data_preview.append(" | ".join(str(c) if c is not None else "" for c in row))

    total_rows = len(rows)
    total_cols = len(header)

    prompt = (
        f"以下是一份 Excel 数据的概览，请生成一份简洁的数据分析报告，"
        f"包括数据规模、字段含义、数据特征和可能的洞察。\n\n"
        f"工作表：{ws.title}\n"
        f"总行数：{total_rows}，总列数：{total_cols}\n"
        f"列名：{', '.join(header)}\n"
        f"前 10 行数据预览：\n" + "\n".join(data_preview)
    )

    wb.close()
    return get_llm().invoke(prompt).content
