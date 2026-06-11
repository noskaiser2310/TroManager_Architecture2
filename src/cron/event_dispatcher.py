"""
Event Dispatcher - Dispatch background events từ Cron vào System 2.
"""

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from ..system2.react_agent import ReActAgent, ReActRequest
from ..user_modeling.services import BehaviorTracker, ActionTypes, ProfileService
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
        self.profile_service: Optional[ProfileService] = None
        self.cron_scheduler = None
        
    def set_dependencies(self, profile_service, cron_scheduler):
        """Tiêm ProfileService và CronScheduler vào sau khi đã khởi tạo."""
        self.profile_service = profile_service
        self.cron_scheduler = cron_scheduler
    
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
            
        # 1.5 Golden Time Delivery Check
        is_delayed_execution = event.data.get("delayed_from_golden_time", False)
        
        if not is_delayed_execution and self.profile_service and self.cron_scheduler:
            profile = await self.profile_service.get_profile(event.tenant_id)
            if profile and profile.personalization_profile:
                active_hours = profile.personalization_profile.get("preferences", {}).get("active_hours", "")
                slots = self._get_active_slots(active_hours)
                
                if slots and not self._is_golden_time(slots):
                    next_time = self._get_next_golden_time(slots)
                    logger.info(f"Golden Time: Not optimal time for tenant {event.tenant_id} (active slots: {slots}). Delaying event to {next_time}")
                    
                    event.data["delayed_from_golden_time"] = True
                    
                    self.cron_scheduler.scheduler.add_job(
                        self.dispatch,
                        trigger='date',
                        run_date=next_time,
                        args=[event],
                        id=f"delayed_{event.event_type}_{event.tenant_id}_{int(datetime.now().timestamp())}"
                    )
                    return f"DELAYED: Scheduled for golden time at {next_time}"
        
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

    def _get_active_slots(self, active_hours: str) -> list[str]:
        """Parse active_hours string into standard slots."""
        if not active_hours:
            return []
        active_hours = active_hours.lower()
        slots = []
        if "sáng" in active_hours: slots.append("sáng")
        if "trưa" in active_hours: slots.append("trưa")
        if "chiều" in active_hours: slots.append("chiều")
        if "tối" in active_hours: slots.append("tối")
        if "nửa đêm" in active_hours or "đêm" in active_hours: slots.append("đêm")
        return slots

    def _is_golden_time(self, slots: list[str]) -> bool:
        """Kiểm tra giờ hiện tại có thuộc khung giờ vàng không."""
        if not slots:
            return True
        
        hour = datetime.now().hour
        current_slot = None
        if 8 <= hour < 12: current_slot = "sáng"
        elif 12 <= hour < 14: current_slot = "trưa"
        elif 14 <= hour < 18: current_slot = "chiều"
        elif 18 <= hour < 22: current_slot = "tối"
        else: current_slot = "đêm"
        
        return current_slot in slots

    def _get_next_golden_time(self, slots: list[str]) -> datetime:
        """Tính toán khung giờ vàng tiếp theo gần nhất."""
        now = datetime.now()
        if not slots:
            return now
        
        slot_starts = {
            "sáng": 8,
            "trưa": 12,
            "chiều": 14,
            "tối": 18,
            "đêm": 22
        }
        
        next_times = []
        for slot in slots:
            start_hour = slot_starts[slot]
            next_time = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
            if next_time <= now:
                next_time += timedelta(days=1)
            next_times.append(next_time)
            
        return min(next_times)


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
