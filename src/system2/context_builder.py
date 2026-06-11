"""
Context Builder - Xây dựng context cho System 2 từ User Modeling Layer.
"""

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Optional

from ..user_modeling.services import (
    ProfileService,
    UserProfile,
    BehaviorTracker,
    BehaviorSummary,
    MemoryManager,
)

logger = logging.getLogger(__name__)


@dataclass
class AgentContext:
    """Context đầy đủ cho Agent."""
    tenant_id: int
    profile: Optional[UserProfile]
    behavior: Optional[BehaviorSummary]
    memories: list[dict] = field(default_factory=list)
    
    def has_personalization(self) -> bool:
        """Check có personalization data không."""
        return bool(self.profile and (self.memories or self.behavior))
    
    def behavior_summary_text(self) -> str:
        """Format behavior summary thành text cho prompt."""
        if not self.behavior:
            return "Chưa có dữ liệu hành vi"
        
        b = self.behavior
        return f"""- Thanh toán trễ: {b.late_payment_count} lần
- Thanh toán đúng hạn: {b.on_time_payment_count} lần
- Yêu cầu sửa chữa: {b.maintenance_count} lần
- Khiếu nại tiếng ồn: {b.noise_complaint_count} lần
- Trung bình trễ: {b.avg_payment_delay_days:.1f} ngày
- Tương tác gần nhất: {b.last_interaction or 'N/A'}"""


class ContextBuilder:
    """
    Builder xây dựng context cho Agent.
    
    Pull data từ:
    - ProfileService (user_profiles)
    - BehaviorTracker (behavior_logs aggregation)
    - MemoryManager (user_embeddings)
    """
    
    def __init__(
        self,
        profile_service: ProfileService,
        behavior_tracker: BehaviorTracker,
        memory_manager: MemoryManager,
    ):
        self.profiles = profile_service
        self.behaviors = behavior_tracker
        self.memories = memory_manager
    
    async def build(
        self,
        tenant_id: int,
        query: str,
        behavior_days: int = 90,
        top_k_memories: int = 3,
    ) -> AgentContext:
        """
        Build full context cho một request.
        Trả về AgentContext rỗng nếu tenant không tồn tại hoặc có lỗi.
        """
        profile = None
        behavior = None
        relevant_memories = []

        try:
            profile = await self.profiles.get_profile(tenant_id)
            if not profile:
                logger.warning(f"No profile found for tenant {tenant_id}")
        except Exception as e:
            logger.exception(f"Profile fetch failed for tenant {tenant_id}: {e}")

        try:
            behavior = await self.behaviors.get_summary(tenant_id, days=behavior_days)
        except Exception as e:
            logger.exception(f"Behavior summary failed for tenant {tenant_id}: {e}")

        try:
            if profile:
                relevant_memories = await self.memories.search_memories(
                    tenant_id=tenant_id,
                    query_text=query,
                    top_k=top_k_memories,
                )
        except Exception as e:
            logger.exception(f"Memory search failed for tenant {tenant_id}: {e}")

        return AgentContext(
            tenant_id=tenant_id,
            profile=profile,
            behavior=behavior,
            memories=relevant_memories,
        )
