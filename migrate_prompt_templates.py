#!/usr/bin/env python3
"""
迁移脚本：更新提示词模板以包含动作定义
用于现有数据库升级到 v2.4.0
"""

from models import db_manager, PromptTemplate
from datetime import datetime, timezone


def migrate_prompt_templates():
    """更新 response_simulation 模板以包含 action_definition 变量"""

    print("开始迁移提示词模板...")

    # 新的模板内容
    new_template = """你是{app_name}系统的模拟器。用户调用了{action}操作，参数如下：
{parameters}

动作完整定义：
{action_definition}

请生成一个真实的API响应结果（JSON格式）。响应应该：
1. 符合真实系统的响应格式
2. 包含合理的数据
3. 反映操作的成功或失败状态
4. 考虑动作定义中的描述和参数要求

直接返回JSON，不要任何其他说明文字。"""

    new_variables = [
        {"name": "app_name", "description": "应用名称"},
        {"name": "action", "description": "动作名称"},
        {"name": "parameters", "description": "调用参数JSON字符串"},
        {"name": "action_definition", "description": "动作完整定义JSON字符串"}
    ]

    try:
        # 获取数据库会话
        session = db_manager.get_session()

        # 查找 response_simulation 模板
        prompt = session.query(PromptTemplate).filter_by(
            name="response_simulation"
        ).first()

        if not prompt:
            print("❌ 未找到 response_simulation 模板")
            session.close()
            return False

        # 检查是否已经更新过
        if "{action_definition}" in prompt.template:
            print("✅ 模板已经包含 action_definition 变量，无需更新")
            session.close()
            return True

        # 备份旧模板
        old_template = prompt.template
        old_variables = prompt.variables
        print(f"\n📋 旧模板内容：\n{old_template}\n")
        print(f"📋 旧变量列表：{old_variables}\n")

        # 更新模板
        prompt.template = new_template
        prompt.variables = new_variables
        prompt.updated_at = datetime.now(timezone.utc)

        # 提交更改
        session.commit()

        print("✅ 成功更新 response_simulation 模板")
        print(f"\n📋 新模板内容：\n{new_template}\n")
        print(f"📋 新变量列表：{new_variables}\n")

        session.close()
        return True

    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return False


def verify_migration():
    """验证迁移结果"""
    print("\n验证迁移结果...")

    try:
        session = db_manager.get_session()

        prompt = session.query(PromptTemplate).filter_by(
            name="response_simulation"
        ).first()

        if not prompt:
            print("❌ 未找到模板")
            session.close()
            return False

        # 检查必要的变量
        has_action_def = "{action_definition}" in prompt.template
        variable_names = [v.get("name") for v in prompt.variables]
        has_action_def_var = "action_definition" in variable_names

        print(f"模板包含 {{action_definition}}: {has_action_def}")
        print(f"变量列表包含 action_definition: {has_action_def_var}")
        print(f"变量列表: {variable_names}")
        print(f"最后更新时间: {prompt.updated_at}")

        session.close()

        if has_action_def and has_action_def_var:
            print("\n✅ 迁移验证成功！")
            return True
        else:
            print("\n❌ 迁移验证失败")
            return False

    except Exception as e:
        print(f"❌ 验证失败: {e}")
        if 'session' in locals():
            session.close()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("UniMCPSim 提示词模板迁移工具 v2.4.0")
    print("=" * 60)
    print()

    # 执行迁移
    success = migrate_prompt_templates()

    if success:
        # 验证迁移
        verify_migration()
        print("\n" + "=" * 60)
        print("迁移完成！请重启服务器以使更改生效。")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("迁移失败，请检查错误信息。")
        print("=" * 60)