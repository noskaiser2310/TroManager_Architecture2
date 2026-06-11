"""
Guardrails - Các cơ chế bảo vệ cho ReAct Agent.
"""

from __future__ import annotations
import logging
import time
from typing import Optional

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage

logger = logging.getLogger(__name__)


class Guardrails:
    """
    Safety guardrails cho ReAct Agent:
    - Token limit protection
    - Tool input validation
    - Sensitive tool approval
    - Loop breaker
    """

    SENSITIVE_TOOLS = {
        "send_payment_reminder": {
            "requires_approval": True,
            "approver_role": "landlord",
            "reason": "Ảnh hưởng quan hệ khách thuê"
        },
    }

    # Default fallback (override qua config["system2"]["guardrails"]["fallback"])
    DEFAULT_FALLBACK_MESSAGE = (
        "Hệ thống đang xử lý yêu cầu phức tạp. "
        "Vui lòng liên hệ trực tiếp {contact_label} qua số {contact_phone} "
        "để được hỗ trợ nhanh nhất."
    )

    def __init__(self, approval_service=None, max_tokens: int = 8000,
                 fallback_config: Optional[dict] = None):
        """
        Args:
            approval_service: ApprovalService instance (optional).
            max_tokens: Token limit for message compression.
            fallback_config: Dict với keys:
                - message (str): Nội dung fallback
                - contact_phone (str): Số điện thoại liên hệ
                - contact_name (str): Tên người liên hệ
        """
        self.approval = approval_service
        self.max_tokens = max_tokens
        fb = fallback_config or {}
        self.fallback_message = fb.get("message") or self.DEFAULT_FALLBACK_MESSAGE
        self.fallback_phone = fb.get("contact_phone", "")
        self.fallback_contact = fb.get("contact_name", "quản lý")

    def validate_tool_input(self, tool_call) -> tuple[bool, Optional[str]]:
        """
        Validate tool input schema. Hỗ trợ cả dict và object.

        Returns:
            (is_valid, error_message)
        """
        # Normalize: dict hoặc object đều OK
        if isinstance(tool_call, dict):
            name = tool_call.get("name", "")
            args = tool_call.get("args", {})
        else:
            name = getattr(tool_call, "name", "")
            args = getattr(tool_call, "args", {})

        if not name:
            return False, "Tool name is empty"

        if not isinstance(args, dict):
            return False, "Tool args must be a dict"

        # Pydantic validation would be done by LangChain
        return True, None

    def is_sensitive_tool(self, tool_name: str) -> bool:
        """Check tool có cần approval không."""
        return tool_name in self.SENSITIVE_TOOLS

    async def request_approval(self, tool_call, tenant_id: int) -> dict:
        """
        Request human approval cho sensitive tool. Hỗ trợ cả dict và object.

        Returns:
            dict với requires_approval flag và message
        """
        # Normalize: dict hoặc object đều OK
        if isinstance(tool_call, dict):
            name = tool_call.get("name", "")
            args = tool_call.get("args", {})
        else:
            name = getattr(tool_call, "name", "")
            args = getattr(tool_call, "args", {})

        config = self.SENSITIVE_TOOLS.get(name, {})
        if not config.get("requires_approval"):
            return {"requires_approval": False}

        if self.approval:
            approval_id = await self.approval.create_request(
                tool_name=name,
                tool_args=args,
                tenant_id=tenant_id,
                approver_role=config["approver_role"],
                reason=config["reason"],
            )
            return {
                "requires_approval": True,
                "approval_id": approval_id,
                "approval_message": f"Yêu cầu #{approval_id} đang chờ quản lý duyệt.",
            }
        else:
            # No approval service - block
            return {
                "requires_approval": True,
                "approval_message": "Hành động này cần quản lý duyệt. Vui lòng liên hệ trực tiếp.",
            }
    
    def check_token_limit(self, messages: list[BaseMessage], max_tokens: int = None) -> list[BaseMessage]:
        """
        Compress message history nếu quá token limit.
        
        Strategy: Giữ system + user + 3 turns gần nhất
        """
        max_t = max_tokens or self.max_tokens
        total_tokens = sum(self._estimate_tokens(m) for m in messages)
        
        if total_tokens <= max_t:
            return messages
        
        logger.warning(f"Token limit exceeded ({total_tokens} > {max_t}), compressing history")
        
        if len(messages) <= 4:
            return messages  # Không thể compress thêm
        
        # Giữ system message đầu tiên + 3 turns gần nhất
        system_msg = messages[0]
        recent = messages[-3:]
        
        # Summarize phần giữa
        middle = messages[1:-3]
        summary = f"[Đã nén: {len(middle)} tin nhắn trước đó]"
        summary_msg = SystemMessage(content=summary)
        
        return [system_msg, summary_msg] + recent
    
    def get_fallback_message(self) -> str:
        """
        Message trả về khi loop breaker triggered.

        Renders self.fallback_message với placeholders:
        - {contact_name} → tên người liên hệ (vd: "anh Minh")
        - {contact_phone} → số điện thoại (hoặc "không có" nếu chưa cấu hình)
        - {contact_label} → "anh Minh" / "quản lý" / etc.
        """
        return self.fallback_message.format(
            contact_name=self.fallback_contact,
            contact_phone=self.fallback_phone or "không có",
            contact_label=self.fallback_contact,
        )
    
    def _estimate_tokens(self, message: BaseMessage) -> int:
        """Rough estimate of tokens (1 token ≈ 4 chars in Vietnamese/English mix)."""
        content = ""
        if hasattr(message, "content"):
            content = str(message.content)
        return len(content) // 3
