# Knowledge Base - TroManager

Thư mục này chứa toàn bộ tri thức nền tảng (knowledge base) của hệ thống TroManager. Các file `.md` được tổ chức theo chủ đề và sẽ được load tự động vào vector store để RAG.

## Cấu trúc

```
knowledge_base/
├── README.md                 -- File này
├── noi_quy/                  -- Nội quy nhà trọ
│   ├── gio_giac.md
│   ├── ve_sinh.md
│   ├── an_ninh.md
│   └── su_dung_tien_ich.md
├── chinh_sach/               -- Chính sách
│   ├── thanh_toan.md
│   ├── hop_dong.md
│   ├── chuyen_phong.md
│   ├── hoan_coc.md
│   └── gia_han.md
├── faq/                      -- Câu hỏi thường gặp
│   ├── wifi_internet.md
│   ├── gui_xe.md
│   ├── sua_chua.md
│   ├── nuoi_thu_cung.md
│   └── them_nguoi_o.md
└── quy_trinh/                -- Quy trình thuê/trả phòng
    ├── thue_phong_moi.md
    ├── tra_phong.md
    └── dang_ky_dich_vu.md
```

## Cách thức hoạt động

1. **Ingestion**: Khi hệ thống khởi động, tất cả file `.md` sẽ được:
   - Đọc và chia thành chunks (mặc định 512 tokens, overlap 50)
   - Encode thành vector embeddings (text-embedding-004, 768 dim)
   - Lưu vào PostgreSQL + pgvector (bảng `semantic_cache` hoặc bảng riêng)

2. **Retrieval**: Khi user hỏi câu hỏi, hệ thống:
   - Encode câu hỏi thành vector
   - Cosine similarity search trong vector store
   - Lấy top-k chunks liên quan nhất
   - Đưa vào context cho LLM

3. **Generation**: LLM (Gemini 3.0 Flash) sinh câu trả lời dựa trên:
   - System prompt (từ `config/prompts/system1_prompt.txt`)
   - Retrieved contexts (từ knowledge base)
   - User query

## Cách thêm tri thức mới

Đơn giản chỉ cần:
1. Tạo file `.md` mới trong thư mục phù hợp
2. Restart service để re-index
3. Hoặc gọi API admin: `POST /admin/knowledge/reindex`

## Format khuyến nghị cho mỗi file

```markdown
# Tiêu đề chính

Mô tả ngắn gọn.

## Câu hỏi thường gặp

### 1. Câu hỏi cụ thể?
Trả lời chi tiết.

### 2. Câu hỏi khác?
Trả lời khác.

## Quy định chi tiết

- Quy tắc 1
- Quy tắc 2
- Quy tắc 3

## Liên hệ hỗ trợ

- Hotline: xxx
- Email: xxx
```

## Tags & Metadata (optional)

Để cải thiện retrieval, có thể thêm frontmatter YAML:

```markdown
---
tags: [wifi, internet, mang]
category: faq
priority: high
last_updated: 2026-06-05
---

# Wifi và Internet
...
```

## Best Practices

1. **Ngắn gọn, rõ ràng**: Mỗi chunk tối đa 512 tokens (~300 từ tiếng Việt)
2. **Cấu trúc heading rõ ràng**: H1, H2, H3 giúp chunking hiệu quả
3. **Câu hỏi thường gặp ở đầu**: Đặt FAQ trước để match với user query
4. **Tránh duplicate**: Không lặp lại nội dung ở nhiều file
5. **Cập nhật thường xuyên**: Đánh dấu ngày cập nhật
