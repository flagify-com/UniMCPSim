#!/usr/bin/env python3
"""
运行所有回归测试
"""

import os
import sys
import subprocess
import time

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRunner:
    """测试运行器"""

    def __init__(self):
        self.tests_dir = os.path.dirname(os.path.abspath(__file__))
        self.passed = []
        self.failed = []

    def check_servers(self) -> bool:
        """检查服务器是否运行"""
        print("="*60)
        print("检查服务器状态")
        print("="*60)

        import httpx

        # 检查MCP服务器
        print("\n检查MCP服务器 (http://localhost:9090)...")
        try:
            response = httpx.get("http://localhost:9090/health", timeout=5)
            if response.status_code == 200:
                print("✅ MCP服务器运行正常")
            else:
                print(f"⚠️ MCP服务器响应异常: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 无法连接到MCP服务器: {e}")
            return False

        # 检查Admin服务器
        print("\n检查Admin服务器 (http://localhost:9091)...")
        try:
            response = httpx.get("http://localhost:9091/admin/login", timeout=5)
            if response.status_code == 200:
                print("✅ Admin服务器运行正常")
            else:
                print(f"⚠️ Admin服务器响应异常: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 无法连接到Admin服务器: {e}")
            return False

        return True

    def run_test(self, test_file: str, test_name: str) -> bool:
        """运行单个测试文件"""
        print("\n" + "="*60)
        print(f"运行测试: {test_name}")
        print("="*60)

        test_path = os.path.join(self.tests_dir, test_file)

        try:
            result = subprocess.run(
                [sys.executable, test_path],
                cwd=os.path.dirname(self.tests_dir),
                capture_output=False,
                text=True
            )

            if result.returncode == 0:
                print(f"\n✅ {test_name} - 通过")
                self.passed.append(test_name)
                return True
            else:
                print(f"\n❌ {test_name} - 失败")
                self.failed.append(test_name)
                return False

        except Exception as e:
            print(f"\n❌ {test_name} - 异常: {e}")
            self.failed.append(test_name)
            return False

    def print_summary(self):
        """打印测试总结"""
        print("\n" + "#"*60)
        print("# 测试总结")
        print("#"*60)

        total = len(self.passed) + len(self.failed)
        print(f"\n总测试套件: {total}")
        print(f"✅ 通过: {len(self.passed)}")
        print(f"❌ 失败: {len(self.failed)}")

        if self.passed:
            print("\n通过的测试:")
            for test in self.passed:
                print(f"  ✅ {test}")

        if self.failed:
            print("\n失败的测试:")
            for test in self.failed:
                print(f"  ❌ {test}")

        if len(self.failed) == 0:
            print("\n🎉 所有测试套件通过!")
        else:
            print(f"\n⚠️ 有 {len(self.failed)} 个测试套件失败")

    def run_all(self) -> int:
        """运行所有测试"""
        print("\n" + "#"*60)
        print("# UniMCPSim 回归测试套件")
        print("#"*60)
        print("\n注意: 请确保已启动服务器 (./start_servers.sh 或 python start_servers.py)")
        time.sleep(2)

        # 检查服务器
        if not self.check_servers():
            print("\n❌ 服务器未运行，测试终止")
            print("请先运行: ./start_servers.sh 或 python start_servers.py")
            return 1

        print("\n✅ 服务器检查通过，开始测试...")
        time.sleep(1)

        # 定义测试列表
        tests = [
            ("test_admin_frontend.py", "前端管理界面测试"),
            ("test_ai_backend.py", "后端AI功能测试"),
            ("test_mcp_client.py", "MCP客户端测试"),
        ]

        # 运行所有测试
        for test_file, test_name in tests:
            self.run_test(test_file, test_name)
            time.sleep(1)  # 测试间隔

        # 打印总结
        self.print_summary()

        return 0 if len(self.failed) == 0 else 1


def main():
    """主函数"""
    runner = TestRunner()
    return runner.run_all()


if __name__ == "__main__":
    sys.exit(main())
