#!/usr/bin/env python3
"""
更新action_generation提示词模板,添加default字段支持
"""

from models import db_manager, PromptTemplate

def update_action_generation_template():
    """更新action_generation模板"""
    session = db_manager.get_session()

    try:
        # 查找现有模板
        template = session.query(PromptTemplate).filter_by(name='action_generation').first()

        if not template:
            print("❌ 未找到action_generation模板")
            return False

        # 新的模板内容
        new_template_content = """你是一个专业的MCP工具定义生成助手。请根据用户提供的应用信息生成JSON格式的动作定义。

目标应用信息：
- 应用分类：{category}
- 应用名称：{name}
- 应用显示名称：{display_name}
- 应用描述：{description}

要创建的动作，参考此处用户的要求设计：
{prompt}

请为"{display_name}"（{category}类应用）生成相应的MCP工具动作。根据应用类型和用户需求，设计能够实现具体功能的动作定义。

动作设计原则：
1. name: 使用snake_case命名，要准确反映动作功能（如：start_meeting, block_ip_address, query_firewall_status）
2. display_name: 使用简洁的中文名称，体现在{display_name}中的功能
3. description: 详细说明动作的功能和用途，要与{display_name}应用场景相符
4. parameters: 根据动作实际需求决定，可以有参数，也可以没有参数
5. key: 参数名要有实际指导意义，便于理解和调用
6. description: 参数说明要具体，包括数据格式、必要性等信息
7. default: 可选参数可以设置默认值，方便用户使用（如：duration_minutes默认60，page_size默认10等）

请生成符合以下格式的JSON数组，包含用户描述的所有动作：

[
  {{
    "name": "具体动作的英文名称，使用snake_case命名，要能准确表达动作功能",
    "display_name": "动作的中文显示名称，简洁明了",
    "description": "动作的详细描述，说明此动作在{display_name}中的具体功能和用途",
    "parameters": [
      {{
        "key": "参数的英文键名，使用snake_case，要能清楚表达参数含义",
        "type": "参数类型：String|Number|Boolean|Object|Array",
        "required": true,
        "description": "参数的详细说明，包括格式要求、取值范围等",
        "default": "可选字段，仅在required=false时使用，提供合理的默认值"
      }}
    ]
  }}
]

参考示例（防火墙管理）：
[
  {{
    "name": "check_firewall_health",
    "display_name": "查询防火墙健康状态",
    "description": "检查防火墙系统的运行状态和健康情况",
    "parameters": []
  }},
  {{
    "name": "block_ip_address",
    "display_name": "封禁IP地址",
    "description": "将指定IP地址加入防火墙黑名单进行封禁",
    "parameters": [
      {{
        "key": "ip_address",
        "type": "String",
        "required": true,
        "description": "要封禁的IP地址，格式如：192.168.1.100"
      }},
      {{
        "key": "duration_minutes",
        "type": "Number",
        "required": false,
        "default": 60,
        "description": "封禁时长（分钟），0表示永久封禁"
      }},
      {{
        "key": "reason",
        "type": "String",
        "required": false,
        "description": "封禁原因说明"
      }}
    ]
  }},
  {{
    "name": "unblock_ip_address",
    "display_name": "解封IP地址",
    "description": "将指定IP地址从防火墙黑名单中移除",
    "parameters": [
      {{
        "key": "ip_address",
        "type": "String",
        "required": true,
        "description": "要解封的IP地址"
      }}
    ]
  }},
  {{
    "name": "query_ip_block_status",
    "display_name": "查询IP封禁状态",
    "description": "查询指定IP地址的封禁状态和相关信息",
    "parameters": [
      {{
        "key": "ip_address",
        "type": "String",
        "required": true,
        "description": "要查询的IP地址"
      }}
    ]
  }}
]

要求：
1. 严格按照以上格式和原则生成
2. 根据用户描述的每个工具生成对应的动作
3. 只返回JSON数组，不要其他文字

请严格按照JSON格式返回，不要包含任何其他说明文字。"""

        print("📝 当前模板内容(前200字符):")
        print(f"   {template.template[:200]}...")
        print()

        # 更新模板
        template.template = new_template_content

        session.commit()

        print("✅ action_generation模板已更新")
        print()
        print("🔍 更新内容:")
        print("   1. 动作设计原则新增第7条: default字段说明")
        print("   2. JSON格式示例中添加default字段说明")
        print("   3. 参考示例中duration_minutes参数添加default:60")
        print()
        print("💡 default字段用途:")
        print("   - 为可选参数(required=false)提供默认值")
        print("   - 简化用户调用,无需每次都指定常用参数")
        print("   - 示例: duration_minutes=60, page_size=10, timeout=30等")

        return True

    except Exception as e:
        session.rollback()
        print(f"❌ 更新失败: {e}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    print("=" * 70)
    print("更新action_generation提示词模板")
    print("=" * 70)
    print()

    if update_action_generation_template():
        print()
        print("=" * 70)
        print("✅ 更新完成!")
        print("=" * 70)
    else:
        print()
        print("=" * 70)
        print("❌ 更新失败")
        print("=" * 70)
