#!/usr/bin/env python3
"""
SOAR MCP 日志配置模块
提供统一的日志输出，支持控制台和文件双重输出
"""

import logging
import os
from datetime import datetime
from pathlib import Path


class SOARLogger:
    """SOAR日志管理器"""
    
    def __init__(self, name: str = "SOAR_MCP", log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 创建logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 避免重复添加handler
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """设置日志处理器"""
        
        # 创建格式器
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        
        # 文件处理器 - 按日期命名
        today = datetime.now().strftime("%Y%m%d")
        log_file = self.log_dir / f"soar_mcp_{today}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """调试信息"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """普通信息"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """警告信息"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """错误信息"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """严重错误"""
        self.logger.critical(message)
    
    def sync_start(self, message: str):
        """同步开始 - 特殊格式"""
        self.logger.info(f"🔄 {message}")
    
    def sync_success(self, message: str):
        """同步成功 - 特殊格式"""
        self.logger.info(f"✅ {message}")
    
    def sync_error(self, message: str):
        """同步错误 - 特殊格式"""
        self.logger.error(f"❌ {message}")
    
    def sync_warning(self, message: str):
        """同步警告 - 特殊格式"""
        self.logger.warning(f"⚠️  {message}")
    
    def sync_skip(self, message: str):
        """同步跳过 - 特殊格式"""
        self.logger.info(f"⏭️  {message}")
    
    def sync_debug(self, message: str):
        """同步调试 - 特殊格式"""
        self.logger.debug(f"🔍 {message}")
    
    def server_info(self, message: str):
        """服务器信息 - 特殊格式"""
        self.logger.info(f"🚀 {message}")
    
    def database_info(self, message: str):
        """数据库信息 - 特殊格式"""
        self.logger.info(f"🗄️  {message}")


# 全局日志实例
logger = SOARLogger()


def get_logger(name: str = None) -> SOARLogger:
    """获取日志实例"""
    if name:
        return SOARLogger(name)
    return logger