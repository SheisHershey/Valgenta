"""
方向5：流程自动化工具

- batch_process: 批量处理文件夹下的所有 docx 文档（统一润色）
- compare_versions: 对比两个版本文档的差异
- email_draft: 根据要点生成商务邮件草稿
"""
import difflib
from pathlib import Path

from langchain_core.tools import tool

from core.docx_processor import read_docx, write_docx
from core.llm import get_llm


@tool
def batch_process(folder_path: str, operation: str = "polish") -> str:
    """
    批量处理文件夹下的所有 .docx 文档。
    operation: polish（润色）/ summarize（总结）/ translate_en（翻译为英文）
    处理后的文件保存到原文件夹下的 processed/ 子目录。
    返回处理结果汇总。
    """
    folder = Path(folder_path)
    if not folder.is_dir():
        return f"不是有效的文件夹：{folder_path}"

    docx_files = list(folder.glob("*.docx"))
    if not docx_files:
        return f"文件夹中没有 .docx 文件。"

    output_dir = folder / "processed"
    output_dir.mkdir(exist_ok=True)

    results = [f"## 批量处理结果（共 {len(docx_files)} 个文件）\n"]
    for f in docx_files:
        try:
            content = read_docx(str(f))
            if operation == "polish":
                prompt = f"请对以下文档进行学术润色，直接输出润色后的全文：\n\n{content}"
                new_content = get_llm().invoke(prompt).content
                out_name = f.stem + "_润色版.docx"
            elif operation == "summarize":
                prompt = f"请用 300 字总结以下文档：\n\n{content}"
                new_content = get_llm().invoke(prompt).content
                out_name = f.stem + "_总结.docx"
            elif operation == "translate_en":
                prompt = f"请将以下文档翻译为英文，直接输出译文：\n\n{content}"
                new_content = get_llm().invoke(prompt).content
                out_name = f.stem + "_EN.docx"
            else:
                results.append(f"- {f.name}：不支持的操作 {operation}")
                continue

            write_docx(str(output_dir / out_name), new_content, title=f.stem)
            results.append(f"- ✅ {f.name} → {out_name}")
        except Exception as e:
            results.append(f"- ❌ {f.name}：处理失败 - {e}")

    results.append(f"\n处理完成，输出目录：{output_dir.resolve()}")
    return "\n".join(results)


@tool
def compare_versions(file_path_a: str, file_path_b: str) -> str:
    """
    对比两个版本文档的内容差异。
    返回差异报告（新增/删除的行）。
    """
    try:
        text_a = read_docx(file_path_a).splitlines()
        text_b = read_docx(file_path_b).splitlines()
    except Exception as e:
        return f"读取文档失败：{e}"

    diff = difflib.unified_diff(
        text_a, text_b,
        fromfile=Path(file_path_a).name,
        tofile=Path(file_path_b).name,
        lineterm="",
    )
    diff_lines = list(diff)
    if not diff_lines:
        return "两个文档内容完全一致，无差异。"

    report = ["## 文档差异报告\n", "```diff"]
    report.extend(diff_lines[:200])  # 限制输出长度
    report.append("```")
    if len(diff_lines) > 200:
        report.append(f"\n（仅显示前 200 行差异，共 {len(diff_lines)} 行）")

    # 统计
    added = sum(1 for l in diff_lines if l.startswith("+") and not l.startswith("+++"))
    removed = sum(1 for l in diff_lines if l.startswith("-") and not l.startswith("---"))
    report.append(f"\n**统计**：新增 {added} 行，删除 {removed} 行")
    return "\n".join(report)


@tool
def email_draft(key_points: str, tone: str = "正式") -> str:
    """
    根据要点生成商务邮件草稿。
    key_points: 邮件要点，用逗号或换行分隔
    tone: 正式 / 友好 / 简洁
    返回完整的邮件草稿（含主题、称呼、正文、落款）。
    """
    prompt = (
        f"请根据以下要点，写一封{tone}风格的商务邮件草稿。"
        f"包含：邮件主题、称呼、正文（分段）、落款。\n\n"
        f"要点：\n{key_points}"
    )
    return get_llm().invoke(prompt).content
