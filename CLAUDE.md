# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**UniMCPSim** (Universal MCP Simulator) is a comprehensive MCP (Model Context Protocol) simulator that can dynamically simulate various product API interfaces for development and testing with AI-enhanced response generation.

## Architecture

### Core Project Structure

```
UniMCPSim/
├── Core Services
│   ├── mcp_server.py        # Main MCP server (FastMCP-based, port 8080)
│   ├── admin_server.py      # Web admin interface (Flask-based, port 8081)
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
│   │   ├── logs.html           # Audit logs
│   │   └── change_password.html # Password change
│   └── static/            # CSS, JS, Monaco editor
│       ├── css/main.css   # Unified styles
│       └── js/            # Monaco editor
│
├── Initialization & Utilities
│   ├── init_simulators.py   # Initialize default simulators (9 products)
│   └── reset_admin_password.py # Password reset utility
│
├── Documentation
│   ├── README.md           # Main documentation
│   ├── prd.md             # Product requirements document
│   └── docs/              # Additional documentation
│
└── Tests
    └── tests/
        ├── simple_test.py  # Core functionality tests
        └── test_e2e.py     # End-to-end tests
```

### Project Architecture

- **Purpose**: General-purpose MCP simulator for multiple products
- **MCP Server** (port 8080): Simulates 9 pre-configured products
- **Admin Server** (port 8081): Web management interface with modern UI
- **AI Integration**: Uses OpenAI API for intelligent response generation

## Key Technical Details

### Database
- **Type**: SQLite (with SQLAlchemy ORM)
- **Location**: `data/unimcp.db` (auto-created)
- **Models**: Users, Tokens, Applications, AppPermissions, PromptTemplates, AuditLogs

### Authentication
- **Admin Login**: Session-based with password hashing
- **API Access**: Token-based (`?token=xxxx` in URL)
- **Default Admin**: admin / admin123

### Pre-configured Simulators (9 Products)
1. **Security**: VirusTotal, ThreatBook (微步在线), QingTengHIDS (青藤云)
2. **Communication**: WeChat Work (企业微信), Tencent Meeting (腾讯会议)
3. **Ticketing**: Jira
4. **Network**: Huawei Switch, Cisco Router
5. **Firewall**: Sangfor (深信服)

### AI Response Generation
- **Provider**: OpenAI API (GPT-4o-mini by default)
- **Purpose**: Generate realistic mock responses and action definitions
- **Configuration**: Via `.env` file (REQUIRED)

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
EOF

# Initialize simulators (optional, auto-runs on first start)
python init_simulators.py
```

### Running the Servers
```bash
# Start both servers (recommended)
python start_servers.py

# Or start individually
python mcp_server.py     # MCP server on port 8080
python admin_server.py   # Admin UI on port 8081
```

### Testing
```bash
# Core functionality test
python tests/simple_test.py

# End-to-end test
python tests/test_e2e.py

# Product endpoints test
python tests/test_product_endpoints.py
```

### Admin Operations
```bash
# Reset admin password
python reset_admin_password.py

# Access admin interface
# Browser: http://localhost:8081/admin/
# Login: admin / admin123
```

## API Endpoints

### MCP Server Endpoints (Port 8080)

#### Product-Specific Endpoints
- **Format**: `http://localhost:8080/{Category}/{Product}?token={token}`
- **Examples**:
  - `/IM/WeChat?token=xxx` - WeChat Work API
  - `/Security/VirusTotal?token=xxx` - VirusTotal API
  - `/Network/HuaweiSwitch?token=xxx` - Huawei Switch API

#### MCP Protocol Methods
- `initialize` - Initialize MCP session
- `tools/list` - List available tools
- `tools/call` - Execute tool/action
- `resources/list` - List available resources
- `prompts/list` - List available prompts

### Admin API Endpoints (Port 8081)
- `/admin/login` - Admin login page
- `/admin/` - Dashboard with system overview
- `/admin/apps` - Application management
- `/admin/tokens` - Token management
- `/admin/prompts` - Prompt template management
- `/admin/logs` - Audit logs
- `/admin/change-password` - Password change
- `/admin/api/*` - REST API for admin operations

## MCP Client Configuration

### For Cherry Studio / Claude Desktop / Cline

```json
{
  "mcpServers": {
    "unimcpsim-wechat": {
      "type": "http",
      "name": "企业微信模拟器",
      "description": "WeChat Work API Simulator",
      "url": "http://127.0.0.1:8080/IM/WeChat?token=your-token-here"
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

### Prompt Template Management
- System provides default templates for action generation and response simulation
- Templates support variables: `{app_name}`, `{action_name}`, `{parameters}`, etc.
- Users can view and edit template content (metadata is read-only)
- Templates are stored in database and loaded on startup

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
1. ✅ Core functionality test passes (`tests/simple_test.py`)
2. ✅ All 9 simulators respond correctly
3. ✅ Token authentication works
4. ✅ Admin panel loads without errors
5. ✅ New apps can be created via UI
6. ✅ AI response generation works (requires OpenAI API)

## Common Issues & Solutions

### Port Already in Use
```bash
# Check what's using ports
lsof -i :8080
lsof -i :8081

# Kill processes if needed
kill -9 <PID>
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

Required `.env` configuration:
```
# OpenAI Configuration (REQUIRED for AI features)
OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_BASE_URL=https://api.openai.com/v1

# Optional configurations
DEBUG=false
LOG_LEVEL=INFO
```

## Project Status

Current Version: **v2.1.0**
- ✅ Core MCP simulator fully functional
- ✅ 9 pre-configured product simulators
- ✅ AI-enhanced response generation
- ✅ Enhanced Web admin interface with modern UI
- ✅ Token permission management with visual modal interface
- ✅ App details viewer with complete action information
- ✅ One-click MCP configuration generator
- ✅ Prompt template management system
- ✅ Unified navigation and footer components
- ✅ Cherry Studio/Claude Desktop/Cline integration tested
- ✅ Comprehensive test coverage

## Quick Test Commands

```bash
# Quick health check
curl "http://localhost:8080/health"

# Test with demo token (get from admin panel)
TOKEN="your-demo-token"
curl "http://localhost:8080/IM/WeChat?token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "send_message", "parameters": {"to_user": "test", "text": "Hello"}}'
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