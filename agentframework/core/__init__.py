"""
core 包：核心基础设施
- llm: ChatOpenAI 模型实例
- prompts: 提示词模板
- chains: LCEL 链（数据通道）
- docx_processor: Word 文档读写
- embeddings: 本地文本向量化（fastembed）
- vectorstore: Chroma 向量库管理
"""
from core.llm import get_llm
from core.prompts import get_agent_prompt, get_teacher_prompt
from core.chains import build_simple_chain
from core.docx_processor import read_docx, write_docx
from core.embeddings import embed_documents, embed_query
from core.vectorstore import VectorStore, get_vector_store

__all__ = [
    "get_llm",
    "get_agent_prompt",
    "get_teacher_prompt",
    "build_simple_chain",
    "read_docx",
    "write_docx",
    "embed_documents",
    "embed_query",
    "VectorStore",
    "get_vector_store",
]
