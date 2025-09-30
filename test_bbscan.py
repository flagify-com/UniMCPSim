#!/usr/bin/env python3
"""
测试 BBScan 扫描器的实际调用
演示提示词模板系统的完整工作流程
"""

import asyncio
import httpx
import json
import sys

class BBScanTester:
    def __init__(self, base_url="http://localhost:8080", token=None):
        self.base_url = base_url
        self.token = token or "f1bb3770-6e46-4fe6-b518-e1c738c7b6a4"  # Demo Token
        self.session_id = None
        self.endpoint = f"{base_url}/Scanner/BBScan"

    async def initialize(self):
        """初始化MCP连接"""
        print("【初始化 MCP 连接】")

        async with httpx.AsyncClient() as client:
            payload = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "0.1.0",
                    "capabilities": {},
                    "clientInfo": {"name": "bbscan-tester", "version": "1.0.0"}
                },
                "id": 1
            }

            response = await client.post(
                f"{self.endpoint}?token={self.token}",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            )

            if response.status_code == 200:
                self.session_id = response.headers.get('mcp-session-id')
                print(f"✅ 连接成功，会话ID: {self.session_id}")

                # 解析SSE响应
                content = response.text
                if content.startswith("event: message"):
                    json_str = content.split("data: ")[1].strip()
                    result = json.loads(json_str)
                    print(f"服务器信息: {result['result']['serverInfo']}")
                return True
            else:
                print(f"❌ 连接失败: {response.status_code}")
                return False

    async def scan_url(self, target_url, scan_type="full", max_depth=3):
        """执行URL扫描"""
        if not self.session_id:
            print("❌ 请先初始化连接")
            return None

        print(f"\n【执行扫描】目标: {target_url}")
        print("发送请求到 AI 生成器...")

        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "scan_url",
                    "arguments": {
                        "target_url": target_url,
                        "scan_type": scan_type,
                        "max_depth": max_depth,
                        "follow_redirects": True,
                        "threads": 10
                    }
                },
                "id": 2
            }

            print("\n请求内容:")
            print(json.dumps(payload, ensure_ascii=False, indent=2))

            response = await client.post(
                f"{self.endpoint}?token={self.token}",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                    "mcp-session-id": self.session_id
                }
            )

            if response.status_code == 200:
                # 解析SSE响应
                content = response.text
                if content.startswith("event: message"):
                    json_str = content.split("data: ")[1].strip()
                    result = json.loads(json_str)

                    if "result" in result and "content" in result["result"]:
                        scan_result = json.loads(result["result"]["content"][0]["text"])
                        return scan_result
                    else:
                        print(f"❌ 响应格式错误: {result}")
                        return None
            else:
                print(f"❌ 扫描失败: {response.status_code}")
                print(response.text)
                return None

    async def list_tools(self):
        """列出可用的工具"""
        if not self.session_id:
            print("❌ 请先初始化连接")
            return None

        print("\n【获取可用工具列表】")

        async with httpx.AsyncClient() as client:
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 3
            }

            response = await client.post(
                f"{self.endpoint}?token={self.token}",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                    "mcp-session-id": self.session_id
                }
            )

            if response.status_code == 200:
                content = response.text
                if content.startswith("event: message"):
                    json_str = content.split("data: ")[1].strip()
                    result = json.loads(json_str)

                    if "result" in result and "tools" in result["result"]:
                        tools = result["result"]["tools"]
                        print(f"✅ 找到 {len(tools)} 个工具:")
                        for tool in tools:
                            print(f"  - {tool['name']}: {tool['description']}")
                        return tools
            return None

async def main():
    print("="*60)
    print("BBScan 扫描器测试 - 提示词模板系统演示")
    print("="*60)
    print()

    # 检查参数
    target_url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"

    # 创建测试器
    tester = BBScanTester()

    # 初始化连接
    if await tester.initialize():
        # 列出可用工具
        await tester.list_tools()

        # 执行扫描
        print("\n" + "="*60)
        print("执行扫描任务")
        print("="*60)

        result = await tester.scan_url(target_url, scan_type="full", max_depth=3)

        if result:
            print("\n【AI 生成的模拟响应】")
            print("="*60)
            print(json.dumps(result, ensure_ascii=False, indent=2))

            # 分析结果
            print("\n【响应分析】")
            print("="*60)
            if "success" in result and result["success"]:
                print("✅ 扫描成功")

                if "statistics" in result:
                    stats = result["statistics"]
                    print(f"\n📊 统计信息:")
                    for key, value in stats.items():
                        print(f"  - {key}: {value}")

                if "vulnerabilities" in result:
                    vuln = result["vulnerabilities"]
                    print(f"\n🔍 漏洞统计:")
                    for level, count in vuln.items():
                        print(f"  - {level}: {count}")

                if "interesting_findings" in result and result["interesting_findings"]:
                    print(f"\n⚠️ 重要发现:")
                    for finding in result["interesting_findings"][:3]:
                        print(f"  - {finding.get('path', 'N/A')}: {finding.get('description', 'N/A')}")

                if "recommendations" in result and result["recommendations"]:
                    print(f"\n💡 建议:")
                    for rec in result["recommendations"][:3]:
                        print(f"  - {rec}")
            else:
                print("❌ 扫描失败")
        else:
            print("❌ 未能获取扫描结果")

    print("\n" + "="*60)
    print("提示词模板工作原理")
    print("="*60)
    print("""
1. 系统从数据库获取 'response_simulation' 模板
2. 替换模板变量:
   - {app_name} → "BBScan网站扫描器"
   - {action} → "scan_url"
   - {parameters} → 用户提供的扫描参数
3. 发送给 OpenAI API (gpt-4o-mini)
4. AI 根据应用类型生成真实的模拟响应
5. 返回格式化的 JSON 结果
""")

if __name__ == "__main__":
    print("注意：确保 MCP 服务器正在运行 (python3 mcp_server.py)")
    print("如果需要指定目标URL，请提供参数：python3 test_bbscan.py https://target.com")
    print()

    asyncio.run(main())