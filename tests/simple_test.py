#!/usr/bin/env python3
"""
简单测试 - 直接测试模拟器功能
"""

import os
import sys
import asyncio

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db_manager
from mcp_server import simulator

def test_simulator_functionality():
    """测试模拟器核心功能"""
    print("="*60)
    print("UniMCPSim 核心功能测试")
    print("="*60)

    # 获取Demo Token
    session = db_manager.get_session()
    try:
        from models import Token
        demo_token = session.query(Token).filter_by(name='Demo Token').first()
        if not demo_token:
            print("❌ 未找到Demo Token")
            return False

        token = demo_token.token
        print(f"✅ 使用Token: {token[:8]}...{token[-4:]}")

    finally:
        session.close()

    # 测试案例
    test_cases = [
        {
            "name": "企业微信发送消息",
            "category": "IM",
            "product": "WeChat",
            "action": "send_text_message",
            "params": {
                "to_user": "test_user",
                "content": "Hello from UniMCPSim!"
            }
        },
        {
            "name": "VirusTotal IP扫描",
            "category": "Security",
            "product": "VirusTotal",
            "action": "scan_ip",
            "params": {
                "ip": "8.8.8.8"
            }
        },
        {
            "name": "Jira创建工单",
            "category": "Ticket",
            "product": "Jira",
            "action": "create_issue",
            "params": {
                "project_key": "TEST",
                "issue_type": "Task",
                "summary": "测试工单",
                "description": "这是一个测试工单",
                "priority": "High"
            }
        },
        {
            "name": "深信服防火墙封禁IP",
            "category": "Firewall",
            "product": "Sangfor",
            "action": "block_ip_address",
            "params": {
                "ip_address": "192.168.1.100",
                "reason": "可疑活动"
            }
        },
        {
            "name": "华为交换机查看接口",
            "category": "Network",
            "product": "HuaweiSwitch",
            "action": "display_interface_brief",
            "params": {}
        }
    ]

    passed = 0
    failed = 0

    for i, test in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test['name']}")
        print("-" * 40)

        try:
            result = simulator.process_request(
                category=test['category'],
                product=test['product'],
                action=test['action'],
                params=test['params'],
                token=token
            )

            if 'error' in result:
                print(f"❌ 失败: {result['error']}")
                failed += 1
            else:
                print(f"✅ 成功")
                print(f"   响应: {result}")
                passed += 1

        except Exception as e:
            print(f"❌ 异常: {e}")
            failed += 1

    # 输出总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    total = passed + failed
    print(f"总测试数: {total}")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")

    if failed == 0:
        print("\n🎉 所有测试通过!")
    else:
        print(f"\n⚠️ 有 {failed} 个测试失败")

    return failed == 0

def test_applications_list():
    """测试应用列表"""
    print("\n" + "="*60)
    print("测试应用列表功能")
    print("="*60)

    session = db_manager.get_session()
    try:
        from models import Application
        apps = session.query(Application).filter_by(enabled=True).all()

        print(f"✅ 找到 {len(apps)} 个已启用的应用:")
        for app in apps:
            print(f"   - {app.display_name} (/{app.category}/{app.name})")
            if app.template and 'actions' in app.template:
                print(f"     动作数量: {len(app.template['actions'])}")

        return len(apps) > 0

    finally:
        session.close()

def main():
    """主函数"""
    print("\n" + "#"*60)
    print("# UniMCPSim 功能验证测试")
    print("#"*60)

    # 测试应用列表
    apps_ok = test_applications_list()

    # 测试模拟器功能
    sim_ok = test_simulator_functionality()

    # 总结
    print("\n" + "#"*60)
    print("# 总测试结果")
    print("#"*60)

    if apps_ok and sim_ok:
        print("🎉 所有功能测试通过！UniMCPSim 工作正常")
        return 0
    else:
        print("❌ 部分测试失败，请检查配置")
        return 1

if __name__ == "__main__":
    sys.exit(main())