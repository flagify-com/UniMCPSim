#!/usr/bin/env python3
"""
更新提示词模板，包含动作定义信息
"""

from models import db_manager

def update_response_simulation_template():
    """更新响应模拟提示词模板"""

    print("更新 response_simulation 提示词模板...")

    # 新的模板内容，包含动作定义
    new_template = """你是{app_name}系统的模拟器。用户调用了{action}操作。

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

    # 更新模板
    result = db_manager.save_prompt_template(
        name="response_simulation",
        display_name="增强版响应模拟提示词",
        description="包含完整动作定义的响应模拟提示词，能更准确地理解参数含义和业务需求",
        template=new_template,
        variables=[
            {"name": "app_name", "description": "应用名称"},
            {"name": "action", "description": "动作名称"},
            {"name": "action_definition", "description": "动作的完整JSON定义，包含参数描述、类型、约束等"},
            {"name": "parameters", "description": "用户提供的调用参数JSON字符串"}
        ]
    )

    print("✅ 模板更新成功")

    return result

def test_template_with_bbscan():
    """使用 BBScan 测试新模板"""

    print("\n" + "="*60)
    print("测试新模板效果")
    print("="*60)

    # 模拟 BBScan 的动作定义
    action_def = {
        "name": "scan_url",
        "display_name": "扫描URL",
        "description": "对目标URL进行目录和文件扫描，发现潜在的安全问题",
        "parameters": [
            {
                "key": "target_url",
                "type": "String",
                "required": True,
                "description": "要扫描的目标URL，必须是有效的HTTP/HTTPS地址"
            },
            {
                "key": "scan_type",
                "type": "String",
                "required": False,
                "default": "basic",
                "options": ["basic", "full", "custom"],
                "description": "扫描类型：basic(基础扫描，快速检查常见路径)、full(完整扫描，深度检查)、custom(自定义扫描)"
            },
            {
                "key": "max_depth",
                "type": "Integer",
                "required": False,
                "default": 2,
                "description": "扫描深度，控制目录遍历的层数，范围1-10"
            },
            {
                "key": "follow_redirects",
                "type": "Boolean",
                "required": False,
                "default": False,
                "description": "是否跟随HTTP重定向，可能会增加扫描时间"
            },
            {
                "key": "threads",
                "type": "Integer",
                "required": False,
                "default": 10,
                "description": "并发线程数，影响扫描速度，范围1-50"
            }
        ]
    }

    # 模拟用户参数
    user_params = {
        "target_url": "https://example.com",
        "scan_type": "full",
        "max_depth": 3,
        "follow_redirects": True,
        "threads": 20
    }

    print("动作定义（AI将获得的完整信息）：")
    print("-" * 40)
    import json
    print(json.dumps(action_def, ensure_ascii=False, indent=2))

    print("\n用户参数：")
    print("-" * 40)
    print(json.dumps(user_params, ensure_ascii=False, indent=2))

    # 获取更新后的模板
    template = db_manager.get_prompt_template('response_simulation')
    if template:
        # 生成最终提示词
        variables = {
            'app_name': 'BBScan网站扫描器',
            'action': 'scan_url',
            'action_definition': json.dumps(action_def, ensure_ascii=False, indent=2),
            'parameters': json.dumps(user_params, ensure_ascii=False, indent=2)
        }

        final_prompt = template.template.format(**variables)

        print("\n生成的完整提示词：")
        print("=" * 60)
        print(final_prompt)
        print("=" * 60)

        print("\n✅ 新提示词的优势：")
        print("1. AI能看到参数的详细描述和业务含义")
        print("2. 了解参数的类型、默认值和约束条件")
        print("3. 能根据 scan_type='full' 理解需要生成完整的扫描结果")
        print("4. 知道 max_depth=3 表示深度遍历，会影响结果的目录结构")
        print("5. 理解 threads=20 是并发设置，可能影响扫描性能数据")
        print("6. 未来可在动作定义中添加输出结构要求，AI会严格遵循")
    else:
        print("❌ 未找到模板")

if __name__ == "__main__":
    # 更新模板
    update_response_simulation_template()

    # 测试新模板
    test_template_with_bbscan()

    print("\n" + "="*60)
    print("升级完成说明")
    print("="*60)
    print("""
主要改进：
1. AI现在能接收动作的完整定义，包括：
   - 参数的业务描述和含义
   - 参数类型、默认值、选项
   - 业务逻辑和约束条件

2. 生成的响应更加准确：
   - 理解参数的实际作用
   - 根据参数值生成相应的业务结果
   - 考虑参数间的逻辑关系

3. 为未来扩展做准备：
   - 可在动作定义中添加输出结构规范
   - 支持更复杂的业务规则定义
   - 便于AI理解特定领域的术语和概念

重启 MCP 服务器后即可生效。
""")