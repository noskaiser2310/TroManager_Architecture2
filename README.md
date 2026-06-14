# TroManager - Kiến Trúc Số 2: Router-Centric ReAct (Dual-Process)

> Code base triển khai cho hệ thống quản lý nhà trọ thông minh **TroManager**, dựa trên kiến trúc **Router-Centric ReAct kết hợp Tiến trình kép (Dual-Process)**.
> Trạng thái dự án: **HOÀN THÀNH 100% MODULE CỐT LÕI (PRODUCTION-READY)**.

---

## 1. Tổng Quan Kiến Trúc

Kiến trúc này lấy cảm hứng từ **Lý thuyết nhận thức kép của Kahneman**, kết hợp với công nghệ định tuyến phân giải ý định (**LLM Intent Routing**):

- **Router Gateway**: Phân tích trực tiếp Intent bằng LLM (`gemma-4-26b-a4b-it`) để quyết định Request nên đi vào hệ thống nào (không dùng Regex lỗi thời).
- **Hệ thống 1 (Fast Layer)**: Phản ứng nhanh, chi phí thấp, xử lý các câu hỏi FAQ và tra cứu đơn giản. Dùng `gemma-4-31b-it` + Semantic Cache.
- **Hệ thống 2 (Slow Layer)**: Suy luận sâu, đa bước, dùng cho các tác vụ phức tạp (tài chính, khiếu nại, bảo trì). Dùng `gemini-3.1-flash-lite` + ReAct loop + Tool Registry + Human-in-the-loop Guardrails.

---

## 2. Công Nghệ Sử Dụng (Tech Stack)

| Component | Công nghệ |
|-----------|-----------|
| **Database** | PostgreSQL 16 + pgvector extension (3072-dim vectors) |
| **LLM Fast / Router** | `gemma-4-31b-it` (Fast), `gemma-4-26b-a4b-it` (Router) |
| **LLM Pro** | `gemini-3.1-flash-lite` |
| **Embedding** | `gemini-embedding-2` (3072 dims) |
| **Agent Framework** | Custom ReAct Loop (thay vì LangGraph để tối ưu <100 tenants) |
| **Notification** | Zalo OA API (Webhook), SMS Gateway |
| **Language & Env** | Python 3.13, Conda, Uvicorn, FastAPI |

---

## 3. Cấu Trúc Thư Mục

```
TroManager_Architecture2/
├── README.md                       -- File này
├── ROADMAP.md                      -- Lộ trình tương lai
├── docs/                           -- Tài liệu thiết kế chi tiết
│   └── BUG_REPORT.md               -- Lịch sử xử lý lỗi
├── database/                       -- Schema PostgreSQL & Data mẫu
├── src/                            -- Source code (Python)
│   ├── gateway/                    -- LLM Intent Router
│   ├── system1/                    -- Fast Layer (RAG)
│   ├── system2/                    -- Slow Layer (ReAct Agent & Guardrails)
│   ├── user_modeling/              -- Persona Optimizer & Behavior Tracking
│   ├── tools/                      -- Dynamic Tool Registry
│   ├── cron/                       -- Background Jobs (Invoice, Contract, Birthday)
│   └── main.py                     -- FastAPI Application
├── config/                         -- Cấu hình hệ thống (YAML)
├── tests/                          -- Bộ 220+ Test cases (100% Passed)
└── diagrams/                       -- Biểu đồ luồng (Mermaid)
```

---

## 4. Hướng Dẫn Cài Đặt Và Chạy Hệ Thống

Để chạy hệ thống thực tế tại Local, làm theo các bước sau:

### Bước 1: Khởi tạo Môi trường (Conda)
Hệ thống yêu cầu Python 3.12 hoặc 3.13. Sử dụng Conda để quản lý môi trường:
```bash
conda create -n tromanager python=3.13
conda activate tromanager
pip install -r requirements.txt
```

### Bước 2: Thiết lập Biến Môi Trường (.env)
Copy file `.env.example` thành `.env` và điền các thông tin bảo mật (Hệ thống tuyệt đối không dùng mock, bạn cần API Key thật):
```bash
cp .env.example .env
```
Mở file `.env` và cung cấp:
- `GEMINI_API_KEY`: API Key để gọi Gemini/Gemma model.
- `DB_PASSWORD`: Mật khẩu truy cập PostgreSQL.

### Bước 3: Khởi chạy Database
Đảm bảo bạn đã cài đặt PostgreSQL 16 với pgvector. Hoặc chạy nhanh qua Docker Compose:
```bash
docker-compose up -d postgres
```
Sau đó, nạp dữ liệu mẫu và schema:
```bash
# Khởi tạo Schema và Dummy Data
psql -h localhost -U postgres -d tromanager_db -f database/schema.sql
psql -h localhost -U postgres -d tromanager_db -f database/seed_data.sql
```

### Bước 4: Kiểm tra nhanh (Smoke Test)
Chạy kịch bản test để đảm bảo LLM và Database đã được nối dây thành công:
```bash
python scripts/run_smoke_test.py
python scripts/test_real_llm.py
```

### Bước 5: Khởi động Máy chủ FastAPI
Khởi chạy hệ thống chính:
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```
Hệ thống đã sẵn sàng tại `http://localhost:8000`. Bạn có thể tương tác qua `/chat` endpoint hoặc chờ các Cron Job ngầm tự động kích hoạt.

