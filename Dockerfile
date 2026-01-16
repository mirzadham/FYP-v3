# Rasa Server Dockerfile
# Multi-stage build for smaller production image

# ================================
# Stage 1: Build dependencies
# ================================
FROM python:3.10-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ================================
# Stage 2: Production image
# ================================
FROM python:3.10-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application files
COPY config.yml .
COPY credentials.yml .
COPY endpoints.yml .
COPY domain/ domain/
COPY data/ data/
COPY prompt/ prompt/

# Create models directory (models are trained separately or at runtime)
RUN mkdir -p models

# Cloud Run uses PORT environment variable
ENV PORT=8080

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Run Rasa server
CMD exec rasa run \
    --enable-api \
    --cors "*" \
    --port ${PORT} \
    --endpoints endpoints.yml \
    --credentials credentials.yml
