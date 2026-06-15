# ============================================================
# TroManager — Dockerfile
# Architecture #2: Router-Centric ReAct (Dual-Process)
#
# Build:  docker build -t tromanager .
# Run:    docker compose up -d app
# ============================================================

# Stage 1: Builder — cài dependencies vào virtual env
FROM python:3.13-slim AS builder

WORKDIR /app

# Cài system deps cần thiết cho asyncpg + psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (không include dev/testing)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================
# Stage 2: Runtime — image gọn nhẹ
# ============================================================
FROM python:3.13-slim AS runtime

WORKDIR /app

# Runtime system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages từ builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source code
COPY src/ ./src/
COPY config/ ./config/
COPY knowledge_base/ ./knowledge_base/
COPY test_ui.html ./test_ui.html

# Non-root user (security best practice)
RUN useradd --no-create-home --shell /bin/false appuser && \
    chown -R appuser:appuser /app
USER appuser

# Port mà FastAPI chạy
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=10s --timeout=5s --retries=5 --start-period=15s \
  CMD curl -f http://localhost:8000/health || exit 1

# Khởi động server
CMD ["python", "-m", "uvicorn", "src.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1", \
     "--log-level", "info"]
