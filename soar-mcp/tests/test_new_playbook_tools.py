#!/usr/bin/env python3
"""
测试新增的6个剧本管理和执行MCP工具
基于FastMCP Client实现，专门验证剧本相关功能
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


class PlaybookToolsTestClient:
    """剧本工具测试客户端"""
    
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
    
    async def test_list_playbooks_quick(self) -> bool:
        """测试1: 获取简洁剧本列表"""
        print("\n" + "="*60)
        print("1️⃣ 测试 list_playbooks_quick - 获取简洁剧本列表")
        
        try:
            result = await self.call_tool("list_playbooks_quick", limit=5)
            if result:
                print(f"📊 总计: {result.get('total', 0)} 个剧本")
                playbooks = result.get('playbooks', [])
                print(f"📋 前{len(playbooks)}个剧本:")
                for i, pb in enumerate(playbooks[:3], 1):
                    print(f"  {i}. ID: {pb['id']}, 名称: {pb['name']}, 显示名: {pb['displayName']}")
                return True
            else:
                print("❌ 未获取到有效结果")
                return False
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            return False
    
    async def test_list_playbooks_detailed(self) -> Optional[list]:
        """测试2: 获取详细剧本列表"""
        print("\n" + "="*60)
        print("2️⃣ 测试 list_playbooks_detailed - 获取详细剧本列表")
        
        try:
            result = await self.call_tool("list_playbooks_detailed", limit=3)
            if result:
                print(f"📊 总计: {result.get('total', 0)} 个剧本")
                playbooks = result.get('playbooks', [])
                
                for i, pb in enumerate(playbooks[:1], 1):
                    print(f"📋 剧本 {i} 详情:")
                    print(f"   - ID: {pb['id']}")
                    print(f"   - 名称: {pb['name']}")
                    print(f"   - 显示名: {pb['displayName']}")
                    print(f"   - 分类: {pb.get('playbookCategory', 'N/A')}")
                    print(f"   - 参数数量: {len(pb.get('playbookParams', []))}")
                    
                    params = pb.get('playbookParams', [])
                    if params:
                        print(f"   - 参数详情:")
                        for param in params[:2]:
                            print(f"     • {param.get('cefColumn', 'N/A')}: {param.get('cefDesc', 'N/A')} ({param.get('valueType', 'N/A')})")
                
                return playbooks
            else:
                print("❌ 未获取到有效结果")
                return None
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            return None
    
    async def test_query_playbook_execution_params(self, playbook_id: int) -> bool:
        """测试3: 查询剧本执行参数"""
        print("\n" + "="*60)
        print(f"3️⃣ 测试 query_playbook_execution_params - 查询剧本执行参数 (ID: {playbook_id})")
        
        try:
            result = await self.call_tool("query_playbook_execution_params", playbook_id=playbook_id)
            if result:
                print(f"📋 剧本: {result.get('playbookDisplayName', 'N/A')}")
                required_params = result.get('requiredParams', [])
                print(f"📊 必需参数: {len(required_params)} 个")
                
                for i, param in enumerate(required_params[:3], 1):
                    print(f"  {i}. {param.get('paramName', 'N/A')}: {param.get('paramDesc', 'N/A')} ({param.get('paramType', 'N/A')})")
                
                return True
            else:
                print("❌ 未获取到有效结果")
                return False
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            return False
    
    async def test_execute_playbook_advanced(self, playbook_id: int) -> Optional[str]:
        """测试4: 执行剧本"""
        print("\n" + "="*60)
        print(f"4️⃣ 测试 execute_playbook_advanced - 执行剧本 (ID: {playbook_id})")
        
        try:
            mock_event_id = f"event_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            mock_params = {
                "sourceAddress": "192.168.1.100",
                "destinationPort": "443",
                "protocol": "TCP"
            }
            
            result = await self.call_tool("execute_playbook_advanced", 
                                        event_id=mock_event_id,
                                        playbook_id=playbook_id, 
                                        parameters=mock_params)
            if result:
                activity_id = result.get('activityId')
                print(f"🚀 执行启动成功!")
                print(f"📄 活动ID: {activity_id}")
                print(f"📊 状态: {result.get('status')}")
                print(f"💬 消息: {result.get('message')}")
                print(f"🕐 开始时间: {result.get('startTime')}")
                
                return activity_id
            else:
                print("❌ 未获取到有效结果")
                return None
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            return None
    
    async def test_query_playbook_execution_status_by_activity_id(self, activity_id: str, query_count: int = 3) -> bool:
        """测试5: 查询执行状态"""
        print("\n" + "="*60)
        print(f"5️⃣ 测试 query_playbook_execution_status_by_activity_id - 查询执行状态 (活动ID: {activity_id})")

        try:
            success_count = 0
            for i in range(query_count):
                print(f"\n🔍 查询 #{i+1}:")

                result = await self.call_tool("query_playbook_execution_status_by_activity_id", activity_id=activity_id)
                if result:
                    print(f"   - 状态: {result.get('status')}")
                    print(f"   - 消息: {result.get('message')}")
                    print(f"   - 运行时间: {result.get('elapsedSeconds')} 秒")
                    success_count += 1
                else:
                    print("   ❌ 查询失败")
                
                if i < query_count - 1:
                    print("   ⏳ 等待10秒...")
                    await asyncio.sleep(10)
            
            return success_count > 0
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            return False
    
    async def test_query_playbook_execution_result_by_activity_id(self, activity_id: str) -> bool:
        """测试6: 查询执行结果"""
        print("\n" + "="*60)
        print(f"6️⃣ 测试 query_playbook_execution_result_by_activity_id - 查询执行结果 (活动ID: {activity_id})")

        try:
            print("⏳ 等待剧本执行完成...")
            await asyncio.sleep(30)  # 等待执行完成

            result = await self.call_tool("query_playbook_execution_result_by_activity_id", activity_id=activity_id)
            if result:
                print(f"📊 最终状态: {result.get('status')}")
                print(f"🎯 剧本: {result.get('playbookName')}")
                print(f"📄 事件ID: {result.get('eventId')}")
                print(f"🕐 开始时间: {result.get('startTime')}")
                print(f"🏁 结束时间: {result.get('endTime')}")
                
                result_data = result.get('result', {})
                if result_data:
                    print(f"✅ 执行结果:")
                    print(f"   - 成功: {result_data.get('success')}")
                    print(f"   - 已执行步骤: {result_data.get('executedSteps')}/{result_data.get('totalSteps')}")
                    
                    outputs = result_data.get('outputs', {})
                    if outputs:
                        print(f"   - 处理事件: {outputs.get('processedEvents')}")
                        print(f"   - 执行动作: {outputs.get('actionsExecuted')}")
                        print(f"   - 发送通知: {outputs.get('notifications')}")
                
                logs = result.get('logs', [])
                if logs:
                    print(f"📝 执行日志 ({len(logs)} 条):")
                    for log in logs[-3:]:  # 显示最后3条日志
                        print(f"   - [{log.get('level')}] {log.get('message')}")
                
                return True
            else:
                print("❌ 未获取到有效结果")
                return False
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            return False
    
    async def run_complete_test_suite(self) -> dict:
        """运行完整的新工具测试套件"""
        print("🚀 开始新增剧本工具完整测试套件")
        print("=" * 80)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "server_url": self.url,
            "tests": {},
            "execution_data": {}
        }
        
        # 连接测试
        if not await self.connect():
            results["tests"]["connection"] = False
            return results
        results["tests"]["connection"] = True
        
        try:
            # 测试1: 简洁剧本列表
            results["tests"]["list_playbooks_quick"] = await self.test_list_playbooks_quick()
            
            # 测试2: 详细剧本列表，获取剧本ID用于后续测试
            playbooks = await self.test_list_playbooks_detailed()
            results["tests"]["list_playbooks_detailed"] = playbooks is not None
            
            if not playbooks:
                print("\n⚠️  未获取到剧本数据，跳过后续测试")
                return results
            
            playbook_id = playbooks[0]['id']
            results["execution_data"]["selected_playbook_id"] = playbook_id
            
            # 测试3: 查询剧本执行参数
            results["tests"]["query_playbook_execution_params"] = await self.test_query_playbook_execution_params(playbook_id)
            
            # 测试4: 执行剧本
            activity_id = await self.test_execute_playbook_advanced(playbook_id)
            results["tests"]["execute_playbook_advanced"] = activity_id is not None
            
            if not activity_id:
                print("\n⚠️  未获取到活动ID，跳过状态和结果查询测试")
                return results
            
            results["execution_data"]["activity_id"] = activity_id
            
            # 测试5: 查询执行状态
            results["tests"]["query_playbook_execution_status_by_activity_id"] = await self.test_query_playbook_execution_status_by_activity_id(activity_id)

            # 测试6: 查询执行结果
            results["tests"]["query_playbook_execution_result_by_activity_id"] = await self.test_query_playbook_execution_result_by_activity_id(activity_id)
            
        finally:
            await self.disconnect()
        
        # 汇总结果
        print("\n" + "=" * 80)
        print("📊 新增剧本工具测试结果汇总:")
        print("-" * 40)
        
        total_tests = 0
        passed_tests = 0
        
        test_descriptions = {
            "connection": "服务器连接",
            "list_playbooks_quick": "获取简洁剧本列表",
            "list_playbooks_detailed": "获取详细剧本列表",
            "query_playbook_execution_params": "查询剧本执行参数",
            "execute_playbook_advanced": "执行剧本",
            "query_playbook_execution_status_by_activity_id": "查询执行状态",
            "query_playbook_execution_result_by_activity_id": "查询执行结果"
        }
        
        for test_name, result in results["tests"].items():
            total_tests += 1
            if result:
                passed_tests += 1
            status = "✅" if result else "❌"
            description = test_descriptions.get(test_name, test_name)
            print(f"  {status} {description}")
        
        results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": f"{passed_tests/total_tests*100:.1f}%" if total_tests > 0 else "0%"
        }
        
        print(f"\n🎯 成功率: {results['summary']['success_rate']} ({passed_tests}/{total_tests})")
        
        if results["execution_data"]:
            print(f"\n📋 执行数据:")
            if "selected_playbook_id" in results["execution_data"]:
                print(f"  - 测试剧本ID: {results['execution_data']['selected_playbook_id']}")
            if "activity_id" in results["execution_data"]:
                print(f"  - 活动ID: {results['execution_data']['activity_id']}")
        
        return results


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="新增剧本工具MCP客户端测试")
    parser.add_argument("--url", default="http://127.0.0.1:12345/mcp", 
                       help="MCP服务器URL (默认: http://127.0.0.1:12345/mcp)")
    parser.add_argument("--tool", help="测试指定工具")
    parser.add_argument("--playbook-id", type=int, help="指定剧本ID (用于单工具测试)")
    parser.add_argument("--activity-id", help="指定活动ID (用于状态/结果查询测试)")
    parser.add_argument("--save-results", help="保存测试结果到文件")
    
    args = parser.parse_args()
    
    client = PlaybookToolsTestClient(args.url)
    
    if args.tool:
        # 测试单个工具
        if not await client.connect():
            return
        
        try:
            if args.tool == "list_playbooks_quick":
                await client.test_list_playbooks_quick()
            elif args.tool == "list_playbooks_detailed":
                await client.test_list_playbooks_detailed()
            elif args.tool == "query_playbook_execution_params":
                if args.playbook_id:
                    await client.test_query_playbook_execution_params(args.playbook_id)
                else:
                    print("❌ 需要指定 --playbook-id 参数")
            elif args.tool == "execute_playbook_advanced":
                if args.playbook_id:
                    await client.test_execute_playbook_advanced(args.playbook_id)
                else:
                    print("❌ 需要指定 --playbook-id 参数")
            elif args.tool == "query_playbook_execution_status_by_activity_id":
                if args.activity_id:
                    await client.test_query_playbook_execution_status_by_activity_id(args.activity_id, 1)
                else:
                    print("❌ 需要指定 --activity-id 参数")
            elif args.tool == "query_playbook_execution_result_by_activity_id":
                if args.activity_id:
                    await client.test_query_playbook_execution_result_by_activity_id(args.activity_id)
                else:
                    print("❌ 需要指定 --activity-id 参数")
            else:
                print(f"❌ 未知工具: {args.tool}")
        finally:
            await client.disconnect()
    else:
        # 运行完整测试套件
        results = await client.run_complete_test_suite()
        
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