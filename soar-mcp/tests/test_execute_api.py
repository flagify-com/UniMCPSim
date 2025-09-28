#!/usr/bin/env python3
"""
测试真实剧本执行的简单客户端
直接调用execute_playbook测试真实API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.mcp_soar_client import SOARMCPClient
import asyncio
import json

async def test_real_execute():
    """测试真实剧本执行"""
    print("🚀 测试真实剧本执行API调用")
    print("=" * 60)
    
    client = SOARMCPClient()
    
    try:
        # 连接到服务器
        await client.connect()
        print("✅ 连接成功")
        
        # 使用您提供的测试参数执行剧本
        playbook_id = 1907203516548373
        parameters = {"src": "15.197.148.33"}
        
        print(f"🚀 执行剧本 ID: {playbook_id}")
        print(f"📋 参数: {parameters}")
        
        # 直接调用工具获取结果
        result = await client.client.call_tool(
            "execute_playbook", 
            arguments={
                "playbook_id": playbook_id,
                "parameters": parameters,
                "event_id": 0
            }
        )
        
        print("✅ 剧本执行结果:")
        print("-" * 60)
        result_text = result.content[0].text if result.content else ""
        result_data = json.loads(result_text)
        print(json.dumps(result_data, indent=2, ensure_ascii=False))
        
        # 如果成功，获取活动ID进行后续测试
        if result_data.get("success") and result_data.get("activityId"):
            activity_id = result_data.get("activityId")
            print(f"\n🔍 查询执行状态，活动ID: {activity_id}")
            
            status_result = await client.client.call_tool(
                "query_playbook_execution_status_by_activity_id",
                arguments={"activity_id": activity_id}
            )
            
            print("✅ 执行状态:")
            print("-" * 60)
            status_text = status_result.content[0].text if status_result.content else ""
            status_data = json.loads(status_text)
            print(json.dumps(status_data, indent=2, ensure_ascii=False))
            
            # 如果状态为SUCCESS，查询详细结果
            if status_data.get("success") and status_data.get("status") == "SUCCESS":
                print(f"\n📊 查询执行结果，活动ID: {activity_id}")
                
                result_result = await client.client.call_tool(
                    "query_playbook_execution_result_by_activity_id",
                    arguments={"activity_id": activity_id}
                )
                
                print("✅ 执行结果:")
                print("-" * 60)
                result_text = result_result.content[0].text if result_result.content else ""
                result_result_data = json.loads(result_text)
                print(json.dumps(result_result_data, indent=2, ensure_ascii=False))
        
        await client.disconnect()
        print("\n🎉 测试完成!")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        try:
            await client.disconnect()
        except:
            pass
        return False

if __name__ == "__main__":
    asyncio.run(test_real_execute())