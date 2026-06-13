"""
SMS Client using Twilio or other providers.
"""

from __future__ import annotations
import logging
import time
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class SMSSendResult:
    """Kết quả gửi SMS."""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    latency_ms: int = 0


class SMSClient:
    """Base SMS client interface."""
    
    async def send_sms(self, phone_number: str, message: str) -> SMSSendResult:
        raise NotImplementedError


class TwilioSMSClient(SMSClient):
    """
    Twilio SMS client (real implementation).
    
    Docs: https://www.twilio.com/docs/sms
    """
    
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        if not account_sid or account_sid == "your_account_sid_here":
            logger.warning(
                "Twilio account_sid chưa được set. "
                "Set trong notifications.yaml"
            )
        
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            try:
                from twilio.rest import Client
                self._client = Client(self.account_sid, self.auth_token)
            except ImportError:
                logger.error(
                    "twilio package not installed. "
                    "Run: pip install twilio"
                )
                raise
        return self._client
    
    async def send_sms(self, phone_number: str, message: str) -> SMSSendResult:
        start = time.time()
        try:
            client = self._get_client()
            twilio_msg = client.messages.create(
                body=message,
                from_=self.from_number,
                to=phone_number,
            )
            latency = int((time.time() - start) * 1000)
            return SMSSendResult(
                success=True,
                message_id=twilio_msg.sid,
                latency_ms=latency,
            )
        except Exception as e:
            logger.exception(f"Twilio SMS error: {e}")
            latency = int((time.time() - start) * 1000)
            return SMSSendResult(
                success=False,
                error=str(e),
                latency_ms=latency,
            )


class VNPTiMessageSMS(SMSClient):
    """
    Vietnamese SMS provider - esms.vn hoặc vnpt-invoice.
    
    Thay thế cho Twilio nếu muốn dùng provider nội địa.
    """
    
    def __init__(self, api_key: str, secret: str, brand_name: str):
        self.api_key = api_key
        self.secret = secret
        self.brand_name = brand_name
    
    async def send_sms(self, phone_number: str, message: str) -> SMSSendResult:
        # Implementation tương tự các SMS provider VN
        # Tuỳ thuộc provider cụ thể
        raise NotImplementedError(
            "Implement SMS provider cụ thể (esms.vn, speedSMS, etc.)"
        )


def create_sms_client_from_config(config: dict) -> SMSClient:
    """Factory tạo SMS client từ config."""
    provider = config.get("provider", "twilio").lower()
    
    if provider == "twilio":
        return TwilioSMSClient(
            account_sid=config.get("account_sid", ""),
            auth_token=config.get("auth_token", ""),
            from_number=config.get("from_number", ""),
        )
    elif provider in ("esms", "vnpt", "speed"):
        return VNPTiMessageSMS(
            api_key=config.get("api_key", ""),
            secret=config.get("secret", ""),
            brand_name=config.get("brand_name", "TROHAIDANG"),
        )
    else:
        raise ValueError(f"Unknown SMS provider: {provider}")
