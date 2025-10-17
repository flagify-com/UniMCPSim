# 常见问题 FAQ

本文档收集了 UniMCPSim 使用过程中的常见问题和解决方案。

## 目录

- [安装与配置](#安装与配置)
- [服务器运行](#服务器运行)
- [大模型配置](#大模型配置)
- [MCP 客户端集成](#mcp-客户端集成)
- [应用管理](#应用管理)
- [Token 管理](#token-管理)
- [故障排查](#故障排查)

---

## 安装与配置

### Q: 需要什么环境才能运行 UniMCPSim？

**A:** 需要以下环境：
- Python 3.9 或更高版本
- pip 包管理器
- 至少 100MB 可用磁盘空间

推荐操作系统：
- macOS 10.14+
- Linux (Ubuntu 20.04+, CentOS 7+)
- Windows 10/11

### Q: 如何安装依赖？

**A:** 在项目根目录执行：
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### Q: `.env` 文件是必需的吗？

**A:** 从 v2.6.0 开始，`.env` 文件是**可选**的。推荐使用 Web 界面配置大模型参数：

1. 启动服务器：`python start_servers.py`
2. 访问：http://localhost:9091/admin/
3. 登录并点击"大模型配置"菜单
4. 填写配置并保存

如果你需要使用 `.env` 文件（如自动化部署），可以复制 `.env.example` 为 `.env` 并填写配置。

**配置优先级**：数据库配置（Web界面）> `.env` 文件

### Q: 如何修改默认端口？

**A:** 在 `.env` 文件中配置：
```bash
MCP_SERVER_PORT=9090    # MCP服务器端口
ADMIN_SERVER_PORT=9091  # Web管理后台端口
```

---

## 服务器运行

### Q: 如何启动服务器？

**A:** 在项目根目录执行：
```bash
python start_servers.py
```

这会同时启动：
- MCP Server (默认端口 9090)
- Admin Server (默认端口 9091)

### Q: 启动时报错 "Address already in use"？

**A:** 端口被占用，有以下解决方案：

**方案1：停止占用端口的进程**
```bash
# macOS/Linux
lsof -ti :9090 | xargs kill -9
lsof -ti :9091 | xargs kill -9

# Windows (PowerShell)
Get-Process -Id (Get-NetTCPConnection -LocalPort 9090).OwningProcess | Stop-Process
Get-Process -Id (Get-NetTCPConnection -LocalPort 9091).OwningProcess | Stop-Process
```

**方案2：修改端口配置**
```bash
echo "MCP_SERVER_PORT=8090" >> .env
echo "ADMIN_SERVER_PORT=8091" >> .env
```

### Q: 如何查看日志？

**A:** 日志文件位于 `logs/` 目录：
- `unimcp_all.log` - 所有日志
- `unimcp_error.log` - 错误日志
- `unimcp_debug.log` - 调试日志 (DEBUG模式开启时)

实时查看：
```bash
tail -f logs/unimcp_all.log
```

### Q: 如何启用 DEBUG 模式？

**A:** 在 `.env` 文件中添加：
```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

重启服务器后生效。

### Q: 可以只启动 MCP Server 不启动 Admin Server 吗？

**A:** 可以，分别启动：
```bash
python mcp_server.py      # 只启动MCP服务器
python admin_server.py    # 只启动管理后台
```

但推荐使用 `python start_servers.py` 同时启动两个服务。

---

## 大模型配置

### Q: 支持哪些大模型？

**A:** 支持所有兼容 OpenAI API 格式的模型，包括：
- **OpenAI**: GPT-4, GPT-4o, GPT-4o-mini, GPT-3.5-turbo
- **阿里云通义千问**: qwen-max, qwen-plus, qwen-turbo
- **DeepSeek**: deepseek-chat, deepseek-coder
- **其他**: 任何提供 OpenAI 兼容接口的服务

### Q: 如何配置通义千问？

**A:** 通过 Web 界面配置：

1. 访问 http://localhost:9091/admin/llm-config
2. 填写配置：
   - **API Base URL**: `https://dashscope.aliyuncs.com/compatible-mode/v1`
   - **API Key**: 你的 DashScope API Key
   - **Model Name**: `qwen-max` 或 `qwen-plus`
   - **Enable Stream**: 根据需要选择
3. 点击"测试连接"验证
4. 保存配置

### Q: 如何配置 DeepSeek？

**A:** 通过 Web 界面配置：

1. 访问 http://localhost:9091/admin/llm-config
2. 填写配置：
   - **API Base URL**: `https://api.deepseek.com/v1`
   - **API Key**: 你的 DeepSeek API Key
   - **Model Name**: `deepseek-chat`
3. 测试并保存

### Q: AI 响应生成失败怎么办？

**A:** 可能的原因和解决方案：

**原因1：API Key 无效**
- 检查 API Key 是否正确
- 确认 API Key 有足够的配额

**原因2：网络连接问题**
- 检查网络连接
- 如果在国内使用 OpenAI，可能需要配置代理

**原因3：模型名称错误**
- 确认模型名称拼写正确
- 查看对应服务商的文档确认可用模型

**降级处理**：
即使 AI 不可用，系统也会返回默认响应，不会完全失败。

### Q: 配置修改后需要重启吗？

**A:** **不需要**！v2.6.0+ 支持配置热重载。通过 Web 界面保存配置后立即生效。

### Q: Enable Thinking 和 Enable Stream 是什么？

**A:**

**Enable Thinking**:
- 用途：控制大模型是否启用"思考过程"输出
- 默认值：`false` (禁用)
- 建议：保持禁用，避免干扰 JSON 输出格式
- 适用场景：仅在调试或特定模型要求时启用

**Enable Stream**:
- 用途：控制是否使用流式输出
- 默认值：`false` (禁用)
- 建议：根据模型要求设置（如 qwq-32b 强制要求启用）
- 注意：流式模式下无法获取 token 使用统计

---

## MCP 客户端集成

### Q: 如何在 Cherry Studio 中配置？

**A:**

1. 在 Web 管理界面创建 Token 并授权应用
2. 点击应用的"MCP配置"按钮生成配置
3. 复制配置内容
4. 在 Cherry Studio 设置中添加 MCP Server
5. 粘贴配置并保存

详细图文教程见项目 README。

### Q: 如何在 Claude Desktop 中配置？

**A:**

1. 获取 MCP 配置（同上）
2. 找到 Claude Desktop 配置文件：
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
3. 编辑文件，添加配置到 `mcpServers` 部分
4. 重启 Claude Desktop

### Q: 为什么 MCP 客户端显示"连接失败"？

**A:** 检查以下几点：

1. **服务器是否启动**：访问 http://localhost:9090/health 确认
2. **Token 是否有效**：在管理后台查看 Token 状态
3. **Token 是否有权限**：确认 Token 已授权对应的应用
4. **URL 是否正确**：格式应为 `http://127.0.0.1:9090/{Category}/{Product}?token=xxx`
5. **防火墙**：确认端口未被防火墙阻止

### Q: MCP 客户端收到 401 错误？

**A:** Token 认证失败，可能原因：
- Token 不存在或拼写错误
- Token 已被禁用
- Token 没有授权访问该应用

解决：在管理后台检查 Token 状态和权限。

---

## 应用管理

### Q: 如何创建新的模拟应用？

**A:** 两种方式：

**方式1：手动创建**
1. 登录管理后台
2. 进入"应用管理"页面
3. 点击"创建新应用"
4. 填写基本信息和动作定义
5. 保存

**方式2：AI 辅助生成**
1. 在创建应用时，使用"AI辅助生成"功能
2. 输入自然语言描述动作需求
3. AI 自动生成动作定义 JSON
4. 检查并保存

### Q: 应用名称有什么限制？

**A:** 应用的 `category` 和 `name` 字段必须符合 URL-safe 规则：
- 只能包含字母、数字、下划线 `_` 和连字符 `-`
- 长度 2-50 个字符
- 不能包含空格、特殊字符

示例：
- ✅ 正确：`Security`, `VirusTotal`, `WeChat_Work`, `cisco-router`
- ❌ 错误：`安全类`, `Virus Total`, `Switch#01`

### Q: 如何查看应用的详细信息？

**A:** 在应用管理页面，点击应用名称即可查看：
- 基本信息（分类、名称、描述）
- 完整的动作列表
- 每个动作的参数定义

### Q: 可以导入/导出应用配置吗？

**A:** 当前版本暂不支持。计划在未来版本添加：
- JSON 格式导出
- 批量导入
- 应用模板市场

---

## Token 管理

### Q: 如何创建 Token？

**A:**
1. 登录管理后台
2. 进入"Token管理"页面
3. 点击"创建新Token"
4. 填写描述并保存
5. 系统自动生成唯一 Token

### Q: 如何给 Token 授权应用？

**A:**
1. 在 Token 列表中找到对应 Token
2. 点击"查看"按钮
3. 在权限管理弹窗中勾选需要授权的应用
4. 可以使用"全选/取消全选"快速操作
5. 点击"保存"

### Q: 一个 Token 可以访问多个应用吗？

**A:** 可以！一个 Token 可以授权访问多个应用，在权限管理中勾选即可。

### Q: 如何禁用 Token 而不删除？

**A:** 在 Token 编辑页面，取消勾选"启用"状态即可。禁用后该 Token 无法用于 API 调用，但历史记录保留。

### Q: Token 会过期吗？

**A:** 当前版本 Token 不会过期，永久有效（除非手动禁用或删除）。未来版本计划添加过期时间和自动轮换功能。

---

## 故障排查

### Q: 数据库文件损坏怎么办？

**A:**

**方案1：使用备份**
```bash
cp data/unimcp.db.backup data/unimcp.db
```

**方案2：重新初始化**
```bash
rm -rf data/
python init_simulators.py
```

注意：重新初始化会丢失所有自定义数据，请谨慎操作。

### Q: Web 界面显示空白或样式错乱？

**A:** 可能原因和解决方案：

**原因1：静态文件未加载**
- 检查 `static/` 目录是否完整
- 检查浏览器控制台是否有 404 错误

**原因2：浏览器缓存**
- 清除浏览器缓存
- 硬刷新：Ctrl+F5 (Windows) 或 Cmd+Shift+R (Mac)

**原因3：Flask 路由问题**
- 重启 Admin Server

### Q: 忘记管理员密码怎么办？

**A:** 使用密码重置工具：
```bash
python reset_admin_password.py
```

按提示输入新密码即可。

### Q: MCP 调用非常慢？

**A:** 可能原因：

**原因1：AI API 响应慢**
- 检查网络延迟
- 考虑更换更快的模型（如 gpt-3.5-turbo）
- 考虑使用国内服务（通义千问、DeepSeek）

**原因2：数据库查询慢**
- 检查数据库文件大小
- 考虑清理旧的审计日志

**原因3：日志级别过高**
- 将 DEBUG 模式关闭
- 设置 `LOG_LEVEL=INFO`

### Q: 代理设置导致无法连接 OpenAI？

**A:** 取消代理环境变量：
```bash
unset HTTPS_PROXY
unset HTTP_PROXY
unset https_proxy
unset http_proxy
```

或者在 `.env` 中配置国内可用的代理地址。

### Q: 如何完全重置系统？

**A:**
```bash
# 停止所有服务
lsof -ti :9090,9091 | xargs kill -9

# 删除数据和日志
rm -rf data/ logs/

# 重新初始化
python init_simulators.py

# 启动服务
python start_servers.py
```

**警告**：此操作会删除所有数据，包括自定义应用、Token、用户等。

---

## 性能优化

### Q: 如何提升响应速度？

**A:**

1. **使用更快的模型**：gpt-3.5-turbo 比 gpt-4o 快很多
2. **减少提示词长度**：优化提示词模板，去掉不必要的内容
3. **启用缓存**（计划中）：对常见请求缓存响应
4. **使用国内服务**：通义千问、DeepSeek 在国内访问更快

### Q: 数据库太大怎么办？

**A:**

**清理审计日志**：
```python
from models import DatabaseManager
db = DatabaseManager()
# 删除30天前的日志
db.cleanup_old_logs(days=30)
```

或者手动删除：
```bash
sqlite3 data/unimcp.db "DELETE FROM audit_logs WHERE created_at < datetime('now', '-30 days')"
```

---

## 其他问题

### Q: 支持多用户吗？

**A:** 当前版本只支持单个管理员账户。多用户支持计划在未来版本添加。

### Q: 可以部署到云服务器吗？

**A:** 可以！但需要注意：
1. 配置防火墙规则开放端口
2. 考虑使用反向代理（Nginx/Caddy）
3. 配置 HTTPS（生产环境强烈推荐）
4. 考虑使用 systemd 或 Docker 部署

### Q: 有 Docker 镜像吗？

**A:** 当前版本暂无官方 Docker 镜像。你可以自己构建：

```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 9090 9091
CMD ["python", "start_servers.py"]
```

### Q: 如何贡献代码或报告问题？

**A:**
- **Bug 报告**: 在 GitHub Issues 提交
- **功能建议**: 在 GitHub Issues 提交
- **代码贡献**: 提交 Pull Request

### Q: 有社区或交流群吗？

**A:** 当前暂无官方社区。如有需求可在 GitHub Issues 反馈。

---

## 联系支持

如果你的问题在这里没有找到答案：

1. 查看 [项目文档](../README.md)
2. 查看 [架构设计](architecture.md)
3. 查看 [API 参考](api.md)
4. 在 [GitHub Issues](https://github.com/wzfukui/UniMCPSim/issues) 提问

---

> 最后更新：2024-10-17 | 版本：v2.6.0
