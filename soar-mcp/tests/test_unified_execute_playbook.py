#!/usr/bin/env python3
"""
测试新的统一剧本执行工具 execute_playbook
验证合并后的功能和API格式
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


class UnifiedExecutePlaybookTestClient:
    """统一剧本执行工具测试客户端"""
    
    def __init__(self, url: str = "http://127.0.0.1:12345/mcp"):
        self.url = url
        self.client = None
        
    async def connect(self) -> bool:
        """连接到MCP服务器"""
        try:
            print(f"🔗 连接到 SOAR MCP 服务器: {self.url}")
            
            transport = StreamableHttpTransport(self.url)
            self.client = Client(transport=transport)
            
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
    
    async def call_tool(self, tool_name: str, **kwargs) -> Optional[dict]:
        """调用工具并返回JSON格式结果"""
        try:
            print(f"\n🧪 测试工具: {tool_name}")
            if kwargs:
                print(f"📥 参数: {json.dumps(kwargs, ensure_ascii=False, indent=2)}")
            
            result = await self.client.call_tool(tool_name, arguments=kwargs)
            
            print("✅ 工具执行成功!")
            
            for content in result.content:
                if hasattr(content, 'text'):
                    try:
                        return json.loads(content.text)
                    except:
                        print(f"⚠️  非JSON格式返回: {content.text}")
                        return {"raw_text": content.text}
                        
            return None
            
        except Exception as e:
            print(f"❌ 工具测试失败: {e}")
            return None
    
    async def test_get_playbook_detail(self, playbook_id: int) -> bool:
        """测试获取剧本详情（用于获取参数格式）"""
        print("\n" + "="*60)
        print(f"📋 测试 get_playbook_detail - 获取剧本参数格式 (ID: {playbook_id})")
        
        try:
            result = await self.call_tool("get_playbook_detail", playbook_id=playbook_id)
            if result and not result.get("error"):
                print(f"✅ 剧本详情:")
                print(f"   - ID: {result.get('id')}")
                print(f"   - 名称: {result.get('displayName')}")
                print(f"   - 分类: {result.get('playbookCategory')}")
                
                params = result.get('playbookParams', [])
                print(f"   - 参数数量: {len(params)}")
                if params:
                    print(f"   - 参数格式:")
                    for param in params:
                        print(f"     • {param.get('cefColumn')}: {param.get('cefDesc')} ({param.get('valueType')})")
                
                return True
            else:
                print(f"❌ 获取失败: {result.get('error', '未知错误')}")
                return False
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            return False
    
    async def test_unified_execute_playbook(self, playbook_id: int, test_scenario: str = "default") -> bool:
        """测试统一的剧本执行工具"""
        print("\n" + "="*60)
        print(f"🚀 测试 execute_playbook - 统一剧本执行接口 (场景: {test_scenario})")
        
        try:
            # 根据测试场景设置不同的参数
            if test_scenario == "no_params":
                # 测试不带参数的执行
                result = await self.call_tool("execute_playbook", 
                                            playbook_id=playbook_id)
            elif test_scenario == "with_params":
                # 测试带参数的执行
                result = await self.call_tool("execute_playbook", 
                                            playbook_id=playbook_id,
                                            parameters={
                                                "dst": "192.168.1.100",
                                                "src": "10.0.0.1"
                                            })
            elif test_scenario == "with_event_id":
                # 测试指定事件ID的执行
                result = await self.call_tool("execute_playbook", 
                                            playbook_id=playbook_id,
                                            parameters={"dst": "8.8.8.8"},
                                            event_id=12345)
            else:  # default
                # 默认测试场景
                result = await self.call_tool("execute_playbook", 
                                            playbook_id=playbook_id,
                                            parameters={"dst": "192.168.1.1"})
            
            if result and result.get("success"):
                print(f"🎉 剧本执行成功!")
                print(f"   📄 活动ID: {result.get('activityId')}")
                print(f"   🎯 剧本: {result.get('playbookDisplayName')}")
                print(f"   📊 状态: {result.get('status')}")
                print(f"   🕐 开始时间: {result.get('startTime')}")
                
                # 显示API请求格式
                api_request = result.get('apiRequest', {})
                if api_request:
                    print(f"   📡 API请求格式:")
                    print(f"      - eventId: {api_request.get('eventId')}")
                    print(f"      - executorInstanceId: {api_request.get('executorInstanceId')}")
                    print(f"      - executorInstanceType: {api_request.get('executorInstanceType')}")
                    params = api_request.get('params', [])
                    print(f"      - params: {len(params)} 个参数")
                    for param in params:
                        print(f"        • {param.get('key')}: {param.get('value')}")
                
                # 显示执行详情
                details = result.get('executionDetails', {})
                if details:
                    print(f"   ✅ 执行详情:")
                    print(f"      - 总步骤: {details.get('totalSteps')}")
                    print(f"      - 已执行: {details.get('executedSteps')}")
                    outputs = details.get('outputs', {})
                    if outputs:
                        print(f"      - 处理事件: {outputs.get('processedEvents')}")
                        print(f"      - 执行动作: {outputs.get('actionsExecuted')}")
                        print(f"      - 发送通知: {outputs.get('notifications')}")
                
                return True
            else:
                error_msg = result.get('error', '未知错误') if result else "无返回结果"
                print(f"❌ 执行失败: {error_msg}")
                return False
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            return False
    
    async def run_unified_execution_tests(self) -> dict:
        """运行统一剧本执行工具的完整测试套件"""
        print("🚀 开始统一剧本执行工具测试套件")
        print("=" * 80)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "server_url": self.url,
            "tests": {},
            "test_scenarios": []
        }
        
        # 连接测试
        if not await self.connect():
            results["tests"]["connection"] = False
            return results
        results["tests"]["connection"] = True
        
        try:
            # 先获取一个测试剧本ID
            print("📋 获取测试剧本...")
            playbook_result = await self.call_tool("list_playbooks_quick", limit=1)
            if not playbook_result or not playbook_result.get('playbooks'):
                print("❌ 未获取到剧本数据，无法进行测试")
                results["tests"]["get_test_playbook"] = False
                return results
            
            playbook_id = playbook_result['playbooks'][0]['id']
            playbook_name = playbook_result['playbooks'][0]['displayName']
            results["test_playbook_id"] = playbook_id
            results["test_playbook_name"] = playbook_name
            results["tests"]["get_test_playbook"] = True
            
            print(f"✅ 选择测试剧本: {playbook_name} (ID: {playbook_id})")
            
            # 测试1: 获取剧本详情（参数格式）
            results["tests"]["get_playbook_detail"] = await self.test_get_playbook_detail(playbook_id)
            
            # 测试2-5: 不同场景的统一执行测试
            test_scenarios = [
                ("default", "默认参数测试"),
                ("no_params", "无参数测试"),  
                ("with_params", "多参数测试"),
                ("with_event_id", "指定事件ID测试")
            ]
            
            for scenario, description in test_scenarios:
                test_key = f"execute_playbook_{scenario}"
                print(f"\n🎬 测试场景: {description}")
                result = await self.test_unified_execute_playbook(playbook_id, scenario)
                results["tests"][test_key] = result
                results["test_scenarios"].append({
                    "scenario": scenario,
                    "description": description,
                    "success": result
                })
            
        finally:
            await self.disconnect()
        
        # 汇总结果
        print("\n" + "=" * 80)
        print("📊 统一剧本执行工具测试结果汇总:")
        print("-" * 40)
        
        total_tests = 0
        passed_tests = 0
        
        for test_name, result in results["tests"].items():
            total_tests += 1
            if result:
                passed_tests += 1
            status = "✅" if result else "❌"
            description = test_name.replace("_", " ").title()
            print(f"  {status} {description}")
        
        results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": f"{passed_tests/total_tests*100:.1f}%" if total_tests > 0 else "0%"
        }
        
        print(f"\n🎯 成功率: {results['summary']['success_rate']} ({passed_tests}/{total_tests})")
        
        if results.get("test_playbook_id"):
            print(f"\n📋 测试数据:")
            print(f"  - 测试剧本: {results.get('test_playbook_name')} (ID: {results['test_playbook_id']})")
            print(f"  - 测试场景: {len(results['test_scenarios'])} 个")
        
        return results


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="统一剧本执行工具MCP客户端测试")
    parser.add_argument("--url", default="http://127.0.0.1:12345/mcp", 
                       help="MCP服务器URL (默认: http://127.0.0.1:12345/mcp)")
    parser.add_argument("--playbook-id", type=int, help="指定剧本ID进行测试")
    parser.add_argument("--scenario", choices=["default", "no_params", "with_params", "with_event_id"], 
                       default="default", help="测试场景")
    parser.add_argument("--save-results", help="保存测试结果到文件")
    
    args = parser.parse_args()
    
    client = UnifiedExecutePlaybookTestClient(args.url)
    
    if args.playbook_id:
        # 测试指定剧本
        if not await client.connect():
            return
        
        try:
            # 先获取剧本详情
            await client.test_get_playbook_detail(args.playbook_id)
            # 然后测试执行
            await client.test_unified_execute_playbook(args.playbook_id, args.scenario)
        finally:
            await client.disconnect()
    else:
        # 运行完整测试套件
        results = await client.run_unified_execution_tests()
        
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
        import traceback
        traceback.print_exc()