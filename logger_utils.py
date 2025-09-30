#!/usr/bin/env python3
"""
增强的日志系统
支持文件日志记录、详细的调用信息记录、DEBUG模式等
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()

class MCPLogger:
    """MCP 增强日志记录器"""

    def __init__(self, name: str = "UniMCPSim"):
        self.name = name
        self.debug_enabled = os.getenv('DEBUG', 'false').lower() == 'true'
        self.log_dir = os.getenv('LOG_DIR', 'logs')

        # 确保日志目录存在
        os.makedirs(self.log_dir, exist_ok=True)

        # 创建logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG if self.debug_enabled else logging.INFO)

        # 防止重复添加handler
        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self):
        """设置日志处理器"""

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # 文件处理器 - 所有日志
        all_log_file = os.path.join(self.log_dir, 'unimcp_all.log')
        all_handler = RotatingFileHandler(
            all_log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
        )
        all_handler.setLevel(logging.DEBUG)
        all_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        all_handler.setFormatter(all_formatter)
        self.logger.addHandler(all_handler)

        # 文件处理器 - 错误日志
        error_log_file = os.path.join(self.log_dir, 'unimcp_error.log')
        error_handler = RotatingFileHandler(
            error_log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(all_formatter)
        self.logger.addHandler(error_handler)

        # DEBUG模式下的详细日志
        if self.debug_enabled:
            debug_log_file = os.path.join(self.log_dir, 'unimcp_debug.log')
            debug_handler = RotatingFileHandler(
                debug_log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
            )
            debug_handler.setLevel(logging.DEBUG)
            debug_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - [%(levelname)s] - %(pathname)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            debug_handler.setFormatter(debug_formatter)
            self.logger.addHandler(debug_handler)

    def log_mcp_request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None,
                       token: Optional[str] = None, headers: Optional[Dict[str, str]] = None,
                       success: bool = True, error: Optional[str] = None,
                       response: Optional[Dict[str, Any]] = None):
        """记录 MCP Server 调用详情"""

        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'mcp_request',
            'method': method,
            'path': path,
            'token': token[:8] + '...' if token else None,  # 只记录token前8位
            'params': params,
            'success': success,
            'error': error,
        }

        # DEBUG模式下记录更多信息
        if self.debug_enabled:
            log_data['headers'] = headers
            log_data['full_token'] = token
            log_data['response'] = response

        log_msg = f"MCP Request: {method} {path}"
        if success:
            self.logger.info(f"{log_msg} - SUCCESS")
            if self.debug_enabled:
                self.logger.debug(f"MCP Request Details: {json.dumps(log_data, ensure_ascii=False, indent=2)}")
        else:
            self.logger.error(f"{log_msg} - FAILED: {error}")
            self.logger.error(f"MCP Request Details: {json.dumps(log_data, ensure_ascii=False, indent=2)}")

    def log_ai_call(self, provider: str, model: str, prompt: str,
                   response: Optional[str] = None, success: bool = True,
                   error: Optional[str] = None, duration: Optional[float] = None,
                   usage: Optional[Dict[str, Any]] = None):
        """记录大模型调用详情"""

        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'ai_call',
            'provider': provider,
            'model': model,
            'success': success,
            'duration_seconds': duration,
            'error': error,
        }

        # DEBUG模式下记录完整的prompt和response
        if self.debug_enabled:
            log_data['prompt'] = prompt
            log_data['response'] = response
            log_data['usage'] = usage

        log_msg = f"AI Call: {provider}/{model}"
        if success:
            self.logger.info(f"{log_msg} - SUCCESS (duration: {duration:.2f}s)" if duration else f"{log_msg} - SUCCESS")
            if self.debug_enabled:
                self.logger.debug(f"AI Call Details: {json.dumps(log_data, ensure_ascii=False, indent=2)}")
        else:
            self.logger.error(f"{log_msg} - FAILED: {error}")
            self.logger.error(f"AI Call Details: {json.dumps(log_data, ensure_ascii=False, indent=2)}")

    def log_tool_call(self, tool_name: str, arguments: Dict[str, Any],
                     result: Optional[Any] = None, success: bool = True,
                     error: Optional[str] = None, app_path: Optional[str] = None):
        """记录工具调用详情"""

        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'tool_call',
            'tool_name': tool_name,
            'app_path': app_path,
            'arguments': arguments,
            'success': success,
            'error': error,
        }

        # DEBUG模式下记录完整结果
        if self.debug_enabled:
            log_data['result'] = result

        log_msg = f"Tool Call: {tool_name}"
        if app_path:
            log_msg += f" (app: {app_path})"

        if success:
            self.logger.info(f"{log_msg} - SUCCESS")
            if self.debug_enabled:
                self.logger.debug(f"Tool Call Details: {json.dumps(log_data, ensure_ascii=False, indent=2)}")
        else:
            self.logger.error(f"{log_msg} - FAILED: {error}")
            self.logger.error(f"Tool Call Details: {json.dumps(log_data, ensure_ascii=False, indent=2)}")

    def log_auth_failure(self, reason: str, token: Optional[str] = None,
                        path: Optional[str] = None, ip: Optional[str] = None):
        """记录认证失败"""

        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'auth_failure',
            'reason': reason,
            'token': token[:8] + '...' if token else None,
            'path': path,
            'ip': ip,
        }

        if self.debug_enabled:
            log_data['full_token'] = token

        self.logger.warning(f"Auth Failure: {reason} (path: {path}, ip: {ip})")
        self.logger.warning(f"Auth Failure Details: {json.dumps(log_data, ensure_ascii=False)}")

    def log_database_operation(self, operation: str, details: Dict[str, Any],
                              success: bool = True, error: Optional[str] = None):
        """记录数据库操作"""

        if not self.debug_enabled:
            return  # 只在DEBUG模式下记录数据库操作

        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'database_operation',
            'operation': operation,
            'details': details,
            'success': success,
            'error': error,
        }

        log_msg = f"DB Operation: {operation}"
        if success:
            self.logger.debug(f"{log_msg} - SUCCESS")
        else:
            self.logger.error(f"{log_msg} - FAILED: {error}")

        self.logger.debug(f"DB Operation Details: {json.dumps(log_data, ensure_ascii=False, indent=2)}")

    def info(self, message: str):
        """信息日志"""
        self.logger.info(message)

    def debug(self, message: str):
        """调试日志"""
        self.logger.debug(message)

    def warning(self, message: str):
        """警告日志"""
        self.logger.warning(message)

    def error(self, message: str, exc_info: bool = False):
        """错误日志"""
        self.logger.error(message, exc_info=exc_info)


# 全局logger实例
mcp_logger = MCPLogger()