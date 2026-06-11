# Bản Thiết Kế Triển Khai: Kiến Trúc Router-Centric ReAct (Dual-Process)

Dựa trên quyết định của chủ dự án, TroManager sẽ triển khai **Kiến trúc số 2: Router-Centric ReAct kết hợp Tiến trình kép (Dual-Process)**. Các quyết định cốt lõi về công nghệ đã được chốt:
- **Cơ sở dữ liệu:** Sử dụng 100% **PostgreSQL** kết hợp extension `pgvector` (Lưu trữ cả dữ liệu quan hệ, Cache và Vector Embeddings).
- **Tech Stack AI:** Sử dụng **kết hợp lai (Hybrid) các Framework**: 
  - *LangChain / LangGraph* để quản lý ReAct Agent và Tool Routing.
  - *LlamaIndex* cho phần RAG / Semantic Search từ tài liệu nội quy.

---

## 1. Thiết Kế Cơ Sở Dữ Liệu (PostgreSQL + pgvector)

Lớp **User Modeling Layer** và **Semantic Cache** sẽ được tổ chức trong PostgreSQL.

### 1.1. Cài đặt Extension
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 1.2. Bảng `user_profiles` (Hồ sơ tường minh)
Lưu trữ các thông tin cơ bản khai báo và các cài đặt tùy chọn của người dùng.
```sql
CREATE TABLE user_profiles (
    tenant_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) UNIQUE,
    room_id INT,
    lease_start DATE,
    lease_end DATE,
    communication_preference VARCHAR(50) DEFAULT 'zalo', -- zalo, sms, app
    tone_preference VARCHAR(50) DEFAULT 'professional', -- friendly, strict, professional
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 1.3. Bảng `behavior_logs` (Hồ sơ ngầm & Hành vi)
Lưu lại lịch sử các hành động để AI phân tích thói quen (ví dụ: thói quen đóng tiền, giờ giấc sinh hoạt).
```sql
CREATE TABLE behavior_logs (
    log_id SERIAL PRIMARY KEY,
    tenant_id INT REFERENCES user_profiles(tenant_id),
    action_type VARCHAR(100), -- vd: 'late_payment', 'maintenance_request', 'noise_complaint'
    description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 1.4. Bảng `user_embeddings` (Semantic Memory)
Lưu trữ các "đúc kết" về sở thích của người dùng dưới dạng Vector để LLM truy xuất theo ngữ nghĩa.
```sql
CREATE TABLE user_embeddings (
    memory_id SERIAL PRIMARY KEY,
    tenant_id INT REFERENCES user_profiles(tenant_id),
    memory_text TEXT NOT NULL, -- vd: "Khách rất nhạy cảm về tiếng ồn sau 10h tối"
    embedding vector(768), -- Kích thước vector phụ thuộc vào embedding model (vd: nomic-embed-text)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 1.5. Bảng `semantic_cache` (Dành cho System 1)
Lưu các cặp câu hỏi - câu trả lời tĩnh đã được xử lý để trả về ngay.
```sql
CREATE TABLE semantic_cache (
    cache_id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    query_embedding vector(768),
    response_text TEXT NOT NULL,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 2. Phân Lớp Kiến Trúc Cốt Lõi

### 2.1. Router Gateway Module (Phân luồng)
* **Nhiệm vụ:** Phân tích từ khóa bằng Regex và Logic thuần để quyết định luồng đi.
* **Logic:**
  - Nếu `source == "CRON"` ➡️ Gọi **System 2**.
  - Quét danh sách từ khóa nhạy cảm: `['tiền', 'nợ', 'hợp đồng', 'chuyển phòng', 'hỏng', 'sửa']`.
    - Nếu match ➡️ Gọi **System 2**.
  - Nếu không match ➡️ Chuyển sang **System 1**.

### 2.2. System 1 (Fast Layer)
* **Mô hình:** Gemini 1.5 Flash (hoặc model tương đương chi phí thấp).
* **Luồng xử lý:**
  1. Chuyển câu hỏi thành vector: `emb = get_embedding(query)`.
  2. So khớp Cosine Similarity với bảng `semantic_cache`:
     ```sql
     SELECT response_text, 1 - (query_embedding <=> emb) AS similarity 
     FROM semantic_cache WHERE 1 - (query_embedding <=> emb) > 0.9 LIMIT 1;
     ```
  3. Nếu có, trả về ngay.
  4. Nếu không, dùng LlamaIndex truy xuất Knowledge Base (nội quy) và sinh câu trả lời. Sau đó lưu vào `semantic_cache`.
* **Guardrails:** Nếu không tìm thấy thông tin hoặc độ tự tin thấp, trả về tín hiệu fallback để Router đẩy tiếp sang System 2.

### 2.3. System 2 (Core ReAct Layer)
* **Mô hình:** Gemini 1.5 Pro (hoặc GPT-4o) có năng lực suy luận tốt.
* **Tiêm ngữ cảnh (Context Injection):**
  - Đọc `user_profiles`, tổng hợp `behavior_logs` và query top các `user_embeddings` của tenant đưa vào System Prompt.
* **Dynamic Tool Registry (Hybrid Framework):**
  Sử dụng LangChain Tool Node để định nghĩa:
  - `Decision Toolkit`: tính tiền, tìm phòng trống.
  - `Knowledge Toolkit`: tra cứu chính sách, hóa đơn.
  - `Automation Toolkit`: gửi thông báo Zalo/SMS.
* **Cơ chế chống nhiễu:**
  - Dựa trên Intent phân loại ở Gateway, chỉ nạp đúng Toolkit cần thiết. (Ví dụ: Sự kiện nhắc nợ sẽ không nạp Decision Toolkit).
  - Giới hạn `max_iterations = 4` cho vòng lặp ReAct.

---

## 3. Tích Hợp Kích Hoạt Nền (Proactive Reminders)

Cron Job gửi tín hiệu ngầm:
```json
{
  "sender": "SYSTEM_CRON",
  "recipient": "SYSTEM_2_AGENT",
  "event": "invoice_overdue",
  "data": { "tenant_id": 123, "invoice_amount": 3500000 },
  "instruction": "Kiểm tra thông tin khách thuê và soạn thông báo nhắc đóng tiền nhà cá nhân hóa dựa trên thói quen của họ."
}
```
**Luồng xử lý:**
1. System 2 nhận event, đọc Profile từ Postgres.
2. Thấy "tone_preference": "friendly", System 2 sinh văn bản nhẹ nhàng.
3. System 2 gọi tool `send_notification(tenant_id, message)`.
4. Ghi nhận log vào `behavior_logs`.

---

## Verification Plan

### Automated/Unit Tests
- Khởi tạo Postgres Database cục bộ với `pgvector`.
- Viết script test luồng định tuyến (Router): Đảm bảo các câu chứa "tiền", "nợ" luôn bị chặn không cho vào System 1.
- Test Semantic Cache: Đảm bảo câu hỏi tương tự nhau trả về cùng một cache response.

### Tích hợp Manual
- Chạy giả lập 1 Agent (System 2) qua CLI. Tiêm Profile giả lập và kiểm tra xem LLM có sinh ra câu trả lời thay đổi giọng điệu (friendly vs strict) hay không.
