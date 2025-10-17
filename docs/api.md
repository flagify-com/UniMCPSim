# API 参考文档

本文档详细介绍 UniMCPSim 的 API 接口规范。

## 目录

- [MCP Server API](#mcp-server-api)
- [Admin Server API](#admin-server-api)
- [认证方式](#认证方式)
- [错误处理](#错误处理)
- [示例代码](#示例代码)

---

## MCP Server API

### 基础信息

- **Base URL**: `http://localhost:9090` (默认端口，可通过环境变量配置)
- **协议**: HTTP/HTTPS
- **认证**: Token 参数 (`?token=xxx`)
- **Content-Type**: `application/json`

### 1. 健康检查

检查 MCP Server 是否正常运行。

**端点**: `GET /health`

**请求示例**:
```bash
curl http://localhost:9090/health
```

**响应**:
```json
{
  "status": "healthy",
  "service": "UniMCPSim MCP Server",
  "version": "2.6.0"
}
```

### 2. 产品专用端点

访问特定产品的 MCP 服务。

**端点**: `POST /{Category}/{Product}?token={token}`

**URL 参数**:
- `Category`: 应用分类 (如 Security, IM, Network)
- `Product`: 产品名称 (如 VirusTotal, WeChat, HuaweiSwitch)
- `token`: 访问令牌 (必需)

**支持的 MCP 方法**:

#### 2.1 初始化 (initialize)

**请求体**:
```json
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "test-client",
      "version": "1.0.0"
    }
  },
  "id": 1
}
```

**响应**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {},
      "resources": {},
      "prompts": {}
    },
    "serverInfo": {
      "name": "UniMCPSim",
      "version": "2.6.0"
    }
  },
  "id": 1
}
```

#### 2.2 列出工具 (tools/list)

**请求体**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": 1
}
```

**响应**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [
      {
        "name": "scan_url",
        "description": "扫描指定URL的安全漏洞",
        "inputSchema": {
          "type": "object",
          "properties": {
            "target_url": {
              "type": "string",
              "description": "目标URL"
            },
            "scan_type": {
              "type": "string",
              "description": "扫描类型: quick/full"
            }
          },
          "required": ["target_url"]
        }
      }
    ]
  },
  "id": 1
}
```

#### 2.3 调用工具 (tools/call)

**请求体**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "scan_url",
    "arguments": {
      "target_url": "https://example.com",
      "scan_type": "quick"
    }
  },
  "id": 2
}
```

**响应**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"success\":true,\"scan_id\":\"scan_20241017_123456\",\"vulnerabilities\":{\"high\":0,\"medium\":2,\"low\":5}}"
      }
    ]
  },
  "id": 2
}
```

#### 2.4 列出资源 (resources/list)

**请求体**:
```json
{
  "jsonrpc": "2.0",
  "method": "resources/list",
  "id": 1
}
```

**响应**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "resources": [
      {
        "uri": "unimcpsim://Security/VirusTotal/status",
        "name": "服务状态",
        "description": "获取VirusTotal服务的当前状态",
        "mimeType": "application/json"
      }
    ]
  },
  "id": 1
}
```

#### 2.5 列出提示词 (prompts/list)

**请求体**:
```json
{
  "jsonrpc": "2.0",
  "method": "prompts/list",
  "id": 1
}
```

**响应**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "prompts": [
      {
        "name": "security_scan",
        "description": "执行安全扫描任务",
        "arguments": [
          {
            "name": "target",
            "description": "扫描目标",
            "required": true
          }
        ]
      }
    ]
  },
  "id": 1
}
```

### 完整请求示例

```bash
curl -X POST "http://localhost:9090/Security/VirusTotal?token=demo-token-123" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "query_ip",
      "arguments": {
        "ip": "8.8.8.8"
      }
    },
    "id": 1
  }'
```

---

## Admin Server API

### 基础信息

- **Base URL**: `http://localhost:9091` (默认端口，可通过环境变量配置)
- **认证**: Session Cookie (登录后自动设置)
- **Content-Type**: `application/json`

### 1. 认证相关

#### 1.1 登录

**端点**: `POST /admin/login`

**请求体**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**响应**:
```json
{
  "message": "登录成功",
  "username": "admin"
}
```

**错误响应**:
```json
{
  "error": "用户名或密码错误"
}
```

#### 1.2 登出

**端点**: `GET /admin/logout`

**响应**: 重定向到登录页面

#### 1.3 修改密码

**端点**: `POST /admin/change-password`

**请求体**:
```json
{
  "old_password": "admin123",
  "new_password": "new_password_123"
}
```

**响应**:
```json
{
  "message": "密码修改成功"
}
```

### 2. 应用管理

#### 2.1 获取应用列表

**端点**: `GET /admin/api/apps`

**响应**:
```json
{
  "apps": [
    {
      "id": 1,
      "category": "Security",
      "name": "VirusTotal",
      "display_name": "VirusTotal威胁情报",
      "description": "查询IP/域名/文件的威胁情报",
      "actions": [...],
      "created_at": "2024-10-17T10:00:00Z"
    }
  ]
}
```

#### 2.2 创建应用

**端点**: `POST /admin/api/apps`

**请求体**:
```json
{
  "category": "Security",
  "name": "NewScanner",
  "display_name": "新扫描器",
  "description": "扫描器描述",
  "ai_notes": "特殊要求说明",
  "actions": [
    {
      "name": "scan",
      "display_name": "扫描",
      "description": "执行扫描",
      "parameters": [
        {
          "key": "target",
          "type": "String",
          "required": true,
          "description": "扫描目标"
        }
      ]
    }
  ]
}
```

**响应**:
```json
{
  "message": "应用创建成功",
  "app": {
    "id": 10,
    "category": "Security",
    "name": "NewScanner",
    ...
  }
}
```

#### 2.3 更新应用

**端点**: `PUT /admin/api/apps/{app_id}`

**请求体**: 同创建应用

**响应**:
```json
{
  "message": "应用更新成功"
}
```

#### 2.4 删除应用

**端点**: `DELETE /admin/api/apps/{app_id}`

**响应**:
```json
{
  "message": "应用删除成功"
}
```

### 3. Token 管理

#### 3.1 获取 Token 列表

**端点**: `GET /admin/api/tokens`

**响应**:
```json
{
  "tokens": [
    {
      "id": 1,
      "token": "demo-token-123",
      "description": "演示Token",
      "enabled": true,
      "apps_count": 5,
      "created_at": "2024-10-17T10:00:00Z"
    }
  ]
}
```

#### 3.2 创建 Token

**端点**: `POST /admin/api/tokens`

**请求体**:
```json
{
  "description": "新Token"
}
```

**响应**:
```json
{
  "message": "Token创建成功",
  "token": {
    "id": 5,
    "token": "auto-generated-token-xyz",
    "description": "新Token",
    "enabled": true
  }
}
```

#### 3.3 更新 Token 权限

**端点**: `PUT /admin/api/tokens/{token_id}/apps`

**请求体**:
```json
{
  "app_ids": [1, 2, 3, 5, 8]
}
```

**响应**:
```json
{
  "message": "Token权限更新成功"
}
```

#### 3.4 删除 Token

**端点**: `DELETE /admin/api/tokens/{token_id}`

**响应**:
```json
{
  "message": "Token删除成功"
}
```

### 4. 提示词模板管理

#### 4.1 获取模板列表

**端点**: `GET /admin/api/prompts`

**响应**:
```json
{
  "prompts": [
    {
      "id": 1,
      "name": "response_simulation",
      "display_name": "响应模拟提示词",
      "description": "用于模拟MCP工具调用响应",
      "template": "你是{app_display_name}系统的模拟器...",
      "variables": [...],
      "enabled": true
    }
  ]
}
```

#### 4.2 更新模板

**端点**: `PUT /admin/api/prompts/{prompt_id}`

**请求体**:
```json
{
  "template": "修改后的模板内容..."
}
```

**响应**:
```json
{
  "message": "模板更新成功"
}
```

### 5. 大模型配置 (v2.6.0+)

#### 5.1 获取配置

**端点**: `GET /admin/api/llm-config`

**响应**:
```json
{
  "api_key": "sk-xxx***xxx",
  "api_base_url": "https://api.openai.com/v1",
  "model_name": "gpt-4o-mini",
  "enable_thinking": false,
  "enable_stream": false
}
```

> 注意: API Key 会自动脱敏显示

#### 5.2 保存配置

**端点**: `POST /admin/api/llm-config`

**请求体**:
```json
{
  "api_key": "sk-xxxxxxxxxxxxxxxx",
  "api_base_url": "https://api.openai.com/v1",
  "model_name": "gpt-4o-mini",
  "enable_thinking": false,
  "enable_stream": false
}
```

**响应**:
```json
{
  "message": "配置保存成功，已重新加载配置"
}
```

#### 5.3 测试连接

**端点**: `POST /admin/api/llm-config/test`

**请求体**: 同保存配置

**响应** (成功):
```json
{
  "success": true,
  "message": "连接测试成功",
  "model": "gpt-4o-mini",
  "response": "我是一个AI助手...",
  "duration": "1.23秒"
}
```

**响应** (失败):
```json
{
  "success": false,
  "error": "API Key无效或网络连接失败"
}
```

### 6. 操作日志

#### 6.1 获取日志列表

**端点**: `GET /admin/api/logs`

**查询参数**:
- `page`: 页码 (默认1)
- `per_page`: 每页数量 (默认50)
- `action`: 过滤操作类型 (可选)

**响应**:
```json
{
  "logs": [
    {
      "id": 123,
      "user_id": 1,
      "username": "admin",
      "action": "create_app",
      "target_type": "Application",
      "target_id": 10,
      "details": {...},
      "ip_address": "127.0.0.1",
      "created_at": "2024-10-17T15:30:00Z"
    }
  ],
  "total": 500,
  "page": 1,
  "per_page": 50
}
```

---

## 认证方式

### MCP Server 认证

使用 URL 参数传递 Token：

```
http://localhost:9090/{Category}/{Product}?token={your_token}
```

Token 验证流程：
1. 从 URL 参数提取 token
2. 查询数据库验证 token 是否存在且启用
3. 检查 token 对应用的访问权限
4. 验证通过后继续处理请求

### Admin Server 认证

使用 Session Cookie：

1. 通过 `/admin/login` 登录
2. 服务器设置 Session Cookie
3. 后续请求自动携带 Cookie
4. 服务器验证 Session 有效性

---

## 错误处理

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 (Token无效或未登录) |
| 403 | 禁止访问 (无权限) |
| 404 | 资源不存在 |
| 406 | 不可接受 (缺少必需的Accept头) |
| 500 | 服务器内部错误 |

### 错误响应格式

```json
{
  "error": "错误描述信息",
  "code": "ERROR_CODE",
  "details": {
    "field": "具体错误字段",
    "message": "详细错误信息"
  }
}
```

### 常见错误

#### MCP Server 错误

**Token 无效**:
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32000,
    "message": "Invalid or missing token"
  },
  "id": 1
}
```

**应用不存在**:
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32001,
    "message": "Application not found: Security/InvalidApp"
  },
  "id": 1
}
```

**动作不存在**:
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32002,
    "message": "Action not found: invalid_action"
  },
  "id": 1
}
```

#### Admin Server 错误

**未登录**:
```json
{
  "error": "Unauthorized",
  "message": "请先登录"
}
```

**应用名称验证失败**:
```json
{
  "error": "应用名称只能包含字母、数字、下划线和连字符"
}
```

---

## 示例代码

### Python 示例

```python
import requests

# MCP Server 调用
def call_mcp_tool():
    url = "http://localhost:9090/Security/VirusTotal"
    params = {"token": "demo-token-123"}
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "query_ip",
            "arguments": {"ip": "8.8.8.8"}
        },
        "id": 1
    }

    response = requests.post(url, params=params, json=payload)
    return response.json()

# Admin Server 调用
def create_app():
    # 先登录
    session = requests.Session()
    session.post(
        "http://localhost:9091/admin/login",
        json={"username": "admin", "password": "admin123"}
    )

    # 创建应用
    app_data = {
        "category": "Security",
        "name": "NewScanner",
        "display_name": "新扫描器",
        "description": "描述",
        "actions": [...]
    }

    response = session.post(
        "http://localhost:9091/admin/api/apps",
        json=app_data
    )
    return response.json()
```

### JavaScript 示例

```javascript
// MCP Server 调用
async function callMcpTool() {
  const url = "http://localhost:9090/Security/VirusTotal?token=demo-token-123";
  const payload = {
    jsonrpc: "2.0",
    method: "tools/call",
    params: {
      name: "query_ip",
      arguments: { ip: "8.8.8.8" }
    },
    id: 1
  };

  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  return await response.json();
}

// Admin Server 调用
async function createApp() {
  // 先登录
  await fetch("http://localhost:9091/admin/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: "admin",
      password: "admin123"
    }),
    credentials: "include" // 重要：携带Cookie
  });

  // 创建应用
  const appData = {
    category: "Security",
    name: "NewScanner",
    display_name: "新扫描器",
    description: "描述",
    actions: [...]
  };

  const response = await fetch("http://localhost:9091/admin/api/apps", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(appData),
    credentials: "include" // 重要：携带Cookie
  });

  return await response.json();
}
```

### cURL 示例

```bash
# MCP Server - 查询威胁情报
curl -X POST "http://localhost:9090/Security/VirusTotal?token=demo-token-123" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "query_ip",
      "arguments": {"ip": "8.8.8.8"}
    },
    "id": 1
  }'

# Admin Server - 登录
curl -X POST "http://localhost:9091/admin/login" \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username": "admin", "password": "admin123"}'

# Admin Server - 创建应用 (使用保存的Cookie)
curl -X POST "http://localhost:9091/admin/api/apps" \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "category": "Security",
    "name": "NewScanner",
    "display_name": "新扫描器",
    "description": "描述",
    "actions": [...]
  }'
```

---

## 速率限制

当前版本暂未实现速率限制，后续版本将添加：

- MCP Server: 100 请求/分钟/Token
- Admin Server: 60 请求/分钟/IP

---

> **相关文档**: [架构设计](architecture.md) | [提示词模板系统](prompt_template_system.md)
