#!/usr/bin/env python3
"""
管理员密码重置工具
"""

import sys
import getpass
from models import db_manager

def reset_admin_password():
    """重置管理员密码"""
    print("UniMCPSim 管理员密码重置工具")
    print("=" * 40)

    # 提示用户选择重置方式
    print("请选择重置方式：")
    print("1. 重置为默认密码 (admin123)")
    print("2. 设置自定义密码")

    while True:
        choice = input("\n请输入选择 (1 或 2): ").strip()
        if choice in ['1', '2']:
            break
        print("无效选择，请输入 1 或 2")

    if choice == '1':
        # 重置为默认密码
        new_password = 'admin123'
        print(f"\n正在重置管理员密码为默认密码...")
    else:
        # 设置自定义密码
        while True:
            new_password = getpass.getpass("\n请输入新密码: ")
            if len(new_password) < 6:
                print("密码长度不能少于6位，请重新输入")
                continue

            confirm_password = getpass.getpass("请确认新密码: ")
            if new_password != confirm_password:
                print("两次输入的密码不一致，请重新输入")
                continue

            break

        print(f"\n正在设置新密码...")

    # 执行密码重置
    try:
        success = db_manager.reset_admin_password(new_password)
        if success:
            print("✓ 管理员密码重置成功！")
            if choice == '1':
                print("新密码: admin123")
            else:
                print("请使用新密码登录管理后台")
        else:
            print("✗ 密码重置失败，请检查数据库连接")
            sys.exit(1)
    except Exception as e:
        print(f"✗ 密码重置失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    try:
        reset_admin_password()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n程序运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()