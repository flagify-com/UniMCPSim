#!/bin/bash

# SOAR管理员密码重置脚本
# 该脚本会生成新的管理员密码并更新数据库

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的信息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否安装了python3
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "python3 未安装，请先安装python3"
        exit 1
    fi
}

# 检查必要的Python模块
check_python_modules() {
    python3 -c "import sqlite3, hashlib, secrets, string" 2>/dev/null || {
        print_error "缺少必要的Python模块"
        exit 1
    }
}

# 检查数据库文件是否存在
check_database() {
    if [ ! -f "soar_mcp.db" ]; then
        print_error "数据库文件 soar_mcp.db 不存在"
        print_info "请确保在正确的目录中运行此脚本"
        exit 1
    fi
}

# 生成新密码的Python脚本
generate_reset_password() {
    python3 << 'EOF'
import sqlite3
import hashlib
import secrets
import string
from datetime import datetime

def generate_admin_password(length=12):
    """生成管理员密码"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def hash_password(password):
    """对密码进行哈希 - 与auth_utils.py中的逻辑保持一致"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def reset_admin_password():
    """重置管理员密码"""
    try:
        # 连接数据库
        conn = sqlite3.connect('soar_mcp.db')
        cursor = conn.cursor()

        # 生成新密码
        new_password = generate_admin_password()
        password_hash = hash_password(new_password)
        current_time = datetime.now().isoformat()

        # 删除现有的管理员密码记录
        cursor.execute("DELETE FROM admin_passwords")

        # 插入新的密码记录
        cursor.execute("""
            INSERT INTO admin_passwords (password_hash, description, is_active, created_time, updated_time)
            VALUES (?, ?, ?, ?, ?)
        """, (password_hash, "脚本重置的管理员密码", True, current_time, current_time))

        # 提交更改
        conn.commit()
        conn.close()

        print(f"SUCCESS|{new_password}")
        return True

    except sqlite3.Error as e:
        print(f"DATABASE_ERROR|{e}")
        return False
    except Exception as e:
        print(f"ERROR|{e}")
        return False

if __name__ == "__main__":
    reset_admin_password()
EOF
}

# 主函数
main() {
    print_info "🔄 开始重置SOAR管理员密码..."

    # 检查环境
    print_info "检查运行环境..."
    check_python
    check_python_modules
    check_database

    print_success "✅ 环境检查通过"

    # 询问用户确认
    echo
    print_warning "⚠️  这将重置管理员密码，旧密码将失效"
    read -p "是否继续? [y/N]: " confirm

    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        print_info "操作已取消"
        exit 0
    fi

    echo
    print_info "正在重置密码..."

    # 执行密码重置
    result=$(generate_reset_password)

    # 解析结果
    if [[ $result == SUCCESS\|* ]]; then
        new_password=${result#SUCCESS|}
        echo
        print_success "🎉 管理员密码重置成功！"
        echo
        echo "=================== 新密码信息 ==================="
        echo -e "${GREEN}管理员密码: ${YELLOW}${new_password}${NC}"
        echo "=================================================="
        echo
        print_warning "请妥善保存此密码，重启服务后生效"
        print_info "建议重启SOAR服务以确保密码变更生效"
        echo
    elif [[ $result == DATABASE_ERROR\|* ]]; then
        error_msg=${result#DATABASE_ERROR|}
        print_error "数据库操作失败: $error_msg"
        exit 1
    else
        error_msg=${result#ERROR|}
        print_error "重置失败: $error_msg"
        exit 1
    fi
}

# 脚本入口点
echo "=========================================="
echo "    SOAR管理员密码重置工具 v1.0"
echo "=========================================="
echo

main "$@"