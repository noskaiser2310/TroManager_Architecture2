"""
Event Dispatcher - Dispatch background events từ Cron vào System 2.
"""

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..system2.react_agent import ReActAgent, ReActRequest
from ..user_modeling.services import BehaviorTracker, ActionTypes
from ..notifications.metrics import ProactiveMetrics

logger = logging.getLogger(__name__)


@dataclass
class BackgroundEvent:
    """Event từ background system."""
    event_type: str  # invoice_overdue, contract_expiring, ...
    tenant_id: int
    data: dict = field(default_factory=dict)
    instruction: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


class EventDispatcher:
    """
    Dispatch background events tới System 2.
    
    Luồng:
    1. Nhận event từ cron detector
    2. Build context cho tenant
    3. Chọn tools dựa trên event type
    4. Chạy ReAct loop
    5. Log behavior
    """
    
    EVENT_INTENT_MAP = {
        "invoice_overdue": "background_event_invoice_overdue",
        "payment_due_soon": "background_event_invoice_overdue",
        "contract_expiring": "background_event_contract_expiring",
        "maintenance_reminder": "background_event_maintenance",
        "birthday_greeting": "background_event_birthday",
        "welcome_message": "background_event_welcome",
        "room_transfer_offer": "room_recommendation",
    }
    
    def __init__(
        self,
        react_agent: ReActAgent,
        behavior_tracker: BehaviorTracker,
        tool_registry,
    ):
        self.agent = react_agent
        self.behaviors = behavior_tracker
        self.tools = tool_registry
        
        self.metrics = ProactiveMetrics()
        self.anti_spam = AntiSpamGuard(behavior_tracker, max_per_week=2)
    
    async def dispatch(self, event: BackgroundEvent) -> str:
        """
        Dispatch một background event.
        
        Returns:
            Response từ ReAct Agent
        """
        logger.info(
            f"Dispatching event: type={event.event_type}, "
            f"tenant={event.tenant_id}, data={event.data}"
        )
        
        # 1. Anti-spam check
        can_send = await self.anti_spam.can_send(event.tenant_id, event.event_type)
        if not can_send:
            logger.info(f"Anti-spam: skip event for tenant {event.tenant_id}")
            return "SKIPPED: anti-spam protection"
        
        # 2. Map event to intent
        intent = self.EVENT_INTENT_MAP.get(event.event_type, "general_chat")
        tools = self.tools.get_for_intent(intent)
        
        # 3. Build instruction
        instruction = event.instruction or self._default_instruction(event)
        
        # 4. Run ReAct
        request = ReActRequest(
            query=instruction,
            tenant_id=event.tenant_id,
            intent=intent,
            tools=tools,
        )
        
        try:
            response = await self.agent.run(request)
            
            # 5. Log behavior
            await self.behaviors.log(
                tenant_id=event.tenant_id,
                action_type=f"auto_{event.event_type}",
                description=response.answer[:200],
                metadata={"event_data": event.data},
            )
            
            # Update metrics
            self.metrics.events_dispatched_today += 1
            self.metrics.events_by_type[event.event_type] = (
                self.metrics.events_by_type.get(event.event_type, 0) + 1
            )
            
            return response.answer
        
        except Exception as e:
            logger.exception(f"Event dispatch error: {e}")
            return f"ERROR: {str(e)}"
    
    def _default_instruction(self, event: BackgroundEvent) -> str:
        """Generate default instruction nếu không có."""
        return f"Xử lý sự kiện {event.event_type} cho tenant {event.tenant_id}. Data: {event.data}"


class AntiSpamGuard:
    """Bảo vệ chống spam notifications."""
    
    def __init__(self, behavior_tracker: BehaviorTracker, max_per_week: int = 2):
        self.behaviors = behavior_tracker
        self.max_per_week = max_per_week
    
    async def can_send(self, tenant_id: int, event_type: str) -> bool:
        """Check có nên gửi event cho tenant không."""
        result = await self.behaviors.get_anti_spam_check(
            tenant_id=tenant_id,
            max_per_week=self.max_per_week,
        )
        return result["can_send"]
