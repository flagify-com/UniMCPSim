#!/usr/bin/env python3
"""
UniMCPSim Version Information
"""

__version__ = "2.7.0"
__version_info__ = (2, 7, 0)

# Version history
VERSION_HISTORY = {
    "2.7.0": {
        "date": "2025-10-17",
        "features": [
            "完整的回归测试套件(前端/后端/MCP)",
            "自动化测试框架支持持续集成",
            "前端测试: 登录/密码/应用/Token管理",
            "后端测试: AI动作生成/响应模拟",
            "MCP测试: StreamableHTTP模式完整验证",
            "精简高效的测试策略(单应用验证系统功能)",
            "详细的测试文档和故障排查指南"
        ]
    },
    "2.6.0": {
        "date": "2025-10-17",
        "features": [
            "Web界面大模型配置管理",
            "数据库优先配置策略(数据库>环境变量)",
            "LLM配置测试连接功能",
            "API Key脱敏显示保护安全",
            "支持OpenAI兼容API(通义千问/DeepSeek等)",
            "配置即时生效无需重启",
            "新增LLMConfig数据表"
        ]
    },
    "2.5.0": {
        "date": "2025-01-17",
        "features": [
            "Toast通知系统替代浏览器alert",
            "应用名称URL安全字符验证(前后端)",
            "智能数据库初始化(尊重用户删除)",
            "Token权限手动绑定提醒",
            "AI动作生成按钮防重复点击",
            "优化response_simulation提示词模板(新增ai_notes字段)",
            "优化action_generation提示词模板(支持default字段)"
        ]
    },
    "2.4.3": {
        "date": "2025-09-30",
        "features": [
            "Optimized log detail modal with side-by-side layout",
            "Request parameters and response results displayed in parallel",
            "Increased JSON viewer height to 450px for better readability",
            "4-column basic info layout for efficient space usage"
        ]
    },
    "2.4.2": {
        "date": "2025-09-30",
        "features": [
            "Enhanced audit log modal with Monaco Editor for JSON display",
            "Fixed modal centering issue in logs page",
            "Improved application list sorting (newest first)",
            "Better UX with syntax highlighting and code folding"
        ]
    },
    "2.4.1": {
        "date": "2025-09-30",
        "features": [
            "Fixed AI prompt template to include action_definition variable",
            "Added database migration script for existing installations",
            "Improved AI response accuracy with complete action context",
            "Documentation updates for upgrade procedures"
        ]
    },
    "2.4.0": {
        "date": "2025-09-30",
        "features": [
            "Enhanced logging system with DEBUG mode support",
            "Comprehensive MCP protocol compliance (ping, notifications/initialized)",
            "Audit log enhancements (IP address tracking, detail modal)",
            "Fixed SQLAlchemy and datetime deprecation warnings",
            "Multi-level log files (all, error, debug) with auto-rotation",
            "Detailed tracking of MCP calls, AI calls, and tool calls"
        ]
    },
    "2.3.0": {
        "date": "2025-09-30",
        "features": [
            "Removed soar-mcp reference project (~4.1MB, 45K+ lines)",
            "Cleaned up temporary debug and utility scripts",
            "Removed unused database.db file",
            "Updated documentation to focus on UniMCPSim core",
            "Project codebase simplified and streamlined"
        ]
    },
    "2.2.0": {
        "date": "2025-09-30",
        "features": [
            "Centralized version management system",
            "Dynamic version display across all pages",
            "Version info in health check endpoint",
            "Version display on login page"
        ]
    },
    "2.1.0": {
        "date": "2025-09-30",
        "features": [
            "Enhanced token permission management with modal interface",
            "App details viewer with complete action information",
            "One-click MCP configuration generator",
            "Prompt template management system",
            "Unified navigation and footer components",
            "Batch permission settings with select all functionality"
        ]
    },
    "2.0.0": {
        "date": "2025-09-29",
        "features": [
            "Core MCP simulator fully functional",
            "9 pre-configured product simulators",
            "AI-enhanced response generation",
            "Web admin interface",
            "Token-based authentication"
        ]
    }
}

def get_version():
    """Get current version string"""
    return __version__

def get_version_info():
    """Get version tuple"""
    return __version_info__

def get_version_history():
    """Get version history"""
    return VERSION_HISTORY