#!/usr/bin/env python3
"""
展示实际的 action_definition 内容
从数据库获取真实的动作定义数据
"""

import json
from models import db_manager, Application

def show_real_action_definition():
    """展示真实的动作定义内容"""

    print("=" * 70)
    print("实际的 {action_definition} 内容展示")
    print("=" * 70)
    print()

    # 从数据库获取 BBScan 应用
    session = db_manager.get_session()
    try:
        app = session.query(Application).filter_by(
            category="Scanner",
            name="BBScan"
        ).first()

        if not app:
            print("❌ 未找到 BBScan 应用")
            return

        print("【从数据库获取的应用信息】")
        print(f"应用名称: {app.name}")
        print(f"显示名称: {app.display_name}")
        print(f"分类: {app.category}")
        print(f"描述: {app.description}")
        print()

        # 获取模板中的动作
        template = app.template if app.template else {}
        actions = template.get('actions', [])

        if not actions:
            print("❌ 应用中没有动作定义")
            return

        # 找到 scan_url 动作
        scan_url_action = None
        for action in actions:
            if action.get('name') == 'scan_url':
                scan_url_action = action
                break

        if not scan_url_action:
            print("❌ 未找到 scan_url 动作")
            return

        print("【实际的 action_definition 内容】")
        print("这就是传递给 AI 的 {action_definition} 变量的完整内容:")
        print("-" * 60)

        # 这就是实际传递给 AI 的内容
        action_definition_content = json.dumps(scan_url_action, ensure_ascii=False, indent=2)
        print(action_definition_content)
        print("-" * 60)
        print()

        # 分析内容
        print("【内容分析】")
        print("AI 从这个定义中能获取到的信息:")
        print()

        print(f"✅ 动作名称: {scan_url_action.get('name')}")
        print(f"✅ 显示名称: {scan_url_action.get('display_name')}")
        print(f"✅ 功能描述: {scan_url_action.get('description')}")
        print()

        parameters = scan_url_action.get('parameters', [])
        print(f"✅ 参数数量: {len(parameters)} 个")
        print()

        for i, param in enumerate(parameters, 1):
            print(f"参数 {i}: {param.get('key')}")
            print(f"  - 类型: {param.get('type')}")
            print(f"  - 必填: {param.get('required', False)}")
            if 'default' in param:
                print(f"  - 默认值: {param.get('default')}")
            if 'options' in param:
                print(f"  - 可选值: {param.get('options')}")
            print(f"  - 描述: {param.get('description')}")
            print()

    finally:
        session.close()

def show_complete_prompt_example():
    """展示完整的提示词示例"""

    print("=" * 70)
    print("完整的 AI 提示词示例（包含真实的 action_definition）")
    print("=" * 70)
    print()

    # 模拟用户请求
    user_params = {
        "target_url": "https://test-website.com",
        "scan_type": "full",
        "max_depth": 3,
        "follow_redirects": True,
        "threads": 20
    }

    # 真实的动作定义（从数据库获取的）
    real_action_def = {
        "name": "scan_url",
        "display_name": "扫描URL",
        "description": "对目标URL进行目录和文件扫描，可以快速发现网站的目录结构、敏感文件和潜在漏洞",
        "parameters": [
            {
                "key": "target_url",
                "type": "String",
                "required": True,
                "description": "要扫描的目标URL"
            },
            {
                "key": "scan_type",
                "type": "String",
                "required": False,
                "default": "basic",
                "options": ["basic", "full", "custom"],
                "description": "扫描类型：basic(基础扫描)、full(完整扫描)、custom(自定义扫描)"
            },
            {
                "key": "max_depth",
                "type": "Integer",
                "required": False,
                "default": 2,
                "description": "扫描深度，默认为2层"
            },
            {
                "key": "follow_redirects",
                "type": "Boolean",
                "required": False,
                "default": False,
                "description": "是否跟随重定向"
            },
            {
                "key": "threads",
                "type": "Integer",
                "required": False,
                "default": 10,
                "description": "并发线程数"
            }
        ]
    }

    # 模板变量
    variables = {
        'app_name': 'BBScan网站扫描器',
        'action': 'scan_url',
        'action_definition': json.dumps(real_action_def, ensure_ascii=False, indent=2),
        'parameters': json.dumps(user_params, ensure_ascii=False, indent=2)
    }

    # 提示词模板
    template = """你是{app_name}系统的模拟器。用户调用了{action}操作。

动作完整定义：
{action_definition}

用户提供的参数：
{parameters}

请根据动作定义中的参数描述、类型要求和业务逻辑，生成一个真实的API响应结果（JSON格式）。

响应要求：
1. 符合真实系统的响应格式和业务场景
2. 包含合理且符合逻辑的数据
3. 正确反映操作的成功或失败状态
4. 充分考虑参数的描述、类型、默认值和约束
5. 如果动作定义中有输出结构要求，严格遵循
6. 响应数据要与输入参数相关联，体现真实的业务处理结果

只返回JSON格式的响应，不要任何其他说明文字。"""

    # 生成最终提示词
    final_prompt = template.format(**variables)

    print("【用户输入的参数】")
    print(json.dumps(user_params, ensure_ascii=False, indent=2))
    print()

    print("【发送给 OpenAI 的完整提示词】")
    print("=" * 60)
    print(final_prompt)
    print("=" * 60)
    print()

    print("【AI 能理解的关键信息】")
    print("通过 action_definition，AI 现在知道:")
    print()
    print("🎯 scan_type='full' 的含义:")
    print("   → '完整扫描' (相对于 'basic' 基础扫描)")
    print("   → AI 会生成更详细、更完整的扫描报告")
    print()
    print("📏 max_depth=3 的含义:")
    print("   → '扫描深度，默认为2层'")
    print("   → AI 知道用户设置了比默认值更深的扫描")
    print("   → 会在目录结构中体现 3 层深度")
    print()
    print("🔄 follow_redirects=True 的含义:")
    print("   → '是否跟随重定向'，默认 False")
    print("   → AI 知道用户启用了重定向跟踪")
    print("   → 可能在结果中包含重定向发现的内容")
    print()
    print("⚡ threads=20 的含义:")
    print("   → '并发线程数'，默认 10")
    print("   → AI 知道用户设置了高并发")
    print("   → 可能在性能指标中体现更快的扫描速度")

def show_parameter_impact():
    """展示参数如何影响 AI 的理解"""

    print("=" * 70)
    print("参数值如何影响 AI 的理解和响应")
    print("=" * 70)
    print()

    scenarios = [
        {
            "name": "基础扫描场景",
            "params": {"scan_type": "basic", "max_depth": 1},
            "ai_understanding": [
                "scan_type='basic' → AI 知道这是'基础扫描'",
                "max_depth=1 → AI 知道只扫描1层，比默认值(2)更浅",
                "AI 会生成：简单的目录列表，较少的发现，快速完成"
            ]
        },
        {
            "name": "深度扫描场景",
            "params": {"scan_type": "full", "max_depth": 5, "threads": 30},
            "ai_understanding": [
                "scan_type='full' → AI 知道这是'完整扫描'",
                "max_depth=5 → AI 知道扫描5层，比默认值(2)深很多",
                "threads=30 → AI 知道高并发，比默认值(10)多3倍",
                "AI 会生成：详细的漏洞报告，深层目录结构，高性能指标"
            ]
        },
        {
            "name": "自定义配置场景",
            "params": {"scan_type": "custom", "follow_redirects": False, "threads": 5},
            "ai_understanding": [
                "scan_type='custom' → AI 知道这是'自定义扫描'",
                "follow_redirects=False → AI 知道不跟随重定向(与默认值相同)",
                "threads=5 → AI 知道低并发，比默认值(10)少一半",
                "AI 会生成：个性化配置，无重定向发现，较慢的扫描速度"
            ]
        }
    ]

    for scenario in scenarios:
        print(f"【{scenario['name']}】")
        print("参数设置:", json.dumps(scenario['params'], ensure_ascii=False))
        print("AI 的理解:")
        for understanding in scenario['ai_understanding']:
            print(f"  ✅ {understanding}")
        print()

if __name__ == "__main__":
    show_real_action_definition()
    print("\n" + "="*70 + "\n")
    show_complete_prompt_example()
    print("\n" + "="*70 + "\n")
    show_parameter_impact()