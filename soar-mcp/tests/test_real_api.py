#!/usr/bin/env python3
"""
真实API调用测试客户端
测试execute_playbook的真实API集成
"""

import asyncio
import json
import sys
import os
import requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger_config import logger

class RealAPITestClient:
    def __init__(self, url="http://127.0.0.1:12345/mcp"):
        self.url = url
        
    def call_tool(self, tool_name, **kwargs):
        """调用MCP工具 - 使用HTTP直接调用"""
        try:
            # 构造MCP请求
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": kwargs
                }
            }
            
            response = requests.post(
                self.url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"HTTP错误: {response.status_code}")
            
            result = response.json()
            
            if "error" in result:
                raise Exception(f"MCP错误: {result['error']}")
            
            # 返回工具调用结果
            if "result" in result and "content" in result["result"]:
                content = result["result"]["content"]
                if content and len(content) > 0:
                    return content[0].get("text", "")
            
            return ""
        except Exception as e:
            logger.error(f"调用工具 {tool_name} 失败: {e}")
            raise

    def test_real_playbook_execution(self, playbook_id: int = 1907203516548373) -> bool:
        """测试真实剧本执行"""
        print(f"🚀 测试真实剧本执行 (剧本ID: {playbook_id})")
        print("=" * 80)
        
        try:
            # 1. 获取剧本详情
            print(f"📋 步骤1: 获取剧本详情")
            detail_result = self.call_tool("get_playbook_detail", playbook_id=playbook_id)
            print(f"✅ 剧本详情: {json.dumps(json.loads(detail_result), indent=2, ensure_ascii=False)}")
            
            # 2. 执行剧本 (使用您提供的测试参数)
            print(f"\n🚀 步骤2: 执行剧本")
            execute_result = self.call_tool("execute_playbook", 
                                          playbook_id=playbook_id,
                                          parameters={
                                              "src": "15.197.148.33"
                                          },
                                          event_id=0)
            
            execute_data = json.loads(execute_result)
            print(f"✅ 剧本执行结果: {json.dumps(execute_data, indent=2, ensure_ascii=False)}")
            
            if not execute_data.get("success"):
                print(f"❌ 剧本执行失败: {execute_data.get('error')}")
                return False
            
            activity_id = execute_data.get("activityId")
            if not activity_id:
                print(f"❌ 未获取到活动ID")
                return False
            
            print(f"✅ 获得活动ID: {activity_id}")
            
            # 3. 查询执行状态
            print(f"\n🔍 步骤3: 查询执行状态")
            status_result = self.call_tool("query_playbook_execution_status_by_activity_id", activity_id=activity_id)
            status_data = json.loads(status_result)
            print(f"✅ 执行状态: {json.dumps(status_data, indent=2, ensure_ascii=False)}")
            
            if status_data.get("success") and status_data.get("status") == "SUCCESS":
                # 4. 查询执行结果
                print(f"\n📊 步骤4: 查询执行结果")
                result_result = self.call_tool("query_playbook_execution_result_by_activity_id", activity_id=activity_id)
                result_data = json.loads(result_result)
                print(f"✅ 执行结果: {json.dumps(result_data, indent=2, ensure_ascii=False)}")
            else:
                print(f"⏳ 执行状态: {status_data.get('status', 'UNKNOWN')}")
                print(f"💡 提示: 如果状态不是SUCCESS，请等待一段时间后再查询结果")
            
            return True
            
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            return False

def main():
    """主测试函数"""
    print("🚀 开始真实API调用测试")
    print("=" * 80)
    
    client = RealAPITestClient()
    
    # 测试使用您在CLAUDE.md中提供的测试参数
    success = client.test_real_playbook_execution(1907203516548373)
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 真实API调用测试通过!")
    else:
        print("❌ 真实API调用测试失败!")
    
    return success

if __name__ == "__main__":
    main()