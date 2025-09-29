#!/usr/bin/env python3
"""
测试剧本参数显示功能
"""
import requests
import json
import sys

BASE_URL = "http://127.0.0.1:12346"

def test_playbook_params():
    """测试剧本参数显示功能"""
    
    # 测试目标剧本ID 
    test_playbooks = [
        {
            "id": 820862018959180,
            "name": "P_IP_INFO_ENRICH", 
            "expected_params": [{"cefColumn": "dst", "cefDesc": "destinationAddress", "valueType": "STRING", "required": True}]
        },
        {
            "id": 821202472646721,
            "name": "P_OFFICE_IP_CHANGED",
            "expected_params": [{"cefColumn": "cs1", "cefDesc": "deviceCustomString1", "valueType": "STRING", "required": False}]
        },
        {
            "id": 866089838510321,
            "name": "P_UCLOUD_IPSEC",
            "expected_params": []
        }
    ]
    
    print("🧪 开始测试剧本参数显示功能")
    print("=" * 60)
    
    all_passed = True
    
    for playbook in test_playbooks:
        playbook_id = playbook["id"]
        playbook_name = playbook["name"]
        expected_params = playbook["expected_params"]
        
        print(f"\n📋 测试剧本: {playbook_name} (ID: {playbook_id})")
        
        try:
            # 调用API获取剧本详情
            response = requests.get(f"{BASE_URL}/api/admin/playbooks/{playbook_id}")
            
            if response.status_code != 200:
                print(f"❌ API调用失败: HTTP {response.status_code}")
                all_passed = False
                continue
                
            data = response.json()
            
            if not data.get("success"):
                print(f"❌ API返回失败: {data.get('error', '未知错误')}")
                all_passed = False
                continue
                
            playbook_data = data["data"]
            playbook_params_str = playbook_data.get("playbookParams")
            
            # 解析参数
            if playbook_params_str:
                try:
                    actual_params = json.loads(playbook_params_str)
                except json.JSONDecodeError:
                    print(f"❌ 参数JSON解析失败: {playbook_params_str}")
                    all_passed = False
                    continue
            else:
                actual_params = []
            
            print(f"   📊 期望参数: {json.dumps(expected_params, ensure_ascii=False)}")
            print(f"   📊 实际参数: {json.dumps(actual_params, ensure_ascii=False)}")
            
            # 验证参数
            if len(actual_params) != len(expected_params):
                print(f"❌ 参数数量不匹配: 期望 {len(expected_params)}, 实际 {len(actual_params)}")
                all_passed = False
                continue
            
            params_match = True
            for i, (expected, actual) in enumerate(zip(expected_params, actual_params)):
                if expected != actual:
                    print(f"❌ 参数 {i+1} 不匹配:")
                    print(f"     期望: {expected}")
                    print(f"     实际: {actual}")
                    params_match = False
            
            if params_match:
                print("✅ 参数验证通过")
                
                # 测试参数显示格式
                if actual_params:
                    param = actual_params[0]  # 测试第一个参数
                    cef_column = param.get("cefColumn", "未知参数")
                    value_type = param.get("valueType", "string")
                    cef_desc = param.get("cefDesc", "")
                    required = param.get("required", False)
                    
                    print(f"   📝 参数显示格式:")
                    print(f"      参数名: {cef_column}")
                    print(f"      类型: {value_type}")
                    print(f"      描述: {cef_desc}")
                    print(f"      必填: {'是' if required else '否'}")
                    
                    # 验证不再显示 "undefined string 必填"
                    if cef_column != "undefined" and value_type != "undefined":
                        print("✅ 修复验证: 不再显示 'undefined string 必填'")
                    else:
                        print("❌ 修复验证失败: 仍然显示 'undefined'")
                        all_passed = False
                else:
                    print("   📝 无参数剧本")
            else:
                all_passed = False
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！剧本参数显示功能修复成功！")
        return True
    else:
        print("❌ 部分测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    success = test_playbook_params()
    sys.exit(0 if success else 1)