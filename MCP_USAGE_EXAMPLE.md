# UniMCPSim MCP服务器使用示例

本文档详细说明如何使用UniMCPSim的MCP服务器，以**企业微信(/IM/WeChat)**为例演示完整的使用流程。

## 🔗 MCP服务器地址

### 新版本 - 产品特定端点（推荐）

**URL格式**: `http://localhost:8080/<Category>/<Product>?token=<your-token>`

**示例端点**:
- 企业微信: `http://localhost:8080/IM/WeChat?token=<your-token>`
- 华为交换机: `http://localhost:8080/Network/HuaweiSwitch?token=<your-token>`
- 深信服防火墙: `http://localhost:8080/Firewall/Sangfor?token=<your-token>`

### 传统格式（兼容性支持）

**基础地址**: `http://localhost:8080/mcp`

**完整URL格式**: `http://localhost:8080/mcp?token=<your-token>`

> ✨ **新特性**: 现在支持产品特定的URL端点，每个应用都有独立的MCP服务地址！
> 🌐 **CORS支持**: 已启用CORS策略，支持任意来源的跨域请求

## 🎫 Demo Token

**默认Demo Token**: `f1bb3770-6e46-4fe6-b518-e1c738c7b6a4`

> ⚠️ 注意：这是系统自动生成的Demo Token，具有所有应用的访问权限，仅用于测试。

## 📋 企业微信可用动作

企业微信模拟器支持以下动作：

### 1. send_message - 发送消息
**参数**:
- `to_user` (String, 必填) - 接收用户ID
- `text` (String, 必填) - 消息内容

### 2. create_group - 创建群组
**参数**:
- `group_name` (String, 必填) - 群组名称
- `members` (Array, 可选) - 成员列表

## 🚀 完整使用示例

### 步骤1：初始化MCP连接

#### 方式一：使用产品特定端点（推荐）

```bash
curl -X POST "http://localhost:8080/IM/WeChat?token=f1bb3770-6e46-4fe6-b518-e1c738c7b6a4" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
      "protocolVersion": "0.1.0",
      "capabilities": {},
      "clientInfo": {
        "name": "demo-client",
        "version": "1.0.0"
      }
    },
    "id": 1
  }' \
  -D headers.txt
```

#### 方式二：使用传统端点（兼容性）

```bash
curl -X POST "http://localhost:8080/mcp?token=f1bb3770-6e46-4fe6-b518-e1c738c7b6a4" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
      "protocolVersion": "0.1.0",
      "capabilities": {},
      "clientInfo": {
        "name": "demo-client",
        "version": "1.0.0"
      }
    },
    "id": 1
  }' \
  -D headers.txt
```

**响应示例**:
```
event: message
data: {
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "experimental": {},
      "prompts": {"listChanged": true},
      "resources": {"subscribe": false, "listChanged": true},
      "tools": {"listChanged": true}
    },
    "serverInfo": {
      "name": "UniMCPSim",
      "version": "1.0.0"
    },
    "instructions": "Universal MCP Simulator - 通用MCP模拟器，可动态模拟各种产品的API接口"
  }
}
```

**重要**: 从响应头中提取`mcp-session-id`：
```bash
session_id=$(grep -i 'mcp-session-id:' headers.txt | tr -d '\r' | cut -d' ' -f2-)
echo "会话ID: $session_id"
```

### 步骤2：企业微信发送消息示例

#### 方式一：使用产品特定端点（推荐）

```bash
# 使用提取的会话ID
curl -X POST "http://localhost:8080/IM/WeChat?token=f1bb3770-6e46-4fe6-b518-e1c738c7b6a4" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $session_id" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "execute_action",
      "arguments": {
        "token": "f1bb3770-6e46-4fe6-b518-e1c738c7b6a4",
        "category": "IM",
        "product": "WeChat",
        "action": "send_message",
        "parameters": {
          "to_user": "zhang.san",
          "text": "项目会议将于明天下午2点在A会议室举行，请准时参加。"
        }
      }
    },
    "id": 2
  }'
```

#### 方式二：使用传统端点

```bash
# 使用提取的会话ID
curl -X POST "http://localhost:8080/mcp?token=f1bb3770-6e46-4fe6-b518-e1c738c7b6a4" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $session_id" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "execute_action",
      "arguments": {
        "token": "f1bb3770-6e46-4fe6-b518-e1c738c7b6a4",
        "category": "IM",
        "product": "WeChat",
        "action": "send_message",
        "parameters": {
          "to_user": "zhang.san",
          "text": "项目会议将于明天下午2点在A会议室举行，请准时参加。"
        }
      }
    },
    "id": 2
  }'
```

**响应示例**:
```
event: message
data: {
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [{
      "type": "text",
      "text": "{
        \"errcode\": 0,
        \"errmsg\": \"ok\",
        \"msgid\": \"1234567890\",
        \"to_user\": \"zhang.san\",
        \"text\": \"项目会议将于明天下午2点在A会议室举行，请准时参加。\",
        \"timestamp\": 1698444800
      }"
    }]
  }
}
```

### 步骤3：企业微信创建群组示例

#### 使用产品特定端点

```bash
curl -X POST "http://localhost:8080/IM/WeChat?token=f1bb3770-6e46-4fe6-b518-e1c738c7b6a4" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $session_id" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "execute_action",
      "arguments": {
        "token": "f1bb3770-6e46-4fe6-b518-e1c738c7b6a4",
        "category": "IM",
        "product": "WeChat",
        "action": "create_group",
        "parameters": {
          "group_name": "项目开发小组",
          "members": ["zhang.san", "li.si", "wang.wu"]
        }
      }
    },
    "id": 3
  }'
```

### 步骤4：查看应用信息（新功能）

```bash
# GET请求获取应用详细信息和可用动作
curl -X GET "http://localhost:8080/IM/WeChat?token=f1bb3770-6e46-4fe6-b518-e1c738c7b6a4" \
  -H "Accept: application/json"
```

**响应示例**:
```json
{
  "category": "IM",
  "name": "WeChat",
  "display_name": "企业微信",
  "description": "企业即时通讯工具",
  "actions": [
    {
      "name": "send_message",
      "display_name": "发送消息",
      "description": "发送文本消息",
      "parameters": [
        {"key": "to_user", "type": "String", "required": true, "description": "接收用户ID"},
        {"key": "text", "type": "String", "required": true, "description": "消息内容"}
      ]
    },
    {
      "name": "create_group",
      "display_name": "创建群组",
      "description": "创建讨论群组",
      "parameters": [
        {"key": "name", "type": "String", "required": true, "description": "群组名称"},
        {"key": "members", "type": "Array", "required": true, "description": "成员ID列表"}
      ]
    }
  ]
}
```

## 🛠️ 一键测试脚本

创建文件 `test_wechat.sh`：

```bash
#!/bin/bash

# 设置变量
MCP_SERVER="http://localhost:8080/IM/WeChat"  # 使用产品特定端点
TOKEN="f1bb3770-6e46-4fe6-b518-e1c738c7b6a4"

echo "=== UniMCPSim 企业微信测试（产品特定端点）==="

# 步骤1：初始化连接
echo "1. 初始化MCP连接..."
init_response=$(curl -s -X POST "${MCP_SERVER}?token=${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
      "protocolVersion": "0.1.0",
      "capabilities": {},
      "clientInfo": {"name": "test-client", "version": "1.0.0"}
    },
    "id": 1
  }' \
  -D /tmp/headers.txt)

# 提取会话ID
session_id=$(grep -i 'mcp-session-id:' /tmp/headers.txt | tr -d '\r' | cut -d' ' -f2-)

if [ -z "$session_id" ]; then
    echo "❌ 获取会话ID失败"
    exit 1
fi

echo "✅ 连接成功，会话ID: $session_id"

# 步骤2：发送消息
echo ""
echo "2. 测试企业微信发送消息..."
msg_response=$(curl -s -X POST "${MCP_SERVER}?token=${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $session_id" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "execute_action",
      "arguments": {
        "token": "'$TOKEN'",
        "category": "IM",
        "product": "WeChat",
        "action": "send_message",
        "parameters": {
          "to_user": "test.user",
          "text": "这是一条测试消息"
        }
      }
    },
    "id": 2
  }')

if echo "$msg_response" | grep -q "event: message"; then
    echo "✅ 消息发送成功"
    echo "$msg_response" | grep "data:" | sed 's/data: //'
else
    echo "❌ 消息发送失败"
    echo "$msg_response"
fi

# 步骤3：创建群组
echo ""
echo "3. 测试企业微信创建群组..."
group_response=$(curl -s -X POST "${MCP_SERVER}?token=${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $session_id" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "execute_action",
      "arguments": {
        "token": "'$TOKEN'",
        "category": "IM",
        "product": "WeChat",
        "action": "create_group",
        "parameters": {
          "group_name": "测试群组",
          "members": ["user1", "user2", "user3"]
        }
      }
    },
    "id": 3
  }')

if echo "$group_response" | grep -q "event: message"; then
    echo "✅ 群组创建成功"
    echo "$group_response" | grep "data:" | sed 's/data: //'
else
    echo "❌ 群组创建失败"
    echo "$group_response"
fi

echo ""
echo "=== 测试完成 ==="
```

使用方法：
```bash
chmod +x test_wechat.sh
./test_wechat.sh
```

## 📋 其他应用示例

### VirusTotal IP扫描

```bash
# 替换action参数即可
{
  "category": "Security",
  "product": "VirusTotal",
  "action": "scan_ip",
  "parameters": {
    "ip": "8.8.8.8"
  }
}
```

### Jira创建工单

```bash
{
  "category": "Ticket",
  "product": "Jira",
  "action": "create_issue",
  "parameters": {
    "title": "系统Bug修复",
    "description": "发现登录页面存在显示问题",
    "priority": "High"
  }
}
```

### 华为交换机查看接口

```bash
{
  "category": "Network",
  "product": "HuaweiSwitch",
  "action": "show_interfaces",
  "parameters": {}
}
```

## 🐍 Python客户端示例

```python
import asyncio
import httpx
import json

class UniMCPSimClient:
    def __init__(self, base_url="http://localhost:8080", token=None, product_path=None):
        self.base_url = base_url
        self.token = token
        self.product_path = product_path  # 例如: "IM/WeChat"
        self.session_id = None

    @property
    def endpoint_url(self):
        """获取完整的端点URL"""
        if self.product_path:
            return f"{self.base_url}/{self.product_path}"
        else:
            return f"{self.base_url}/mcp"

    async def initialize(self):
        """初始化MCP连接"""
        async with httpx.AsyncClient() as client:
            payload = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "0.1.0",
                    "capabilities": {},
                    "clientInfo": {"name": "python-client", "version": "1.0.0"}
                },
                "id": 1
            }

            response = await client.post(
                f"{self.endpoint_url}?token={self.token}",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            )

            # 提取会话ID
            self.session_id = response.headers.get('mcp-session-id')
            return response.status_code == 200

    async def execute_action(self, category, product, action, parameters):
        """执行模拟器动作"""
        if not self.session_id:
            raise Exception("请先调用initialize()初始化连接")

        async with httpx.AsyncClient() as client:
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "execute_action",
                    "arguments": {
                        "token": self.token,
                        "category": category,
                        "product": product,
                        "action": action,
                        "parameters": parameters
                    }
                },
                "id": 2
            }

            response = await client.post(
                f"{self.endpoint_url}?token={self.token}",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                    "mcp-session-id": self.session_id
                }
            )

            return response.text

# 使用示例
async def main():
    # 使用产品特定端点（推荐）
    client = UniMCPSimClient(
        token="f1bb3770-6e46-4fe6-b518-e1c738c7b6a4",
        product_path="IM/WeChat"
    )

    # 初始化连接
    if await client.initialize():
        print("✅ MCP连接初始化成功")

        # 企业微信发送消息
        result = await client.execute_action(
            category="IM",
            product="WeChat",
            action="send_message",
            parameters={
                "to_user": "zhang.san",
                "text": "Python客户端测试消息"
            }
        )
        print("发送消息结果:", result)

        # 企业微信创建群组
        result = await client.execute_action(
            category="IM",
            product="WeChat",
            action="create_group",
            parameters={
                "group_name": "Python测试群",
                "members": ["user1", "user2"]
            }
        )
        print("创建群组结果:", result)
    else:
        print("❌ MCP连接初始化失败")

# 运行示例
if __name__ == "__main__":
    asyncio.run(main())
```

## 🔍 调试和故障排除

### 常见错误

1. **HTTP 406 Not Acceptable**
   - 缺少正确的Accept头
   - 解决：添加 `Accept: application/json, text/event-stream`

2. **HTTP 400 Bad Request: Missing session ID**
   - 未先进行initialize或session ID丢失
   - 解决：先调用initialize方法获取session ID

3. **HTTP 401 Unauthorized**
   - Token无效或已过期
   - 解决：检查Token是否正确

4. **工具调用返回error**
   - 参数不正确或缺少必填参数
   - 解决：检查API文档确认参数格式

### 查看详细日志

启动服务器时可以看到详细的请求日志：
```bash
python mcp_server.py
```

### 获取可用Token

```bash
# 通过Web管理后台
curl "http://localhost:8081/admin/api/tokens" -H "Authorization: Bearer <session>"

# 或直接查询数据库
python -c "
from models import db_manager, Token
session = db_manager.get_session()
tokens = session.query(Token).filter_by(enabled=True).all()
for token in tokens:
    print(f'{token.name}: {token.token}')
session.close()
"
```

## 📚 更多资源

- **完整文档**: [README.md](README.md)
- **快速开始**: [QUICKSTART.md](QUICKSTART.md)
- **Web管理后台**: http://localhost:8081/admin/
- **所有可用应用**: 运行 `python tests/simple_test.py` 查看

---

**恭喜！您已经掌握了UniMCPSim MCP服务器的使用方法！** 🎉

现在您可以：
- 🔌 集成到您的应用中
- 🧪 进行API测试和开发
- 🛠️ 自定义更多模拟器
- 📊 监控使用情况