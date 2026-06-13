"""
Zalo OA Client - Gửi tin nhắn Zalo Official Account.
"""

from __future__ import annotations
import logging
import time
from dataclasses import dataclass
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass
class ZaloMessage:
    """Cấu trúc tin nhắn Zalo."""
    recipient_id: str
    message: str
    template_id: Optional[str] = None
    template_data: Optional[dict] = None
    attachment: Optional[dict] = None


@dataclass
class ZaloSendResult:
    """Kết quả gửi tin nhắn."""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    latency_ms: int = 0


class ZaloClient:
    """
    Real Zalo OA client.
    
    Docs: https://developers.zalo.me/docs/api/official-account-api
    
    Cần config:
    - access_token: Zalo OA access token (từ Zalo for Developers)
    - oa_id: OA ID
    """
    
    BASE_URL = "https://openapi.zalo.me/v2.0/oa"
    
    def __init__(
        self,
        access_token: str,
        oa_id: str,
        api_url: Optional[str] = None,
        timeout: int = 10,
    ):
        if not access_token or access_token == "your_access_token_here":
            logger.warning(
                "Zalo access_token chưa được set. "
                "Set trong config/llm_config.yaml hoặc notifications.yaml"
            )
        
        self.access_token = access_token
        self.oa_id = oa_id
        self.api_url = api_url or self.BASE_URL
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.api_url,
                headers={
                    "access_token": self.access_token,
                    "Content-Type": "application/json",
                },
                timeout=self.timeout,
            )
        return self._client
    
    async def close(self):
        """Đóng client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def send_message(self, message: ZaloMessage) -> ZaloSendResult:
        """
        Gửi tin nhắn qua Zalo OA API.
        """
        start = time.time()
        
        try:
            client = await self._get_client()
            
            if message.template_id:
                payload = {
                    "recipient": {"user_id": message.recipient_id},
                    "message": {
                        "attachment": {
                            "type": "template",
                            "payload": {
                                "template_type": "list",
                                "template_id": message.template_id,
                                "data": message.template_data or {},
                            }
                        }
                    }
                }
            else:
                payload = {
                    "recipient": {"user_id": message.recipient_id},
                    "message": {"text": message.message}
                }
            
            response = await client.post("/message", json=payload)
            latency = int((time.time() - start) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("error") == 0:
                    return ZaloSendResult(
                        success=True,
                        message_id=str(data.get("data", {}).get("message_id", "")),
                        latency_ms=latency,
                    )
                else:
                    error_msg = data.get("message", "Unknown Zalo API error")
                    logger.error(f"Zalo API error: {error_msg}")
                    return ZaloSendResult(
                        success=False,
                        error=error_msg,
                        latency_ms=latency,
                    )
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                logger.error(error_msg)
                return ZaloSendResult(
                    success=False,
                    error=error_msg,
                    latency_ms=latency,
                )
        
        except httpx.TimeoutException as e:
            latency = int((time.time() - start) * 1000)
            logger.error(f"Zalo timeout: {e}")
            return ZaloSendResult(
                success=False,
                error=f"Timeout after {self.timeout}s",
                latency_ms=latency,
            )
        except Exception as e:
            latency = int((time.time() - start) * 1000)
            logger.exception(f"Zalo send error: {e}")
            return ZaloSendResult(
                success=False,
                error=str(e),
                latency_ms=latency,
            )
    
    async def send_to_tenant(
        self,
        tenant_zalo_id: str,
        message_text: str,
        template_id: Optional[str] = None,
        template_data: Optional[dict] = None,
    ) -> ZaloSendResult:
        """Helper gửi tin cho tenant."""
        message = ZaloMessage(
            recipient_id=tenant_zalo_id,
            message=message_text,
            template_id=template_id,
            template_data=template_data,
        )
        return await self.send_message(message)
    
    async def get_user_profile(self, user_id: str) -> Optional[dict]:
        """Lấy thông tin user từ Zalo."""
        try:
            client = await self._get_client()
            response = await client.get(
                "/getprofile",
                params={"user_id": user_id},
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("error") == 0:
                    return data.get("data")
        except Exception as e:
            logger.exception(f"Zalo get profile error: {e}")
        return None


def create_zalo_client_from_config(config: dict) -> ZaloClient:
    """
    Factory tạo ZaloClient từ config dict.
    """
    return ZaloClient(
        access_token=config.get("access_token", ""),
        oa_id=config.get("oa_id", ""),
        api_url=config.get("api_url"),
        timeout=config.get("timeout", 10),
    )
