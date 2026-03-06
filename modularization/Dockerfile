# OpenCode Multi-Account System Dockerfile
# ==========================================
#
# Multi-stage build for production deployment
# Supports both development and production environments

# Build stage
FROM python:3.10-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# Add labels
LABEL maintainer="OpenCode Team <team@opencode.ai>"
LABEL description="OpenCode Multi-Account System - Multi-provider AI orchestration"
LABEL version=$VERSION
LABEL build-date=$BUILD_DATE
LABEL vcs-ref=$VCS_REF

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Development stage
FROM builder as development

# Install development dependencies
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Set environment for development
ENV PYTHONPATH=/app
ENV OPENCODE_ENV=development
ENV DEBUG=true

# Production stage
FROM python:3.10-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r opencode && useradd -r -g opencode opencode

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/config /app/data /app/logs /app/backups \
    && chown -R opencode:opencode /app

# Set permissions
RUN chmod +x /app/bin/* 2>/dev/null || true

# Expose ports
EXPOSE 8080 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Switch to non-root user
USER opencode

# Set environment for production
ENV PYTHONPATH=/app
ENV OPENCODE_ENV=production
ENV DEBUG=false

# Default command
CMD ["./bin/opencode-multi-account", "start"]

# Metadata
LABEL org.opencontainers.image.source="https://github.com/opencode/multi-account-system"
LABEL org.opencontainers.image.documentation="https://docs.opencode.ai/multi-account"
LABEL org.opencontainers.image.licenses="MIT"