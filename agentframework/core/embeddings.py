"""
本地 Embeddings 模块

使用 fastembed（Qdrant 出品）加载 bge-small-zh-v1.5 中文 embedding 模型。
- 无需 torch，轻量（首次使用自动下载约 90MB）
- 完全本地运行，文档不发到第三方 API
- 兼容 LangChain 的 Embeddings 接口
"""
from typing import List

from fastembed import TextEmbedding

# 模型名称：BAAI 的中文轻量 embedding 模型
_MODEL_NAME = "BAAI/bge-small-zh-v1.5"

# 懒加载单例：首次调用 embed 时才下载/加载模型
_model: TextEmbedding | None = None


def _get_model() -> TextEmbedding:
    """懒加载 embedding 模型，避免模块导入时即下载。"""
    global _model
    if _model is None:
        _model = TextEmbedding(model_name=_MODEL_NAME)
    return _model


def embed_documents(texts: List[str]) -> List[List[float]]:
    """
    将文本列表向量化

    Args:
        texts: 待向量化的文本列表

    Returns:
        List[List[float]]: 每个文本对应的向量（维度 512）
    """
    model = _get_model()
    embeddings = list(model.embed(texts))
    # 将 np.float32 转换为原生 Python float，兼容 chromadb
    return [[float(x) for x in e] for e in embeddings]


def embed_query(text: str) -> List[float]:
    """
    将单个查询文本向量化

    Args:
        text: 查询文本

    Returns:
        List[float]: 查询向量
    """
    return embed_documents([text])[0]
