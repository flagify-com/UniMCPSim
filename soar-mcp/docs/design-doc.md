# SOAR MCP Server 架构设计文档

## 项目概述

基于 OctoMation SOAR 平台的 MCP (Model Context Protocol) 服务器，为安全团队提供智能化的自动化响应能力。通过 MCP 协议，让 Claude Desktop、Cherry Studio 等 AI 工具能够直接调用 SOAR 平台的剧本和动作，实现自然语言驱动的安全响应自动化。

## 核心目标

- **智能化安全响应**：通过自然语言指令驱动复杂的 SOAR 自动化流程
- **降低使用门槛**：替代复杂的 UI 操作，简化安全响应流程
- **提升响应效率**：本地缓存 + 异步执行，显著提升操作响应速度
- **标准化集成**：严格遵循 MCP 协议，确保与主流 AI 工具的兼容性

## 功能需求分析

### 核心功能模块

1. **事件管理**
   - 查看事件列表和详情
   - 创建安全事件

2. **剧本管理**
   - 查询/搜索可用剧本
   - 获取剧本执行参数
   - 执行剧本
   - 获取剧本执行结果

3. **动作管理**
   - 查看可用应用及其动作（按应用分组）
   - 执行单个动作
   - 获取动作执行结果

4. **资源整合**
   - 从动作→应用→资源的层级数据重组
   - 默认选择每个应用的第一个 asset 资源
   - 提供应用视角的数据展示

### 数据整合策略

```
原始 API 结构: 动作列表 → 各自独立
↓ 重新整合
目标结构: 应用 → 动作组 → 默认资源配置
```

**整合流程**：
1. 调用动作列表 API
2. 根据动作的应用 ID 查询应用信息
3. 查询每个应用的 asset 资源配置
4. 按应用维度重新组织数据结构
5. 为每个应用设置默认 asset（选择第一个）

## 技术架构设计

### 技术选型

```python
{
    "web_framework": "FastAPI",           # 高性能异步框架，自动文档生成
    "mcp_library": "mcp Python SDK",     # Anthropic 官方 MCP 实现
    "database": "SQLite + SQLAlchemy 2.0", # 轻量级数据库 + 现代 ORM
    "http_client": "httpx",              # 异步 HTTP 客户端
    "validation": "Pydantic v2",         # 数据验证和序列化
    "logging": "structlog",              # 结构化日志
    "config": "pydantic-settings",      # 环境配置管理
    "task_queue": "asyncio + APScheduler", # 异步任务调度
    "ssl_handling": "urllib3",           # 支持 SSL_VERIFY=0 配置
}
```

### 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Client    │    │   MCP Server    │    │  OctoMation API │
│ (Claude/Cherry) │◄──►│   (FastAPI)     │◄──►│   (SOAR系统)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  SQLite Cache   │
                       │ + Sync Service  │
                       └─────────────────┘
```

## 数据库设计

### SQLite 缓存表结构

```sql
-- 应用表（安全产品）
CREATE TABLE applications (
    id INTEGER PRIMARY KEY,
    app_id TEXT UNIQUE NOT NULL,        -- OctoMation应用ID
    name TEXT NOT NULL,                 -- 应用名称
    description TEXT,                   -- 应用描述
    vendor TEXT,                        -- 厂商名称
    category TEXT,                      -- 应用类别：fw, edr, siem等
    status TEXT DEFAULT 'active',       -- 应用状态
    last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 动作表
CREATE TABLE actions (
    id INTEGER PRIMARY KEY,
    action_id TEXT UNIQUE NOT NULL,     -- OctoMation动作ID
    app_id TEXT NOT NULL,               -- 关联应用ID
    name TEXT NOT NULL,                 -- 动作名称
    description TEXT,                   -- 动作描述
    parameters TEXT,                    -- JSON格式存储参数定义
    category TEXT,                      -- 动作分类
    last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (app_id) REFERENCES applications(app_id)
);

-- 应用资源表（asset配置）
CREATE TABLE app_assets (
    id INTEGER PRIMARY KEY,
    app_id TEXT NOT NULL,               -- 关联应用ID
    asset_name TEXT,                    -- 资源名称
    asset_config TEXT,                  -- JSON格式：IP、端口、认证信息等
    is_default BOOLEAN DEFAULT 0,       -- 是否为默认资源
    last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (app_id) REFERENCES applications(app_id)
);

-- 剧本表
CREATE TABLE playbooks (
    id INTEGER PRIMARY KEY,
    playbook_id TEXT UNIQUE NOT NULL,   -- OctoMation剧本ID
    name TEXT NOT NULL,                 -- 剧本名称
    description TEXT,                   -- 剧本描述
    parameters TEXT,                    -- JSON格式参数定义
    category TEXT,                      -- 剧本分类
    publish_status TEXT,                -- 发布状态
    last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 执行历史表（可选，用于统计分析）
CREATE TABLE execution_history (
    id INTEGER PRIMARY KEY,
    execution_id TEXT UNIQUE NOT NULL,  -- 执行ID
    type TEXT NOT NULL,                 -- 类型：'playbook' or 'action'
    target_id TEXT NOT NULL,            -- playbook_id or action_id
    status TEXT,                        -- 执行状态
    start_time TIMESTAMP,               -- 开始时间
    end_time TIMESTAMP,                 -- 结束时间
    result TEXT,                        -- JSON格式结果
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 数据同步机制

### 多层同步策略

1. **启动时全量同步**
   - 服务启动时检查缓存是否为空或过期
   - 批量拉取应用、动作、剧本数据
   - 构建应用→动作的关联关系

2. **定时增量同步**
   ```python
   SYNC_CONFIG = {
       "applications": {"interval": 3600, "last_sync": None},  # 1小时
       "playbooks": {"interval": 1800, "last_sync": None},     # 30分钟
       "actions": {"interval": 3600, "last_sync": None},       # 1小时
   }
   ```

3. **按需刷新机制**
   - MCP 调用时检查缓存时效性
   - 发现数据过期时触发后台同步
   - 提供手动刷新 API 接口

4. **变更检测优化**
   ```python
   def sync_if_needed(resource_type: str, max_age_seconds: int = 1800):
       last_sync = get_last_sync_time(resource_type)
       if not last_sync or (datetime.now() - last_sync).seconds > max_age_seconds:
           background_sync(resource_type)
   ```

## 项目结构

```
mcp-server-soar/
├── src/
│   ├── mcp_soar/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI应用入口
│   │   ├── mcp_server.py        # MCP服务器实现
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── settings.py      # 配置管理
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── models.py        # SQLAlchemy模型
│   │   │   ├── session.py       # 数据库会话
│   │   │   └── migrations/      # 数据库迁移
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── octomation.py    # OctoMation API客户端
│   │   │   ├── cache.py         # 缓存服务
│   │   │   ├── sync.py          # 数据同步服务
│   │   │   └── execution.py     # 执行管理服务
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── octomation.py    # OctoMation数据模型
│   │   │   ├── mcp.py           # MCP数据模型
│   │   │   └── api.py           # API响应模型
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── playbook.py      # 剧本相关工具
│   │   │   ├── action.py        # 动作相关工具
│   │   │   ├── event.py         # 事件相关工具
│   │   │   └── application.py   # 应用相关工具
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── applications.py
│   │   │   │   ├── playbooks.py
│   │   │   │   ├── events.py
│   │   │   │   └── executions.py
│   │   │   └── deps.py          # 依赖注入
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py
│   │       ├── exceptions.py
│   │       └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── test_octomation_client.py
│   ├── test_data_integration.py
│   └── test_mcp_tools.py
├── docs/
├── scripts/
│   ├── setup_db.py
│   └── test_octomation_api.py    # 用于测试真实API数据结构
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

## MCP 工具定义

### 核心工具集

```python
MCP_TOOLS = [
    # 应用和动作查询
    {
        "name": "list_applications_with_actions",
        "description": "查询所有安全应用及其可用动作，按应用分组展示",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "应用类别筛选"},
                "keyword": {"type": "string", "description": "关键字搜索"}
            }
        }
    },
    
    # 剧本管理
    {
        "name": "list_playbooks",
        "description": "查询可用剧本列表，支持搜索和筛选",
        "inputSchema": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "剧本名称关键字"},
                "category": {"type": "string", "description": "剧本分类"},
                "limit": {"type": "integer", "default": 20}
            }
        }
    },
    
    {
        "name": "get_playbook_params",
        "description": "获取指定剧本的执行参数定义",
        "inputSchema": {
            "type": "object",
            "properties": {
                "playbook_id": {"type": "string", "description": "剧本ID"}
            },
            "required": ["playbook_id"]
        }
    },
    
    {
        "name": "execute_playbook",
        "description": "执行指定剧本",
        "inputSchema": {
            "type": "object",
            "properties": {
                "playbook_id": {"type": "string", "description": "剧本ID"},
                "params": {"type": "object", "description": "执行参数"},
                "event_id": {"type": "string", "description": "关联事件ID（可选）"}
            },
            "required": ["playbook_id"]
        }
    },
    
    # 动作执行
    {
        "name": "execute_action",
        "description": "执行指定的安全应用动作",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action_id": {"type": "string", "description": "动作ID"},
                "params": {"type": "object", "description": "动作参数"},
                "use_default_asset": {"type": "boolean", "default": True}
            },
            "required": ["action_id"]
        }
    },
    
    # 执行状态查询
    {
        "name": "get_execution_status",
        "description": "查询剧本或动作的执行状态",
        "inputSchema": {
            "type": "object",
            "properties": {
                "execution_id": {"type": "string", "description": "执行ID"}
            },
            "required": ["execution_id"]
        }
    },
    
    # 事件管理
    {
        "name": "create_event",
        "description": "创建安全事件",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "事件标题"},
                "description": {"type": "string", "description": "事件描述"},
                "severity": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"]},
                "category": {"type": "string", "description": "事件类型"}
            },
            "required": ["title", "description", "severity"]
        }
    }
]
```

## 配置管理

### 环境配置 (.env)

```bash
# OctoMation平台配置
API_URL=https://hg.wuzhi-ai.com
SSL_VERIFY=0
API_TOKEN=eyJhbGciOiJIUzI...

# 服务配置
MCP_SERVER_PORT=3000
LOG_LEVEL=INFO

# 缓存配置
CACHE_DB_PATH=./cache.db
SYNC_INTERVAL_SECONDS=1800

# 开发配置
DEBUG=False
RELOAD=False
```

## 性能优化策略

### 缓存优化
- **本地缓存优先**：优先使用 SQLite 缓存，减少 90%+ API 调用延迟
- **智能刷新**：基于时间戳的增量更新机制
- **预加载策略**：服务启动时预加载常用数据

### 异步处理
- **全异步架构**：FastAPI + asyncio 支持高并发
- **后台任务**：数据同步和长时间执行的任务异步处理
- **连接池管理**：复用 HTTP 连接，减少连接开销

### 数据整合优化
- **批量查询**：一次性获取相关数据，减少 API 调用次数
- **关系映射**：在内存中维护应用-动作关系映射
- **默认资源缓存**：预先确定每个应用的默认 asset

## 实施计划

### 第一阶段：基础框架（1周）
- [ ] 建立 FastAPI 项目结构
- [ ] 实现 OctoMation API 客户端
- [ ] 设计 SQLite 数据库模型
- [ ] 编写数据拉取测试脚本

### 第二阶段：核心功能（2周）
- [ ] 实现数据同步服务
- [ ] 开发应用视角数据整合逻辑
- [ ] 实现 MCP 工具集
- [ ] 构建执行状态跟踪机制

### 第三阶段：完善优化（1周）
- [ ] 添加错误处理和重试机制
- [ ] 实现监控和日志系统
- [ ] 编写完整的测试用例
- [ ] 生成 API 文档

## 技术风险与应对

### 风险点
1. **API 变更**：OctoMation API 接口变更可能影响兼容性
2. **数据一致性**：缓存与实时数据的一致性问题
3. **性能瓶颈**：大量数据同步可能影响服务响应

### 应对策略
1. **版本管理**：API 客户端支持多版本适配
2. **一致性检查**：定期校验缓存数据有效性
3. **分批处理**：大数据量采用分批同步策略

## 总结

这个架构设计充分考虑了性能、可维护性和扩展性，通过本地缓存和智能数据整合，为安全团队提供了一个高效的 SOAR 自动化操作界面。下一步需要通过实际的 API 调用测试来验证数据结构设计的合理性。