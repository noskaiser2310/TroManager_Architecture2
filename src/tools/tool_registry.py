"""
Tool Registry - Quản lý và load tools động theo intent.
"""

from __future__ import annotations
import logging
from typing import Optional

from langchain_core.tools import BaseTool

from .decision_tools import DECISION_TOOLS
from .knowledge_tools import KNOWLEDGE_TOOLS
from .automation_tools import AUTOMATION_TOOLS

logger = logging.getLogger(__name__)


# Intent → Toolkits mapping
INTENT_TOOLKIT_MAP = {
    # Billing & payment
    "billing_inquiry": ["knowledge"],
    "payment_reminder": ["knowledge", "automation"],
    "billing_dispute": ["knowledge", "decision"],
    
    # Maintenance
    "maintenance_request": ["knowledge", "automation"],
    "maintenance_status": ["knowledge"],
    
    # Rooms
    "room_recommendation": ["decision", "knowledge"],
    "room_transfer": ["decision", "knowledge", "automation"],
    "room_inquiry": ["knowledge"],
    
    # Contract
    "contract_inquiry": ["knowledge"],
    "contract_renewal": ["knowledge", "decision", "automation"],
    
    # General
    "policy_question": ["knowledge"],
    "general_chat": [],
    "greeting": [],
    
    # Background events
    "background_event_invoice_overdue": ["knowledge", "automation"],
    "background_event_contract_expiring": ["knowledge", "automation"],
    "background_event_maintenance": ["knowledge", "automation"],
    "background_event_birthday": ["automation"],
    "background_event_welcome": ["knowledge", "automation"],
    
    # Default safe
    "unknown": ["knowledge"],
}


class Toolkit:
    """Một bộ toolkit."""
    
    def __init__(self, name: str, tools: list[BaseTool]):
        self.name = name
        self.tools = tools


class ToolRegistry:
    """
    Registry quản lý tất cả tools.
    
    Cung cấp:
    - get_all_tools(): Tất cả tools
    - get_for_intent(intent): Tools cho một intent cụ thể
    - get_tools_by_names(names): Tools theo tên
    """
    
    def __init__(self):
        self.toolkits = {
            "decision": Toolkit("decision", DECISION_TOOLS),
            "knowledge": Toolkit("knowledge", KNOWLEDGE_TOOLS),
            "automation": Toolkit("automation", AUTOMATION_TOOLS),
        }
    
    def get_all_tools(self) -> list[BaseTool]:
        """Lấy tất cả tools từ tất cả toolkits."""
        all_tools = []
        for toolkit in self.toolkits.values():
            all_tools.extend(toolkit.tools)
        return all_tools
    
    def get_for_intent(self, intent: str) -> list[BaseTool]:
        """
        Lấy tools cho một intent cụ thể.
        
        Args:
            intent: Tên intent
            
        Returns:
            list các tools
        """
        toolkit_names = INTENT_TOOLKIT_MAP.get(intent, ["knowledge"])
        return self.get_toolkits_by_names(toolkit_names)
    
    def get_toolkits_by_names(self, names: list[str]) -> list[BaseTool]:
        """Lấy tools từ nhiều toolkits."""
        tools = []
        for name in names:
            toolkit = self.toolkits.get(name)
            if toolkit:
                tools.extend(toolkit.tools)
            else:
                logger.warning(f"Toolkit '{name}' not found")
        return tools
    
    def get_tool_by_name(self, name: str) -> Optional[BaseTool]:
        """Tìm tool theo tên."""
        for toolkit in self.toolkits.values():
            for tool in toolkit.tools:
                if tool.name == name:
                    return tool
        return None
    
    def describe_tools(self, tools: list[BaseTool]) -> str:
        """Format tool descriptions cho system prompt."""
        return "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in tools
        ])


# ============ Factory ============

_default_registry: Optional[ToolRegistry] = None

def get_default_registry() -> ToolRegistry:
    """Singleton registry."""
    global _default_registry
    if _default_registry is None:
        _default_registry = ToolRegistry()
    return _default_registry


# ============ CLI demo ============

if __name__ == "__main__":
    registry = get_default_registry()
    
    print("=== All Tools ===")
    for tool in registry.get_all_tools():
        print(f"  - {tool.name}")
    
    print("\n=== Tools for 'billing_inquiry' ===")
    for tool in registry.get_for_intent("billing_inquiry"):
        print(f"  - {tool.name}")
    
    print("\n=== Tools for 'maintenance_request' ===")
    for tool in registry.get_for_intent("maintenance_request"):
        print(f"  - {tool.name}")
    
    print("\n=== Tools for 'room_transfer' ===")
    for tool in registry.get_for_intent("room_transfer"):
        print(f"  - {tool.name}")
