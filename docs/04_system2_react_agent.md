# 04. System 2 - Core ReAct Agent Design

## 1. Vai Trò

System 2 (Slow Layer) là **bộ não chính** của hệ thống, xử lý:
- Câu hỏi phức tạp cần suy luận đa bước
- Các tác vụ cần gọi tool (gửi thông báo, tính tiền, tạo ticket)
- Background events từ Cron
- Personalization sâu dựa trên User Modeling

## 2. ReAct Loop

```mermaid
graph TD
    Start[User Query / Event] --> CI[Context Injection]
    CI --> T1[Thought 1: Phân tích vấn đề]
    T1 --> A1{Action needed?}
    A1 -->|Yes| TC[Tool Call]
    A1 -->|No| FIN[Final Answer]
    TC --> O1[Observation 1: Tool result]
    O1 -->|Not done| T2[Thought 2: Phân tích kết quả]
    T2 --> A2{Action needed?}
    A2 -->|Yes| TC2[Tool Call]
    A2 -->|No| FIN
    TC2 --> O2[Observation 2]
    O2 -->|Not done| T3[...]
    T3 --> LOOP{Iter < 4?}
    LOOP -->|Yes| T1
    LOOP -->|No| FALL[Fallback message]
    FIN --> LOG[Log behavior]
    LOG --> END[Return response]
```

## 3. Context Injection

Trước khi vào ReAct loop, System 2 xây dựng context từ User Modeling:

### 3.1. Profile Context
```python
profile_context = {
    "tenant_id": 123,
    "full_name": "Nguyễn Văn A",
    "room_id": 205,
    "lease_end": "2026-12-31",
    "communication_preference": "zalo",
    "tone_preference": "friendly"
}
```

### 3.2. Behavior Summary
```python
behavior_context = {
    "avg_payment_delay_days": 2,
    "preferred_payment_method": "bank_transfer",
    "maintenance_requests_count": 3,
    "noise_complaints_count": 0,
    "last_interaction": "2026-05-30"
}
```

### 3.3. Relevant Memories (Vector Search)
```python
relevant_memories = user_embeddings.similarity_search(
    query=current_question,
    tenant_id=123,
    top_k=3
)
# Returns: ["Khách hay quên đóng tiền vào ngày 5", "Khách nhạy cảm về tiếng ồn", ...]
```

## 4. Dynamic Tool Loading

Dựa trên **intent classification** (thực hiện ngay sau Context Injection), chỉ nạp toolkit cần thiết:

```python
def select_toolkits(intent: str) -> list[str]:
    intent_to_toolkits = {
        "billing_inquiry": ["knowledge", "decision"],
        "maintenance_request": ["knowledge", "automation"],
        "room_recommendation": ["decision", "knowledge"],
        "contract_question": ["knowledge"],
        "payment_reminder": ["knowledge", "automation"],
        "general_chat": [],  # Không cần tool
    }
    return intent_to_toolkits.get(intent, ["knowledge"])  # Default safe
```

## 5. Tool Definitions

Xem chi tiết trong `06_dynamic_tool_registry.md`.

Các tool được define bằng **Pydantic schema** cho input validation:

```python
class SendZaloInput(BaseModel):
    tenant_id: int
    message: str
    template_id: Optional[str] = None

@tool(args_schema=SendZaloInput)
def send_zalo(tenant_id: int, message: str, template_id: str = None) -> str:
    """Gửi tin nhắn Zalo cho khách thuê."""
    return zalo_client.send(tenant_id, message, template_id)
```

## 6. ReAct Loop Implementation

### 6.1. Pseudocode

```python
async def react_loop(query: str, tenant_id: int) -> str:
    # 1. Context injection
    context = build_context(tenant_id, query)
    tools = select_tools(context.intent)
    system_prompt = build_system_prompt(context, tools)
    
    # 2. Initialize state
    history = [SystemMessage(content=system_prompt), HumanMessage(content=query)]
    
    # 3. Loop (max 4 iterations, 30s tool timeout, 360s LLM timeout)
    for iteration in range(MAX_ITERATIONS):
        with timeout(LLM_TIMEOUT_SECONDS):   # 360s
            response = await pro_client.chat(messages=history)
        history.append(response)
        
        # b. Empty content check - regenerate
        if not response.content and not response.tool_calls:
            response = await pro_client.chat(messages=[SystemMessage("...")])
        
        # c. Final answer check
        if not response.tool_calls:
            return response.content
        
        # d. Duplicate tool call detection
        for tool_call in response.tool_calls:
            if _is_duplicate_call(tool_call, history):
                continue
        
        # e. Execute tools (with timeout)
        for tool_call in response.tool_calls:
            try:
                result = await asyncio.wait_for(
                    execute_tool(tool_call, tools),
                    timeout=TOOL_TIMEOUT_SECONDS  # 30s
                )
                observation = ToolMessage(content=result, ...)
            except asyncio.TimeoutError:
                observation = ToolMessage(content="Tool timeout", ...)
            except Exception as e:
                observation = ToolMessage(content=f"Error: {e}", ...)
            history.append(observation)
    
    # 4. Loop breaker
    return FALLBACK_MESSAGE
```

### 6.2. Tool Execution

```python
def execute_tool(tool_call: dict, tools: list) -> str:
    tool = next((t for t in tools if t.name == tool_call["name"]), None)
    if not tool:
        return f"Tool {tool_call['name']} not found"
    
    try:
        # Execute
        result = tool.invoke(tool_call["args"])
        return str(result)
    except Exception as e:
        return f"Tool execution failed: {e}"
```

## 7. Guardrails

### 7.1. Loop Breaker
```python
MAX_ITERATIONS = 4
LLM_TIMEOUT_SECONDS = 360  # 6 phút cho LLM call
TOOL_TIMEOUT_SECONDS = 30  # 30 giây cho tool execution

if iteration >= MAX_ITERATIONS and response.tool_calls:
    log.warning(f"ReAct loop exceeded max iterations for tenant {tenant_id}")
    return "Hệ thống đang xử lý phức tạp, vui lòng liên hệ trực tiếp quản lý."
```

### 7.2. Retry Logic (3 lần với exponential backoff)
```python
for attempt in range(MAX_RETRIES):  # 3
    try:
        response = await pro_client.chat(messages)
        break
    except Exception as e:
        if attempt < MAX_RETRIES - 1:
            wait = 1.5 ** attempt  # 1s, 1.5s, 2.25s
            await asyncio.sleep(wait)
        else:
            raise
```

### 7.3. Sensitive Action Approval

Một số tool yêu cầu **human approval** trước khi thực thi:

```python
def check_and_execute(tool_call: dict, tenant_id: int):
    # Trích xuất id và name
    tool_id = tool_call.get("id")
    tool_name = tool_call.get("name")
    
    if is_sensitive(tool_name):
        # Đẩy vào queue thay vì chạy thật
        approval_id = push_to_approval_queue(tool_call, tenant_id)
        
        # PHẢI trả về ToolMessage với đúng ID và Name để LLM không bị lỗi parse
        return ToolMessage(
            content=f"Đã tạo yêu cầu duyệt #{approval_id}, quản lý sẽ duyệt. Hãy báo cho user.",
            tool_call_id=tool_id,
            name=tool_name
        )
    else:
        # Thực thi bình thường
        ...
```

### 7.4. Token Limit Protection

```python
MAX_TOKENS_PER_REQUEST = 8000

def check_token_limit(history):
    total_tokens = sum(count_tokens(msg) for msg in history)
    if total_tokens > MAX_TOKENS_PER_REQUEST:
        # Nén history: chỉ giữ system + user + 3 turn gần nhất
        compressed = compress_history(history)
        return compressed
    return history
```

### 7.5. Output Validation

```python
FINAL_ANSWER_SCHEMA = {
    "answer": str,
    "actions_taken": list[str],
    "tone_used": str,
    "personalization_applied": bool,
    "confidence": float
}
```

## 8. Background Event Handling

Khi nhận event từ Cron (không qua Router):

```python
def handle_background_event(event: dict):
    """
    Event format:
    {
        "sender": "SYSTEM_CRON",
        "event": "invoice_overdue",
        "data": {"tenant_id": 123, "invoice_amount": 3500000},
        "instruction": "..."
    }
    """
    tenant_id = event["data"]["tenant_id"]
    context = build_context(tenant_id, event["instruction"])
    
    # Load only relevant tools
    tools = ["knowledge", "automation"]
    
    # Run ReAct loop with custom instruction
    response = react_loop(
        query=event["instruction"],
        tenant_id=tenant_id,
        tools=tools,
        context=context
    )
    
    # Log
    behavior_logs.log(
        tenant_id=tenant_id,
        action_type=f"auto_{event['event']}",
        description=response
    )
    
    return response
```

## 9. Personalization Tone Control

Dựa trên `tone_preference` của tenant, điều chỉnh system prompt:

| Tone | Cách diễn đạt |
|------|---------------|
| `friendly` | "Anh/chị ơi, phòng mình...", emoji vừa phải, xưng hô thân mật |
| `professional` | "Kính gửi anh/chị...", ngôn ngữ lịch sự, không emoji |
| `strict` | "Thông báo: ...", ngắn gọn, đi thẳng vào vấn đề |

```python
TONE_TEMPLATES = {
    "friendly": "Bạn là trợ lý AI thân thiện, xưng hô 'mình' với khách thuê...",
    "professional": "Bạn là trợ lý AI chuyên nghiệp, sử dụng ngôn ngữ lịch sự...",
    "strict": "Bạn là trợ lý AI nghiêm túc, thông báo rõ ràng, ngắn gọn..."
}
```

## 10. Metrics

```python
class System2Metrics:
    total_requests: int
    avg_iterations: float
    max_iterations_hit: int
    tool_calls_total: int
    tool_failures: int
    sensitive_actions_approved: int
    avg_latency_ms: float
    avg_tokens_used: int
    cost_usd: float
    background_events_handled: int
```

## 11. Configuration

```yaml
system2:
  model: "gemini-3.1-flash-lite"  # bản pro
  max_iterations: 4
  max_tokens: 8000
  temperature: 0.4
  max_retries: 3
  retry_backoff_base: 1.5
  llm_timeout_seconds: 360
  tool_timeout_seconds: 30
  enable_dynamic_tool_loading: true
  enable_history_compression: true
```

## 12. Tham Khảo Code

- `../src/system2/react_agent.py` - ReAct loop
- `../src/system2/context_builder.py` - Context injection
- `../src/system2/guardrails.py` - Safety checks
- `../config/prompts/system2_prompt.txt` - Prompt template
- `../tests/test_react_loop.py` - Test cases

## 13. Comparison với System 1

| Tiêu chí | System 1 | System 2 |
|----------|----------|----------|
| Model | Flash (rẻ, nhanh) | Pro (mạnh, đắt) |
| Latency | < 2s | < 15s |
| Tool calls | Không | Có |
| Context depth | Surface | Deep (vector memory) |
| Personalization | Cơ bản | Sâu |
| Use cases | FAQ, lookup | Reasoning, action |
| Cost/query | ~$0.001 | ~$0.01-0.05 |
