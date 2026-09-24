# ==============================================================================
# Multi-stage Production Dockerfile for LawerAI (Qanoon Sahayak) Backend
# Includes system binaries for Poppler (PDF conversion) & Tesseract (OCR)
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Builder
# ------------------------------------------------------------------------------
FROM python:3.12-slim-bookworm AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ------------------------------------------------------------------------------
# Stage 2: Minimal Production Runtime
# ------------------------------------------------------------------------------
FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/appuser/.local/bin:${PATH}" \
    PORT=8000

# Install runtime system packages: Poppler utilities, Tesseract OCR with English & Urdu packs, and curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-urd \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create unprivileged system user and directories
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser && \
    mkdir -p /app/data/uploads /app/data/indexes /app/logs && \
    chown -R appuser:appgroup /app

WORKDIR /app

# Copy installed Python packages from builder stage
COPY --from=builder --chown=appuser:appgroup /root/.local /home/appuser/.local

# Copy application source code
COPY --chown=appuser:appgroup backend /app/backend
COPY --chown=appuser:appgroup ingestion /app/ingestion
COPY --chown=appuser:appgroup data/legal_corpus /app/data/legal_corpus
COPY --chown=appuser:appgroup data/lawyer_directory.json /app/data/lawyer_directory.json
COPY --chown=appuser:appgroup alembic /app/alembic
COPY --chown=appuser:appgroup alembic.ini /app/alembic.ini

# Switch to non-root user
USER appuser

EXPOSE 8000

# Container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start production ASGI server with multiple workers
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT} --workers 2"]
