# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/yourusername/UniMCPSim/compare/v2.5.0...HEAD
[2.5.0]: https://github.com/yourusername/UniMCPSim/compare/v2.4.3...v2.5.0
[2.4.3]: https://github.com/yourusername/UniMCPSim/compare/v2.4.0...v2.4.3
[2.4.0]: https://github.com/yourusername/UniMCPSim/compare/v2.3.0...v2.4.0
[2.3.0]: https://github.com/yourusername/UniMCPSim/compare/v2.2.0...v2.3.0
[2.2.0]: https://github.com/yourusername/UniMCPSim/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/yourusername/UniMCPSim/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/yourusername/UniMCPSim/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/yourusername/UniMCPSim/releases/tag/v1.0.0
