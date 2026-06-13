"""
System 1 - Fast Layer
Xử lý câu hỏi đơn giản với Semantic Cache + RAG + Gemini Flash.
"""

from __future__ import annotations
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ..user_modeling.profile_service import ProfileService
from .semantic_cache import SemanticCache
from .knowledge_lookup import KnowledgeLookup
from ..notifications.metrics import System1Metrics

logger = logging.getLogger(__name__)


@dataclass
class System1Request:
    """Request đầu vào cho System 1."""
    query: str
    tenant_id: Optional[int] = None
    skip_cache: bool = False
    history_context: str = ""  # Formatted history từ ConversationMemory


@dataclass
class System1Response:
    """Response từ System 1."""
    answer: str
    confidence: float
    source: str  # "cache", "rag", "fallback"
    latency_ms: int
    tokens_used: int = 0
    sources: list[str] = field(default_factory=list)
    should_fallback: bool = False
    fallback_reason: Optional[str] = None


class FastLayer:
    """
    System 1 - xử lý nhanh các câu hỏi FAQ và tra cứu đơn giản.
    
    Pipeline:
    1. Embedding query
    2. Cache lookup (cosine similarity > 0.9)
    3. Nếu miss → RAG retrieval
    4. LLM generation (Gemini Flash)
    5. Validate confidence → fallback nếu thấp
    """
    
    def __init__(
        self,
        config: dict,
        semantic_cache: SemanticCache,
        knowledge_lookup: KnowledgeLookup,
        profile_service: ProfileService,
        llm_client,  # Gemini Flash client
        embedding_model,  # nomic-embed-text
    ):
        self.config = config
        self.cache = semantic_cache
        self.knowledge = knowledge_lookup
        self.profiles = profile_service
        self.llm = llm_client
        self.embedding = embedding_model
        
        self.confidence_threshold = config.get("confidence_threshold", 0.7)
        self.cache_threshold = config.get("cache_similarity_threshold", 0.9)
        self.rag_top_k = config.get("rag_top_k", 3)
        
        self.metrics = System1Metrics()

        # Load prompt template một lần khi khởi tạo (absolute path giống react_agent.py)
        # Tránh đọc file mỗi request và crash nếu CWD không phải project root
        prompt_path = (
            Path(__file__).resolve().parent.parent.parent
            / "config" / "prompts" / "system1_prompt.txt"
        )
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                self._system_prompt_template = f.read()
        except FileNotFoundError:
            logger.error(f"System 1 prompt file not found: {prompt_path}")
            self._system_prompt_template = (
                "Query: {query}\nContext: {contexts}\n"
                'Respond in JSON: {{"answer": "...", "confidence": 0.5}}'
            )
    
    async def process(self, request: System1Request) -> System1Response:
        """
        Xử lý request qua pipeline System 1.
        """
        start_time = time.time()
        self.metrics.total_requests += 1
        
        try:
            # Step 1: Embedding
            query_embedding = None
            try:
                import asyncio
                query_embedding = await asyncio.wait_for(
                    self._get_embedding(request.query),
                    timeout=self.timeout
                )
            except Exception as emb_err:
                logger.warning(f"Failed to generate query embedding: {emb_err}. Skipping semantic cache.")
            
            # Step 2: Profile context (optional cho System 1)
            profile = None
            if request.tenant_id:
                profile = await self.profiles.get_profile(request.tenant_id)
            
            # Step 3: Cache lookup
            if query_embedding is not None and not request.skip_cache:
                cached = await self.cache.lookup(
                    query_embedding,
                    threshold=self.cache_threshold,
                )
                if cached:
                    self.metrics.cache_hits += 1
                    latency = int((time.time() - start_time) * 1000)
                    logger.info(f"System 1 cache hit for query: {request.query[:50]}")
                    return System1Response(
                        answer=cached.response_text,
                        confidence=cached.similarity,
                        source="cache",
                        latency_ms=latency,
                        sources=[cached.query_text],
                        should_fallback=False,
                    )
                self.metrics.cache_misses += 1
            
            # Step 4: RAG retrieval
            contexts = await self.knowledge.retrieve(
                request.query,
                top_k=self.rag_top_k,
                query_embedding=query_embedding,
            )
            
            if not contexts:
                # No knowledge found - fallback
                self.metrics.fallbacks_to_system2 += 1
                latency = int((time.time() - start_time) * 1000)
                return System1Response(
                    answer="Xin lỗi, tôi không tìm thấy thông tin phù hợp.",
                    confidence=0.0,
                    source="fallback",
                    latency_ms=latency,
                    should_fallback=True,
                    fallback_reason="no_knowledge_found",
                )
            
            # Truncate history_context to avoid context overflow in System 1
            history = request.history_context
            if history and len(history) > 2000:
                history = "...[truncated]...\n" + history[-2000:]
                
            # Step 5: LLM generation
            response = await self._generate(
                query=request.query,
                contexts=contexts,
                profile=profile,
                history_context=history,
            )
            
            # Step 6: Confidence check
            if response["confidence"] < self.confidence_threshold:
                self.metrics.fallbacks_to_system2 += 1
                latency = int((time.time() - start_time) * 1000)
                return System1Response(
                    answer=response["answer"],
                    confidence=response["confidence"],
                    source="rag",
                    latency_ms=latency,
                    tokens_used=response.get("tokens_used", 0),
                    sources=[c["source"] for c in contexts],
                    should_fallback=True,
                    fallback_reason="low_confidence",
                )
            
            # Step 7: Save to cache (async, don't block)
            if response["confidence"] > 0.85 and query_embedding is not None:
                await self.cache.save(
                    query=request.query,
                    query_embedding=query_embedding,
                    response=response["answer"],
                )
            
            self.metrics.rag_responses += 1
            latency = int((time.time() - start_time) * 1000)
            self.metrics.avg_latency_ms = (
                (self.metrics.avg_latency_ms * (self.metrics.rag_responses - 1) + latency)
                / self.metrics.rag_responses
            )
            
            return System1Response(
                answer=response["answer"],
                confidence=response["confidence"],
                source="rag",
                latency_ms=latency,
                tokens_used=response.get("tokens_used", 0),
                sources=[c["source"] for c in contexts],
                should_fallback=False,
            )
        
        except Exception as e:
            logger.exception(f"System 1 error: {e}")
            latency = int((time.time() - start_time) * 1000)
            return System1Response(
                answer="Hệ thống đang gặp sự cố, vui lòng thử lại sau.",
                confidence=0.0,
                source="error",
                latency_ms=latency,
                should_fallback=True,
                fallback_reason=f"error: {str(e)}",
            )
    
    async def _get_embedding(self, text: str) -> list[float]:
        """Generate embedding vector."""
        return await self.embedding.encode(text)
    
    async def _generate(
        self,
        query: str,
        contexts: list[dict],
        profile: Optional[dict],
        history_context: str = "",
    ) -> dict:
        """Generate response using Gemini Flash."""
        import json
        
        # Build prompt
        prompt = self._build_prompt(query, contexts, profile, history_context)
        
        # Call LLM
        messages = [{"role": "user", "content": prompt}]
        response = await self.llm.generate(
            messages=messages,
            response_format={"type": "json_object"},
        )
        
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
            
        try:
            parsed = json.loads(content.strip())
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM JSON in fast_layer: {content}")
            parsed = {}
        
        if not parsed or "answer" not in parsed:
            parsed = {
                "answer": response.content,
                "confidence": 0.5,
                "sources": [],
            }
            
        try:
            parsed["confidence"] = float(parsed.get("confidence", 0.5))
        except (ValueError, TypeError):
            parsed["confidence"] = 0.5
            
        parsed["tokens_used"] = response.total_tokens
        return parsed

    
    def _build_prompt(
        self,
        query: str,
        contexts: list[dict],
        profile: Optional[dict],
        history_context: str = "",
    ) -> str:
        """Build prompt cho System 1 (dùng template đã load sẵn từ __init__)."""
        context_text = "\n\n".join([
            f"[Source: {c['source']}]\n{c['text']}"
            for c in contexts
        ])
        
        # Tone adjustment
        tone = "professional"
        profile_data = "(Không có thông tin cá nhân)"
        tenant_name = "khách"
        
        if profile:
            tone = getattr(profile, "tone_preference", "professional")
            tenant_name = getattr(profile, "full_name", "khách")
            
            # Serialize profile data for LLM
            profile_dict = {}
            if hasattr(profile, "to_dict"):
                profile_dict = profile.to_dict()
            elif isinstance(profile, dict):
                profile_dict = profile
                
            # Filter useful info
            useful_info = {
                "Họ tên": profile_dict.get("full_name"),
                "SĐT": profile_dict.get("phone_number"),
                "Phòng": profile_dict.get("room_id") or profile_dict.get("room_number"),
                "Ngày bắt đầu thuê": profile_dict.get("lease_start"),
                "Ngày hết hạn": profile_dict.get("lease_end")
            }
            # Remove None values
            useful_info = {k: v for k, v in useful_info.items() if v}
            if useful_info:
                profile_data = "\n".join([f"- {k}: {v}" for k, v in useful_info.items()])
        
        return self._system_prompt_template.format(
            tone=tone,
            query=query,
            contexts=context_text,
            profile_data=profile_data,
            tenant_name=tenant_name,
            history_context=history_context or "(Không có lịch sử hội thoại trước đó)",
        )


# ============ Factory ============

def create_fast_layer(config: dict, dependencies: dict) -> FastLayer:
    """Factory function tạo FastLayer với dependencies."""
    return FastLayer(
        config=config,
        semantic_cache=dependencies["semantic_cache"],
        knowledge_lookup=dependencies["knowledge_lookup"],
        profile_service=dependencies["profile_service"],
        llm_client=dependencies["flash_llm"],
        embedding_model=dependencies["embedding_model"],
    )
