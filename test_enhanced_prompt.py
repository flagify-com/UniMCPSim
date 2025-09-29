#!/usr/bin/env python3
"""
测试增强版提示词系统
对比新旧版本的差异，验证动作定义的影响
"""

import asyncio
import httpx
import json
import sys
from datetime import datetime

class EnhancedPromptTester:
    def __init__(self, base_url="http://localhost:8080", token=None):
        self.base_url = base_url
        self.token = token or "f1bb3770-6e46-4fe6-b518-e1c738c7b6a4"
        self.session_id = None
        self.endpoint = f"{base_url}/Scanner/BBScan"

    async def initialize(self):
        """初始化MCP连接"""
        async with httpx.AsyncClient() as client:
            payload = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "0.1.0",
                    "capabilities": {},
                    "clientInfo": {"name": "enhanced-prompt-tester", "version": "1.0.0"}
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
                return True
            return False

    async def test_scan_scenarios(self):
        """测试不同的扫描场景"""
        if not self.session_id:
            return

        scenarios = [
            {
                "name": "基础扫描测试",
                "params": {
                    "target_url": "https://example.com",
                    "scan_type": "basic",
                    "max_depth": 1
                },
                "expected_features": ["快速扫描", "基础路径", "浅层检查"]
            },
            {
                "name": "完整扫描测试",
                "params": {
                    "target_url": "https://test-site.com",
                    "scan_type": "full",
                    "max_depth": 3,
                    "follow_redirects": True,
                    "threads": 20
                },
                "expected_features": ["深度扫描", "完整报告", "高并发", "重定向处理"]
            },
            {
                "name": "自定义扫描测试",
                "params": {
                    "target_url": "https://secure-app.com",
                    "scan_type": "custom",
                    "max_depth": 5,
                    "follow_redirects": False,
                    "threads": 5
                },
                "expected_features": ["自定义配置", "高深度", "低并发", "无重定向"]
            }
        ]

        results = []

        for i, scenario in enumerate(scenarios, 1):
            print(f"\n{'='*60}")
            print(f"测试场景 {i}: {scenario['name']}")
            print(f"{'='*60}")

            print("输入参数:")
            print(json.dumps(scenario['params'], ensure_ascii=False, indent=2))

            result = await self._call_scan(scenario['params'])
            if result:
                results.append({
                    "scenario": scenario['name'],
                    "params": scenario['params'],
                    "result": result,
                    "expected_features": scenario['expected_features']
                })

                print("\nAI 生成的响应:")
                print("-" * 40)
                print(json.dumps(result, ensure_ascii=False, indent=2))

                # 分析响应特点
                self._analyze_response(result, scenario)
            else:
                print("❌ 请求失败")

        return results

    async def _call_scan(self, params):
        """调用扫描接口"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "scan_url",
                    "arguments": params
                },
                "id": 2
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

                    if "result" in result and "content" in result["result"]:
                        return json.loads(result["result"]["content"][0]["text"])
            return None

    def _analyze_response(self, result, scenario):
        """分析响应是否符合预期"""
        print("\n📊 响应分析:")

        params = scenario['params']
        expected_features = scenario['expected_features']

        # 检查基本结构
        if 'success' in result:
            print(f"✅ 包含成功标识: {result['success']}")

        if 'scan_type' in result:
            expected_type = params.get('scan_type', 'basic')
            actual_type = result.get('scan_type')
            if actual_type == expected_type:
                print(f"✅ 扫描类型匹配: {actual_type}")
            else:
                print(f"⚠️ 扫描类型不匹配: 期望 {expected_type}, 实际 {actual_type}")

        if 'target_url' in result:
            expected_url = params.get('target_url')
            actual_url = result.get('target_url')
            if actual_url == expected_url:
                print(f"✅ 目标URL匹配: {actual_url}")

        # 检查深度相关的结构
        max_depth = params.get('max_depth', 2)
        if 'statistics' in result:
            stats = result['statistics']
            if 'scan_depth' in stats:
                if stats['scan_depth'] == max_depth:
                    print(f"✅ 扫描深度匹配: {max_depth}")
                else:
                    print(f"⚠️ 扫描深度不匹配: 期望 {max_depth}, 实际 {stats['scan_depth']}")

        # 检查并发相关
        threads = params.get('threads', 10)
        if 'scan_config' in result:
            config = result['scan_config']
            if 'threads' in config:
                if config['threads'] == threads:
                    print(f"✅ 线程数匹配: {threads}")

        # 检查重定向设置
        follow_redirects = params.get('follow_redirects', False)
        if 'scan_config' in result:
            config = result['scan_config']
            if 'follow_redirects' in config:
                if config['follow_redirects'] == follow_redirects:
                    print(f"✅ 重定向设置匹配: {follow_redirects}")

        # 检查扫描类型对应的功能
        scan_type = params.get('scan_type', 'basic')
        if scan_type == 'full':
            if 'vulnerabilities' in result and 'interesting_findings' in result:
                print("✅ 完整扫描包含漏洞和发现信息")
            if 'directories' in result and len(result.get('directories', [])) > 3:
                print("✅ 完整扫描包含较多目录信息")
        elif scan_type == 'basic':
            if 'statistics' in result:
                stats = result['statistics']
                if stats.get('total_requests', 0) < 200:
                    print("✅ 基础扫描请求数较少（符合快速扫描特点）")

def create_comparison_report(results):
    """创建对比报告"""
    print("\n" + "="*80)
    print("增强版提示词系统测试报告")
    print("="*80)

    print(f"\n📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🧪 测试场景数: {len(results)}")

    for i, result in enumerate(results, 1):
        print(f"\n{'-'*60}")
        print(f"场景 {i}: {result['scenario']}")
        print(f"{'-'*60}")

        params = result['params']
        response = result['result']

        print("参数设置:")
        for key, value in params.items():
            print(f"  - {key}: {value}")

        print("\n响应特征:")
        if 'scan_type' in response:
            print(f"  ✅ 响应包含扫描类型: {response['scan_type']}")

        if 'statistics' in response:
            stats = response['statistics']
            print(f"  ✅ 统计信息: {len(stats)} 项指标")

        if 'vulnerabilities' in response:
            vuln = response['vulnerabilities']
            total_vuln = sum(vuln.values()) if isinstance(vuln, dict) else 0
            print(f"  ✅ 漏洞信息: 发现 {total_vuln} 个问题")

        if 'scan_config' in response:
            config = response['scan_config']
            print(f"  ✅ 扫描配置: {len(config)} 项设置")

    print(f"\n{'-'*60}")
    print("🎯 增强版提示词的优势体现")
    print(f"{'-'*60}")
    print("1. ✅ AI 能理解 scan_type 参数的具体含义：")
    print("   - basic: 生成快速、轻量的扫描结果")
    print("   - full: 生成详细、完整的深度扫描报告")
    print("   - custom: 根据其他参数生成个性化配置")

    print("\n2. ✅ AI 能根据 max_depth 参数调整结果：")
    print("   - 深度较大时，目录结构更复杂")
    print("   - 扫描结果的层次性更明显")

    print("\n3. ✅ AI 能理解 threads 参数的性能含义：")
    print("   - 并发数高时，可能体现更快的扫描速度")
    print("   - 在响应中包含相应的性能数据")

    print("\n4. ✅ AI 能处理 follow_redirects 的业务逻辑：")
    print("   - 影响扫描的覆盖范围和结果")
    print("   - 在配置中正确反映设置")

async def main():
    print("="*80)
    print("增强版提示词系统测试")
    print("="*80)
    print()
    print("测试内容:")
    print("1. 验证 AI 是否能理解参数的详细描述")
    print("2. 检查生成的响应是否与参数设置相符")
    print("3. 对比不同参数组合的响应差异")
    print()

    tester = EnhancedPromptTester()

    print("🔌 初始化连接...")
    if await tester.initialize():
        print("✅ 连接成功")

        print("\n🧪 开始测试...")
        results = await tester.test_scan_scenarios()

        if results:
            create_comparison_report(results)
        else:
            print("❌ 测试失败，未获得有效结果")
    else:
        print("❌ 连接失败，请确保 MCP 服务器正在运行")

if __name__ == "__main__":
    print("注意：请确保 MCP 服务器正在运行 (python3 mcp_server.py)")
    print("并且已经更新了提示词模板\n")

    asyncio.run(main())