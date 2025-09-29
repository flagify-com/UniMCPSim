#!/usr/bin/env python3
"""
SOAR MCP客户端测试工具
基于FastMCP Client实现，用于验证SOAR MCP服务器功能
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Optional

try:
    from fastmcp import Client
    from fastmcp.client.transports import StreamableHttpTransport
except ImportError:
    print("❌ 需要安装fastmcp包: pip install fastmcp")
    sys.exit(1)


class SOARMCPClient:
    """SOAR MCP客户端测试工具"""
    
    def __init__(self, url: str = "http://127.0.0.1:12345/mcp"):
        self.url = url
        self.client = None
        
    async def connect(self) -> bool:
        """连接到MCP服务器"""
        try:
            print(f"🔗 连接到 SOAR MCP 服务器: {self.url}")
            
            # 创建StreamableHttp传输
            transport = StreamableHttpTransport(self.url)
            self.client = Client(transport=transport)
            
            # 测试连接
            await self.client.__aenter__()
            print("✅ 连接成功!")
            return True
            
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    async def disconnect(self):
        """断开连接"""
        if self.client:
            try:
                await self.client.__aexit__(None, None, None)
                print("🔌 连接已断开")
            except Exception as e:
                print(f"⚠️  断开连接时出错: {e}")
    
    async def list_tools(self) -> bool:
        """列出所有可用工具"""
        try:
            print("\n📋 获取工具列表...")
            
            # 获取工具列表
            tools_response = await self.client.list_tools()
            
            # 处理不同的响应格式
            if hasattr(tools_response, 'tools'):
                tools = tools_response.tools
            elif isinstance(tools_response, list):
                tools = tools_response
            else:
                tools = tools_response
            
            print(f"✅ 发现 {len(tools)} 个工具:")
            print("-" * 60)
            
            for i, tool in enumerate(tools, 1):
                print(f"{i:2d}. {tool.name}")
                print(f"    📝 描述: {tool.description}")
                if hasattr(tool, 'inputSchema') and tool.inputSchema:
                    schema = tool.inputSchema
                    if 'properties' in schema:
                        params = list(schema['properties'].keys())
                        print(f"    🔧 参数: {', '.join(params)}")
                print()
            
            return True
            
        except Exception as e:
            print(f"❌ 获取工具列表失败: {e}")
            return False
    
    async def list_resources(self) -> bool:
        """列出所有可用资源"""
        try:
            print("\n📚 获取资源列表...")
            
            # 获取资源列表
            resources_response = await self.client.list_resources()
            
            # 处理不同的响应格式
            if hasattr(resources_response, 'resources'):
                resources = resources_response.resources
            elif isinstance(resources_response, list):
                resources = resources_response
            else:
                resources = resources_response
            
            print(f"✅ 发现 {len(resources)} 个资源:")
            print("-" * 60)
            
            for i, resource in enumerate(resources, 1):
                print(f"{i:2d}. {resource.uri}")
                print(f"    📝 描述: {resource.description or '无描述'}")
                print(f"    🏷️  类型: {resource.mimeType or '未知'}")
                print()
            
            return True
            
        except Exception as e:
            print(f"❌ 获取资源列表失败: {e}")
            return False
    
    async def test_tool(self, tool_name: str, **kwargs) -> bool:
        """测试指定工具"""
        try:
            print(f"\n🧪 测试工具: {tool_name}")
            print(f"📥 参数: {json.dumps(kwargs, ensure_ascii=False, indent=2)}")
            
            # 调用工具
            result = await self.client.call_tool(tool_name, arguments=kwargs)
            
            print("✅ 工具执行成功!")
            print("📤 返回结果:")
            
            # 处理不同的响应格式
            if hasattr(result, 'content'):
                # FastMCP标准响应格式
                for content in result.content:
                    if hasattr(content, 'text'):
                        # 尝试格式化JSON输出
                        try:
                            json_data = json.loads(content.text)
                            print(json.dumps(json_data, ensure_ascii=False, indent=2))
                        except:
                            print(content.text)
                    else:
                        print(content)
            elif isinstance(result, list):
                # 如果result本身是内容列表 (TextContent等)
                for content in result:
                    if hasattr(content, 'text'):
                        # 尝试格式化JSON输出
                        try:
                            json_data = json.loads(content.text)
                            print(json.dumps(json_data, ensure_ascii=False, indent=2))
                        except:
                            print(content.text)
                    else:
                        print(content)
            else:
                # 如果result本身就是字符串或其他格式
                try:
                    if isinstance(result, str):
                        json_data = json.loads(result)
                        print(json.dumps(json_data, ensure_ascii=False, indent=2))
                    else:
                        print(result)
                except:
                    print(result)
            
            return True
            
        except Exception as e:
            print(f"❌ 工具测试失败: {e}")
            return False
    
    async def run_basic_tests(self) -> dict:
        """运行基础测试套件"""
        print("🚀 开始 SOAR MCP 基础测试")
        print("=" * 60)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "server_url": self.url,
            "tests": {}
        }
        
        # 测试1: 连接
        print("📡 测试1: 服务器连接")
        results["tests"]["connection"] = await self.connect()
        
        if not results["tests"]["connection"]:
            print("❌ 连接失败，停止测试")
            return results
        
        # 测试2: 列出工具
        print("\n🔧 测试2: 工具列表")
        results["tests"]["list_tools"] = await self.list_tools()
        
        # 测试3: 列出资源
        print("\n📚 测试3: 资源列表") 
        results["tests"]["list_resources"] = await self.list_resources()
        
        # 测试4: 基础工具调用
        print("\n🧪 测试4: 基础工具调用")
        test_cases = [
            ("list_playbooks_quick", {"limit": 5}),
            ("query_playbook_execution_params", {"playbook_id": "1907203516548373"}),  # 使用已知的剧本ID
        ]
        
        results["tests"]["tool_calls"] = {}
        for tool_name, args in test_cases:
            success = await self.test_tool(tool_name, **args)
            results["tests"]["tool_calls"][tool_name] = success
        
        # 断开连接
        await self.disconnect()
        
        # 汇总结果
        print("\n" + "=" * 60)
        print("📊 测试结果汇总:")
        total_tests = 0
        passed_tests = 0
        
        for test_name, result in results["tests"].items():
            if isinstance(result, dict):
                for sub_test, sub_result in result.items():
                    total_tests += 1
                    if sub_result:
                        passed_tests += 1
                    status = "✅" if sub_result else "❌"
                    print(f"  {status} {test_name}.{sub_test}")
            else:
                total_tests += 1
                if result:
                    passed_tests += 1
                status = "✅" if result else "❌"
                print(f"  {status} {test_name}")
        
        results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": f"{passed_tests/total_tests*100:.1f}%" if total_tests > 0 else "0%"
        }
        
        print(f"\n🎯 成功率: {results['summary']['success_rate']} ({passed_tests}/{total_tests})")
        
        return results


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SOAR MCP客户端测试工具")
    parser.add_argument("--url", default="http://127.0.0.1:12345/mcp", 
                       help="MCP服务器URL (默认: http://127.0.0.1:12345/mcp)")
    parser.add_argument("--tool", help="测试指定工具")
    parser.add_argument("--args", help="工具参数 (JSON格式)")
    parser.add_argument("--save-results", help="保存测试结果到文件")
    
    args = parser.parse_args()
    
    client = SOARMCPClient(args.url)
    
    if args.tool:
        # 测试单个工具
        if not await client.connect():
            return
        
        tool_args = {}
        if args.args:
            try:
                tool_args = json.loads(args.args)
            except json.JSONDecodeError as e:
                print(f"❌ 参数格式错误: {e}")
                return
        
        await client.test_tool(args.tool, **tool_args)
        await client.disconnect()
    else:
        # 运行完整测试套件
        results = await client.run_basic_tests()
        
        if args.save_results:
            with open(args.save_results, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"📁 测试结果已保存到: {args.save_results}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"❌ 测试执行出错: {e}")