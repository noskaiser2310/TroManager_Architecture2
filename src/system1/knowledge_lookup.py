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
        self.similarity_threshold = config.get("rag_similarity_threshold", 0.5)  # ngưỡng lọc độ liên quan tối thiểu
        self.chunk_size = config.get("rag_chunk_size", 512)
        self.chunk_overlap = config.get("rag_chunk_overlap", 50)
        
        # Lazy init - chỉ build index khi cần
        self._index = None
        self._retriever = None
        self._loaded_doc_count = 0
        self._index_build_attempted = False
        self.persist_dir = Path("config/llama_index_storage")
    
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
                StorageContext,
                load_index_from_storage,
            )
            from llama_index.core.node_parser import SentenceSplitter
            
            # Configure global settings
            Settings.chunk_size = self.chunk_size
            Settings.chunk_overlap = self.chunk_overlap
            
            # Try to load from persisted storage first
            embed_model = self._get_llama_embedding_wrapper()
            if self.persist_dir.exists():
                try:
                    logger.info(f"Attempting to load index from persisted storage: {self.persist_dir}")
                    storage_context = StorageContext.from_defaults(persist_dir=str(self.persist_dir))
                    self._index = load_index_from_storage(
                        storage_context=storage_context,
                        embed_model=embed_model,
                    )
                    self._retriever = self._index.as_retriever(
                        similarity_top_k=self.top_k,
                    )
                    # Count documents by looking at docstore keys
                    self._loaded_doc_count = len(self._index.docstore.docs)
                    logger.info(f"Loaded knowledge index from storage: {self._loaded_doc_count} nodes/docs")
                    return self._index
                except Exception as e:
                    logger.warning(f"Failed to load index from storage: {e}. Rebuilding...")
            
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
                embed_model=embed_model,
                show_progress=True,
            )
            
            # Persist index
            try:
                self.persist_dir.mkdir(parents=True, exist_ok=True)
                self._index.storage_context.persist(persist_dir=str(self.persist_dir))
                logger.info(f"Persisted knowledge index to {self.persist_dir}")
            except Exception as e:
                logger.warning(f"Failed to persist knowledge index: {e}")
            
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

                async def _aget_text_embeddings(self, texts: list[str]) -> list[list[float]]:
                    return await self._client.encode_batch(texts)

                def _get_query_embedding(self, query: str) -> list[float]:
                    return asyncio.run(self._client.encode(query))

                def _get_text_embedding(self, text: str) -> list[float]:
                    return asyncio.run(self._client.encode(text))

                def _get_text_embeddings(self, texts: list[str]) -> list[list[float]]:
                    return asyncio.run(self._client.encode_batch(texts))
            
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
        
        # Lazy build index — chạy trong thread pool để không block event loop
        if self._index is None and not self._index_build_attempted:
            self._index_build_attempted = True
            await asyncio.get_event_loop().run_in_executor(None, self._build_index)
        
        if self._index is None or self._retriever is None:
            logger.warning("Index not available, falling back to retrieve_simple")
            return await self.retrieve_simple(query, top_k=k)
        
        try:
            # Query retriever — SYNC call, phải chạy trong executor
            nodes = await asyncio.get_event_loop().run_in_executor(
                None, self._retriever.retrieve, query
            )
            
            # Format kết quả
            results = []
            for node in nodes[:k]:
                score = getattr(node, "score", 0.0) or 0.0
                # LlamaIndex đôi khi trả score = None hoặc âm khi dùng in-memory index
                # Nếu score == 0 (không có score) vẫn include để không bỏ sót kết quả
                if score > 0 and score < self.similarity_threshold:
                    continue
                
                # Get source file path — fix Windows path separator
                source = "unknown"
                if hasattr(node, "metadata") and node.metadata:
                    source = node.metadata.get("file_path", source)
                    kb_prefix = str(self.knowledge_base_dir)
                    source_str = str(source)
                    # Strip prefix (handle both / and \ separators)
                    for sep in ["/", "\\"]:
                        prefix = kb_prefix + sep
                        if source_str.startswith(prefix):
                            source_str = source_str[len(prefix):]
                            break
                    source = source_str
                
                results.append({
                    "text": node.text,
                    "source": source,
                    "score": float(score),
                    "metadata": node.metadata if hasattr(node, "metadata") else {},
                })
            
            logger.debug(
                f"Retrieved {len(results)}/{len(nodes)} docs for query: {query[:50]}, "
                f"threshold={self.similarity_threshold}"
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
        Nếu API embedding bị lỗi hoặc hết quota, tự động fallback sang tìm kiếm theo từ khóa (Keyword/TF-IDF).
        """
        k = top_k or self.top_k
        
        # Load all .md files
        if not self.knowledge_base_dir.exists():
            return []
        
        md_files = list(self.knowledge_base_dir.rglob("*.md"))
        if not md_files:
            return []
        
        # 1. Thử dùng Embedding-based similarity
        try:
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
            
            if results:
                # Sort by score desc
                results.sort(key=lambda x: x["score"], reverse=True)
                return results[:k]
        except Exception as e:
            logger.warning(f"Embedding retrieval failed (likely limit/quota): {e}. Falling back to keyword search.")
        
        # 2. Fallback: Keyword-based matching (đảm bảo hoạt động kể cả khi API sập)
        import re
        query_words = set(re.findall(r"\w+", query.lower()))
        if not query_words:
            return []
            
        results = []
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8")
                if not content.strip():
                    continue
                
                chunks = self._simple_chunk(content, self.chunk_size, self.chunk_overlap)
                for chunk_idx, chunk in enumerate(chunks):
                    chunk_lower = chunk.lower()
                    match_count = 0
                    for word in query_words:
                        if word in chunk_lower:
                            if word.isdigit() or len(word) > 2:
                                match_count += 2
                            else:
                                match_count += 1
                                
                    if match_count > 0:
                        score = match_count / (len(query_words) + 5)
                        file_name_lower = md_file.name.lower()
                        for word in query_words:
                            if word in file_name_lower:
                                score += 0.3
                        results.append({
                            "text": chunk,
                            "source": f"{md_file.relative_to(self.knowledge_base_dir)}#{chunk_idx}",
                            "score": min(score, 1.0),
                            "metadata": {},
                        })
            except Exception as ex:
                logger.warning(f"Keyword search failed for {md_file}: {ex}")
                
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
        """Reload index từ .md files — chạy trong thread pool."""
        self._index = None
        self._retriever = None
        self._loaded_doc_count = 0
        self._index_build_attempted = False
        
        # Delete persisted index directory to force rebuild
        import shutil
        if self.persist_dir.exists():
            try:
                shutil.rmtree(self.persist_dir)
                logger.info(f"Cleared persisted index at {self.persist_dir} to force reload")
            except Exception as e:
                logger.warning(f"Failed to clear persisted index: {e}")
                
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._build_index)
        return self._index is not None

    async def warm_up(self):
        """Pre-build index khi khởi động server — chạy trong thread pool."""
        if self._index is not None:
            return  # Đã build rồi
        logger.info("[KnowledgeLookup] Pre-warming RAG index...")
        self._index_build_attempted = True
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._build_index)
        if self._index is not None:
            logger.info(f"[KnowledgeLookup] RAG index ready ({self._loaded_doc_count} docs)")
        else:
            logger.warning("[KnowledgeLookup] RAG index build failed — will use fallback")


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
            "rag_similarity_threshold": 0.5,  # ngưỡng lọc kết quả liên quan
            "rag_chunk_size": 512,
            "rag_chunk_overlap": 50,
        }
    
    return KnowledgeLookup(
        config=config,
        embedding_client=embedding_client,
        db_pool=db_pool,
        knowledge_base_dir=knowledge_base_dir,
    )
