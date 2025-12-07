# Docker 部署指南

本文档介绍如何使用 Docker 部署 UniMCPSim。

## 目录

- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [构建镜像](#构建镜像)
- [运行容器](#运行容器)
- [配置说明](#配置说明)
- [数据持久化](#数据持久化)
- [离线部署](#离线部署)
- [常用命令](#常用命令)
- [故障排查](#故障排查)

## 环境要求

- Docker 20.10+
- Docker Compose 2.0+（可选，推荐）
- 至少 512MB 可用内存
- 至少 1GB 可用磁盘空间

## 快速开始

### 使用 Docker Compose（推荐）

```bash
# 1. 克隆代码
git clone -b feature/oem https://github.com/wzfukui/UniMCPSim.git
cd UniMCPSim

# 2. 创建环境配置文件
cp .env.example .env
# 编辑 .env 文件，填入您的配置

# 3. 启动服务
docker-compose up -d

# 4. 查看运行状态
docker-compose ps
```

服务启动后：
- MCP Server: http://localhost:9090
- Admin Panel: http://localhost:9091/admin/
- 默认账号: admin / admin123

## 构建镜像

### 标准构建

```bash
docker build -t unimcpsim:oem .
```

### 指定版本标签

```bash
docker build -t unimcpsim:2.8.2-oem .
```

### 构建参数

Dockerfile 已配置中国大陆镜像源（阿里云），如需使用其他镜像源，可修改 Dockerfile 中的相关配置。

## 运行容器

### 方式一：Docker Compose（推荐）

```bash
# 前台运行（查看日志）
docker-compose up

# 后台运行
docker-compose up -d

# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

### 方式二：Docker Run

```bash
# 基础运行
docker run -d \
  --name unimcpsim \
  -p 9090:9090 \
  -p 9091:9091 \
  unimcpsim:oem

# 完整配置运行
docker run -d \
  --name unimcpsim \
  --restart unless-stopped \
  -p 9090:9090 \
  -p 9091:9091 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/.env:/app/.env:ro \
  -e TZ=Asia/Shanghai \
  unimcpsim:oem
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `MCP_SERVER_PORT` | MCP 服务端口 | 9090 |
| `ADMIN_SERVER_PORT` | 管理后台端口 | 9091 |
| `TZ` | 时区 | Asia/Shanghai |
| `OPENAI_API_KEY` | OpenAI API 密钥 | - |
| `OPENAI_MODEL` | OpenAI 模型 | gpt-4o-mini |
| `OPENAI_API_BASE_URL` | OpenAI API 地址 | https://api.openai.com/v1 |

### .env 配置文件示例

```env
# OpenAI 配置（可选，用于 AI 响应生成）
OPENAI_API_KEY=sk-xxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_BASE_URL=https://api.openai.com/v1

# 服务端口配置
MCP_SERVER_PORT=9090
ADMIN_SERVER_PORT=9091

# 其他配置
DEBUG=false
LOG_LEVEL=INFO
```

### 端口映射

| 容器端口 | 说明 | 建议映射 |
|----------|------|----------|
| 9090 | MCP Server | 必须映射 |
| 9091 | Admin Panel | 按需映射 |

## 数据持久化

### 数据卷说明

| 路径 | 说明 | 是否必须 |
|------|------|----------|
| `/app/data` | SQLite 数据库 | **是** |
| `/app/logs` | 运行日志 | 推荐 |
| `/app/.env` | 环境配置 | 推荐 |

### 数据备份

```bash
# 备份数据库
docker cp unimcpsim:/app/data/unimcp.db ./backup/

# 备份日志
docker cp unimcpsim:/app/logs ./backup/

# 完整备份
docker run --rm \
  -v unimcpsim_data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/unimcpsim-backup.tar.gz /data
```

### 数据恢复

```bash
# 恢复数据库
docker cp ./backup/unimcp.db unimcpsim:/app/data/

# 重启容器使配置生效
docker restart unimcpsim
```

## 离线部署

适用于无法访问外网的服务器环境。

### 1. 在联网机器上构建并导出镜像

```bash
# 构建镜像
docker build -t unimcpsim:oem .

# 导出为 tar.gz 文件
docker save unimcpsim:oem | gzip > unimcpsim-oem.tar.gz

# 文件大小约 200-300MB
ls -lh unimcpsim-oem.tar.gz
```

### 2. 传输到目标服务器

```bash
# 使用 scp
scp unimcpsim-oem.tar.gz user@server:/path/to/

# 或使用其他方式（U盘、内网传输等）
```

### 3. 在目标服务器导入并运行

```bash
# 导入镜像
docker load < unimcpsim-oem.tar.gz

# 验证镜像
docker images | grep unimcpsim

# 运行容器
docker run -d \
  --name unimcpsim \
  --restart unless-stopped \
  -p 9090:9090 \
  -p 9091:9091 \
  -v /data/unimcpsim/data:/app/data \
  -v /data/unimcpsim/logs:/app/logs \
  unimcpsim:oem
```

## 常用命令

### 容器管理

```bash
# 查看运行状态
docker ps | grep unimcpsim

# 查看日志
docker logs -f unimcpsim

# 查看最近 100 行日志
docker logs --tail 100 unimcpsim

# 进入容器
docker exec -it unimcpsim /bin/bash

# 重启容器
docker restart unimcpsim

# 停止容器
docker stop unimcpsim

# 删除容器
docker rm unimcpsim
```

### Docker Compose 命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 重新构建并启动
docker-compose up -d --build
```

### 健康检查

```bash
# 检查 MCP Server 健康状态
curl http://localhost:9090/health

# 检查 Admin Panel
curl http://localhost:9091/admin/login
```

## 故障排查

### 容器无法启动

```bash
# 查看容器日志
docker logs unimcpsim

# 检查端口占用
netstat -tlnp | grep -E '9090|9091'
lsof -i :9090
lsof -i :9091
```

### 数据库问题

```bash
# 进入容器检查数据库
docker exec -it unimcpsim /bin/bash
ls -la /app/data/
sqlite3 /app/data/unimcp.db ".tables"
```

### 网络问题

```bash
# 检查容器网络
docker inspect unimcpsim | grep -A 20 "NetworkSettings"

# 测试容器内部网络
docker exec unimcpsim curl -v http://localhost:9090/health
```

### 权限问题

```bash
# 检查数据目录权限
ls -la ./data/

# 修复权限（如需要）
sudo chown -R 1000:1000 ./data ./logs
```

### 镜像构建失败

```bash
# 清理构建缓存后重试
docker builder prune -f
docker build --no-cache -t unimcpsim:oem .
```

## 生产环境建议

### 安全配置

1. **修改默认密码**：首次登录后立即修改 admin 密码
2. **限制端口暴露**：Admin Panel (9091) 建议仅内网访问
3. **使用 HTTPS**：通过反向代理（Nginx/Traefik）配置 SSL

### 反向代理示例（Nginx）

```nginx
server {
    listen 443 ssl;
    server_name mcp.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # MCP Server
    location / {
        proxy_pass http://127.0.0.1:9090;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl;
    server_name mcp-admin.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Admin Panel
    location / {
        proxy_pass http://127.0.0.1:9091;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 资源限制

在 docker-compose.yml 中添加资源限制：

```yaml
services:
  unimcpsim:
    # ... 其他配置
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 256M
```

### 日志轮转

```yaml
services:
  unimcpsim:
    # ... 其他配置
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 版本更新

### 使用 Docker Compose 更新

```bash
# 拉取最新代码
git pull origin feature/oem

# 重新构建并启动
docker-compose up -d --build
```

### 手动更新

```bash
# 停止旧容器
docker stop unimcpsim

# 备份数据
docker cp unimcpsim:/app/data ./backup/

# 删除旧容器
docker rm unimcpsim

# 构建新镜像
docker build -t unimcpsim:oem .

# 启动新容器
docker run -d \
  --name unimcpsim \
  -p 9090:9090 \
  -p 9091:9091 \
  -v $(pwd)/backup/data:/app/data \
  unimcpsim:oem
```
