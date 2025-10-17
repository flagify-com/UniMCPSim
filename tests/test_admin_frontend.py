#!/usr/bin/env python3
"""
前端测试 - Admin管理界面测试
测试登录、修改密码、应用管理、Token管理
"""

import os
import sys
import time
import httpx
from typing import Optional

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class AdminFrontendTester:
    """前端管理界面测试器"""

    def __init__(self, base_url: str = "http://localhost:9091"):
        self.base_url = base_url
        self.client = httpx.Client(follow_redirects=True)
        self.session_cookies = None
        self.passed_tests = 0
        self.failed_tests = 0

    def test_login(self) -> bool:
        """测试1: 登录功能"""
        print("\n" + "="*60)
        print("测试1: 登录功能")
        print("="*60)

        # 测试成功登录
        print("\n1.1 测试正确的用户名密码登录...")
        try:
            response = self.client.post(
                f"{self.base_url}/admin/api/login",
                json={
                    "username": "admin",
                    "password": "admin123"
                }
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ 登录成功")
                    self.session_cookies = self.client.cookies
                    self.passed_tests += 1
                else:
                    print(f"❌ 登录失败: {result}")
                    self.failed_tests += 1
                    return False
            else:
                print(f"❌ 登录失败: {response.status_code}")
                self.failed_tests += 1
                return False
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            self.failed_tests += 1
            return False

        # 测试错误密码登录
        print("\n1.2 测试错误密码登录...")
        try:
            # 创建新的client避免session干扰
            test_client = httpx.Client()
            response = test_client.post(
                f"{self.base_url}/admin/api/login",
                json={
                    "username": "admin",
                    "password": "wrong_password"
                }
            )

            # 应该返回错误信息
            if response.status_code == 401 or (response.status_code == 200 and not response.json().get('success')):
                print("✅ 错误密码正确被拒绝")
                self.passed_tests += 1
            else:
                print("❌ 错误密码未被拒绝")
                self.failed_tests += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            self.failed_tests += 1

        return True

    def test_change_password(self) -> bool:
        """测试2: 修改密码功能"""
        print("\n" + "="*60)
        print("测试2: 修改密码功能")
        print("="*60)

        # 2.1 修改密码为 admin456
        print("\n2.1 修改密码为 admin456...")
        try:
            response = self.client.post(
                f"{self.base_url}/admin/api/change-password",
                json={
                    "current_password": "admin123",
                    "new_password": "admin456",
                    "confirm_password": "admin456"
                }
            )

            if response.status_code == 200:
                print("✅ 密码修改成功")
                self.passed_tests += 1
            else:
                print(f"❌ 密码修改失败: {response.status_code}, {response.text}")
                self.failed_tests += 1
                return False
        except Exception as e:
            print(f"❌ 修改密码异常: {e}")
            self.failed_tests += 1
            return False

        # 2.2 使用新密码登录
        print("\n2.2 使用新密码 admin456 登录...")
        try:
            new_client = httpx.Client(follow_redirects=True)
            response = new_client.post(
                f"{self.base_url}/admin/api/login",
                json={
                    "username": "admin",
                    "password": "admin456"
                }
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ 新密码登录成功")
                    self.client = new_client  # 更新client
                    self.session_cookies = self.client.cookies
                    self.passed_tests += 1
                else:
                    print(f"❌ 新密码登录失败: {result}")
                    self.failed_tests += 1
                    return False
            else:
                print(f"❌ 新密码登录失败: {response.status_code}")
                self.failed_tests += 1
                return False
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            self.failed_tests += 1
            return False

        # 2.3 改回原密码 admin123
        print("\n2.3 恢复密码为 admin123...")
        try:
            response = self.client.post(
                f"{self.base_url}/admin/api/change-password",
                json={
                    "current_password": "admin456",
                    "new_password": "admin123",
                    "confirm_password": "admin123"
                }
            )

            if response.status_code == 200:
                print("✅ 密码恢复成功")
                self.passed_tests += 1
            else:
                print(f"❌ 密码恢复失败: {response.status_code}")
                self.failed_tests += 1
                return False
        except Exception as e:
            print(f"❌ 恢复密码异常: {e}")
            self.failed_tests += 1
            return False

        # 2.4 验证恢复后的密码
        print("\n2.4 验证恢复后的密码 admin123...")
        try:
            final_client = httpx.Client(follow_redirects=True)
            response = final_client.post(
                f"{self.base_url}/admin/api/login",
                json={
                    "username": "admin",
                    "password": "admin123"
                }
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ 恢复后的密码验证成功")
                    self.client = final_client  # 更新client
                    self.session_cookies = self.client.cookies
                    self.passed_tests += 1
                else:
                    print(f"❌ 恢复后的密码验证失败")
                    self.failed_tests += 1
            else:
                print(f"❌ 恢复后的密码验证失败: {response.status_code}")
                self.failed_tests += 1
        except Exception as e:
            print(f"❌ 验证异常: {e}")
            self.failed_tests += 1

        return True

    def test_application_management(self) -> bool:
        """测试3: 应用管理功能"""
        print("\n" + "="*60)
        print("测试3: 应用管理功能 (创建、更新、删除)")
        print("="*60)

        app_id = None

        # 3.1 创建应用
        print("\n3.1 创建测试应用...")
        try:
            response = self.client.post(
                f"{self.base_url}/admin/api/apps",
                json={
                    "name": "TestApp",
                    "category": "Testing",
                    "display_name": "测试应用",
                    "description": "这是一个用于回归测试的应用",
                    "ai_notes": "测试专用",
                    "template": {
                        "actions": [
                            {
                                "name": "test_action",
                                "display_name": "测试动作",
                                "description": "用于测试的动作",
                                "parameters": [
                                    {
                                        "key": "test_param",
                                        "type": "String",
                                        "required": True,
                                        "description": "测试参数"
                                    }
                                ]
                            }
                        ]
                    }
                }
            )

            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                app_id = result.get('id')
                print(f"✅ 应用创建成功, ID: {app_id}")
                self.passed_tests += 1
            else:
                print(f"❌ 应用创建失败: {response.status_code}, {response.text}")
                self.failed_tests += 1
                return False
        except Exception as e:
            print(f"❌ 创建应用异常: {e}")
            self.failed_tests += 1
            return False

        # 等待一下确保数据已保存
        time.sleep(0.5)

        # 3.2 获取应用列表,验证创建成功
        print("\n3.2 获取应用列表，验证创建...")
        try:
            response = self.client.get(f"{self.base_url}/admin/api/apps")

            if response.status_code == 200:
                apps = response.json()
                test_app = next((app for app in apps if app['name'] == 'TestApp'), None)
                if test_app:
                    print(f"✅ 在应用列表中找到测试应用: {test_app['display_name']}")
                    app_id = test_app['id']  # 确保有正确的ID
                    self.passed_tests += 1
                else:
                    print("❌ 未在应用列表中找到测试应用")
                    self.failed_tests += 1
            else:
                print(f"❌ 获取应用列表失败: {response.status_code}")
                self.failed_tests += 1
        except Exception as e:
            print(f"❌ 获取应用列表异常: {e}")
            self.failed_tests += 1

        # 3.3 更新应用
        print("\n3.3 更新测试应用...")
        try:
            response = self.client.put(
                f"{self.base_url}/admin/api/apps/{app_id}",
                json={
                    "display_name": "测试应用(已更新)",
                    "description": "这是一个用于回归测试的应用(已更新)",
                    "ai_notes": "测试专用(已更新)",
                    "template": {
                        "actions": [
                            {
                                "name": "test_action",
                                "display_name": "测试动作",
                                "description": "用于测试的动作",
                                "parameters": [
                                    {
                                        "key": "test_param",
                                        "type": "String",
                                        "required": True,
                                        "description": "测试参数"
                                    }
                                ]
                            },
                            {
                                "name": "test_action_2",
                                "display_name": "测试动作2",
                                "description": "新增的测试动作",
                                "parameters": []
                            }
                        ]
                    }
                }
            )

            if response.status_code == 200:
                print("✅ 应用更新成功")
                self.passed_tests += 1
            else:
                print(f"❌ 应用更新失败: {response.status_code}, {response.text}")
                self.failed_tests += 1
        except Exception as e:
            print(f"❌ 更新应用异常: {e}")
            self.failed_tests += 1

        # 3.4 验证更新
        print("\n3.4 验证应用更新...")
        try:
            response = self.client.get(f"{self.base_url}/admin/api/apps/{app_id}")

            if response.status_code == 200:
                app = response.json()
                if app['display_name'] == "测试应用(已更新)" and \
                   len(app['template']['actions']) == 2:
                    print("✅ 应用更新验证成功")
                    self.passed_tests += 1
                else:
                    print("❌ 应用更新验证失败")
                    self.failed_tests += 1
            else:
                print(f"❌ 获取应用详情失败: {response.status_code}")
                self.failed_tests += 1
        except Exception as e:
            print(f"❌ 验证更新异常: {e}")
            self.failed_tests += 1

        # 3.5 删除应用
        print("\n3.5 删除测试应用...")
        try:
            response = self.client.delete(f"{self.base_url}/admin/api/apps/{app_id}")

            if response.status_code == 200:
                print("✅ 应用删除成功")
                self.passed_tests += 1
            else:
                print(f"❌ 应用删除失败: {response.status_code}")
                self.failed_tests += 1
        except Exception as e:
            print(f"❌ 删除应用异常: {e}")
            self.failed_tests += 1

        # 3.6 验证删除
        print("\n3.6 验证应用已删除...")
        try:
            response = self.client.get(f"{self.base_url}/admin/api/apps")

            if response.status_code == 200:
                apps = response.json()
                test_app = next((app for app in apps if app['name'] == 'TestApp'), None)
                if not test_app:
                    print("✅ 应用删除验证成功")
                    self.passed_tests += 1
                else:
                    print("❌ 应用仍然存在，删除验证失败")
                    self.failed_tests += 1
            else:
                print(f"❌ 获取应用列表失败: {response.status_code}")
                self.failed_tests += 1
        except Exception as e:
            print(f"❌ 验证删除异常: {e}")
            self.failed_tests += 1

        return True

    def test_token_management(self) -> bool:
        """测试4: Token管理功能"""
        print("\n" + "="*60)
        print("测试4: Token管理功能 (创建、设置权限、删除)")
        print("="*60)

        token_id = None
        app_id = None

        # 4.1 先创建一个测试应用用于权限测试
        print("\n4.1 创建测试应用用于权限测试...")
        try:
            response = self.client.post(
                f"{self.base_url}/admin/api/apps",
                json={
                    "name": "TokenTestApp",
                    "category": "Testing",
                    "display_name": "Token测试应用",
                    "description": "用于Token权限测试",
                    "template": {"actions": []}
                }
            )

            if response.status_code in [200, 201]:
                result = response.json()
                app_id = result.get('id')
                print(f"✅ 测试应用创建成功, ID: {app_id}")
                self.passed_tests += 1
            else:
                print(f"❌ 测试应用创建失败: {response.status_code}")
                self.failed_tests += 1
                return False
        except Exception as e:
            print(f"❌ 创建测试应用异常: {e}")
            self.failed_tests += 1
            return False

        # 4.2 创建Token
        print("\n4.2 创建测试Token...")
        try:
            response = self.client.post(
                f"{self.base_url}/admin/api/tokens",
                json={
                    "name": "测试Token"
                }
            )

            if response.status_code in [200, 201]:
                result = response.json()
                token_id = result.get('id')
                print(f"✅ Token创建成功, ID: {token_id}")
                print(f"   Token: {result.get('token')[:16]}...")
                self.passed_tests += 1
            else:
                print(f"❌ Token创建失败: {response.status_code}, {response.text}")
                self.failed_tests += 1
                return False
        except Exception as e:
            print(f"❌ 创建Token异常: {e}")
            self.failed_tests += 1
            return False

        time.sleep(0.5)

        # 4.3 设置Token权限
        print("\n4.3 为Token设置应用权限...")
        try:
            response = self.client.put(
                f"{self.base_url}/admin/api/tokens/{token_id}/apps",
                json={
                    "app_ids": [app_id]
                }
            )

            if response.status_code == 200:
                print("✅ Token权限设置成功")
                self.passed_tests += 1
            else:
                print(f"❌ Token权限设置失败: {response.status_code}, {response.text}")
                self.failed_tests += 1
        except Exception as e:
            print(f"❌ 设置权限异常: {e}")
            self.failed_tests += 1

        # 4.4 验证Token权限
        print("\n4.4 验证Token权限...")
        try:
            # 使用 /tokens/<id>/apps 端点获取授权的应用
            response = self.client.get(f"{self.base_url}/admin/api/tokens/{token_id}/apps")

            if response.status_code == 200:
                apps = response.json()
                if len(apps) == 1 and apps[0]['id'] == app_id:
                    print("✅ Token权限验证成功")
                    self.passed_tests += 1
                else:
                    print(f"❌ Token权限验证失败，应用数量: {len(apps)}")
                    self.failed_tests += 1
            else:
                print(f"❌ 获取Token权限失败: {response.status_code}")
                self.failed_tests += 1
        except Exception as e:
            print(f"❌ 验证权限异常: {e}")
            self.failed_tests += 1

        # 4.5 删除Token
        print("\n4.5 删除测试Token...")
        try:
            response = self.client.delete(f"{self.base_url}/admin/api/tokens/{token_id}")

            if response.status_code == 200:
                print("✅ Token删除成功")
                self.passed_tests += 1
            else:
                print(f"❌ Token删除失败: {response.status_code}")
                self.failed_tests += 1
        except Exception as e:
            print(f"❌ 删除Token异常: {e}")
            self.failed_tests += 1

        # 4.6 删除测试应用
        print("\n4.6 清理：删除测试应用...")
        try:
            response = self.client.delete(f"{self.base_url}/admin/api/apps/{app_id}")
            if response.status_code == 200:
                print("✅ 测试应用删除成功")
                self.passed_tests += 1
            else:
                print(f"⚠️ 测试应用删除失败: {response.status_code}")
        except Exception as e:
            print(f"⚠️ 删除测试应用异常: {e}")

        return True

    def run_all_tests(self) -> bool:
        """运行所有测试"""
        print("\n" + "#"*60)
        print("# UniMCPSim 前端管理界面测试")
        print("#"*60)

        # 运行测试
        self.test_login()
        self.test_change_password()
        self.test_application_management()
        self.test_token_management()

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

        # 关闭客户端
        self.client.close()

        return self.failed_tests == 0


def main():
    """主函数"""
    # 检查服务器是否运行
    print("检查Admin服务器是否运行在 http://localhost:9091 ...")
    try:
        response = httpx.get("http://localhost:9091/admin/login", timeout=5)
        print("✅ Admin服务器正在运行\n")
    except Exception as e:
        print(f"❌ 无法连接到Admin服务器: {e}")
        print("请先运行: ./start_servers.sh 或 python start_servers.py")
        return 1

    # 运行测试
    tester = AdminFrontendTester()
    success = tester.run_all_tests()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
