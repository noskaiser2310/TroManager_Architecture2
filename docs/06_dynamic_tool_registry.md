# 06. Dynamic Tool Registry Design

## 1. Vai Trò

Dynamic Tool Registry là tập hợp các **tools** mà System 2 (ReAct Agent) có thể gọi. Đặc biệt ở chỗ các tool **được nạp động** dựa trên intent, tránh tình trạng "tool confusion" khi số lượng tools tăng lên.

## 2. Cấu Trúc

```mermaid
graph TB
    subgraph "Tool Registry"
        REG[Tool Registry]
        DT[Decision Toolkit]
        KT[Knowledge Toolkit]
        AT[Automation Toolkit]
    end
    
    REG --> DT
    REG --> KT
    REG --> AT
    
    DT --> T1[fetch_available_rooms]
    DT --> T2[calc_rent]
    DT --> T3[recommend_transfer]
    
    KT --> T4[query_policies]
    KT --> T5[get_invoice_detail]
    KT --> T6[get_contract_status]
    
    AT --> T7[send_zalo]
    AT --> T8[send_sms]
    AT --> T9[create_maintenance_ticket]
```

## 3. 3 Bộ Toolkit

### 3.1. Decision Toolkit
**Mục đích**: Hỗ trợ ra quyết định về phòng, giá, chuyển phòng.

| Tool | Mô tả | Input | Output |
|------|-------|-------|--------|
| `fetch_available_rooms` | Lấy danh sách phòng trống | `budget_max`, `min_area`, `floor_preference` | `list[Room]` |
| `calc_rent` | Tính tiền thuê tháng | `room_id`, `month`, `electricity_kwh`, `water_m3` | `RentBreakdown` |
| `recommend_transfer` | Đề xuất phòng phù hợp hơn | `tenant_id` | `RoomRecommendation` |
| `compare_rooms` | So sánh 2 phòng | `room_id_1`, `room_id_2` | `Comparison` |

### 3.2. Knowledge Toolkit
**Mục đích**: Tra cứu thông tin từ database và knowledge base.

| Tool | Mô tả | Input | Output |
|------|-------|-------|--------|
| `query_policies` | Tìm chính sách theo câu hỏi | `query: str` | `list[PolicyDoc]` |
| `get_invoice_detail` | Chi tiết hóa đơn | `tenant_id`, `month` | `InvoiceDetail` |
| `get_contract_status` | Trạng thái hợp đồng | `tenant_id` | `ContractStatus` |
| `get_payment_history` | Lịch sử thanh toán | `tenant_id`, `months` | `list[Payment]` |
| `get_room_info` | Thông tin phòng hiện tại | `tenant_id` | `RoomInfo` |

### 3.3. Automation Toolkit
**Mục đích**: Gửi thông báo và thực hiện hành động tự động.

| Tool | Mô tả | Input | Output | Sensitive? |
|------|-------|-------|--------|------------|
| `send_zalo` | Gửi tin Zalo | `tenant_id`, `message`, `template_id?` | `SendResult` | No |
| `send_sms` | Gửi SMS | `tenant_id`, `message` | `SendResult` | No |
| `create_maintenance_ticket` | Tạo phiếu sửa chữa | `tenant_id`, `issue`, `priority` | `Ticket` | No |
| `send_payment_reminder` | Gửi nhắc nợ | `tenant_id`, `invoice_id` | `SendResult` | **Yes** |
| `schedule_room_viewing` | Đặt lịch xem phòng | `tenant_id`, `room_id`, `datetime` | `Appointment` | No |

## 4. Dynamic Tool Loading

### 4.1. Intent → Toolkit Mapping

```python
INTENT_TOOLKIT_MAP = {
    # Billing
    "billing_inquiry": ["knowledge"],  # Chỉ tra cứu
    "payment_reminder": ["knowledge", "automation"],  # Có thể gửi nhắc
    "billing_dispute": ["knowledge", "decision"],  # Có thể tính lại
    
    # Maintenance
    "maintenance_request": ["knowledge", "automation"],  # Tạo ticket
    "maintenance_status": ["knowledge"],
    
    # Rooms
    "room_recommendation": ["decision", "knowledge"],
    "room_transfer": ["decision", "knowledge", "automation"],
    "contract_renewal": ["knowledge", "decision"],
    
    # General
    "policy_question": ["knowledge"],
    "general_chat": [],  # Không cần tool
    
    # Default safe
    "unknown": ["knowledge"]
}
```

### 4.2. Implementation

```python
def get_tools_for_intent(intent: str) -> list:
    """Lấy danh sách tools dựa trên intent."""
    toolkit_names = INTENT_TOOLKIT_MAP.get(intent, ["knowledge"])
    tools = []
    for name in toolkit_names:
        tools.extend(TOOLKITS[name].tools)
    return tools

def get_tools_description(tools: list) -> str:
    """Format tool descriptions cho system prompt."""
    return "\n".join([
        f"- {t.name}: {t.description}"
        for t in tools
    ])
```

## 5. Tool Definition Standard

### 5.1. Pydantic Schema

```python
from pydantic import BaseModel, Field
from langchain.tools import tool

class CalcRentInput(BaseModel):
    room_id: int = Field(..., description="ID của phòng cần tính tiền")
    month: str = Field(..., description="Tháng cần tính, format YYYY-MM")
    electricity_kwh: float = Field(0, description="Số kWh điện tiêu thụ")
    water_m3: float = Field(0, description="Số m3 nước tiêu thụ")

@tool(args_schema=CalcRentInput)
def calc_rent(room_id: int, month: str, electricity_kwh: float = 0, water_m3: float = 0) -> dict:
    """Tính tổng tiền thuê phòng trong tháng, bao gồm tiền phòng + điện + nước + dịch vụ."""
    # Implementation
    room = db.get_room(room_id)
    base_rent = room.monthly_rent
    elec_cost = electricity_kwh * room.electricity_price
    water_cost = water_m3 * room.water_price
    service_cost = room.service_fee
    total = base_rent + elec_cost + water_cost + service_cost
    
    return {
        "room_id": room_id,
        "month": month,
        "breakdown": {
            "base_rent": base_rent,
            "electricity": elec_cost,
            "water": water_cost,
            "service": service_cost,
        },
        "total": total
    }
```

### 5.2. JSON Schema (alternative)

```json
{
  "name": "calc_rent",
  "description": "Tính tổng tiền thuê phòng trong tháng",
  "parameters": {
    "type": "object",
    "properties": {
      "room_id": {"type": "integer", "description": "ID phòng"},
      "month": {"type": "string", "pattern": "^\\d{4}-\\d{2}$"},
      "electricity_kwh": {"type": "number", "default": 0},
      "water_m3": {"type": "number", "default": 0}
    },
    "required": ["room_id", "month"]
  }
}
```

## 6. Tool Execution Flow

```mermaid
sequenceDiagram
    participant Agent
    participant Registry
    participant Tool
    participant DB
    participant External
    
    Agent->>Registry: Get tools for intent
    Registry-->>Agent: [calc_rent, send_zalo]
    Agent->>Agent: Thought: "Cần tính tiền + gửi nhắc"
    Agent->>Agent: Action: calc_rent(room_id=205, month="2026-06")
    Agent->>Tool: execute(args)
    Tool->>DB: Query room + rates
    DB-->>Tool: Room data
    Tool-->>Agent: {total: 3500000}
    Agent->>Agent: Observation: Tiền tháng này là 3.5tr
    Agent->>Agent: Action: send_zalo(tenant_id=123, message="...")
    Agent->>Tool: execute(args)
    Tool->>External: Zalo OA API
    External-->>Tool: {success: true}
    Tool-->>Agent: "Sent"
    Agent->>Agent: Final Answer
```

## 7. Sensitive Tool Approval

Một số tool yêu cầu human approval:

```python
SENSITIVE_TOOLS = {
    "send_payment_reminder": {
        "requires_approval": True,
        "approver_role": "landlord",
        "reason": "Ảnh hưởng đến quan hệ khách thuê"
    },
    "modify_contract": {
        "requires_approval": True,
        "approver_role": "landlord",
        "reason": "Thay đổi điều khoản hợp đồng"
    }
}
```

Khi tool được gọi:
1. Tạo approval request trong queue
2. Gửi notification cho approver (landlord)
3. Tool return message "Đang chờ duyệt"
4. Sau khi approved, tool thực sự được execute

## 8. Error Handling

```python
def execute_tool_safely(tool_call, tools: list) -> ToolMessage:
    tool = find_tool(tool_call.name, tools)
    if not tool:
        return ToolMessage(content=f"Tool '{tool_call.name}' không tồn tại", tool_call_id=tool_call.id)
    
    try:
        # Validate input
        if tool.args_schema:
            validated = tool.args_schema(**tool_call.args)
            result = tool.run(validated.dict())
        else:
            result = tool.run(tool_call.args)
        
        # Convert to string for LLM
        return ToolMessage(content=json.dumps(result, ensure_ascii=False), tool_call_id=tool_call.id)
    
    except ValidationError as e:
        return ToolMessage(content=f"Input không hợp lệ: {e}", tool_call_id=tool_call.id)
    
    except ToolException as e:
        return ToolMessage(content=f"Tool thất bại: {e}", tool_call_id=tool_call.id)
    
    except Exception as e:
        log.exception("Unexpected tool error")
        return ToolMessage(content=f"Lỗi hệ thống khi thực thi tool", tool_call_id=tool_call.id)
```

## 9. Tool Testing

Mỗi tool cần có:
- **Unit test**: Test happy path + edge cases
- **Integration test**: Test với database thật
- **Schema test**: Đảm bảo input/output đúng schema

Ví dụ:
```python
def test_calc_rent():
    result = calc_rent.func(room_id=205, month="2026-06", electricity_kwh=100, water_m3=5)
    assert result["total"] == 2050000 + 100*3500 + 5*100000 + 50000
    assert "breakdown" in result
```

## 10. Tool Versioning

Khi cần update tool mà không break agent:

```python
@tool(name="calc_rent_v2", args_schema=CalcRentInputV2)
def calc_rent_v2(...):
    """Tính tiền thuê với logic mới (có giảm giá theo tháng)."""
    # New logic
    pass

# Tool registry handles version
TOOLKITS["decision"].tools["calc_rent"] = calc_rent  # current
TOOLKITS["decision"].tools["calc_rent_v2"] = calc_rent_v2  # experimental
```

## 11. Tham Khảo Code

- `../src/tools/decision_tools.py` - Decision toolkit
- `../src/tools/knowledge_tools.py` - Knowledge toolkit
- `../src/tools/automation_tools.py` - Automation toolkit
- `../src/tools/tool_registry.py` - Dynamic loading
- `../tests/test_tools.py` - Tool tests

## 12. Best Practices

1. **Description rõ ràng**: Tool description phải mô tả chính xác khi nào dùng tool đó
2. **Input validation**: Luôn dùng Pydantic schema
3. **Idempotent tools**: Tool nên idempotent khi có thể (gửi 2 lần = 1 lần)
4. **Logging đầy đủ**: Log mọi tool call với input/output
5. **Rate limiting**: Một số tool (gửi Zalo) cần rate limit
