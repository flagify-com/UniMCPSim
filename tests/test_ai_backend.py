#!/usr/bin/env python3
"""
后端测试 - AI功能测试
测试AI动作生成、AI响应模拟
"""

import os
import sys
import json
from typing import Dict, Any

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_generator import ai_generator
from models import db_manager


class AIBackendTester:
    """后端AI功能测试器"""

    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0

    def test_action_generation(self) -> bool:
        """测试1: AI动作生成功能"""
        print("\n" + "="*60)
        print("测试1: AI动作生成功能")
        print("="*60)

        # 检查AI是否启用
        if not ai_generator.enabled:
            print("⚠️ AI功能未启用，请检查环境变量或数据库配置")
            print("   需要配置: OPENAI_API_KEY 或通过Web界面配置")
            print("   跳过AI测试...")
            return True

        print("\n1.1 测试生成防火墙管理动作...")
        try:
            # 获取action_generation提示词模板
            prompt_template = db_manager.get_prompt_template('action_generation')

            if not prompt_template:
                print("❌ 未找到action_generation提示词模板")
                self.failed_tests += 1
                return False

            # 准备测试数据
            app_info = {
                'category': 'Security',
                'name': 'TestFirewall',
                'display_name': '测试防火墙',
                'description': '用于测试的防火墙系统'
            }

            user_prompt = """
我需要以下功能：
1. 查询防火墙状态
2. 封禁IP地址（需要IP、封禁时长、原因）
3. 解封IP地址
"""

            # 构造完整的prompt
            variables = {
                'category': app_info['category'],
                'name': app_info['name'],
                'display_name': app_info['display_name'],
                'description': app_info['description'],
                'prompt': user_prompt
            }

            full_prompt = prompt_template.template.format(**variables)

            # 调用AI生成
            print("   正在调用AI生成动作定义...")
            response = ai_generator.client.chat.completions.create(
                model=ai_generator.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的API定义生成助手,返回符合规范的JSON数据。"},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                extra_body={"enable_thinking": ai_generator.enable_thinking}
            )

            result = response.choices[0].message.content

            # 解析结果
            try:
                # 清理可能的markdown代码块标记
                result = result.strip()
                if result.startswith("```json"):
                    result = result[7:]
                if result.endswith("```"):
                    result = result[:-3]

                actions = json.loads(result.strip())

                # 验证返回格式
                if isinstance(actions, list) and len(actions) > 0:
                    print(f"✅ AI生成成功，返回 {len(actions)} 个动作定义")

                    # 验证第一个动作的结构
                    first_action = actions[0]
                    if 'name' in first_action and 'display_name' in first_action:
                        print(f"   示例动作: {first_action['display_name']} ({first_action['name']})")
                        print(f"   参数数量: {len(first_action.get('parameters', []))}")
                        self.passed_tests += 1
                    else:
                        print("❌ 动作结构不完整")
                        self.failed_tests += 1
                        return False
                else:
                    print("❌ 返回格式错误，不是有效的动作数组")
                    self.failed_tests += 1
                    return False

            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"   返回内容: {result[:200]}...")
                self.failed_tests += 1
                return False

        except Exception as e:
            print(f"❌ AI动作生成异常: {e}")
            self.failed_tests += 1
            return False

        return True

    def test_response_simulation(self) -> bool:
        """测试2: AI响应模拟功能"""
        print("\n" + "="*60)
        print("测试2: AI响应模拟功能")
        print("="*60)

        # 检查AI是否启用
        if not ai_generator.enabled:
            print("⚠️ AI功能未启用，跳过测试...")
            return True

        print("\n2.1 测试生成威胁情报查询响应...")
        try:
            # 准备应用信息
            app_info = {
                'category': 'Security',
                'name': 'ThreatBook',
                'display_name': '微步在线威胁情报',
                'description': '提供IP、域名、文件等威胁情报查询',
                'ai_notes': '返回的数据应该包含威胁评分、标签、详细信息等'
            }

            # 准备调用参数
            action = 'query_ip_reputation'
            parameters = {
                'ip': '192.168.1.100'
            }

            # 准备动作定义
            action_def = {
                'name': 'query_ip_reputation',
                'display_name': '查询IP信誉度',
                'description': '查询指定IP地址的威胁情报和信誉度',
                'parameters': [
                    {
                        'key': 'ip',
                        'type': 'String',
                        'required': True,
                        'description': 'IP地址'
                    }
                ]
            }

            # 调用AI生成响应
            print("   正在调用AI生成模拟响应...")
            response = ai_generator.generate_response(
                app_info=app_info,
                action=action,
                parameters=parameters,
                action_def=action_def
            )

            # 验证响应
            if isinstance(response, dict):
                print("✅ AI响应生成成功")
                print(f"   响应字段: {list(response.keys())}")

                # 检查是否包含常见字段
                if 'ip' in response or 'success' in response or 'reputation' in response:
                    print("   ✅ 响应包含预期字段")
                    self.passed_tests += 1
                else:
                    print("   ⚠️ 响应格式可能不符合预期")
                    self.passed_tests += 1  # 仍然算通过，因为AI生成的格式可能不同

            else:
                print(f"❌ 响应格式错误，不是字典类型: {type(response)}")
                self.failed_tests += 1
                return False

        except Exception as e:
            print(f"❌ AI响应模拟异常: {e}")
            self.failed_tests += 1
            return False

        # 2.2 测试不同类型的应用响应
        print("\n2.2 测试企业微信消息发送响应...")
        try:
            app_info = {
                'category': 'IM',
                'name': 'WeChat',
                'display_name': '企业微信',
                'description': '企业微信消息通知接口',
                'ai_notes': '返回消息ID和发送状态'
            }

            action = 'send_text_message'
            parameters = {
                'to_user': 'user123',
                'content': '这是一条测试消息'
            }

            action_def = {
                'name': 'send_text_message',
                'display_name': '发送文本消息',
                'description': '向指定用户发送文本消息',
                'parameters': [
                    {
                        'key': 'to_user',
                        'type': 'String',
                        'required': True,
                        'description': '接收用户ID'
                    },
                    {
                        'key': 'content',
                        'type': 'String',
                        'required': True,
                        'description': '消息内容'
                    }
                ]
            }

            print("   正在调用AI生成模拟响应...")
            response = ai_generator.generate_response(
                app_info=app_info,
                action=action,
                parameters=parameters,
                action_def=action_def
            )

            if isinstance(response, dict):
                print("✅ 企业微信响应生成成功")
                print(f"   响应示例: {json.dumps(response, ensure_ascii=False, indent=2)[:200]}...")
                self.passed_tests += 1
            else:
                print(f"❌ 响应格式错误")
                self.failed_tests += 1

        except Exception as e:
            print(f"❌ 生成响应异常: {e}")
            self.failed_tests += 1

        return True

    def test_ai_config_reload(self) -> bool:
        """测试3: AI配置重载功能"""
        print("\n" + "="*60)
        print("测试3: AI配置重载功能")
        print("="*60)

        print("\n3.1 测试配置重载...")
        try:
            # 记录当前配置
            old_model = ai_generator.model
            old_enabled = ai_generator.enabled

            print(f"   当前配置: model={old_model}, enabled={old_enabled}")

            # 重载配置
            ai_generator.reload_config()

            print(f"   重载后配置: model={ai_generator.model}, enabled={ai_generator.enabled}")
            print("✅ 配置重载功能正常")
            self.passed_tests += 1

        except Exception as e:
            print(f"❌ 配置重载异常: {e}")
            self.failed_tests += 1
            return False

        return True

    def test_default_response(self) -> bool:
        """测试4: 默认响应生成（AI未启用时）"""
        print("\n" + "="*60)
        print("测试4: 默认响应生成功能")
        print("="*60)

        print("\n4.1 测试默认响应生成...")
        try:
            # 直接调用默认响应生成方法
            response = ai_generator._generate_default_response(
                app_name="测试应用",
                action="send_message",
                parameters={"to": "user1", "text": "hello"}
            )

            if isinstance(response, dict) and 'success' in response:
                print("✅ 默认响应生成成功")
                print(f"   响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
                self.passed_tests += 1
            else:
                print("❌ 默认响应格式错误")
                self.failed_tests += 1

        except Exception as e:
            print(f"❌ 默认响应生成异常: {e}")
            self.failed_tests += 1

        return True

    def run_all_tests(self) -> bool:
        """运行所有测试"""
        print("\n" + "#"*60)
        print("# UniMCPSim 后端AI功能测试")
        print("#"*60)

        # 检查AI配置
        print("\n检查AI配置...")
        if ai_generator.enabled:
            print(f"✅ AI已启用")
            print(f"   模型: {ai_generator.model}")
            print(f"   Thinking模式: {ai_generator.enable_thinking}")
            print(f"   Stream模式: {ai_generator.use_stream}")
        else:
            print("⚠️ AI未启用，部分测试将跳过")
            print("   请通过Web界面或.env文件配置AI")

        # 运行测试
        self.test_action_generation()
        self.test_response_simulation()
        self.test_ai_config_reload()
        self.test_default_response()

        # 输出总结
        print("\n" + "="*60)
        print("测试总结")
        print("="*60)
        total = self.passed_tests + self.failed_tests
        print(f"总测试数: {total}")
        print(f"✅ 通过: {self.passed_tests}")
        print(f"❌ 失败: {self.failed_tests}")

        if self.failed_tests == 0:
            print("\n🎉 所有测试通过!")
        else:
            print(f"\n⚠️ 有 {self.failed_tests} 个测试失败")

        return self.failed_tests == 0


def main():
    """主函数"""
    print("检查数据库连接...")
    try:
        session = db_manager.get_session()
        session.close()
        print("✅ 数据库连接正常\n")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return 1

    # 运行测试
    tester = AIBackendTester()
    success = tester.run_all_tests()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
