# Multi-stage build for DevOS
FROM golang:1.21-alpine AS go-builder

# Install build dependencies
RUN apk add --no-cache git

WORKDIR /app

# Copy Go module files
COPY go.mod go.sum ./
RUN go mod download

# Copy Go source code
COPY cmd/ ./cmd/
COPY internal/ ./internal/

# Build Go binary
RUN cd cmd/devos && \
    CGO_ENABLED=0 GOOS=linux go build -ldflags="-w -s" -o /app/devos .

# Python stage
FROM python:3.11-slim AS python-deps

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python dependencies from python-deps stage
COPY --from=python-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-deps /usr/local/bin /usr/local/bin

# Copy Go binary
COPY --from=go-builder /app/devos /usr/local/bin/devos

# Copy Python source code
COPY ai_engine/ ./ai_engine/
COPY adapters/ ./adapters/

# Create config directory
RUN mkdir -p /root/.config/devos

# Set environment variables
ENV PYTHONPATH=/app
ENV DEVOS_CONFIG_PATH=/root/.config/devos

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD devos version || exit 1

# Run DevOS
ENTRYPOINT ["devos"]
