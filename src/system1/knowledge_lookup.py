"""
Knowledge Lookup - RAG retrieval using .md files + vector search.

Sử dụng:
- LlamaIndex để load và index .md files
- EmbeddingClient để encode queries
- PostgreSQL + pgvector để lưu vector store
"""

from __future__ import annotations
import asyncio
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class KnowledgeLookup:
    """
    RAG retrieval cho System 1.
    
    Sử dụng LlamaIndex với:
    - Documents: từ knowledge_base/*.md
    - Embedding: text-embedding-004 (768 dim)
    - Vector store: PostgreSQL + pgvector
    """
    
    def __init__(
        self,
        config: dict,
        embedding_client,
        db_pool=None,
        knowledge_base_dir: str = "knowledge_base",
    ):
        self.config = config
        self.embedding = embedding_client
        self.db_pool = db_pool
        self.knowledge_base_dir = Path(knowledge_base_dir)
        
        self.top_k = config.get("rag_top_k", 3)
        self.similarity_threshold = config.get("rag_similarity_threshold", 0.5)
        self.chunk_size = config.get("rag_chunk_size", 512)
        self.chunk_overlap = config.get("rag_chunk_overlap", 50)
        
        # Lazy init - chỉ build index khi cần
        self._index = None
        self._retriever = None
        self._loaded_doc_count = 0
    
    def _build_index(self):
        """
        Build LlamaIndex từ .md files.
        Cache index trong self._index.
        """
        if not self.knowledge_base_dir.exists():
            logger.warning(
                f"Knowledge base directory not found: {self.knowledge_base_dir}"
            )
            return None
        
        try:
            from llama_index.core import (
                SimpleDirectoryReader,
                VectorStoreIndex,
                Settings,
            )
            from llama_index.core.node_parser import SentenceSplitter
            
            # Configure global settings
            Settings.chunk_size = self.chunk_size
            Settings.chunk_overlap = self.chunk_overlap
            
            # Load documents
            logger.info(f"Loading documents from {self.knowledge_base_dir}")
            documents = SimpleDirectoryReader(
                input_dir=str(self.knowledge_base_dir),
                recursive=True,
                required_exts=[".md"],
            ).load_data()
            
            self._loaded_doc_count = len(documents)
            logger.info(f"Loaded {len(documents)} markdown documents")
            
            if not documents:
                logger.warning("No documents found in knowledge base")
                return None
            
            # Build index
            # Note: vector_store có thể truyền vào để dùng pgvector
            self._index = VectorStoreIndex.from_documents(
                documents=documents,
                embed_model=self._get_llama_embedding_wrapper(),
                show_progress=True,
            )
            
            # Configure retriever
            self._retriever = self._index.as_retriever(
                similarity_top_k=self.top_k,
            )
            
            logger.info(
                f"Knowledge index built: {len(documents)} docs, "
                f"top_k={self.top_k}"
            )
            
            return self._index
        
        except ImportError as e:
            logger.error(f"llama_index not installed: {e}")
            return None
        except Exception as e:
            logger.exception(f"Failed to build knowledge index: {e}")
            return None
    
    def _get_llama_embedding_wrapper(self):
        """Wrap EmbeddingClient thành BaseEmbedding cho LlamaIndex."""
        try:
            from llama_index.core.embeddings import BaseEmbedding
            from llama_index.core.bridge.pydantic import PrivateAttr
            
            class EmbeddingWrapper(BaseEmbedding):
                _client: object = PrivateAttr()
                
                def __init__(self, client):
                    super().__init__()
                    self._client = client
                
                async def _aget_query_embedding(self, query: str):
                    return await self._client.encode(query)

                async def _aget_text_embedding(self, text: str) -> list[float]:
                    return await self._client.encode(text)

                def _get_query_embedding(self, query: str) -> list[float]:
                    return asyncio.run(self._client.encode(query))

                def _get_text_embedding(self, text: str) -> list[float]:
                    return asyncio.run(self._client.encode(text))
            
            return EmbeddingWrapper(self.embedding)
        
        except ImportError:
            logger.warning("llama_index not available, using fallback")
            return None
    
    async def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
    ) -> list[dict]:
        """
        Retrieve top-k documents liên quan.
        
        Args:
            query: Câu hỏi
            top_k: Số lượng kết quả (default: self.top_k)
            
        Returns:
            list of {"text": str, "source": str, "score": float}
        """
        k = top_k or self.top_k
        
        # Lazy build index
        if self._index is None:
            self._build_index()
        
        if self._index is None or self._retriever is None:
            logger.warning("Index not available, returning empty results")
            return []
        
        try:
            # Query retriever
            nodes = self._retriever.retrieve(query)
            
            # Format kết quả
            results = []
            for node in nodes[:k]:
                score = getattr(node, "score", 0.0)
                if score < self.similarity_threshold:
                    continue
                
                # Get source file path
                source = "unknown"
                if hasattr(node, "metadata") and node.metadata:
                    source = node.metadata.get("file_path", source)
                    source = str(source).replace(str(self.knowledge_base_dir) + "/", "")
                
                results.append({
                    "text": node.text,
                    "source": source,
                    "score": float(score),
                    "metadata": node.metadata if hasattr(node, "metadata") else {},
                })
            
            logger.debug(
                f"Retrieved {len(results)} docs for query: {query[:50]}"
            )
            return results
        
        except Exception as e:
            logger.exception(f"RAG retrieval error: {e}")
            return []
    
    async def retrieve_simple(
        self,
        query: str,
        top_k: Optional[int] = None,
    ) -> list[dict]:
        """
        Simplified retrieval - chỉ dùng embedding + cosine similarity
        không qua LlamaIndex (fallback khi LlamaIndex không available).
        """
        k = top_k or self.top_k
        
        # Load all .md files
        if not self.knowledge_base_dir.exists():
            return []
        
        md_files = list(self.knowledge_base_dir.rglob("*.md"))
        if not md_files:
            return []
        
        # Encode query
        query_emb = await self.embedding.encode(query)
        
        # Read và encode từng file
        results = []
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8")
                if not content.strip():
                    continue
                
                # Simple chunking
                chunks = self._simple_chunk(content, self.chunk_size, self.chunk_overlap)
                
                for chunk_idx, chunk in enumerate(chunks):
                    chunk_emb = await self.embedding.encode(chunk)
                    similarity = self._cosine_similarity(query_emb, chunk_emb)
                    
                    if similarity >= self.similarity_threshold:
                        results.append({
                            "text": chunk,
                            "source": f"{md_file.relative_to(self.knowledge_base_dir)}#{chunk_idx}",
                            "score": similarity,
                            "metadata": {},
                        })
            except Exception as e:
                logger.warning(f"Failed to process {md_file}: {e}")
        
        # Sort by score desc
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:k]
    
    def _simple_chunk(
        self,
        text: str,
        chunk_size: int,
        overlap: int,
    ) -> list[str]:
        """Simple text chunking theo paragraphs."""
        paragraphs = text.split("\n\n")
        chunks = []
        current = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if len(current) + len(para) <= chunk_size:
                current += "\n\n" + para if current else para
            else:
                if current:
                    chunks.append(current)
                # Start new chunk with overlap
                current = para
        
        if current:
            chunks.append(current)
        
        return chunks
    
    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Tính cosine similarity giữa 2 vectors."""
        import math
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)
    
    async def add_document(
        self,
        text: str,
        doc_id: str,
        metadata: dict = None,
    ) -> bool:
        """
        Thêm document mới vào index (runtime).
        """
        if self._index is None:
            self._build_index()
        
        if self._index is None:
            logger.warning("Cannot add document - index not available")
            return False
        
        try:
            from llama_index.core import Document
            doc = Document(
                text=text,
                id_=doc_id,
                metadata=metadata or {},
            )
            self._index.insert(doc)
            logger.info(f"Added document {doc_id} to index")
            return True
        except Exception as e:
            logger.exception(f"Failed to add document: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Lấy thống kê về knowledge base."""
        if not self.knowledge_base_dir.exists():
            return {"exists": False}
        
        md_files = list(self.knowledge_base_dir.rglob("*.md"))
        total_size = sum(f.stat().st_size for f in md_files if f.is_file())
        
        return {
            "exists": True,
            "file_count": len(md_files),
            "total_size_bytes": total_size,
            "index_built": self._index is not None,
            "loaded_doc_count": self._loaded_doc_count,
            "top_k": self.top_k,
            "similarity_threshold": self.similarity_threshold,
        }
    
    async def reload(self):
        """Reload index từ .md files."""
        self._index = None
        self._retriever = None
        self._loaded_doc_count = 0
        return self._build_index() is not None


# ============ Builder helper ============

def build_knowledge_lookup(
    embedding_client,
    config: dict = None,
    knowledge_base_dir: str = "knowledge_base",
    db_pool=None,
) -> KnowledgeLookup:
    """
    Build KnowledgeLookup instance.
    
    Args:
        embedding_client: EmbeddingClient instance
        config: optional config dict
        knowledge_base_dir: path to .md knowledge base
        db_pool: optional asyncpg pool for pgvector
    """
    if config is None:
        config = {
            "rag_top_k": 3,
            "rag_similarity_threshold": 0.5,
            "rag_chunk_size": 512,
            "rag_chunk_overlap": 50,
        }
    
    return KnowledgeLookup(
        config=config,
        embedding_client=embedding_client,
        db_pool=db_pool,
        knowledge_base_dir=knowledge_base_dir,
    )
