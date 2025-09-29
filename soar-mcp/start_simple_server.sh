#!/bin/bash
# SOAR MCP 服务器智能启动脚本
# 支持首次运行检测和环境验证

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 函数：打印带颜色的信息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# 主标题
clear
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                                  ║"
echo "║                          🚀 SOAR MCP 服务器启动器                                ║"
echo "║                                                                                  ║"
echo "║            基于 Model Context Protocol 的 SOAR 安全编排平台集成服务器             ║"
echo "║                                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# 环境检查
print_header "🔍 环境检查"

# 检查Python版本
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_success "Python 版本: $PYTHON_VERSION"
else
    print_error "Python3 未安装，请先安装 Python 3.8+"
    exit 1
fi

# 检查虚拟环境
if [ -d "venv" ]; then
    print_info "激活虚拟环境..."
    source venv/bin/activate
    print_success "虚拟环境已激活"
else
    print_warning "虚拟环境未找到，使用系统Python"
    print_info "建议创建虚拟环境：python3 -m venv venv"
fi

# 检查依赖
print_info "检查依赖..."
if pip show fastmcp &> /dev/null; then
    print_success "FastMCP 已安装"
else
    print_warning "FastMCP 未安装，请运行：pip install -r requirements.txt"
fi

# 检查数据库状态
print_info "检查数据库状态..."
if [ -f "soar_mcp.db" ]; then
    print_success "数据库文件存在"
    DB_EXISTS=true
else
    print_info "数据库文件不存在，将创建新数据库"
    DB_EXISTS=false
fi

# 检查端口占用
print_info "检查端口状态..."
if lsof -i :12345 &> /dev/null; then
    print_warning "端口 12345 已被占用"
    print_info "您可能需要停止其他服务或修改端口"
fi

if lsof -i :12346 &> /dev/null; then
    print_warning "端口 12346 已被占用"
    print_info "您可能需要停止其他服务或修改端口"
fi

# 清除代理环境变量（避免连接问题）
unset https_proxy http_proxy HTTPS_PROXY HTTP_PROXY

echo ""
print_header "🎯 服务信息"
echo "┌────────────────────────────────────────────────────────────────────────────────┐"
echo "│  MCP 服务器: http://127.0.0.1:12345/mcp                                        │"
echo "│  Web 管理后台: http://127.0.0.1:12346/admin                                     │"
echo "│  传输协议: Streamable HTTP                                                      │"
echo "│  SSL 验证: 默认关闭（开箱即用）                                                  │"
echo "└────────────────────────────────────────────────────────────────────────────────┘"

echo ""
if [ "$DB_EXISTS" = false ]; then
    print_header "🔧 首次运行引导"
    echo "┌────────────────────────────────────────────────────────────────────────────────┐"
    echo "│  ✨ 检测到首次运行，系统将自动：                                                │"
    echo "│     • 创建数据库和表结构                                                        │"
    echo "│     • 生成管理员密码（请保存控制台显示的密码）                                   │"
    echo "│     • 启动核心服务（MCP + Web管理后台）                                         │"
    echo "│     • 跳过 SOAR 数据同步（等待配置）                                           │"
    echo "│                                                                                │"
    echo "│  🎯 下一步操作：                                                               │"
    echo "│     1. 等待服务启动完成                                                        │"
    echo "│     2. 记录控制台显示的管理员密码                                               │"
    echo "│     3. 访问 http://127.0.0.1:12346/admin                                      │"
    echo "│     4. 使用密码登录并配置 SOAR 连接信息                                         │"
    echo "│     5. 在 MCP 客户端中添加服务器                                               │"
    echo "└────────────────────────────────────────────────────────────────────────────────┘"
else
    print_header "🔄 常规启动"
    echo "┌────────────────────────────────────────────────────────────────────────────────┐"
    echo "│  ✅ 数据库已存在，将执行常规启动                                                │"
    echo "│     • 检查配置完整性                                                            │"
    echo "│     • 启动 MCP 服务器和管理后台                                                 │"
    echo "│     • 根据配置状态决定是否同步数据                                              │"
    echo "└────────────────────────────────────────────────────────────────────────────────┘"
fi

echo ""
print_header "🤖 MCP 客户端配置"
echo "┌────────────────────────────────────────────────────────────────────────────────┐"
echo "│  Cherry Studio（推荐）:                                                        │"
echo "│    • 类型: HTTP                                                                │"
echo "│    • URL: http://127.0.0.1:12345/mcp                                          │"
echo "│                                                                                │"
echo "│  Claude Desktop:                                                               │"
echo "│    • 参考 README.md 中的详细配置说明                                           │"
echo "│    • 需要修改配置文件并重启应用                                                 │"
echo "└────────────────────────────────────────────────────────────────────────────────┘"

echo ""
print_header "🛠️ 可用 MCP 工具"
echo "┌────────────────────────────────────────────────────────────────────────────────┐"
echo "│  • list_playbooks_quick           - 快速获取剧本列表                            │"
echo "│  • query_playbook_execution_params - 查询剧本执行参数                          │"
echo "│  • execute_playbook              - 执行 SOAR 剧本                             │"
echo "│  • query_playbook_execution_status_by_activity_id   - 查询剧本执行状态      │"
echo "│  • query_playbook_execution_result_by_activity_id   - 查询剧本执行结果      │"
echo "└────────────────────────────────────────────────────────────────────────────────┘"

echo ""
print_header "📋 可用 MCP 资源"
echo "┌────────────────────────────────────────────────────────────────────────────────┐"
echo "│  • soar://applications           - SOAR 应用列表                              │"
echo "│  • soar://playbooks             - SOAR 剧本列表                              │"
echo "│  • soar://executions            - 剧本执行记录                                │"
echo "└────────────────────────────────────────────────────────────────────────────────┘"

echo ""
print_header "🎬 启动服务器"
echo "========================================"
print_info "正在启动 SOAR MCP 服务器..."
echo ""

# 启动服务器
python3 soar_mcp_server.py