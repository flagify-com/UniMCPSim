#!/usr/bin/env python3
"""
端到端测试 - MCP服务器调用完整测试
"""

import os
import sys
import json
import asyncio
import httpx
from typing import Dict, Any

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class UniMCPSimTester:
    """UniMCPSim测试器"""

    def __init__(self, base_url: str = "http://localhost:8080", token: str = None):
        self.base_url = base_url
        self.token = token
        self.passed_tests = 0
        self.failed_tests = 0

    async def test_direct_api(self):
        """测试直接API调用"""
        print("\n" + "="*60)
        print("测试1: 直接API调用测试")
        print("="*60)

        async with httpx.AsyncClient() as client:
            # 测试获取应用列表
            print("\n1. 获取可用应用列表...")
            url = f"{self.base_url}/mcp"
            headers = {"Content-Type": "application/json"}

            payload = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": 1
            }

            if self.token:
                url = f"{url}?token={self.token}"

            try:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ 成功获取工具列表")
                    if 'result' in result and 'tools' in result['result']:
                        print(f"   可用工具数量: {len(result['result']['tools'])}")
                        for tool in result['result']['tools'][:3]:
                            print(f"   - {tool.get('name', 'unknown')}")
                    self.passed_tests += 1
                else:
                    print(f"❌ 请求失败: {response.status_code}")
                    self.failed_tests += 1
            except Exception as e:
                print(f"❌ 测试失败: {e}")
                self.failed_tests += 1

            # 测试执行动作
            print("\n2. 测试执行模拟器动作...")
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "execute_action",
                    "arguments": {
                        "token": self.token,
                        "category": "IM",
                        "product": "WeChat",
                        "action": "send_message",
                        "parameters": {
                            "to_user": "user123",
                            "text": "测试消息"
                        }
                    }
                },
                "id": 2
            }

            try:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ 动作执行成功")
                    if 'result' in result:
                        print(f"   响应: {json.dumps(result['result'], ensure_ascii=False, indent=2)}")
                    self.passed_tests += 1
                else:
                    print(f"❌ 请求失败: {response.status_code}")
                    self.failed_tests += 1
            except Exception as e:
                print(f"❌ 测试失败: {e}")
                self.failed_tests += 1

    async def test_mcp_client(self):
        """测试MCP客户端连接"""
        print("\n" + "="*60)
        print("测试2: MCP客户端连接测试")
        print("="*60)

        try:
            # 创建HTTP传输
            transport = httpx.AsyncHTTPTransport()
            url = f"{self.base_url}/mcp"
            if self.token:
                url = f"{url}?token={self.token}"

            async with httpx.AsyncClient(transport=transport, base_url=url) as client:
                # 初始化会话
                session = ClientSession()

                # 初始化连接
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

                response = await client.post("", json=init_payload)
                if response.status_code == 200:
                    print("✅ MCP连接初始化成功")
                    self.passed_tests += 1
                else:
                    print(f"❌ 初始化失败: {response.status_code}")
                    self.failed_tests += 1

                # 列出工具
                print("\n2. 列出可用工具...")
                tools_payload = {
                    "jsonrpc": "2.0",
                    "method": "tools/list",
                    "id": 2
                }

                response = await client.post("", json=tools_payload)
                if response.status_code == 200:
                    result = response.json()
                    tools = result.get('result', {}).get('tools', [])
                    print(f"✅ 获取到 {len(tools)} 个工具")
                    self.passed_tests += 1
                else:
                    print(f"❌ 获取工具列表失败")
                    self.failed_tests += 1

        except Exception as e:
            print(f"❌ MCP客户端测试失败: {e}")
            self.failed_tests += 1

    async def test_multiple_simulators(self):
        """测试多个模拟器"""
        print("\n" + "="*60)
        print("测试3: 多模拟器功能测试")
        print("="*60)

        test_cases = [
            {
                "name": "VirusTotal IP扫描",
                "category": "Security",
                "product": "VirusTotal",
                "action": "scan_ip",
                "params": {"ip": "192.168.1.1"}
            },
            {
                "name": "Jira创建工单",
                "category": "Ticket",
                "product": "Jira",
                "action": "create_issue",
                "params": {
                    "title": "测试工单",
                    "description": "这是一个测试工单",
                    "priority": "High"
                }
            },
            {
                "name": "深信服防火墙封禁IP",
                "category": "Firewall",
                "product": "Sangfor",
                "action": "block_ip",
                "params": {
                    "ip": "10.0.0.1",
                    "reason": "恶意攻击"
                }
            }
        ]

        async with httpx.AsyncClient() as client:
            for i, test in enumerate(test_cases, 1):
                print(f"\n测试 {i}: {test['name']}")

                url = f"{self.base_url}/mcp"
                if self.token:
                    url = f"{url}?token={self.token}"

                payload = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "execute_action",
                        "arguments": {
                            "token": self.token,
                            "category": test['category'],
                            "product": test['product'],
                            "action": test['action'],
                            "parameters": test['params']
                        }
                    },
                    "id": i
                }

                try:
                    response = await client.post(url, json=payload)
                    if response.status_code == 200:
                        result = response.json()
                        if 'result' in result:
                            print(f"✅ 成功: {test['name']}")
                            self.passed_tests += 1
                        else:
                            print(f"❌ 失败: 无结果返回")
                            self.failed_tests += 1
                    else:
                        print(f"❌ 请求失败: {response.status_code}")
                        self.failed_tests += 1
                except Exception as e:
                    print(f"❌ 测试失败: {e}")
                    self.failed_tests += 1

    async def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "#"*60)
        print("# UniMCPSim 端到端测试")
        print("#"*60)

        # 运行测试
        await self.test_direct_api()
        await self.test_mcp_client()
        await self.test_multiple_simulators()

        # 输出总结
        print("\n" + "="*60)
        print("测试总结")
        print("="*60)
        total = self.passed_tests + self.failed_tests
        print(f"总测试数: {total}")
        print(f"✅ 通过: {self.passed_tests}")
        print(f"❌ 失败: {self.failed_tests}")

        if self.failed_tests == 0:
            print("\n🎉 所有测试通过!")
        else:
            print(f"\n⚠️ 有 {self.failed_tests} 个测试失败")

        return self.failed_tests == 0


async def main():
    """主函数"""
    # 从环境变量或默认值获取Token
    token = os.getenv('TEST_TOKEN', '')

    if not token:
        print("提示: 未设置TEST_TOKEN环境变量，尝试使用默认Demo Token")
        print("您可以通过以下方式设置Token:")
        print("export TEST_TOKEN=your_token_here")
        print("")

        # 尝试获取Demo Token
        try:
            # 这里假设已经运行了初始化脚本
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from models import db_manager, Token

            session = db_manager.get_session()
            demo_token = session.query(Token).filter_by(name='Demo Token').first()
            if demo_token:
                token = demo_token.token
                print(f"使用Demo Token: {token[:8]}...{token[-4:]}")
            session.close()
        except:
            print("警告: 无法获取Demo Token，测试可能失败")
            token = "test-token"

    # 运行测试
    tester = UniMCPSimTester(token=token)
    success = await tester.run_all_tests()

    # 返回状态码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    # 确保使用正确的事件循环
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试出错: {e}")
        sys.exit(1)