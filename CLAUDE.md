# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**UniMCPSim** (Universal MCP Simulator) is a comprehensive MCP (Model Context Protocol) simulator that can dynamically simulate various product API interfaces for development and testing with AI-enhanced response generation.

## Architecture

### Core Project Structure

```
UniMCPSim/
├── Core Services
│   ├── mcp_server.py        # Main MCP server (FastMCP-based, port 9090)
│   ├── admin_server.py      # Web admin interface (Flask-based, port 9091)
│   ├── start_servers.py     # Service launcher script
│   └── ai_generator.py      # OpenAI integration for response generation
│
├── Data Layer
│   ├── models.py            # SQLAlchemy ORM models and database management
│   ├── auth_utils.py        # Authentication utilities (JWT, password hashing)
│   └── data/               # SQLite database directory (auto-created)
│       └── unimcp.db       # Main database file
│
├── Web Interface
│   ├── templates/          # HTML templates (Jinja2)
│   │   ├── _navigation.html    # Navigation component
│   │   ├── _footer.html        # Footer component
│   │   ├── login.html          # Login page
│   │   ├── dashboard.html      # Dashboard
│   │   ├── apps.html           # App management
│   │   ├── tokens.html         # Token management
│   │   ├── prompts.html        # Prompt template management
│   │   ├── llm_config.html     # LLM configuration (NEW in v2.6.0)
│   │   ├── logs.html           # Audit logs
│   │   └── change_password.html # Password change
│   └── static/            # CSS, JS, Monaco editor
│       ├── css/main.css   # Unified styles
│       └── js/            # Monaco editor
│
├── Initialization & Utilities
│   ├── init_simulators.py   # Initialize default simulators (10 products)
│   └── reset_admin_password.py # Password reset utility
│
├── Documentation
│   ├── README.md           # Main documentation
│   ├── prd.md             # Product requirements document
│   └── docs/              # Additional documentation
│
└── Tests
    └── tests/
        ├── test_admin_frontend.py  # Admin frontend tests
        ├── test_ai_backend.py      # AI backend tests
        ├── test_mcp_client.py      # MCP client tests
        └── run_all_tests.py        # Test runner
```

### Project Architecture

- **Purpose**: General-purpose MCP simulator for multiple products
- **MCP Server** (port 9090): Simulates 10 pre-configured products
- **Admin Server** (port 9091): Web management interface with modern UI
- **AI Integration**: Uses OpenAI API for intelligent response generation

## Key Technical Details

### Database
- **Type**: SQLite (with SQLAlchemy ORM)
- **Location**: `data/unimcp.db` (auto-created)
- **Models**: Users, Tokens, Applications, AppPermissions, PromptTemplates, AuditLogs, **LLMConfig**

### Authentication
- **Admin Login**: Session-based with password hashing
- **API Access**: Token-based (`?token=xxxx` in URL)
- **Default Admin**: admin / admin123

### Pre-configured Simulators (10 Products)
1. **HIDS**: QingTengYun-HIDS (青藤云HIDS)
2. **Meeting**: TencentMeeting (腾讯会议)
3. **Ticketing**: Jira (工单系统)
4. **Network**: HuaweiSwitch (华为交换机), Cisco3750 (思科交换机)
5. **IT**: LDAP (Windows AD), CMDB (资产管理)
6. **Firewall**: USGFirewall (华为USG防火墙)
7. **ThreatIntelligence**: Threatbook (微步在线威胁情报)
8. **IM**: WeWork (腾讯企业微信)

### AI Response Generation
- **Provider**: OpenAI API (GPT-4o-mini by default)
- **Purpose**: Generate realistic mock responses and action definitions
- **Configuration**: Database-first strategy (Database > `.env`)
  - **Web UI**: Configure via "大模型配置" menu in admin panel
  - **Fallback**: `.env` file for backward compatibility
- **Thinking Mode**: Disabled by default to prevent thinking process from interfering with JSON output format

## Common Commands

### Initial Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file (REQUIRED)
cat > .env << 'EOF'
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_BASE_URL=https://api.openai.com/v1
OPENAI_ENABLE_THINKING=false
OPENAI_STREAM=false
EOF

# Initialize simulators (optional, auto-runs on first start)
python init_simulators.py
```

### Running the Servers
```bash
# Start both servers (recommended)
python start_servers.py

# Or start individually
python mcp_server.py     # MCP server on port 9090 (default)
python admin_server.py   # Admin UI on port 9091 (default)
```

**Note**: Default ports are 9090 (MCP) and 9091 (Admin). You can customize ports in `.env`:
```
MCP_SERVER_PORT=9090
ADMIN_SERVER_PORT=9091
```

### Testing
```bash
# Run all tests (recommended)
python tests/run_all_tests.py

# Or run individual tests
python tests/test_admin_frontend.py   # Admin UI tests
python tests/test_ai_backend.py       # AI backend tests
python tests/test_mcp_client.py       # MCP client tests
```

### Admin Operations
```bash
# Reset admin password
python reset_admin_password.py

# Access admin interface
# Browser: http://localhost:9091/admin/ (default port)
# Login: admin / admin123
```

## API Endpoints

### MCP Server Endpoints (Default Port 9090)

#### Product-Specific Endpoints
- **Format**: `http://localhost:9090/{Category}/{Product}?token={token}`
- **Examples**:
  - `/IM/WeWork?token=xxx` - WeChat Work API
  - `/ThreatIntelligence/Threatbook?token=xxx` - ThreatBook API
  - `/Network/HuaweiSwitch?token=xxx` - Huawei Switch API

#### MCP Protocol Methods
- `initialize` - Initialize MCP session
- `tools/list` - List available tools
- `tools/call` - Execute tool/action
- `resources/list` - List available resources
- `prompts/list` - List available prompts

### Admin API Endpoints (Default Port 9091)
- `/admin/login` - Admin login page
- `/admin/` - Dashboard with system overview
- `/admin/apps` - Application management
- `/admin/tokens` - Token management
- `/admin/prompts` - Prompt template management
- `/admin/llm-config` - **LLM configuration management (NEW in v2.6.0)**
- `/admin/logs` - Audit logs
- `/admin/change-password` - Password change
- `/admin/api/*` - REST API for admin operations

## MCP Client Configuration

### For Cherry Studio / Claude Desktop / Cline

```json
{
  "mcpServers": {
    "unimcpsim-wework": {
      "type": "http",
      "name": "企业微信模拟器",
      "description": "WeChat Work API Simulator",
      "url": "http://127.0.0.1:9090/IM/WeWork?token=your-token-here"
    }
  }
}
```

## Important Implementation Notes

### Token Validation
- Tokens are checked in URL parameters (`?token=xxx`)
- Each token can have specific permissions per app
- Tokens are stored in database with enabled/disabled status

### Token Permission Management (New Feature)
- **Visual Modal Interface**: Click "查看" button to view/edit token permissions
- **Batch Operations**: "全选/取消全选" button for quick permission assignment
- **Real-time Updates**: PUT `/admin/api/tokens/<id>/apps` endpoint for updating permissions
- **Permission Display**: Shows count of authorized apps in token list

### App Details Viewer (New Feature)
- **Clickable App Names**: Click any app name in the table to view full details
- **Comprehensive Information**: Shows metadata, description, and complete action list
- **Parameter Details**: Displays each action's parameters with type and requirement info
- **Modal Display**: Clean modal interface for easy viewing

### MCP Configuration Generator (New Feature)
- **One-Click Generation**: "MCP配置" button generates standard MCP client config
- **Format**: Compatible with Cherry Studio, Claude Desktop, and Cline
- **Token Placeholder**: Uses `YOUR_TOKEN_HERE` to remind users to fill in actual token
- **Copy Function**: One-click copy to clipboard with reminder message

### AI Action Generation
- When creating new apps, AI can auto-generate action definitions
- Uses database templates for consistent formatting
- Requires OpenAI API configuration in `.env`

### App Name Validation
- **URL-Safe Characters**: Category and name must match `^[a-zA-Z0-9_-]+$` (2-50 chars)
- **Validation Layer**: Both frontend (JavaScript) and backend (Python) enforce validation
- **Rationale**: Ensures clean URL paths like `/mcp/Security/VirusTotal?token=xxx`

### Database Initialization Logic
- **Idempotency**: Checks if applications exist (count > 0), skips if yes
- **Design Principle**: Respects user modifications, prevents re-import of deleted apps
- **Fresh Install**: Auto-initializes default apps only on first run

### Token Permission Workflow
- **Explicit Authorization**: New apps require manual token binding
- **Security Principle**: No automatic permission grants to prevent unintended access
- **User Guidance**: UI prompts users to manually bind permissions after app creation

### Prompt Template Management
- System provides default templates for action generation and response simulation
- Templates support variables: `{app_name}`, `{action_name}`, `{parameters}`, etc.
- Users can view and edit template content (metadata is read-only)
- Templates are stored in database and loaded on startup

### LLM Configuration Management (NEW in v2.6.0)
- **Database-First Strategy**: Configuration stored in database takes priority over `.env`
- **Web Interface**: Configure via `/admin/llm-config` page
  - API Base URL (supports OpenAI-compatible APIs)
  - API Key (masked display for security: `sk-xxx***xxx`)
  - Model Name (e.g., gpt-4o-mini, qwen-max, deepseek-chat)
  - Enable Thinking (default: false)
  - Enable Stream (default: false, required for some models like qwq-32b)
- **Test Connection**: Built-in test feature sends "你是谁?" to verify configuration
- **Instant Reload**: Changes take effect immediately without server restart
- **Backward Compatible**: Falls back to `.env` if no database configuration exists
- **Security**: API keys are masked in UI and API responses

### Session Management
- MCP sessions use `mcp-session-id` header
- Admin sessions use Flask session cookies
- Both support concurrent sessions

### Error Handling
- HTTP 401: Invalid/missing token
- HTTP 406: Missing Accept header for MCP
- HTTP 400: Invalid request format
- HTTP 404: Unknown endpoint/action

## Development Guidelines

### Adding New Simulators
1. Via Web Admin (Recommended):
   - Login to admin panel
   - Go to "应用管理" (Apps)
   - Click "创建新应用" (Create New App)
   - Fill details: category, name, display_name, description
   - Use AI to auto-generate action definitions from natural language prompts
   - Click app name to view details after creation
   - Use "MCP配置" button to generate client configuration

2. Via Code:
   - Add to `init_simulators.py`
   - Define actions in JSON format
   - Run initialization script

### Extending MCP Tools
```python
# In mcp_server.py
@mcp.tool()
async def new_tool(param1: str, param2: int) -> dict:
    """Tool description"""
    # Implementation
    return {"result": "success"}
```

### Custom AI Templates
Edit `ai_generator.py` to modify response generation templates.

## Testing Checklist

When testing changes:
1. ✅ All tests pass (`python tests/run_all_tests.py`)
2. ✅ All 10 simulators respond correctly
3. ✅ Token authentication works
4. ✅ Admin panel loads without errors
5. ✅ New apps can be created via UI
6. ✅ AI response generation works (requires OpenAI API)

## Common Issues & Solutions

### Port Already in Use
```bash
# Check what's using ports
lsof -i :9090
lsof -i :9091

# Kill processes if needed
kill -9 <PID>

# Or change ports in .env file
echo "MCP_SERVER_PORT=9090" >> .env
echo "ADMIN_SERVER_PORT=9091" >> .env
```

### Database Issues
```bash
# Reset database completely
rm -rf data/
python init_simulators.py
```

### Proxy Interference
```bash
# Unset proxy variables
unset HTTPS_PROXY HTTP_PROXY http_proxy https_proxy
```

### OpenAI API Issues
- Ensure `.env` file exists with valid API key
- Check API quota and limits
- Verify network connectivity to OpenAI

## Environment Variables

### Configuration Priority (v2.6.0+)
**Database Configuration > `.env` File**

You can now configure LLM settings via:
1. **Web UI** (Recommended): Visit `/admin/llm-config` to manage settings visually
2. **Environment Variables** (Fallback): Use `.env` file for backward compatibility

### `.env` Configuration (Optional)
```
# OpenAI Configuration (Optional - can be configured via Web UI)
OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_BASE_URL=https://api.openai.com/v1
OPENAI_ENABLE_THINKING=false  # 禁用思考模式,防止影响JSON输出(默认false)
OPENAI_STREAM=false  # 控制stream模式,某些模型如qwq-32b强制要求true(默认false)

# Server Configuration
MCP_SERVER_PORT=9090
ADMIN_SERVER_PORT=9091

# Optional configurations
DEBUG=false
LOG_LEVEL=INFO
```

**Note**: If LLM configuration exists in database, it will override `.env` settings.

**OPENAI_ENABLE_THINKING说明**:
- 默认值: `false` (禁用thinking模式)
- 用途: 控制大模型是否启用思考过程输出
- 重要性: 许多支持thinking模式的大模型(如qwen-thinking、DeepSeek-R1等)在启用thinking时会在响应中包含思考过程,这会干扰JSON格式的解析,导致API响应生成失败
- 建议: 保持默认值`false`,除非你明确知道使用的模型不会因thinking模式影响JSON输出
- 设置为`true`: 仅在需要调试或使用特定模型时启用

**OPENAI_STREAM说明**:
- 默认值: `false` (禁用stream模式)
- 用途: 控制是否使用stream模式调用AI API
- 重要性: 某些模型(如qwq-32b)强制要求使用stream模式,否则会返回400错误
- 适用模型: qwq-32b、部分deepseek-r1变体等
- 建议: 根据使用的模型调整
  - 常规模型(gpt-4o-mini、qwen3-max等): 保持`false`
  - 强制stream模型(qwq-32b等): 设置为`true`
- 注意: Stream模式下无法获取token使用量统计信息

## Project Status

Current Version: **v2.12.1**
- ✅ Core MCP simulator fully functional
- ✅ Pre-configured product simulators
- ✅ AI-enhanced response generation
- ✅ Web admin interface with modern UI
- ✅ Token permission management system
- ✅ MCP configuration generator
- ✅ Prompt template management
- ✅ **LLM configuration via Web UI (NEW)**
- ✅ **Database-first configuration strategy (NEW)**
- ✅ Cherry Studio/Claude Desktop/Cline integration tested
- ✅ Comprehensive test coverage

See CHANGELOG.md for detailed feature history.

## Quick Test Commands

```bash
# Quick health check
curl "http://localhost:9090/health"

# Test with demo token (get from admin panel)
TOKEN="your-demo-token"
curl "http://localhost:9090/IM/WeWork?token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

## Support & Debugging

For issues:
1. Check logs in terminal where servers are running
2. Verify `.env` file configuration
3. Ensure all dependencies installed (`pip list`)
4. Run test suite to identify specific failures
5. Check database integrity (`sqlite3 data/unimcp.db .schema`)

---

**Note**: This project uses AI to generate mock responses. Ensure OpenAI API is properly configured for full functionality.
- 我们的项目有两个分支：main 分支和 feature/oem 分支。在 main 分支里，要保持我们产品的品牌名称，比如“雾帜智能”和github项目原始地址；而在 OEM 分支里面就不需要了。所以你在做代码合并的时候，得注意这些区别。