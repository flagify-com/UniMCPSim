#!/usr/bin/env python3
"""
测试产品特定端点功能
"""

import asyncio
import sys
import os
import httpx

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import DatabaseManager, Token

class ProductEndpointTester:
    def __init__(self, base_url="http://localhost:8080", token=None):
        self.base_url = base_url
        self.token = token
        self.passed_tests = 0
        self.failed_tests = 0

    async def run_tests(self):
        """运行所有测试"""
        print("############################################################")
        print("# UniMCPSim 产品端点测试")
        print("############################################################")

        # 获取Token
        if not self.token:
            await self.get_demo_token()

        print(f"\n使用Token: {self.token[:10]}...{self.token[-6:]}")

        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=10.0)) as client:
            # 测试企业微信端点
            await self.test_wechat_endpoint(client)

            # 测试VirusTotal端点
            await self.test_virustotal_endpoint(client)

            # 测试Jira端点
            await self.test_jira_endpoint(client)

            # 测试深信服防火墙端点
            await self.test_sangfor_firewall_endpoint(client)

            # 测试华为交换机端点
            await self.test_huawei_switch_endpoint(client)

        self.print_summary()

    async def get_demo_token(self):
        """从数据库获取Demo Token"""
        try:
            db_manager = DatabaseManager()
            session = db_manager.get_session()
            try:
                demo_token = session.query(Token).filter_by(name='Demo Token').first()
                if not demo_token:
                    print("❌ 未找到Demo Token")
                    exit(1)

                self.token = demo_token.token
                print(f"✅ 自动获取Demo Token")
            finally:
                session.close()
        except Exception as e:
            print(f"❌ 获取Token失败: {e}")
            exit(1)

    async def test_wechat_endpoint(self, client):
        """测试企业微信端点"""
        print("\n============================================================")
        print("测试企业微信端点")
        print("============================================================")

        url = f"{self.base_url}/IM/WeChat?token={self.token}"

        # 测试获取工具列表
        print("1. 获取工具列表...")
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 1
        }

        try:
            response = await client.post(url, json=payload, headers={"Content-Type": "application/json"})
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 成功获取工具列表")
                if 'result' in result and 'tools' in result['result']:
                    tools = result['result']['tools']
                    print(f"   可用工具数量: {len(tools)}")
                    for tool in tools[:3]:
                        print(f"   - {tool.get('name', 'unknown')}")
                self.passed_tests += 1
            else:
                print(f"❌ 请求失败: {response.status_code}")
                self.failed_tests += 1
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            self.failed_tests += 1

        # 测试发送消息
        print("\n2. 测试发送消息...")
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "send_text_message",
                "arguments": {
                    "to_user": "test_user",
                    "content": "Hello from UniMCPSim!"
                }
            },
            "id": 2
        }

        try:
            response = await client.post(url, json=payload, headers={"Content-Type": "application/json"})
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 发送消息成功")
                self.passed_tests += 1
            else:
                print(f"❌ 请求失败: {response.status_code}")
                self.failed_tests += 1
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            self.failed_tests += 1

    async def test_virustotal_endpoint(self, client):
        """测试VirusTotal端点"""
        print("\n============================================================")
        print("测试VirusTotal端点")
        print("============================================================")

        url = f"{self.base_url}/Security/VirusTotal?token={self.token}"

        # 测试IP扫描
        print("1. 测试IP威胁扫描...")
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "scan_ip",
                "arguments": {
                    "ip": "8.8.8.8"
                }
            },
            "id": 1
        }

        try:
            response = await client.post(url, json=payload, headers={"Content-Type": "application/json"})
            if response.status_code == 200:
                result = response.json()
                print(f"✅ IP扫描成功")
                self.passed_tests += 1
            else:
                print(f"❌ 请求失败: {response.status_code}")
                self.failed_tests += 1
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            self.failed_tests += 1

    async def test_jira_endpoint(self, client):
        """测试Jira端点"""
        print("\n============================================================")
        print("测试Jira工单系统端点")
        print("============================================================")

        url = f"{self.base_url}/Ticket/Jira?token={self.token}"

        # 测试创建工单
        print("1. 测试创建工单...")
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "create_issue",
                "arguments": {
                    "summary": "测试工单",
                    "description": "这是一个测试工单"
                }
            },
            "id": 1
        }

        try:
            response = await client.post(url, json=payload, headers={"Content-Type": "application/json"})
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 创建工单成功")
                self.passed_tests += 1
            else:
                print(f"❌ 请求失败: {response.status_code}")
                self.failed_tests += 1
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            self.failed_tests += 1

    async def test_sangfor_firewall_endpoint(self, client):
        """测试深信服防火墙端点"""
        print("\n============================================================")
        print("测试深信服防火墙端点")
        print("============================================================")

        url = f"{self.base_url}/Firewall/Sangfor?token={self.token}"

        # 测试封禁IP
        print("1. 测试封禁IP...")
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "block_ip",
                "arguments": {
                    "ip": "192.168.1.100",
                    "reason": "恶意行为"
                }
            },
            "id": 1
        }

        try:
            response = await client.post(url, json=payload, headers={"Content-Type": "application/json"})
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 封禁IP成功")
                self.passed_tests += 1
            else:
                print(f"❌ 请求失败: {response.status_code}")
                self.failed_tests += 1
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            self.failed_tests += 1

    async def test_huawei_switch_endpoint(self, client):
        """测试华为交换机端点"""
        print("\n============================================================")
        print("测试华为交换机端点")
        print("============================================================")

        url = f"{self.base_url}/Network/HuaweiSwitch?token={self.token}"

        # 测试查看接口状态
        print("1. 测试查看接口状态...")
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "show_interface",
                "arguments": {
                    "interface": "GigabitEthernet0/0/1"
                }
            },
            "id": 1
        }

        try:
            response = await client.post(url, json=payload, headers={"Content-Type": "application/json"})
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 查看接口状态成功")
                self.passed_tests += 1
            else:
                print(f"❌ 请求失败: {response.status_code}")
                self.failed_tests += 1
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            self.failed_tests += 1

    def print_summary(self):
        """打印测试总结"""
        print("\n============================================================")
        print("测试总结")
        print("============================================================")
        total_tests = self.passed_tests + self.failed_tests

        if total_tests > 0:
            pass_rate = (self.passed_tests / total_tests) * 100
            print(f"总测试数: {total_tests}")
            print(f"通过: {self.passed_tests}")
            print(f"失败: {self.failed_tests}")
            print(f"通过率: {pass_rate:.1f}%")

            if self.failed_tests == 0:
                print("🎉 所有测试通过!")
            else:
                print("❌ 部分测试失败")
        else:
            print("❌ 没有运行任何测试")

async def main():
    """主函数"""
    tester = ProductEndpointTester()
    await tester.run_tests()

if __name__ == "__main__":
    asyncio.run(main())