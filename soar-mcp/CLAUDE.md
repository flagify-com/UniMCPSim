# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **SOAR MCP Server** designed specifically for the [OctoMation SOAR Platform](https://github.com/flagify-com/OctoMation). It bridges SOAR (Security Orchestration, Automation and Response) capabilities to AI clients through the Model Context Protocol (MCP).

## Architecture

### Core Components

- **`soar_mcp_server.py`** - Main FastMCP server implementing MCP tools and resources
- **`models.py`** - SQLAlchemy database models and Pydantic schemas for playbooks, apps, and executions
- **`sync_service.py`** - Asynchronous service for syncing data from OctoMation SOAR API
- **`auth_utils.py`** - Authentication management (JWT, password hashing, token validation)
- **`config_manager.py`** - Configuration management with database persistence
- **`auth_provider.py`** - SOAR authentication provider for MCP integration

### Dual Server Architecture

The system runs **two servers simultaneously**:

1. **MCP Server** (port 12345): FastMCP-based server providing MCP tools and resources
2. **Web Admin Server** (port 12346): Flask-based web management interface

### MCP Tools (Available to AI Clients)

- `list_playbooks_quick` - Get concise playbook list (ID, name, displayName)
- `query_playbook_execution_params` - Get playbook parameter definitions
- `execute_playbook` - Execute SOAR playbooks with parameters
- `query_playbook_execution_status_by_activity_id` - Check execution status by activity ID
- `query_playbook_execution_result_by_activity_id` - Get detailed execution results

### Key Technical Details

- **Playbook IDs**: LONG type (64-bit integers), support both integer and string formats
- **Authentication**: Token-based via URL parameters (`?token=xxxx`)
- **Database**: SQLite with SQLAlchemy ORM, supports PostgreSQL/MySQL
- **Async Architecture**: httpx for API calls, asyncio for concurrency

## Common Commands

### Development Setup
```bash
# Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your OctoMation SOAR API credentials
```

### Running the Server
```bash
# Start both MCP and Web servers
python3 soar_mcp_server.py

# Or use the intelligent startup script
./start_simple_server.sh
```

### Testing

```bash
# Test MCP client connection
cd tests
python mcp_soar_client.py

# Test specific playbook tools
python test_new_playbook_tools.py --playbook-id 1907203516548373

# Test real API integration
python test_real_api.py

# Test playbook execution (use actual test data)
python test_unified_execute_playbook.py --playbook-id 1907203516548373

# Run automation test suite
./test_automation.sh
```

### Database Management
```bash
# Reset admin password
./reset_admin_password.sh

# Database is auto-created on first run
# Manual database operations via models.py DatabaseManager
```

### Configuration
- **Web Admin**: `http://127.0.0.1:12346/admin` (configure SOAR API settings)
- **MCP Endpoint**: `http://127.0.0.1:12345/mcp?token=xxxx`
- **Environment**: `.env` file for persistent configuration

## Test Data Parameters

When testing playbook execution, use these parameters (from actual OctoMation setup):

```json
{
    "eventId": 0,
    "executorInstanceId": 1907203516548373,
    "executorInstanceType": "PLAYBOOK",
    "params": [
        {
            "key": "src",
            "value": "15.197.148.33"
        }
    ]
}
```

## MCP Client Configuration

For Cherry Studio, Claude Desktop, and other MCP clients:

```json
{
  "mcpServers": {
    "soar-mcp": {
      "type": "http",
      "name": "soar-mcp",
      "description": "SOAR 安全编排平台集成",
      "url": "http://127.0.0.1:12345/mcp?token=xxxx"
    }
  }
}
```

Replace `xxxx` with actual API token from web admin interface.

## Important Notes

- SSL verification disabled by default (`SSL_VERIFY=0`) for development
- Supports both Chinese and English interfaces
- Requires active OctoMation SOAR platform connection
- Thread-local storage used for request context and user authentication
- Audit logging for all MCP operations