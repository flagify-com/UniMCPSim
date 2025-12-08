# UniMCPSim Docker Image
# OEM White-label Version

FROM python:3.11-slim

# Set labels
LABEL maintainer="UniMCPSim"
LABEL version="2.9.0"
LABEL description="Universal MCP Simulator - OEM Edition"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV TZ=Asia/Shanghai

# Set working directory
WORKDIR /app

# Configure China mainland mirrors (Aliyun)
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources \
    && sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies (use Aliyun PyPI mirror)
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data /app/logs

# Expose ports
# MCP Server: 9090, Admin Server: 9091
EXPOSE 9090 9091

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9090/health || exit 1

# Default command
CMD ["python", "start_servers.py"]
