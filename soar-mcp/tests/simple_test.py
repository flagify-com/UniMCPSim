#!/usr/bin/env python3
"""
简单测试execute_playbook真实API集成
"""

import requests
import json


def test_execute_playbook():
    """测试execute_playbook工具"""
    print("🧪 测试execute_playbook真实API集成")
    print("=" * 60)
    
    # 构造MCP请求
    mcp_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "execute_playbook",
            "arguments": {
                "playbook_id": 1907203516548373,
                "parameters": {"src": "15.197.148.33"},
                "event_id": 0
            }
        }
    }
    
    try:
        # 发送请求
        response = requests.post(
            "http://127.0.0.1:12345/mcp",
            json=mcp_request,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            },
            timeout=30
        )
        
        print(f"📤 HTTP状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result and "content" in result["result"]:
                content = result["result"]["content"][0]["text"]
                data = json.loads(content)
                print("✅ 执行结果:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # 分析结果
                if data.get("success"):
                    if "apiResponse" in data:
                        print("\n🎯 检测到真实API调用!")
                        print(f"📋 状态: {data.get('status', 'UNKNOWN')}")
                        if data.get("status") == "SUBMITTED":
                            print("✅ 使用真实API！")
                        else:
                            print("⚠️ 可能还是mock数据")
                    else:
                        print("⚠️ 未检测到apiResponse字段")
                else:
                    print(f"❌ 执行失败: {data.get('error')}")
            else:
                print("❌ 响应格式错误")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    test_execute_playbook()