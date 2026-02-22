# ══════════════════════════════════════════════════════════
# Warm Hook Hugs — Production Dockerfile
# ══════════════════════════════════════════════════════════
# Multi-stage build | Python 3.12-slim | Non-root user
# WSGI: Gunicorn binding to port 8000
# ══════════════════════════════════════════════════════════

# ── Stage 1: Builder ──
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Production ──
FROM python:3.12-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Copy application code
COPY . .

# Create directories for static & media
RUN mkdir -p /app/staticfiles /app/media && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose Gunicorn port
EXPOSE 8000

# Collect static files at build time
RUN python manage.py collectstatic --noinput 2>/dev/null || true

# Start Gunicorn
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
