#!/usr/bin/env python3
"""
启动UniMCPSim服务器
"""

import os
import sys
import time
import threading
import subprocess
from init_simulators import init_default_simulators

def run_mcp_server():
    """运行MCP服务器"""
    subprocess.run([sys.executable, 'mcp_server.py'])

def run_admin_server():
    """运行管理后台服务器"""
    subprocess.run([sys.executable, 'admin_server.py'])

def main():
    print("=" * 60)
    print("UniMCPSim - Universal MCP Simulator")
    print("=" * 60)

    # 创建数据目录
    os.makedirs('data', exist_ok=True)

    # 初始化默认模拟器
    print("\n初始化默认模拟器...")
    init_default_simulators()

    print("\n启动服务...")
    print("-" * 60)

    # 启动MCP服务器线程
    mcp_thread = threading.Thread(target=run_mcp_server)
    mcp_thread.daemon = True
    mcp_thread.start()

    # 等待一下让MCP服务器启动
    time.sleep(2)

    # 启动管理后台服务器线程
    admin_thread = threading.Thread(target=run_admin_server)
    admin_thread.daemon = True
    admin_thread.start()

    print("\n服务已启动:")
    print("-" * 60)
    print("MCP服务器: http://localhost:8080/mcp")
    print("管理后台: http://localhost:8081/admin/")
    print("默认账号: admin / admin123")
    print("-" * 60)
    print("\n按 Ctrl+C 停止服务")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止服务...")
        sys.exit(0)

if __name__ == "__main__":
    main()