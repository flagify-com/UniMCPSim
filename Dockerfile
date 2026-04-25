# UniMCPSim Docker Image

ARG PYTHON_IMAGE=python:3.11-slim
FROM ${PYTHON_IMAGE}

ARG VERSION=dev
ARG USE_CHINA_MIRRORS=false

# Set labels
LABEL org.opencontainers.image.title="UniMCPSim"
LABEL org.opencontainers.image.description="Universal MCP Simulator"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.source="https://github.com/flagify-com/UniMCPSim"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV TZ=Asia/Shanghai

# Set working directory
WORKDIR /app

# Optional China mainland mirrors for local builds:
# docker build --build-arg USE_CHINA_MIRRORS=true .
RUN if [ "$USE_CHINA_MIRRORS" = "true" ]; then \
        sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources \
        && sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources; \
    fi

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN if [ "$USE_CHINA_MIRRORS" = "true" ]; then \
        pip install --no-cache-dir -r requirements.txt \
            -i https://mirrors.aliyun.com/pypi/simple/ \
            --trusted-host mirrors.aliyun.com; \
    else \
        pip install --no-cache-dir -r requirements.txt; \
    fi

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data /app/logs

# Expose ports
# MCP Server: 9090, Admin Server: 9091
EXPOSE 9090 9091

# Override any entrypoint inherited from a custom base image.
ENTRYPOINT []

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9090/health || exit 1

# Default command
CMD ["python", "start_servers.py"]
