# UniMCPSim 提示词模板系统详解

## 概述

UniMCPSim 使用提示词模板系统来生成动态的 API 响应。当用户发起请求时，系统会从数据库获取提示词模板，替换相关变量，然后发送给 OpenAI API 生成智能响应。

## 系统架构

```
用户请求 → Token验证 → 获取应用定义 → 获取提示词模板 → 变量替换 → AI生成 → 返回响应
```

## 核心组件

### 1. 数据库模型 (`models.py`)

#### PromptTemplate 表结构
```python
class PromptTemplate(Base):
    __tablename__ = 'prompt_templates'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    template = Column(Text, nullable=False)  # 模板内容
    variables = Column(JSON)  # 可用变量定义
    enabled = Column(Boolean, default=True)
```

### 2. 预置模板

系统预置了两个核心模板：

#### response_simulation 模板
用于模拟API响应：
```
你是{app_name}系统的模拟器。用户调用了{action}操作，参数如下：
{parameters}

请生成一个真实的API响应结果（JSON格式）。响应应该：
1. 符合真实系统的响应格式
2. 包含合理的数据
3. 反映操作的成功或失败状态

直接返回JSON，不要任何其他说明文字。
```

#### action_generation 模板
用于生成动作定义（创建新应用时使用）

### 3. 模板变量

#### response_simulation 的变量
- `{app_name}`: 应用的显示名称（如 "BBScan网站扫描器"）
- `{action}`: 调用的动作名称（如 "scan_url"）
- `{parameters}`: 用户提供的参数（JSON格式字符串）

## 工作流程示例

### 以 BBScan 扫描器为例

#### 1. 用户请求
```http
POST http://127.0.0.1:8080/Scanner/BBScan?token=xxx
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "scan_url",
    "arguments": {
      "target_url": "https://example.com",
      "scan_type": "full",
      "max_depth": 3
    }
  },
  "id": 2
}
```

#### 2. 系统处理流程

##### 步骤 1: 验证和获取应用
```python
# mcp_server.py:62-81
app = db_manager.get_application_by_path("Scanner", "BBScan")
```

##### 步骤 2: 获取提示词模板
```python
# ai_generator.py:44-45
prompt_template = self.db_manager.get_prompt_template('response_simulation')
```

##### 步骤 3: 准备变量
```python
# ai_generator.py:47-51
variables = {
    'app_name': 'BBScan网站扫描器',
    'action': 'scan_url',
    'parameters': '{"target_url": "https://example.com", ...}'
}
```

##### 步骤 4: 模板替换
```python
# ai_generator.py:54
prompt = prompt_template.template.format(**variables)
```

结果：
```
你是BBScan网站扫描器系统的模拟器。用户调用了scan_url操作，参数如下：
{
  "target_url": "https://example.com",
  "scan_type": "full",
  "max_depth": 3
}

请生成一个真实的API响应结果（JSON格式）。响应应该：
1. 符合真实系统的响应格式
2. 包含合理的数据
3. 反映操作的成功或失败状态

直接返回JSON，不要任何其他说明文字。
```

##### 步骤 5: 调用 OpenAI
```python
# ai_generator.py:67-75
response = self.client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "你是一个API响应模拟器，返回符合规范的JSON数据。"},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=1000
)
```

##### 步骤 6: 返回响应
AI 生成的响应示例：
```json
{
  "success": true,
  "scan_id": "scan_20240930_154823",
  "target_url": "https://example.com",
  "status": "completed",
  "statistics": {
    "total_requests": 453,
    "directories_found": 28,
    "files_found": 156
  },
  "vulnerabilities": {
    "high": 2,
    "medium": 5,
    "low": 13
  },
  "interesting_findings": [
    {
      "path": "/admin/",
      "severity": "high",
      "description": "发现管理后台入口"
    }
  ]
}
```

## 自定义提示词模板

### 修改现有模板

通过数据库管理器更新模板：
```python
db_manager.save_prompt_template(
    name="response_simulation",
    display_name="响应模拟提示词",
    description="用于模拟MCP工具调用响应",
    template="新的模板内容，包含 {app_name}, {action}, {parameters} 变量",
    variables=[
        {"name": "app_name", "description": "应用名称"},
        {"name": "action", "description": "动作名称"},
        {"name": "parameters", "description": "调用参数"}
    ]
)
```

### 添加新模板

创建专用模板：
```python
db_manager.save_prompt_template(
    name="security_scan_template",
    display_name="安全扫描专用模板",
    description="用于安全扫描类应用",
    template="""作为{app_name}安全扫描器，执行{action}扫描任务。
目标：{target}
配置：{config}

生成详细的安全扫描报告，包含：
- 发现的漏洞
- 风险等级
- 修复建议

以JSON格式返回。""",
    variables=[
        {"name": "app_name", "description": "扫描器名称"},
        {"name": "action", "description": "扫描类型"},
        {"name": "target", "description": "扫描目标"},
        {"name": "config", "description": "扫描配置"}
    ]
)
```

## 模板优化建议

### 1. 针对性模板
为不同类型的应用创建专门的模板：
- 安全扫描类
- 通信消息类
- 网络设备类
- 工单系统类

### 2. 上下文增强
在模板中添加更多上下文信息：
```
你是{app_name}系统的模拟器。
系统版本：{version}
当前时间：{timestamp}
用户权限：{user_role}

用户调用了{action}操作...
```

### 3. 响应格式指导
提供更详细的响应格式示例：
```
请按照以下格式生成响应：
{
  "status": "success|error",
  "data": {...},
  "metadata": {
    "timestamp": "ISO-8601",
    "request_id": "uuid"
  }
}
```

## 环境配置

### .env 文件配置
```bash
# OpenAI API 配置（必需）
OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_BASE_URL=https://api.openai.com/v1
```

### 模型选择
- `gpt-4o-mini`: 快速、经济，适合大多数模拟场景
- `gpt-4o`: 更强大，适合复杂的模拟需求
- `gpt-3.5-turbo`: 更快速，适合简单响应

## 故障处理

### AI 生成失败时的降级策略

当 OpenAI API 不可用时，系统会使用默认响应模板：
```python
# ai_generator.py:94-148
def _generate_default_response(self, app_name, action, parameters):
    """生成默认响应（不依赖AI）"""
    # 根据动作名称匹配预定义模板
    # 返回静态但合理的响应
```

## 性能优化

### 1. 缓存机制
可以为常见请求缓存AI响应：
```python
# 伪代码
cache_key = f"{app_name}:{action}:{hash(parameters)}"
if cache_key in response_cache:
    return response_cache[cache_key]
```

### 2. 批量处理
对多个相似请求批量调用 OpenAI API

### 3. 模板预编译
预先编译常用模板，减少运行时处理

## 安全考虑

### 1. 参数验证
在发送给 AI 前验证和清理用户参数

### 2. 响应过滤
过滤 AI 响应中的敏感信息

### 3. Rate Limiting
限制 API 调用频率，防止滥用

## 总结

UniMCPSim 的提示词模板系统提供了：
- ✅ 灵活的模板管理
- ✅ 动态变量替换
- ✅ AI 智能响应生成
- ✅ 降级处理机制
- ✅ 可扩展的架构

通过这个系统，可以轻松模拟各种 API 的响应，为开发和测试提供强大支持。