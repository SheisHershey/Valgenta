"""
方向6：知识管理工具（RAG 知识库）

- build_knowledge_base: 加载文件夹中的多格式文档，分块向量化，存入 Chroma
- search_knowledge_base: 从知识库语义检索相关内容
- extract_keywords: 从文档中提取关键词/标签
"""
from pathlib import Path
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.tools import tool

from core.docx_processor import read_docx
from core.vectorstore import get_vector_store
from core.llm import get_llm


def _load_file(file_path: str) -> str:
    """按文件后缀加载文档内容。"""
    suffix = Path(file_path).suffix.lower()
    if suffix == ".docx":
        return read_docx(file_path)
    elif suffix == ".pdf":
        import pdfplumber
        parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                if text.strip():
                    parts.append(text)
        return "\n".join(parts)
    elif suffix in (".txt", ".md"):
        return Path(file_path).read_text(encoding="utf-8")
    else:
        return ""


@tool
def build_knowledge_base(folder_path: str) -> str:
    """
    构建知识库：将指定文件夹中的所有文档（docx/pdf/txt/md）
    分块向量化并存入本地 Chroma 向量库。
    重复内容会自动去重。返回构建结果统计。
    """
    folder = Path(folder_path)
    if not folder.is_dir():
        return f"不是有效的文件夹：{folder_path}"

    supported = {".docx", ".pdf", ".txt", ".md"}
    files = [f for f in folder.rglob("*") if f.suffix.lower() in supported]

    if not files:
        return f"文件夹中没有支持的文档（支持 docx/pdf/txt/md）。"

    # 文本分块器：500 字符一块，重叠 50 字符
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""],
    )

    store = get_vector_store()
    total_added = 0
    file_stats = []

    for f in files:
        try:
            content = _load_file(str(f))
            if not content.strip():
                file_stats.append(f"- {f.name}：内容为空，跳过")
                continue

            chunks = splitter.split_text(content)
            metadatas = [{"source": f.name, "chunk_idx": i} for i in range(len(chunks))]
            added = store.add_documents(chunks, metadatas=metadatas, source=str(f))
            total_added += added
            file_stats.append(f"- {f.name}：{len(chunks)} 块，新增 {added} 块")
        except Exception as e:
            file_stats.append(f"- {f.name}：处理失败 - {e}")

    result = [
        f"## 知识库构建完成",
        f"- 扫描文件：{len(files)} 个",
        f"- 新增向量：{total_added} 块",
        f"- 向量库总量：{store.count()} 块",
        "",
        "### 文件明细",
    ]
    result.extend(file_stats)
    return "\n".join(result)


@tool
def search_knowledge_base(query: str, k: int = 5) -> str:
    """
    从已构建的知识库中语义检索相关内容。
    query: 查询问题；k: 返回结果数量。
    返回检索到的相关文本片段（供 LLM 生成答案使用）。
    """
    store = get_vector_store()
    results = store.similarity_search(query, k=k)

    if not results:
        return "知识库为空或未检索到相关内容，请先调用 build_knowledge_base 构建知识库。"

    parts = [f"## 检索到 {len(results)} 条相关内容\n"]
    for i, r in enumerate(results, 1):
        source = r["metadata"].get("source", "未知") if r["metadata"] else "未知"
        score = 1 - r["distance"]  # 余弦相似度
        parts.append(f"### 片段 {i}（来源：{source}，相关度：{score:.2f}）")
        parts.append(r["content"])
        parts.append("")
    return "\n".join(parts)


@tool
def extract_keywords(text: str, max_keywords: int = 10) -> str:
    """
    从文本中提取关键词/标签。
    text: 文档内容；max_keywords: 最大关键词数量。
    返回关键词列表（逗号分隔）。
    """
    prompt = (
        f"请从以下文本中提取 {max_keywords} 个最核心的关键词或标签，"
        f"用于文档分类和索引。只输出关键词，用逗号分隔，不要解释。\n\n"
        f"文本：\n{text[:3000]}"
    )
    return get_llm().invoke(prompt).content
