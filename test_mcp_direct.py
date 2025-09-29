#!/usr/bin/env python3
"""
Direct MCP Server Test - 测试MCP服务器的tool调用
"""

import asyncio
import httpx
import json
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db_manager, Token

async def test_mcp_tools():
    """测试MCP工具调用"""
    print("="*60)
    print("UniMCPSim MCP服务器工具测试")
    print("="*60)

    # 获取Demo Token
    session = db_manager.get_session()
    try:
        demo_token = session.query(Token).filter_by(name='Demo Token').first()
        if not demo_token:
            print("❌ 未找到Demo Token")
            return False
        token = demo_token.token
        print(f"✅ 使用Token: {token[:8]}...{token[-4:]}")
    finally:
        session.close()

    base_url = "http://localhost:8080/mcp"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }

    async with httpx.AsyncClient() as client:
        # 1. 初始化连接
        print("\n1. 初始化MCP连接...")
        init_payload = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "0.1.0",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            },
            "id": 1
        }

        url = f"{base_url}?token={token}"
        response = await client.post(url, json=init_payload, headers=headers)

        if response.status_code != 200:
            print(f"❌ 初始化失败: {response.status_code}")
            return False

        # 从Server-Sent Events响应中提取JSON数据
        content = response.text
        if "event: message" in content and "data: " in content:
            # 处理不同的换行符格式
            lines = content.replace('\r\n', '\n').split('\n')
            json_data = None
            for i, line in enumerate(lines):
                if line.startswith("data: "):
                    json_data = line[6:]  # 移除"data: "前缀
                    break
            if json_data:
                init_result = json.loads(json_data)
            print(f"✅ 初始化成功")
            print(f"   服务器: {init_result['result']['serverInfo']['name']}")
            print(f"   版本: {init_result['result']['serverInfo']['version']}")
        else:
            print(f"❌ 初始化响应格式错误")
            return False

        # 获取会话ID
        session_id = response.headers.get('mcp-session-id')
        if not session_id:
            print("❌ 未获取到会话ID")
            return False
        print(f"   会话ID: {session_id}")

        # 更新headers
        headers['mcp-session-id'] = session_id

        # 2. 测试list_available_apps工具
        print("\n2. 测试list_available_apps工具...")
        tool_payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "list_available_apps",
                "arguments": {
                    "token": token
                }
            },
            "id": 2
        }

        response = await client.post(url, json=tool_payload, headers=headers)
        if response.status_code == 200:
            content = response.text
            if "event: message" in content and "data: " in content:
                lines = content.replace('\r\n', '\n').split('\n')
                json_data = None
                for line in lines:
                    if line.startswith("data: "):
                        json_data = line[6:]
                        break
                if json_data:
                    result = json.loads(json_data)
                    if 'result' in result:
                        apps = result['result']['content'][0]['text']
                        apps_data = json.loads(apps)
                        print(f"✅ 获取到 {len(apps_data)} 个应用")
                        for app in apps_data[:3]:  # 显示前3个
                            print(f"   - {app['display_name']} ({app['path']})")
                    else:
                        print(f"❌ 工具调用失败: {result.get('error', '未知错误')}")
                        return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return False

        # 3. 测试execute_action工具
        print("\n3. 测试execute_action工具...")
        action_payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "execute_action",
                "arguments": {
                    "token": token,
                    "category": "IM",
                    "product": "WeChat",
                    "action": "send_message",
                    "parameters": {
                        "to_user": "testuser",
                        "text": "MCP测试消息"
                    }
                }
            },
            "id": 3
        }

        response = await client.post(url, json=action_payload, headers=headers)
        if response.status_code == 200:
            content = response.text
            if "event: message" in content and "data: " in content:
                lines = content.replace('\r\n', '\n').split('\n')
                json_data = None
                for line in lines:
                    if line.startswith("data: "):
                        json_data = line[6:]
                        break
                if json_data:
                    result = json.loads(json_data)
                    if 'result' in result:
                        action_result = result['result']['content'][0]['text']
                        action_data = json.loads(action_result)
                        print(f"✅ 动作执行成功")
                        print(f"   结果: {action_data.get('errmsg', 'success')}")
                    else:
                        print(f"❌ 动作执行失败: {result.get('error', '未知错误')}")
                        return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return False

        print("\n" + "="*60)
        print("🎉 MCP服务器所有测试通过!")
        return True

async def main():
    """主函数"""
    print("\n" + "#"*60)
    print("# UniMCPSim MCP服务器测试")
    print("#"*60)

    success = await test_mcp_tools()

    print("\n" + "#"*60)
    if success:
        print("# 🎉 所有MCP测试通过！")
        return 0
    else:
        print("# ❌ MCP测试失败")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试出错: {e}")
        sys.exit(1)