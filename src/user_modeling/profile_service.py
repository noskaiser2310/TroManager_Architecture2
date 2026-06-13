"""
User Profile Service - CRUD operations cho user_profiles table.
"""

from __future__ import annotations
import logging
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

import asyncpg

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """User profile data class."""
    tenant_id: int
    full_name: str
    phone_number: Optional[str]
    email: Optional[str]
    zalo_id: Optional[str]
    room_id: Optional[int]
    lease_start: Optional[date]
    lease_end: Optional[date]
    communication_preference: str
    tone_preference: str
    notification_opt_out: list[str]
    personalization_profile: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> dict:
        return {
            "tenant_id": self.tenant_id,
            "full_name": self.full_name,
            "phone_number": self.phone_number,
            "email": self.email,
            "zalo_id": self.zalo_id,
            "room_id": self.room_id,
            "lease_start": self.lease_start.isoformat() if self.lease_start else None,
            "lease_end": self.lease_end.isoformat() if self.lease_end else None,
            "communication_preference": self.communication_preference,
            "tone_preference": self.tone_preference,
            "notification_opt_out": self.notification_opt_out,
            "personalization_profile": self.personalization_profile,
            "is_active": self.is_active,
        }


class ProfileService:
    """
    Service quản lý user profiles.
    """
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.db = db_pool
    
    async def get_profile(self, tenant_id: int) -> Optional[UserProfile]:
        """
        Lấy profile theo tenant_id.
        """
        sql = """
        SELECT
            tenant_id, full_name, phone_number, email, zalo_id,
            room_id, lease_start, lease_end,
            communication_preference, tone_preference,
            notification_opt_out, personalization_profile, is_active,
            created_at, updated_at
        FROM user_profiles
        WHERE tenant_id = $1 AND is_active = TRUE
        """
        async with self.db.acquire() as conn:
            row = await conn.fetchrow(sql, tenant_id)
            if row:
                return self._row_to_profile(row)
        return None
    
    async def get_profile_by_phone(self, phone: str) -> Optional[UserProfile]:
        """Lấy profile theo số điện thoại."""
        sql = "SELECT * FROM user_profiles WHERE phone_number = $1 AND is_active = TRUE"
        async with self.db.acquire() as conn:
            row = await conn.fetchrow(sql, phone)
            if row:
                return self._row_to_profile(row)
        return None
    
    async def get_profile_by_zalo_id(self, zalo_id: str) -> Optional[UserProfile]:
        """Lấy profile theo Zalo ID."""
        sql = "SELECT * FROM user_profiles WHERE zalo_id = $1 AND is_active = TRUE"
        async with self.db.acquire() as conn:
            row = await conn.fetchrow(sql, zalo_id)
            if row:
                return self._row_to_profile(row)
        return None
    
    async def update_profile(self, tenant_id: int, updates: dict) -> bool:
        """
        Update profile fields.
        
        Args:
            tenant_id: ID khách thuê
            updates: Dict các field cần update
            
        Returns:
            True nếu update thành công
        """
        if not updates:
            return False
        
        # Whitelist allowed fields
        allowed_fields = {
            "full_name", "phone_number", "email", "zalo_id",
            "room_id", "lease_start", "lease_end",
            "communication_preference", "tone_preference",
            "notification_opt_out", "personalization_profile", "is_active",
        }
        safe_updates = {k: v for k, v in updates.items() if k in allowed_fields}
        
        # Validate tone_preference
        if "tone_preference" in safe_updates:
            valid_tones = {"professional", "friendly", "concise"}
            if safe_updates["tone_preference"] not in valid_tones:
                safe_updates["tone_preference"] = "professional"
        
        if not safe_updates:
            return False
        
        set_clause = ", ".join([f"{k} = ${i+2}" for i, k in enumerate(safe_updates.keys())])
        sql = f"UPDATE user_profiles SET {set_clause} WHERE tenant_id = $1"
        
        async with self.db.acquire() as conn:
            result = await conn.execute(sql, tenant_id, *safe_updates.values())
            return result == "UPDATE 1"
    
    async def get_active_tenants(self) -> list[UserProfile]:
        """Lấy tất cả tenants đang active."""
        sql = """
        SELECT * FROM user_profiles
        WHERE is_active = TRUE
        ORDER BY tenant_id
        """
        async with self.db.acquire() as conn:
            rows = await conn.fetch(sql)
            return [self._row_to_profile(row) for row in rows]
    
    async def get_tenants_with_lease_ending(self, days: int) -> list[UserProfile]:
        """Lấy tenants có hợp đồng sắp hết hạn trong N ngày."""
        sql = """
        SELECT * FROM user_profiles
        WHERE is_active = TRUE
          AND lease_end IS NOT NULL
          AND lease_end BETWEEN CURRENT_DATE AND CURRENT_DATE + $1 * INTERVAL '1 day'
        ORDER BY lease_end
        """
        async with self.db.acquire() as conn:
            rows = await conn.fetch(sql, days)
            return [self._row_to_profile(row) for row in rows]
    
    async def delete_tenant(self, tenant_id: int) -> bool:
        """Xóa tenant (GDPR compliance)."""
        sql = "DELETE FROM user_profiles WHERE tenant_id = $1"
        async with self.db.acquire() as conn:
            result = await conn.execute(sql, tenant_id)
            return result == "DELETE 1"
    
    def _row_to_profile(self, row) -> UserProfile:
        """Convert asyncpg.Record to UserProfile."""
        import json
        
        # Parse JSONB fields if they come as string, else keep as is (asyncpg handles JSONB to string usually)
        opt_out = row["notification_opt_out"]
        if isinstance(opt_out, str):
            opt_out = json.loads(opt_out)
            
        pers_profile = row.get("personalization_profile", "{}")
        if isinstance(pers_profile, str):
            pers_profile = json.loads(pers_profile)

        return UserProfile(
            tenant_id=row["tenant_id"],
            full_name=row["full_name"],
            phone_number=row["phone_number"],
            email=row["email"],
            zalo_id=row["zalo_id"],
            room_id=row["room_id"],
            lease_start=row["lease_start"],
            lease_end=row["lease_end"],
            communication_preference=row["communication_preference"],
            tone_preference=row["tone_preference"],
            notification_opt_out=opt_out or [],
            personalization_profile=pers_profile or {},
            is_active=row["is_active"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
