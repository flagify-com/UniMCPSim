# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.11.1] - 2025-12-13

### Fixed
- Button disabled state now has visual feedback (opacity, cursor change)
- "Test Connection" button in LLM config page shows disabled state during testing
- "Auto Generate Actions" button in apps page shows disabled state during AI generation
- Fixed AI generate button not re-enabled after successful generation

## [2.11.0] - 2025-12-12

### Added
- Multi-LLM configuration management
  - Pre-register multiple LLM configurations for different providers/models
  - Card list view displaying all configs with active indicator
  - Add/edit/delete configurations via modal dialog
  - One-click activation to switch between configs
  - Auto-enable first config when only one exists
- Hot config switching across processes
  - MCP Server automatically detects config changes from database
  - No server restart required when switching LLM configs
- Enhanced JSON response parsing
  - Support for multiple JSON objects (extract first valid object)
  - Handle "Extra data" format issues from some LLM providers
  - Better markdown code block cleanup

### Fixed
- SQLAlchemy session error when updating LLM config (`Instance not bound to Session`)
- Test connection now uses correct API Key from specific config (not just active config)
- API Key not updated when unchanged (masked format detection)
- Empty response hint for reasoning models (suggest enabling Stream mode)

### Changed
- Test connection button shows "Testing..." and disabled state during request
- Improved error messages with model name and stream status for debugging

## [2.10.1] - 2025-12-12

### Added
- LLM configuration page UI enhancements
  - Provider dropdown with 10 mainstream LLM services (OpenAI, Aliyun Bailian, Zhipu AI, DeepSeek, Moonshot, Doubao, SiliconFlow, Google Gemini, Ollama)
  - Auto-fill API Base URL when selecting provider
  - Compact two-column layout (Provider+URL, API Key+Model, Thinking+Stream)
  - Collapsible configuration help section

### Fixed
- Fixed `generate_actions_with_ai()` not reading database LLM configuration
- Fixed Zhipu GLM models (e.g., glm-4.6) returning empty response in test connection
  - Added support for `reasoning_content` field in both stream and non-stream modes
- Increased max_tokens to 100 for more complete test responses

### Changed
- Simplified `.env.example` with LLM configs commented out (Web UI recommended)

## [2.10.0] - 2025-12-11

### Added
- OEM white-label deployment support
  - Removed vendor branding from navigation and footer
  - Configurable branding via OEM branch
- Default example values in create app modal (HoneyGuide-SOAR template)
- Smart AI prompt pre-fill with tool definition template
- Docker containerization support
  - Dockerfile with China mirror acceleration
  - docker-compose.yml for easy deployment
  - UTF-8 locale settings for OpenEuler compatibility

### Fixed
- Token validation and SQLAlchemy object comparison issues
- UnicodeDecodeError on OpenEuler containers

## [2.9.0] - 2025-12-08

### Added
- MCP Playground feature for testing MCP Servers interactively
  - New "Playground" menu item in admin navigation
  - Left-right split layout (40% config / 60% chat)
  - Editable system prompt with Monaco Editor
  - MCP Server configuration editor (JSON format)
  - Test connection button to verify MCP Server and list tools
  - Real-time tool list display after successful connection
- AI-powered chat interface with function calling
  - Automatic tool invocation based on user requests
  - Tool call and result display in conversation
  - Conversation history management (clear/reset)
- MCP Client implementation (`mcp_client.py`)
  - Support for `initialize`, `tools/list`, `tools/call` methods
  - SSE (Server-Sent Events) response parsing
  - Error handling and timeout control
- Playground Service (`playground_service.py`)
  - Session management for multiple users
  - Integration with existing LLM configuration
  - Automatic tool execution loop (max 10 iterations)
- New API endpoints
  - `GET /admin/playground` - Playground page
  - `POST /admin/api/playground/test` - Test MCP connection
  - `POST /admin/api/playground/chat` - Send chat message
  - `POST /admin/api/playground/clear` - Clear conversation
  - `GET /admin/api/playground/history` - Get conversation history
  - `GET /admin/api/playground/system-prompt` - Get default system prompt

### Changed
- Navigation bar updated to include Playground menu item
- Admin server now imports and uses playground_service

## [2.6.0] - 2025-10-17

### Added
- Web-based LLM configuration management interface
  - New "大模型配置" menu item in admin navigation
  - User-friendly form for configuring OpenAI-compatible APIs
  - API Key masking for security (displays as `sk-xxx***xxx`)
  - Test connection feature with "你是谁?" test message
  - Real-time response display with duration metrics
- Database-first configuration strategy
  - New `llm_config` table for persistent storage
  - Priority: Database config > `.env` environment variables
  - Backward compatible with existing `.env` configuration
- LLM configuration API endpoints
  - `GET /admin/api/llm-config` - Retrieve current configuration
  - `POST /admin/api/llm-config` - Save/update configuration
  - `POST /admin/api/llm-config/test` - Test connection with live request
- Automatic configuration reload
  - AI generator reloads config after saving
  - No server restart required for changes to take effect

### Changed
- `AIResponseGenerator` now loads config from database first, falls back to environment variables
- Admin server now includes LLM config page route (`/admin/llm-config`)
- Database schema expanded with `LLMConfig` model

### Fixed
- Configuration changes now apply immediately without restart
- API Key security improved with masking in UI and API responses

## [2.5.0] - 2025-01-17

### Added
- Toast notification system replacing browser alerts for better UX
- URL-safe app name validation (frontend & backend)
  - Category and name fields now enforce `^[a-zA-Z0-9_-]+$` pattern
  - Length validation (2-50 characters)
  - Clear error messages for invalid input
- Smart database initialization logic
  - Checks application count before initialization
  - Respects user deletions (prevents re-import)
  - One-time initialization on first run
- Token permission reminder after app creation
  - Guides users to manually bind token permissions
  - Explicit authorization workflow

### Changed
- AI action generation button now disables during API call to prevent double-clicks
- App creation success message now includes permission binding reminder
- Database initialization script updated with current schema (including ai_notes field)
- Optimized action_generation prompt template with default field support
  - Added principle #7 for default values in optional parameters
  - Parameter definitions now support "default" field (e.g., duration_minutes=60, page_size=10)
  - Improved AI-generated action quality with better parameter defaults

### Fixed
- Issue where deleted apps would be re-imported on server restart
- Improved user feedback when creating applications

## [2.4.3] - 2025-01-15

### Added
- `ai_notes` field to Application model for AI generation context
- Three-column layout in create app modal (基本信息 | 动作定义 | AI辅助生成)
- Enhanced AI prompt templates with full application context

### Changed
- Redesigned create app modal with improved UI/UX
- Optimized prompt templates to provide more context to AI

### Fixed
- AI call error responses now properly returned instead of being masked
- DateTime deprecation warnings resolved

## [2.4.0] - 2025-01-10

### Added
- Stream mode support for AI API calls (required by models like qwq-32b)
- `.env.example` template file
- `OPENAI_ENABLE_THINKING` configuration option
- `OPENAI_STREAM` configuration option

### Changed
- AI thinking mode now disabled by default to prevent JSON parsing issues
- Enhanced error handling for AI API calls

## [2.3.0] - 2024-12-20

### Added
- Enhanced logging system with three log files (all/error/debug)
- DEBUG mode for detailed diagnostic information
- MCP call logging with duration and token usage
- Authentication failure logging
- Tool call logging

### Changed
- Improved log organization with automatic rotation (10MB per file, 5 backups)
- Enhanced security logging (only first 8 chars of tokens in INFO mode)

## [2.2.0] - 2024-12-15

### Added
- Token permission management with visual modal interface
- Batch operations for token permissions (全选/取消全选)
- App details viewer with clickable app names
- One-click MCP configuration generator
- Copy to clipboard functionality

### Changed
- Token list now shows count of authorized apps
- Improved token management UI/UX

## [2.1.0] - 2024-12-10

### Added
- Prompt template management system
- Template editor with Monaco editor integration
- System variable support in templates
- Unified navigation and footer components

### Changed
- Improved admin interface consistency
- Enhanced CSS styling with modern design

## [2.0.0] - 2024-09-29

### Added
- Direct product-specific endpoints (e.g., `/IM/WeChat?token=xxx`)
- Cherry Studio integration support with screenshots
- Application creation examples in documentation

### Changed
- Removed generic `/mcp` endpoint in favor of product-specific endpoints
- Consolidated all documentation into README.md
- Improved Web management interface

### Removed
- Generic MCP endpoint (breaking change)

## [1.0.0] - 2024-09-28

### Added
- Initial release
- 9 pre-configured product simulators
  - VirusTotal, ThreatBook, QingTengHIDS (Security)
  - WeChat Work, Tencent Meeting (Communication)
  - Jira (Ticketing)
  - Huawei Switch, Cisco Router (Network)
  - Sangfor (Firewall)
- Full MCP protocol support
- Web admin interface (Flask-based)
- MCP server (FastMCP-based)
- Token-based authentication
- AI-enhanced response generation
- SQLite database with SQLAlchemy ORM
- Comprehensive test coverage

[Unreleased]: https://github.com/flagify-com/UniMCPSim/compare/v2.11.0...HEAD
[2.11.0]: https://github.com/flagify-com/UniMCPSim/compare/v2.10.1...v2.11.0
[2.10.1]: https://github.com/flagify-com/UniMCPSim/compare/v2.10.0...v2.10.1
[2.10.0]: https://github.com/flagify-com/UniMCPSim/compare/v2.9.0...v2.10.0
[2.9.0]: https://github.com/flagify-com/UniMCPSim/compare/v2.6.0...v2.9.0
[2.6.0]: https://github.com/flagify-com/UniMCPSim/compare/v2.5.0...v2.6.0
[2.5.0]: https://github.com/flagify-com/UniMCPSim/compare/v2.4.3...v2.5.0
[2.4.3]: https://github.com/flagify-com/UniMCPSim/compare/v2.4.0...v2.4.3
[2.4.0]: https://github.com/flagify-com/UniMCPSim/compare/v2.3.0...v2.4.0
[2.3.0]: https://github.com/flagify-com/UniMCPSim/compare/v2.2.0...v2.3.0
[2.2.0]: https://github.com/flagify-com/UniMCPSim/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/flagify-com/UniMCPSim/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/flagify-com/UniMCPSim/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/flagify-com/UniMCPSim/releases/tag/v1.0.0
