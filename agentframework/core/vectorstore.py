"""
Chroma 向量库管理模块

封装 chromadb 原生 API，提供：
- create/get collection
- add_documents: 添加文档（含分块内容 + 元数据）
- similarity_search: 语义检索 Top-K
- 持久化到本地目录

不依赖 langchain-chroma 包，避免版本兼容问题，直接用 chromadb 原生 API。
"""
import hashlib
from pathlib import Path
from typing import List, Optional

import chromadb
from chromadb.config import Settings

from core.embeddings import embed_documents, embed_query

# 向量库持久化目录
_DEFAULT_PERSIST_DIR = str(Path("chroma_db").resolve())


class VectorStore:
    """Chroma 向量库封装"""

    def __init__(
        self,
        collection_name: str = "default",
        persist_dir: str = _DEFAULT_PERSIST_DIR,
    ):
        """
        Args:
            collection_name: 集合名称（不同知识库用不同 collection 隔离）
            persist_dir: 本地持久化目录
        """
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},  # 余弦相似度
        )

    def _make_id(self, text: str, source: str, index: int) -> str:
        """生成唯一文档 ID（基于内容 hash，用于去重）。"""
        raw = f"{source}::{index}::{text[:100]}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        source: str = "",
    ) -> int:
        """
        添加文档到向量库

        Args:
            texts: 文本块列表
            metadatas: 每个文本块的元数据（如来源文件、页码）
            source: 来源标识（用于去重）

        Returns:
            int: 实际添加的文档数量
        """
        if not texts:
            return 0

        ids = [self._make_id(t, source, i) for i, t in enumerate(texts)]

        # 检查已存在的 ID，避免重复添加
        existing = self._collection.get(ids=ids)["ids"]
        new_indices = [i for i, _id in enumerate(ids) if _id not in existing]

        if not new_indices:
            return 0  # 全部已存在

        new_texts = [texts[i] for i in new_indices]
        new_ids = [ids[i] for i in new_indices]
        new_metadatas = (
            [metadatas[i] for i in new_indices] if metadatas else None
        )

        embeddings = embed_documents(new_texts)

        self._collection.add(
            ids=new_ids,
            embeddings=embeddings,
            documents=new_texts,
            metadatas=new_metadatas,
        )
        return len(new_indices)

    def similarity_search(self, query: str, k: int = 5) -> List[dict]:
        """
        语义检索

        Args:
            query: 查询文本
            k: 返回结果数量

        Returns:
            List[dict]: 检索结果，每个含 content、metadata、distance
        """
        if self._collection.count() == 0:
            return []

        query_embedding = embed_query(query)
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(k, self._collection.count()),
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        return [
            {
                "content": doc,
                "metadata": meta,
                "distance": dist,
            }
            for doc, meta, dist in zip(documents, metadatas, distances)
        ]

    def count(self) -> int:
        """返回向量库中的文档数量。"""
        return self._collection.count()

    def clear(self) -> None:
        """清空当前 collection 的所有文档。"""
        ids = self._collection.get()["ids"]
        if ids:
            self._collection.delete(ids=ids)


# 全局默认向量库实例（懒加载）
_default_store: Optional[VectorStore] = None


def get_vector_store(collection_name: str = "default") -> VectorStore:
    """获取全局默认向量库实例。"""
    global _default_store
    if _default_store is None:
        _default_store = VectorStore(collection_name=collection_name)
    return _default_store
