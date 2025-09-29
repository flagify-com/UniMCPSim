#!/usr/bin/env python3
"""
SOAR MCP Server 版本管理
"""

__version__ = "1.0.4"
__version_info__ = (1, 0, 4)

# 版本说明
VERSION_NOTES = {
    "1.0.0": "首个稳定版本，支持SOAR剧本执行和MCP集成",
    "1.0.1": "修复统计页面最后同步时间显示问题和时区处理问题",
    "1.0.2": "统一MCP工具名称，修复文档和代码中的命名不一致问题",
    "1.0.3": "优化MCP工具命名，增强AI可理解性和语义明确性",
    "1.0.4": "优化剧本标签管理逻辑，支持空标签同步所有剧本，适配社区免费版"
}

def get_version():
    """获取当前版本号"""
    return __version__

def get_version_info():
    """获取版本信息元组"""
    return __version_info__

def get_version_string():
    """获取详细版本字符串"""
    return f"SOAR MCP Server v{__version__}"