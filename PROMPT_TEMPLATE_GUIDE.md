# UniMCPSim 提示词模板系统完全指南

## 📋 系统概述

当用户发起请求到 UniMCPSim（如 `http://127.0.0.1:8080/Scanner/BBScan?token=xxx`）时，系统使用提示词模板来生成智能的 API 响应。

## 🔄 完整工作流程

```
用户请求 → Token验证 → 获取应用 → 获取模板 → 变量替换 → AI生成 → 返回响应
```

## 📊 提示词模板结构

### 数据库存储

提示词模板存储在 SQLite 数据库的 `prompt_templates` 表中：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String(100) | 模板名称（唯一标识） |
| display_name | String(200) | 显示名称 |
| description | Text | 模板描述 |
| template | Text | 模板内容（包含变量占位符） |
| variables | JSON | 变量定义列表 |
| enabled | Boolean | 是否启用 |

### 默认模板

系统预置了两个核心模板：

#### 1. response_simulation（响应模拟）
```
你是{app_name}系统的模拟器。用户调用了{action}操作，参数如下：
{parameters}

请生成一个真实的API响应结果（JSON格式）。响应应该：
1. 符合真实系统的响应格式
2. 包含合理的数据
3. 反映操作的成功或失败状态

直接返回JSON，不要任何其他说明文字。
```

#### 2. action_generation（动作生成）
用于自动生成应用的动作定义（创建新应用时使用）

## 🔧 模板变量系统

### response_simulation 的变量

| 变量名 | 来源 | 示例值 |
|--------|------|--------|
| `{app_name}` | app.display_name | "BBScan网站扫描器" |
| `{action}` | 请求的 tool name | "scan_url" |
| `{parameters}` | 请求的 arguments（JSON） | `{"target_url": "https://example.com", "scan_type": "full"}` |

## 🎯 BBScan 扫描器完整示例

### 1️⃣ 用户发起请求

```http
POST http://127.0.0.1:8080/Scanner/BBScan?token=0eb0d5b1-4597-4cc9-a9df-a750455d34fa
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "scan_url",
    "arguments": {
      "target_url": "https://example.com",
      "scan_type": "full",
      "max_depth": 3,
      "follow_redirects": true
    }
  },
  "id": 2
}
```

### 2️⃣ 系统处理过程

#### 步骤 1: 路径解析和验证
```python
# mcp_server.py:296-310
category = "Scanner"
product = "BBScan"
token = "0eb0d5b1-4597-4cc9-a9df-a750455d34fa"

# 验证Token
token_info = db_manager.validate_token(token)

# 获取应用
app = db_manager.get_application_by_path(category, product)
```

#### 步骤 2: 获取应用定义
```json
{
  "category": "Scanner",
  "name": "BBScan",
  "display_name": "BBScan网站扫描器",
  "template": {
    "actions": [
      {
        "name": "scan_url",
        "parameters": [...]
      }
    ]
  }
}
```

#### 步骤 3: 处理请求（SimulatorEngine）
```python
# mcp_server.py:102 - 调用AI生成器
response = ai_generator.generate_response(
    app.display_name,  # "BBScan网站扫描器"
    action,            # "scan_url"
    params             # {"target_url": "...", ...}
)
```

#### 步骤 4: AI生成器获取模板
```python
# ai_generator.py:44-45
prompt_template = self.db_manager.get_prompt_template('response_simulation')
```

从数据库获取的原始模板：
```
你是{app_name}系统的模拟器。用户调用了{action}操作，参数如下：
{parameters}
...
```

#### 步骤 5: 准备变量并替换
```python
# ai_generator.py:47-54
variables = {
    'app_name': 'BBScan网站扫描器',
    'action': 'scan_url',
    'parameters': '''{
  "target_url": "https://example.com",
  "scan_type": "full",
  "max_depth": 3,
  "follow_redirects": true
}'''
}

prompt = prompt_template.template.format(**variables)
```

替换后的最终提示词：
```
你是BBScan网站扫描器系统的模拟器。用户调用了scan_url操作，参数如下：
{
  "target_url": "https://example.com",
  "scan_type": "full",
  "max_depth": 3,
  "follow_redirects": true
}

请生成一个真实的API响应结果（JSON格式）。响应应该：
1. 符合真实系统的响应格式
2. 包含合理的数据
3. 反映操作的成功或失败状态

直接返回JSON，不要任何其他说明文字。
```

#### 步骤 6: 发送给 OpenAI
```python
# ai_generator.py:67-75
response = self.client.chat.completions.create(
    model="gpt-4o-mini",  # 从.env配置
    messages=[
        {
            "role": "system",
            "content": "你是一个API响应模拟器，返回符合规范的JSON数据。"
        },
        {
            "role": "user",
            "content": prompt  # 替换后的完整提示词
        }
    ],
    temperature=0.7,
    max_tokens=1000
)
```

#### 步骤 7: AI 生成响应
OpenAI 返回的模拟响应：
```json
{
  "success": true,
  "scan_id": "scan_20240930_154823",
  "target_url": "https://example.com",
  "scan_type": "full",
  "status": "completed",
  "start_time": "2024-09-30T15:48:23Z",
  "end_time": "2024-09-30T15:49:45Z",
  "duration_seconds": 82,
  "statistics": {
    "total_requests": 453,
    "successful_requests": 412,
    "failed_requests": 41,
    "directories_found": 28,
    "files_found": 156,
    "scan_depth": 3
  },
  "vulnerabilities": {
    "high": 2,
    "medium": 5,
    "low": 13,
    "info": 27
  },
  "interesting_findings": [
    {
      "path": "/admin/",
      "status_code": 401,
      "type": "admin_panel",
      "severity": "high",
      "description": "发现管理后台入口，需要认证"
    },
    {
      "path": "/backup.sql",
      "status_code": 200,
      "type": "database_backup",
      "severity": "high",
      "size_bytes": 1048576,
      "description": "发现数据库备份文件"
    }
  ],
  "recommendations": [
    "移除或限制访问管理后台",
    "删除数据库备份文件",
    "配置适当的访问控制策略"
  ]
}
```

### 3️⃣ 返回给用户

最终的 MCP 响应格式：
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [{
      "type": "text",
      "text": "{...AI生成的JSON响应...}"
    }]
  }
}
```

## 🎨 自定义提示词模板

### 方法 1: 通过代码更新

```python
from models import db_manager

# 更新现有模板
db_manager.save_prompt_template(
    name="response_simulation",
    display_name="增强版响应模拟",
    description="包含更多上下文的响应模拟",
    template="""你是{app_name}系统的模拟器。
系统版本：2.0
当前时间：{timestamp}

用户调用了{action}操作，参数如下：
{parameters}

请生成一个真实且详细的API响应结果（JSON格式）。
要求：
1. 包含成功/失败状态
2. 包含时间戳
3. 包含请求ID
4. 反映真实的业务逻辑

只返回JSON，无需其他说明。""",
    variables=[
        {"name": "app_name", "description": "应用名称"},
        {"name": "action", "description": "动作名称"},
        {"name": "parameters", "description": "调用参数"},
        {"name": "timestamp", "description": "当前时间戳"}
    ]
)
```

### 方法 2: 创建专用模板

```python
# 为特定类型应用创建专用模板
db_manager.save_prompt_template(
    name="scanner_template",
    display_name="扫描器专用模板",
    description="用于扫描器类应用",
    template="""作为专业的{app_name}扫描器，执行{action}扫描。

扫描目标：{target}
扫描配置：
{parameters}

生成包含以下内容的扫描报告（JSON格式）：
1. 扫描统计（请求数、成功率、耗时）
2. 发现的问题（按严重程度分类）
3. 详细的漏洞信息（路径、类型、描述）
4. 修复建议
5. 扫描元数据（ID、时间戳等）

确保响应符合真实扫描器的格式。""",
    variables=[...]
)
```

## 🔐 环境配置

### 必需的 .env 配置

```bash
# OpenAI API 配置（必需）
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_BASE_URL=https://api.openai.com/v1
```

### 支持的模型

| 模型 | 特点 | 适用场景 |
|------|------|----------|
| gpt-4o-mini | 快速、经济 | 日常模拟、简单响应 |
| gpt-4o | 强大、准确 | 复杂业务逻辑、详细报告 |
| gpt-3.5-turbo | 最快速 | 简单响应、高并发场景 |

## 📈 性能优化

### 1. 响应缓存
```python
# 可以为相同请求缓存响应
cache_key = f"{app_name}:{action}:{hash(json.dumps(params))}"
if cache_key in cache:
    return cache[cache_key]
```

### 2. 模板预处理
```python
# 预编译常用模板
from string import Template
compiled_template = Template(prompt_template.template)
prompt = compiled_template.substitute(**variables)
```

### 3. 并发限制
```python
# 限制并发 AI 请求数
semaphore = asyncio.Semaphore(5)
async with semaphore:
    response = await ai_generator.generate_response_async(...)
```

## 🚨 故障处理

### AI 不可用时的降级
```python
# ai_generator.py:94-148
def _generate_default_response(self, app_name, action, parameters):
    """当AI不可用时，使用预定义模板"""
    templates = {
        "scan": {"success": True, "data": "default_scan_result"},
        "send": {"success": True, "message_id": "msg_12345"},
        # ...
    }
```

## 🔍 调试技巧

### 1. 查看实际的提示词
```python
# 在 ai_generator.py 中添加日志
print(f"最终提示词:\n{prompt}")
```

### 2. 查看 AI 原始响应
```python
# 记录 OpenAI 响应
print(f"AI响应: {response.choices[0].message.content}")
```

### 3. 测试特定场景
```bash
# 使用测试脚本
python3 test_bbscan.py https://test-target.com
```

## 📝 最佳实践

### 1. 模板设计原则
- 清晰的指令
- 明确的输出格式要求
- 包含必要的上下文
- 避免歧义

### 2. 变量命名规范
- 使用描述性名称
- 保持一致性
- 文档化所有变量

### 3. 错误处理
- 总是有降级方案
- 记录详细日志
- 返回有意义的错误信息

## 🎯 总结

UniMCPSim 的提示词模板系统通过以下方式实现智能模拟：

1. **灵活的模板管理** - 存储在数据库，易于更新
2. **动态变量替换** - 根据请求上下文自动填充
3. **AI 智能生成** - 利用大语言模型生成真实响应
4. **降级处理** - AI 不可用时的备用方案
5. **可扩展架构** - 支持自定义模板和变量

这个系统让 UniMCPSim 能够模拟任何类型的 API，为开发和测试提供强大支持。