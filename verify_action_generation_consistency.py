#!/usr/bin/env python3
"""
验证action_generation模板的一致性
"""

from models import db_manager, PromptTemplate

def verify_template():
    """验证模板内容"""
    session = db_manager.get_session()

    try:
        # 获取数据库中的模板
        template = session.query(PromptTemplate).filter_by(name='action_generation').first()

        if not template:
            print("❌ 未找到action_generation模板")
            return False

        print("=" * 70)
        print("验证action_generation模板一致性")
        print("=" * 70)
        print()

        # 检查模板内容关键部分
        checks = {
            "动作设计原则第7条": "7. default: 可选参数可以设置默认值",
            "JSON格式中default字段说明": '"default": "可选字段，仅在required=false时使用',
            "参考示例中duration_minutes的default": '"default": 60',
        }

        all_passed = True
        for check_name, check_content in checks.items():
            if check_content in template.template:
                print(f"✅ {check_name}: 存在")
            else:
                print(f"❌ {check_name}: 不存在")
                all_passed = False

        print()
        if all_passed:
            print("✅ 所有检查通过,模板已正确更新!")
        else:
            print("❌ 部分检查失败,请检查模板内容")

        return all_passed

    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    verify_template()
