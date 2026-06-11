# Database Setup Guide

## Yêu Cầu

- PostgreSQL 16+
- pgvector extension
- Quyền superuser để cài extension

## Cài Đặt

### 1. Cài pgvector

**Ubuntu/Debian:**
```bash
sudo apt install postgresql-16-pgvector
```

**macOS (Homebrew):**
```bash
brew install pgvector
```

**Windows:**
Download từ https://github.com/pgvector/pgvector/releases

### 2. Tạo Database

```bash
# Login với superuser
psql -U postgres

# Tạo database
CREATE DATABASE tromanager;
\c tromanager

# Cài extension
CREATE EXTENSION vector;
```

### 3. Chạy Schema

```bash
psql -U postgres -d tromanager -f schema.sql
```

### 4. Load Seed Data (optional, cho dev)

```bash
psql -U postgres -d tromanager -f seed_data.sql
```

## Schema Overview

| Table | Purpose | Rows (seed) |
|-------|---------|-------------|
| `rooms` | Danh sách phòng | 9 |
| `user_profiles` | Hồ sơ khách thuê | 5 |
| `contracts` | Hợp đồng thuê | 5 |
| `invoices` | Hóa đơn hàng tháng | 12 |
| `payments` | Lịch sử thanh toán | 0 (chưa seed) |
| `behavior_logs` | Logs hành vi | 27 |
| `user_embeddings` | Vector memory | 5 |
| `semantic_cache` | Q&A cache | 4 |
| `maintenance_tickets` | Phiếu sửa chữa | 5 |
| `conversation_history` | Lịch sử chat | 5 |
| `approval_queue` | Hàng chờ duyệt | 3 |

## Useful Queries

### Test Vector Search

```sql
-- Tìm memories gần giống với một query
SELECT memory_text, 
       1 - (embedding <=> (SELECT embedding FROM user_embeddings WHERE memory_id = 1)) as similarity
FROM user_embeddings
WHERE tenant_id = 1
ORDER BY embedding <=> (SELECT embedding FROM user_embeddings WHERE memory_id = 1)
LIMIT 3;
```

### Test Semantic Cache

```sql
-- Giả lập tìm cache với embedding giống cache_id = 1
SELECT response_text,
       1 - (query_embedding <=> (SELECT query_embedding FROM semantic_cache WHERE cache_id = 1)) as similarity
FROM semantic_cache
WHERE 1 - (query_embedding <=> (SELECT query_embedding FROM semantic_cache WHERE cache_id = 1)) > 0.8
ORDER BY similarity DESC;
```

### Top Overdue Invoices

```sql
SELECT * FROM v_overdue_invoices
ORDER BY days_overdue DESC;
```

### Tenant Behavior Summary

```sql
SELECT * FROM v_tenant_behavior_90d
WHERE late_payment_count > 0
ORDER BY late_payment_count DESC;
```

## Maintenance

### Cleanup Expired Cache (chạy daily)

```sql
SELECT cleanup_expired_cache();
```

Hoặc setup cron job:
```bash
# Daily at 3 AM
0 3 * * * psql -U postgres -d tromanager -c "SELECT cleanup_expired_cache();"
```

### Vacuum & Analyze (chạy weekly)

```sql
VACUUM ANALYZE;
```

## Indexes

Các index đã được tạo sẵn:
- B-tree indexes cho foreign keys và timestamps
- HNSW indexes cho vector columns (pgvector)
- Unique indexes cho natural keys

## Performance Tips

1. **Connection pooling**: Dùng PgBouncer hoặc SQLAlchemy pool
2. **Read replicas**: Cho analytics queries
3. **Partitioning**: `behavior_logs` nên partition by month nếu data lớn
4. **Vector index**: Đã có HNSW, có thể tweak `m` và `ef_construction`

## Backup

```bash
# Full backup
pg_dump -U postgres tromanager > backup.sql

# Restore
psql -U postgres -d tromanager < backup.sql
```
