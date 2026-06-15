# 01. Architecture Overview - Router-Centric ReAct (Dual-Process)

## 1. Triết Lý Thiết Kế

Kiến trúc **Router-Centric ReAct với Tiến Trình Kép** được xây dựng dựa trên nguyên lý:

- **Một Agent Lõi duy nhất** quản lý toàn bộ các khả năng AI, tránh phân mảnh logic giữa nhiều agent.
- **Hai lớp nhận thức tách biệt** (System 1 & System 2) tối ưu hóa sự cân bằng giữa **chi phí**, **độ trễ** và **chất lượng suy luận**.
- **Router Gateway** đóng vai trò "bảo vệ" - đảm bảo các vấn đề nhạy cảm (tài chính, hợp đồng) luôn được xử lý bởi System 2.

## 2. Lý Do Chọn Kiến Trúc Này

| Tiêu chí | Đánh giá |
|----------|----------|
| Chi phí vận hành | Tốt - System 1 xử lý ~80% câu hỏi đơn giản với Flash model rẻ |
| Độ trễ phản hồi | Tốt - Cache hit trả lời tức thì |
| Độ chính xác | Tốt - System 2 với ReAct loop cho các bài toán phức tạp |
| Khả năng mở rộng | Khá - Dynamic Tool Loading giúp thêm tools mới không ảnh hưởng context |
| Độ phức tạp code | Trung bình - Một agent duy nhất, ít boilerplate |
| Tích hợp Proactive | Tốt - Background events đi thẳng vào System 2 |

## 3. Sơ Đồ Kiến Trúc Tổng Thể

```mermaid
graph TB
    subgraph Input
        U[User Chat]
        CR[Cron Event]
    end

    subgraph "Entry Point"
        GW[Router Gateway]
    end

    subgraph "System 1 - Fast Layer"
        S1[Cache Lookup]
        S1B[RAG - Knowledge Base]
        S1C[Simple DB Query]
    end

    subgraph "System 2 - Core ReAct Agent"
        S2[ReAct Loop]
        CTX[Context Builder]
        GRD[Guardrails]
    end

    subgraph "Tool Registry"
        DT[Decision Toolkit]
        KT[Knowledge Toolkit]
        AT[Automation Toolkit]
    end

    subgraph "User Modeling Layer"
        UP[User Profiles]
        BL[Behavior Logs]
        UE[User Embeddings]
        SC[Semantic Cache]
    end

    subgraph "External Services"
        ZALO[Zalo OA API]
        SMS[SMS Gateway]
    end

    U --> GW
    CR --> S2
    GW -->|FAQ/Static| S1
    GW -->|Sensitive/Complex| S2
    
    S1 --> S1A[1. Cache Lookup]
    S1 --> S1B
    S1 --> S1C
    S1A -->|Miss| S1B
    S1A -->|Miss| S1C
    S1A -->|Low Confidence| S2
    
    S2 --> CTX
    CTX --> UP
    CTX --> BL
    CTX --> UE
    S2 --> GRD
    S2 --> DT
    S2 --> KT
    S2 --> AT
    
    DT --> UP
    KT --> UP
    KT --> BL
    AT --> ZALO
    AT --> SMS
    AT --> BL
```

## 4. Các Thành Phần Chính

### 4.1. Router Gateway
- **Nhiệm vụ**: Phân luồng request đầu vào
- **Logic**:
  - Nếu `source == "CRON"` → System 2 (luôn)
  - Nếu query > 500 ký tự → System 2 (cần context sâu)
  - Còn lại → **LLMIntentRouter** dùng `gemma-4-26b-a4b-it` để phân loại SYSTEM1 / SYSTEM2
  - Timeout > 5s hoặc LLM error → fallback System 2 (confidence 0.5)
- **Triển khai**: LLM Intent Routing (xem `src/gateway/router.py` + `src/gateway/keyword_classifier.py`)

### 4.2. System 1 - Fast Layer
- **Model**: `gemma-4-31b-it` (bản flash)
- **Luồng**:
  1. Chuyển query thành vector (embedding)
  2. So khớp Cosine Similarity với `semantic_cache` (threshold 0.9)
  3. Nếu hit → trả về response
  4. Nếu miss → RAG từ Knowledge Base bằng LlamaIndex
  5. Nếu confidence < 0.7 → fallback System 2
- **Output guard**: Mọi response phải có confidence score; nếu thấp thì escalate

### 4.3. System 2 - Core ReAct Agent
- **Model**: `gemini-3.1-flash-lite` (bản pro)
- **Luồng**:
  1. Context Injection: Đọc `user_profiles`, tổng hợp `behavior_logs`, query top-k `user_embeddings`
  2. Dynamic Tool Loading: Dựa trên intent chỉ nạp toolkit cần thiết
  3. ReAct loop: Thought → Action → Observation (max 4 iterations)
  4. Guardrails: Validate tool input schema, loop breaker
- **Output**: Câu trả lời cuối cùng hoặc action đã thực hiện

### 4.4. User Modeling Layer
- **Vai trò**: Hạ tầng dữ liệu chung cung cấp context cho cả System 1 và System 2
- **4 module**:
  - `user_profiles`: Thông tin tường minh (họ tên, số phòng, hợp đồng)
  - `behavior_logs`: Lịch sử hành vi (thanh toán, sửa chữa, khiếu nại)
  - `user_embeddings`: Vector semantic memory về sở thích
  - `semantic_cache`: Cache câu hỏi - câu trả lời thường gặp

### 4.5. Dynamic Tool Registry
3 bộ toolkit (18 tools) được load động dựa trên intent:

| Toolkit | Tools | Use cases |
|---------|-------|-----------|
| Decision (5) | `fetch_available_rooms`, `calc_rent`, `recommend_transfer`, `compare_rooms`, `recommend_renewal` | Tư vấn phòng, tính tiền, gia hạn |
| Knowledge (7) | `query_policies`, `get_invoice_detail`, `get_contract_status`, `get_payment_history`, `get_room_info`, `get_maintenance_status`, `get_room_by_number` | Tra cứu thông tin |
| Automation (6) | `send_zalo`, `send_sms`, `create_maintenance_ticket`, `send_payment_reminder`, `schedule_room_viewing`, `update_user_preference` | Gửi thông báo, tạo ticket |

## 5. Design Principles

1. **Separation of Concerns**: Gateway, System 1, System 2, Tools tách biệt rõ ràng
2. **Fail-Safe Default**: Mọi request không phân loại được đều mặc định chuyển sang System 2
3. **Observability First**: Mọi quyết định routing phải log lại để debug
4. **Cost-Aware**: Track số lượng tokens tiêu thụ bởi mỗi System
5. **Tenant-Centric**: Mọi response đều được cá nhân hóa dựa trên profile

## 6. Non-Functional Requirements

| Yêu cầu | Mục tiêu |
|---------|----------|
| Latency (System 1 cache hit) | < 200ms |
| Latency (System 1 RAG) | < 2s |
| Latency (System 2 simple) | < 5s |
| Latency (System 2 with tools) | < 15s |
| Uptime | 99.5% |
| Concurrent users | 100 |
| Cost per 1000 queries | < $2 |

## 7. Công Nghệ Cốt Lõi

| Component | Tech |
|-----------|------|
| Database | PostgreSQL 16 + pgvector |
| Vector Search | pgvector HNSW index |
| LLM | Google Gemini (`gemini-3.1-flash-lite`, `gemma-4-31b-it`, `gemma-4-26b-a4b-it`) |
| Agent Framework | Custom ReAct / LangChain |
| RAG | LlamaIndex |
| Embedding | `gemini-embedding-2` (3072 dim) |
| Message Queue | Không dùng message queue (xử lý đồng bộ) |
| Scheduler | APScheduler |
| Webhook Receiver | FastAPI |
| Notification | Zalo OA API, Twilio SMS |

## 8. Mở Rộng Tương Lai

- **Phase 2**: Tích hợp LoRA/PEFT cho personalization sâu hơn
- **Phase 3**: Thêm Multi-Modal (đọc ảnh hóa đơn, gửi ảnh hướng dẫn)
- **Phase 4**: Mem0 cho smart memory management
- **Phase 5**: Chuyển sang Multi-Agent nếu domain complexity tăng

## 9. Tham Khảo

- `../implementation_plan.md` - Kế hoạch triển khai
- `../Architecture_Design/router_centric_react_design.md` - Bản thiết kế gốc
- `../Architecture_Design/architecture_comparison.md` - So sánh 3 kiến trúc
- `../diagrams/04_react_architecture.png` - Sơ đồ trực quan
