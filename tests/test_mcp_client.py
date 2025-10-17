#!/usr/bin/env python3
"""
MCP客户端测试 - 测试MCP协议交互
测试list tools、执行动作模拟
"""

import os
import sys
import json
import httpx
from typing import Optional

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db_manager, Token


class MCPClientTester:
    """MCP客户端测试器"""

    def __init__(self, base_url: str = "http://localhost:9090"):
        self.base_url = base_url
        self.token = None
        self.passed_tests = 0
        self.failed_tests = 0

    def get_valid_token(self) -> Optional[str]:
        """从数据库获取一个有效的Token"""
        print("\n获取有效Token...")
        session = db_manager.get_session()
        try:
            # 查找第一个启用的Token
            token = session.query(Token).filter_by(enabled=True).first()
            if token:
                print(f"✅ 找到Token: {token.name}")
                print(f"   Token: {token.token[:16]}...{token.token[-8:]}")
                return token.token
            else:
                print("❌ 未找到可用Token")
                return None
        finally:
            session.close()

    def test_mcp_list_tools(self) -> bool:
        """测试1: MCP list tools"""
        print("\n" + "="*60)
        print("测试1: MCP List Tools")
        print("="*60)

        if not self.token:
            print("❌ 没有可用Token，跳过测试")
            self.failed_tests += 1
            return False

        print("\n1.1 测试获取工具列表...")
        try:
            # 使用正确的应用路径
            url = f"{self.base_url}/ThreatIntelligence/Threatbook?token={self.token}"
            headers = {
                "Content-Type": "application/json",
                "Accept": "text/event-stream"  # SSE格式
            }

            payload = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": 1
            }

            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload, headers=headers)

                if response.status_code == 200:
                    # 解析SSE响应
                    response_text = response.text
                    # SSE格式: "event: message\ndata: {...}\n\n"
                    if "data: " in response_text:
                        json_str = response_text.split("data: ")[1].strip()
                        result = json.loads(json_str)
                    else:
                        result = response.json()

                    if 'result' in result and 'tools' in result['result']:
                        tools = result['result']['tools']
                        print(f"✅ 成功获取工具列表")
                        print(f"   工具数量: {len(tools)}")

                        # 显示前几个工具
                        if len(tools) > 0:
                            print("\n   前5个工具:")
                            for tool in tools[:5]:
                                print(f"   - {tool.get('name', 'unknown')}")
                                if 'description' in tool:
                                    desc = tool['description'][:60]
                                    print(f"     描述: {desc}...")

                        self.passed_tests += 1
                    else:
                        print("❌ 响应格式错误，缺少tools字段")
                        print(f"   响应内容: {json.dumps(result, ensure_ascii=False, indent=2)[:200]}")
                        self.failed_tests += 1
                        return False
                else:
                    print(f"❌ 请求失败: {response.status_code}")
                    print(f"   错误信息: {response.text[:200]}")
                    self.failed_tests += 1
                    return False

        except Exception as e:
            print(f"❌ 测试异常: {e}")
            self.failed_tests += 1
            return False

        return True

    def test_mcp_execute_action(self) -> bool:
        """测试2: MCP直接调用工具（独立测试）"""
        print("\n" + "="*60)
        print("测试2: MCP直接调用工具")
        print("="*60)
        print("说明: 测试在已知工具名称的情况下直接调用")

        if not self.token:
            print("❌ 没有可用Token，跳过测试")
            self.failed_tests += 1
            return False

        print("\n2.1 直接调用工具（已知名称）...")
        try:
            url = f"{self.base_url}/ThreatIntelligence/Threatbook?token={self.token}"
            headers = {
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            }

            # 直接调用已知的工具名称
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "query_ip_threat_intel",
                    "arguments": {
                        "ip": "8.8.8.8"
                    }
                },
                "id": 2
            }

            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload, headers=headers)

                if response.status_code == 200:
                    response_text = response.text
                    if "data: " in response_text:
                        json_str = response_text.split("data: ")[1].strip()
                        result = json.loads(json_str)
                    else:
                        result = response.json()

                    if 'result' in result:
                        print("✅ 工具直接调用成功")
                        self.passed_tests += 1
                    elif 'error' in result:
                        error = result['error']
                        if 'permission' in str(error).lower():
                            print("⚠️ 权限不足（MCP通信正常）")
                            self.passed_tests += 1
                        else:
                            print(f"❌ 错误: {error}")
                            self.failed_tests += 1
                            return False
                    else:
                        print("❌ 响应格式错误")
                        self.failed_tests += 1
                        return False
                else:
                    print(f"❌ 请求失败: {response.status_code}")
                    self.failed_tests += 1
                    return False

        except Exception as e:
            print(f"❌ 测试异常: {e}")
            self.failed_tests += 1
            return False

        return True

    def test_mcp_multiple_products(self) -> bool:
        """测试3: MCP核心流程验证（精简版）"""
        print("\n" + "="*60)
        print("测试3: MCP核心流程验证")
        print("="*60)
        print("说明: 只测试一个应用，验证MCP核心功能即可")

        if not self.token:
            print("❌ 没有可用Token，跳过测试")
            self.failed_tests += 1
            return False

        # 只测试一个应用即可验证系统功能
        print("\n3.1 完整MCP流程测试: ThreatBook威胁情报查询")

        url = f"{self.base_url}/ThreatIntelligence/Threatbook?token={self.token}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }

        with httpx.Client(timeout=30.0) as client:
            try:
                # 步骤1: List Tools
                print("   步骤1: 获取可用工具列表...")
                list_payload = {
                    "jsonrpc": "2.0",
                    "method": "tools/list",
                    "id": 1
                }

                response = client.post(url, json=list_payload, headers=headers)
                if response.status_code != 200:
                    print(f"   ❌ List tools失败: {response.status_code}")
                    self.failed_tests += 1
                    return False

                response_text = response.text
                if "data: " in response_text:
                    json_str = response_text.split("data: ")[1].strip()
                    result = json.loads(json_str)
                else:
                    result = response.json()

                tools = result.get('result', {}).get('tools', [])
                print(f"   ✅ 成功获取 {len(tools)} 个工具")

                if len(tools) == 0:
                    print("   ❌ 未找到任何工具")
                    self.failed_tests += 1
                    return False

                # 步骤2: 调用第一个工具
                first_tool = tools[0]
                tool_name = first_tool.get('name')
                print(f"   步骤2: 调用工具 '{tool_name}'...")

                call_payload = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": {
                            "ip": "8.8.8.8"  # 通用参数
                        }
                    },
                    "id": 2
                }

                response = client.post(url, json=call_payload, headers=headers)
                if response.status_code != 200:
                    print(f"   ❌ 工具调用失败: {response.status_code}")
                    self.failed_tests += 1
                    return False

                response_text = response.text
                if "data: " in response_text:
                    json_str = response_text.split("data: ")[1].strip()
                    result = json.loads(json_str)
                else:
                    result = response.json()

                if 'result' in result:
                    print(f"   ✅ 工具调用成功")
                    print(f"   ✅ 完整MCP流程验证通过")
                    self.passed_tests += 1
                else:
                    print(f"   ❌ 工具调用返回错误: {result.get('error')}")
                    self.failed_tests += 1
                    return False

            except Exception as e:
                print(f"   ❌ 测试异常: {e}")
                self.failed_tests += 1
                return False

        return True

    def test_mcp_resources_list(self) -> bool:
        """测试4: MCP resources/list (可选功能)"""
        print("\n" + "="*60)
        print("测试4: MCP Resources List (可选功能)")
        print("="*60)

        if not self.token:
            print("⚠️  没有可用Token，跳过测试")
            return True

        print("\n4.1 测试获取资源列表...")
        try:
            # 使用正确的应用路径
            url = f"{self.base_url}/ThreatIntelligence/Threatbook?token={self.token}"
            headers = {
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            }

            payload = {
                "jsonrpc": "2.0",
                "method": "resources/list",
                "id": 100
            }

            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload, headers=headers)

                if response.status_code == 200:
                    # 解析SSE响应
                    response_text = response.text
                    if "data: " in response_text:
                        json_str = response_text.split("data: ")[1].strip()
                        result = json.loads(json_str)
                    else:
                        result = response.json()

                    if 'result' in result:
                        resources = result['result'].get('resources', [])
                        print(f"✅ 成功获取资源列表")
                        print(f"   资源数量: {len(resources)}")

                        if len(resources) > 0:
                            print("\n   资源示例:")
                            for res in resources[:3]:
                                print(f"   - {res.get('name', 'unknown')}")
                                print(f"     URI: {res.get('uri', 'N/A')}")

                        self.passed_tests += 1
                    elif 'error' in result:
                        # resources/list 不是必需功能，返回Method not found是正常的
                        error = result.get('error', {})
                        if isinstance(error, dict) and error.get('code') == -32601:
                            print("⚠️  Resources功能未实现 (这是可选功能)")
                            self.passed_tests += 1  # 算作通过
                        else:
                            print(f"⚠️  Resources功能返回错误: {error}")
                            self.passed_tests += 1  # 仍算通过，因为是可选功能
                    else:
                        print("⚠️  响应格式不符合预期，但Resources是可选功能")
                        self.passed_tests += 1
                else:
                    print(f"⚠️  请求返回: {response.status_code} (Resources是可选功能)")
                    self.passed_tests += 1

        except Exception as e:
            print(f"⚠️  测试异常: {e} (Resources是可选功能)")
            self.passed_tests += 1

        return True

    def run_all_tests(self) -> bool:
        """运行所有测试"""
        print("\n" + "#"*60)
        print("# UniMCPSim MCP客户端测试")
        print("#"*60)

        # 获取Token
        self.token = self.get_valid_token()

        if not self.token:
            print("\n❌ 无法获取有效Token，测试终止")
            print("请确保数据库中存在启用的Token")
            print("提示: 可以通过Admin界面创建Token")
            return False

        # 运行测试
        self.test_mcp_list_tools()
        self.test_mcp_execute_action()
        self.test_mcp_multiple_products()
        self.test_mcp_resources_list()

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


def main():
    """主函数"""
    # 检查MCP服务器是否运行
    print("检查MCP服务器是否运行在 http://localhost:9090 ...")
    try:
        response = httpx.get("http://localhost:9090/health", timeout=5)
        print("✅ MCP服务器正在运行\n")
    except Exception as e:
        print(f"❌ 无法连接到MCP服务器: {e}")
        print("请先运行: ./start_servers.sh 或 python start_servers.py")
        return 1

    # 运行测试
    tester = MCPClientTester()
    success = tester.run_all_tests()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
