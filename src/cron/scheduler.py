"""
Cron Scheduler - Setup scheduled jobs cho proactive events.

Mỗi job query DB để tìm events cần xử lý, sau đó dispatch qua EventDispatcher.
EventDispatcher sẽ:
1. Anti-spam check
2. Map event → intent
3. Chạy ReAct Agent với tools phù hợp
4. Log behavior
"""

from __future__ import annotations
import logging
from datetime import datetime, date
from typing import Optional
import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .event_dispatcher import EventDispatcher, BackgroundEvent
from ..core import parse_llm_json

logger = logging.getLogger(__name__)


class CronScheduler:
    """
    APScheduler wrapper cho TroManager.

    Setup các job:
    - check_invoice_overdue: Hàng ngày 9h
    - check_payment_due_soon: Hàng ngày 8h
    - check_contract_expiring: Ngày 1 hàng tháng 10h
    - check_maintenance_reminder: Hàng tuần
    - check_birthdays: Hàng ngày 7h
    - persona_optimizer_daily: Hàng ngày 23h (tổng hợp behavior thành memories)
    """

    def __init__(
        self,
        event_dispatcher: EventDispatcher,
        config: Optional[dict] = None,
        db_pool=None,
        profile_service=None,
        behavior_tracker=None,
        memory_manager=None,
        llm_client=None,
        conversation_memory=None,
        persona_optimizer=None,
    ):
        self.dispatcher = event_dispatcher
        self.config = config or {}
        self.db_pool = db_pool
        self.profile_service = profile_service
        self.behavior_tracker = behavior_tracker
        self.memory_manager = memory_manager
        self.llm_client = llm_client
        self.conversation_memory = conversation_memory
        self.persona_optimizer = persona_optimizer
        self.scheduler = AsyncIOScheduler()
        self._pending_persona: dict[int, asyncio.Task] = {}
        self._setup_jobs()

    def _setup_jobs(self):
        """Setup tất cả scheduled jobs."""
        
        cron_config = self.config.get("cron", {}).get("rules", {})
        
        def parse_time(time_str: str, default_h: int, default_m: int):
            if not time_str:
                return default_h, default_m
            try:
                h, m = time_str.split(":")
                return int(h), int(m)
            except Exception:
                return default_h, default_m

        # Invoice overdue check
        h, m = parse_time(cron_config.get("invoice_overdue", {}).get("check_time"), 9, 0)
        self.scheduler.add_job(
            self._check_invoice_overdue,
            CronTrigger(hour=h, minute=m),
            id="invoice_overdue_check",
            replace_existing=True,
        )

        # Payment due soon
        h, m = parse_time(cron_config.get("payment_due_soon", {}).get("check_time"), 8, 0)
        self.scheduler.add_job(
            self._check_payment_due_soon,
            CronTrigger(hour=h, minute=m),
            id="payment_due_check",
            replace_existing=True,
        )

        # Contract expiring
        h, m = parse_time(cron_config.get("contract_expiring", {}).get("check_time"), 10, 0)
        day = cron_config.get("contract_expiring", {}).get("check_day", 1)
        self.scheduler.add_job(
            self._check_contract_expiring,
            CronTrigger(day=day, hour=h, minute=m),
            id="contract_expiring_check",
            replace_existing=True,
        )

        # Maintenance reminder
        h, m = parse_time(cron_config.get("maintenance_reminder", {}).get("check_time"), 8, 0)
        dow = cron_config.get("maintenance_reminder", {}).get("check_day_of_week", "mon")
        self.scheduler.add_job(
            self._check_maintenance_reminder,
            CronTrigger(day_of_week=dow, hour=h, minute=m),
            id="maintenance_reminder_check",
            replace_existing=True,
        )

        # Birthday check
        h, m = parse_time(cron_config.get("birthday_greeting", {}).get("check_time"), 7, 0)
        self.scheduler.add_job(
            self._check_birthdays,
            CronTrigger(hour=h, minute=m),
            id="birthday_check",
            replace_existing=True,
        )

        # Persona Optimizer - KHÔNG chạy daily batch (tốn token).
        # Chỉ trigger per-tenant sau 5h kể từ tin nhắn cuối.
        # Xem schedule_persona_update() để biết chi tiết.

        # Conversation cleanup - daily 02:00 (xóa turn cũ hơn 30 ngày)
        if self.conversation_memory:
            self.scheduler.add_job(
                self._conversation_cleanup,
                CronTrigger(hour=2, minute=0),
                id="conversation_cleanup",
                replace_existing=True,
            )
            logger.info("Conversation cleanup job enabled")
        else:
            logger.warning("Conversation cleanup job disabled (missing conversation_memory)")

        logger.info("Scheduled jobs configured")

    def schedule_persona_update(self, tenant_id: int, delay_seconds: int = 18000):
        """
        Schedule persona optimization for a tenant after a cooldown period.
        
        Hủy lịch cũ nếu có, đặt lịch mới sau delay_seconds kể từ tin nhắn cuối.
        Mặc định 18000s = 5h. Chỉ optimize tenant cụ thể để tiết kiệm token.
        """
        existing = self._pending_persona.pop(tenant_id, None)
        if existing and not existing.done():
            existing.cancel()
            logger.info(f"[Persona] Cancelled pending update for tenant {tenant_id} (new message)")

        async def _delayed_optimize():
            try:
                await asyncio.sleep(delay_seconds)
                logger.info(f"[Persona] Running delayed optimization for tenant {tenant_id}")
                if self.persona_optimizer:
                    await self.persona_optimizer.optimize_tenant_profile(tenant_id)
            except asyncio.CancelledError:
                logger.info(f"[Persona] Delayed update cancelled for tenant {tenant_id} (new message arrived)")
            except Exception as e:
                logger.warning(f"[Persona] Delayed update failed for tenant {tenant_id}: {e}")
            finally:
                self._pending_persona.pop(tenant_id, None)

        self._pending_persona[tenant_id] = asyncio.create_task(_delayed_optimize())
        logger.info(f"[Persona] Scheduled update for tenant {tenant_id} in {delay_seconds}s")

    def start(self):
        """Start scheduler."""
        self.scheduler.start()
        logger.info("Cron scheduler started")

    def shutdown(self):
        """Shutdown scheduler."""
        self.scheduler.shutdown()
        logger.info("Cron scheduler stopped")

    # ============ Job handlers ============

    async def _check_invoice_overdue(self):
        """
        Check invoices quá hạn và dispatch reminder events.

        Strategy: chỉ gửi ở mốc 1, 3, 7 ngày quá hạn (tránh spam).
        Anti-spam guard ở EventDispatcher sẽ filter tiếp.
        """
        logger.info("[CRON] Checking overdue invoices...")
        if not self.db_pool:
            logger.warning("DB pool not set, skipping")
            return

        sql = """
        SELECT invoice_id, tenant_id, full_name, total_amount,
               days_overdue, room_number
        FROM v_overdue_invoices
        WHERE days_overdue IN (1, 3, 7, 14)
        """

        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(sql)

            logger.info(f"[CRON] Found {len(rows)} overdue invoices to notify")

            for row in rows:
                days = row["days_overdue"]
                # Tone theo mức độ trễ
                if days >= 7:
                    tone = "strict"
                elif days >= 3:
                    tone = "firm"
                else:
                    tone = "friendly"

                event = BackgroundEvent(
                    event_type="invoice_overdue",
                    tenant_id=row["tenant_id"],
                    data={
                        "invoice_id": row["invoice_id"],
                        "amount": float(row["total_amount"]),
                        "days_overdue": days,
                        "tone": tone,
                        "room_number": row["room_number"],
                    },
                    instruction=(
                        f"Nhac khach thue {row['full_name']} (phong {row['room_number']}) "
                        f"dong hoa don {float(row['total_amount']):,.0f}d "
                        f"qua han {days} ngay. Su dung tone giong {tone}."
                    ),
                )
                await self.dispatcher.dispatch(event)

        except Exception as e:
            logger.exception(f"[CRON] _check_invoice_overdue error: {e}")

    async def _check_payment_due_soon(self):
        """
        Check invoices sắp đến hạn (trong 3 ngày tới) để nhắc trước.
        """
        logger.info("[CRON] Checking payment due soon...")
        if not self.db_pool:
            logger.warning("DB pool not set, skipping")
            return

        sql = """
        SELECT invoice_id, tenant_id, full_name, total_amount,
               days_until_due, room_number
        FROM v_payment_due_soon
        WHERE days_until_due IN (3, 1, 0)
        """

        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(sql)

            logger.info(f"[CRON] Found {len(rows)} invoices due soon")

            for row in rows:
                days_until = row["days_until_due"]
                if days_until == 0:
                    message = "den han hom nay"
                else:
                    message = f"se den han trong {days_until} ngay"

                event = BackgroundEvent(
                    event_type="payment_due_soon",
                    tenant_id=row["tenant_id"],
                    data={
                        "invoice_id": row["invoice_id"],
                        "amount": float(row["total_amount"]),
                        "days_until_due": days_until,
                        "room_number": row["room_number"],
                    },
                    instruction=(
                        f"Nhac khach {row['full_name']} (phong {row['room_number']}) "
                        f"hoa don {float(row['total_amount']):,.0f}d {message}."
                    ),
                )
                await self.dispatcher.dispatch(event)

        except Exception as e:
            logger.exception(f"[CRON] _check_payment_due_soon error: {e}")

    async def _check_contract_expiring(self):
        """
        Check hợp đồng sắp hết hạn (trong 30 ngày tới).
        Nhắc nhở ở các mốc 30, 14, 7, 1 ngày trước.
        """
        logger.info("[CRON] Checking expiring contracts...")
        if not self.db_pool:
            logger.warning("DB pool not set, skipping")
            return

        sql = """
        SELECT contract_id, tenant_id, full_name, phone_number,
               end_date, days_until_expiry, room_number, monthly_rent
        FROM v_expiring_contracts
        WHERE days_until_expiry IN (30, 14, 7, 1)
        """

        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(sql)

            logger.info(f"[CRON] Found {len(rows)} contracts expiring soon")

            for row in rows:
                days_left = row["days_until_expiry"]
                event = BackgroundEvent(
                    event_type="contract_expiring",
                    tenant_id=row["tenant_id"],
                    data={
                        "contract_id": row["contract_id"],
                        "end_date": row["end_date"].isoformat(),
                        "days_until_expiry": days_left,
                        "room_number": row["room_number"],
                        "monthly_rent": float(row["monthly_rent"]),
                    },
                    instruction=(
                        f"Thong bao cho khach {row['full_name']} (phong {row['room_number']}) "
                        f"hop dong sap het han trong {days_left} ngay (ngay {row['end_date']}). "
                        f"Goi y gia han hoac chuyen phong neu can."
                    ),
                )
                await self.dispatcher.dispatch(event)

        except Exception as e:
            logger.exception(f"[CRON] _check_contract_expiring error: {e}")

    async def _check_maintenance_reminder(self):
        """
        Check tickets maintenance đang mở quá lâu cần follow-up.
        """
        logger.info("[CRON] Checking maintenance reminders...")
        if not self.db_pool:
            logger.warning("DB pool not set, skipping")
            return

        sql = """
        SELECT ticket_id, ticket_code, tenant_id, full_name, phone_number,
               issue_category, priority, title, days_open
        FROM v_open_maintenance_tickets
        WHERE
            (priority = 'urgent' AND days_open >= 1)
            OR (priority = 'high' AND days_open >= 2)
            OR (priority = 'normal' AND days_open >= 5)
            OR (priority = 'low' AND days_open >= 7)
        """

        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(sql)

            logger.info(f"[CRON] Found {len(rows)} maintenance tickets needing follow-up")

            for row in rows:
                event = BackgroundEvent(
                    event_type="maintenance_reminder",
                    tenant_id=row["tenant_id"],
                    data={
                        "ticket_id": row["ticket_id"],
                        "ticket_code": row["ticket_code"],
                        "category": row["issue_category"],
                        "priority": row["priority"],
                        "title": row["title"],
                        "days_open": row["days_open"],
                    },
                    instruction=(
                        f"Theo doi ticket bao tri {row['ticket_code']} ({row['issue_category']}, "
                        f"muc do {row['priority']}) mo {row['days_open']} ngay chua xong. "
                        f"Lien he tho va thong bao lai cho khach {row['full_name']}."
                    ),
                )
                await self.dispatcher.dispatch(event)

        except Exception as e:
            logger.exception(f"[CRON] _check_maintenance_reminder error: {e}")

    async def _check_birthdays(self):
        """
        Check sinh nhật khách thuê trong 7 ngày tới và gửi lời chúc.
        """
        logger.info("[CRON] Checking upcoming birthdays...")
        if not self.db_pool:
            logger.warning("DB pool not set, skipping")
            return

        sql = """
        SELECT tenant_id, full_name, zalo_id, phone_number,
               birthday, days_until_birthday
        FROM v_upcoming_birthdays
        WHERE days_until_birthday IN (0, 1, 3)
        """

        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(sql)

            logger.info(f"[CRON] Found {len(rows)} upcoming birthdays")

            for row in rows:
                days = row["days_until_birthday"]
                event = BackgroundEvent(
                    event_type="birthday_greeting",
                    tenant_id=row["tenant_id"],
                    data={
                        "full_name": row["full_name"],
                        "days_until_birthday": days,
                        "is_today": days == 0,
                    },
                    instruction=(
                        f"Gui loi chuc sinh nhat cho khach {row['full_name']}. "
                        + ("Hom nay la sinh nhat." if days == 0
                           else f"Sinh nhat trong {days} ngay.")
                        + " Dung tone am ap, than thien."
                    ),
                )
                await self.dispatcher.dispatch(event)

        except Exception as e:
            logger.exception(f"[CRON] _check_birthdays error: {e}")

    async def _persona_optimizer_daily(self):
        """
        Persona Optimizer - Cuối mỗi ngày, tổng hợp behavior logs của mỗi tenant
        và cập nhật personalization_profile thông qua PersonaOptimizer.
        """
        logger.info("[CRON] Running Persona Optimizer daily job...")
        if not self.profile_service or not self.persona_optimizer:
            logger.warning("Required services (profile_service, persona_optimizer) not set, skipping")
            return

        try:
            tenants = await self.profile_service.get_active_tenants()
            logger.info(f"[CRON] Processing {len(tenants)} active tenants")

            success_count = 0
            error_count = 0

            # Limit concurrency to 10 parallel LLM calls to avoid rate limiting / overload
            sem = asyncio.Semaphore(10)

            async def process_tenant(tenant):
                nonlocal success_count, error_count
                async with sem:
                    try:
                        profile = await self.persona_optimizer.optimize_tenant_profile(tenant.tenant_id)
                        if profile:
                            success_count += 1
                            logger.debug(
                                f"[CRON] Persona Optimizer: tenant {tenant.tenant_id} "
                                f"updated successfully"
                            )
                        else:
                            logger.debug(
                                f"[CRON] Persona Optimizer: tenant {tenant.tenant_id} "
                                f"no optimization performed (no recent convos)"
                            )
                    except Exception as e:
                        error_count += 1
                        logger.warning(
                            f"[CRON] Persona Optimizer failed for tenant "
                            f"{tenant.tenant_id}: {e}"
                        )

            tasks = [process_tenant(tenant) for tenant in tenants]
            await asyncio.gather(*tasks, return_exceptions=True)

            logger.info(
                f"[CRON] Persona Optimizer done: {success_count} success, "
                f"{error_count} errors"
            )

        except Exception as e:
            logger.exception(f"[CRON] _persona_optimizer_daily error: {e}")

    async def _conversation_cleanup(self):
        """
        Xóa các conversation turn cũ hơn 30 ngày để giải phóng DB.
        Chạy hàng ngày lúc 02:00.
        """
        logger.info("[CRON] Running conversation cleanup...")
        if not self.conversation_memory:
            logger.warning("conversation_memory not set, skipping")
            return

        try:
            retention_days = 30
            deleted = await self.conversation_memory.cleanup_old(days=retention_days)
            logger.info(
                f"[CRON] Conversation cleanup done: deleted {deleted} turns "
                f"older than {retention_days} days"
            )
        except Exception as e:
            logger.exception(f"[CRON] _conversation_cleanup error: {e}")
