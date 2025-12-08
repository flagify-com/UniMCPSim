#!/usr/bin/env python3
"""
UniMCPSim Version Information
"""

__version__ = "2.9.0"
__version_info__ = (2, 9, 0)

# Version history
VERSION_HISTORY = {
    "2.9.0": {
        "date": "2025-12-08",
        "features": [
            "MCP Playground 功能",
            "支持配置和测试任意 MCP Server",
            "大模型对话交互，自动调用 MCP 工具",
            "可编辑的系统提示词",
            "左右分栏布局：配置区 + 对话区",
            "实时显示工具调用过程和结果",
            "MCP 客户端实现（支持 SSE 格式响应）"
        ]
    },
    "2.8.2": {
        "date": "2025-11-08",
        "features": [
            "修复 README.md 中所有图片路径",
            "更新项目结构说明反映实际目录布局",
            "修正技术架构图路径 (docs/images/diagrams/)",
            "修正功能截图路径 (docs/images/screenshots/)",
            "确保文档中图片正确显示"
        ]
    },
    "2.8.1": {
        "date": "2025-11-08",
        "features": [
            "清理过时的数据库迁移脚本",
            "移除 migrate_prompt_templates.py (v2.4.0迁移)",
            "移除 update_action_generation_template.py (v2.5.0迁移)",
            "移除 verify_action_generation_consistency.py (v2.5.0验证)",
            "精简 README.md，移除过时的升级指南",
            "提升代码库可维护性"
        ]
    },
    "2.8.0": {
        "date": "2025-11-08",
        "features": [
            "应用配置导入导出功能",
            "支持导出全部应用或选择性导出",
            "导入前预览(新建/覆盖应用列表)",
            "自动识别同名应用并直接覆盖",
            "JSON格式验证和友好错误提示",
            "导出文件自动生成时间戳文件名",
            "导入后提醒用户手动设置Token权限"
        ]
    },
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