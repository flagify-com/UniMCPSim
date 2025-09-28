#!/bin/bash
# SOAR MCP 自动化测试脚本
# 支持启动服务器、运行测试、生成报告

set -e  # 遇到错误时立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 配置
SERVER_SCRIPT="soar_mcp_server.py"
CLIENT_SCRIPT="mcp_soar_client.py"
SERVER_PORT=12345
TEST_TIMEOUT=30
RESULTS_DIR="test_results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# 创建结果目录
mkdir -p "$RESULTS_DIR"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查端口是否被占用
check_port() {
    if lsof -ti:$SERVER_PORT >/dev/null 2>&1; then
        return 0  # 端口被占用
    else
        return 1  # 端口空闲
    fi
}

# 等待服务器启动
wait_for_server() {
    local max_attempts=30
    local attempt=1
    
    log_info "等待服务器启动..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "http://127.0.0.1:$SERVER_PORT/mcp" >/dev/null 2>&1; then
            log_success "服务器已就绪 (尝试 $attempt/$max_attempts)"
            return 0
        fi
        
        echo -n "."
        sleep 1
        ((attempt++))
    done
    
    log_error "服务器启动超时"
    return 1
}

# 启动服务器
start_server() {
    log_info "激活虚拟环境..."
    source venv/bin/activate
    
    # 清除代理环境变量
    unset https_proxy http_proxy HTTPS_PROXY HTTP_PROXY
    
    log_info "启动 SOAR MCP 服务器..."
    python "$SERVER_SCRIPT" > "$RESULTS_DIR/server_${TIMESTAMP}.log" 2>&1 &
    SERVER_PID=$!
    
    log_info "服务器 PID: $SERVER_PID"
    echo $SERVER_PID > "$RESULTS_DIR/server.pid"
    
    # 等待服务器启动
    if wait_for_server; then
        return 0
    else
        return 1
    fi
}

# 停止服务器
stop_server() {
    if [ -f "$RESULTS_DIR/server.pid" ]; then
        SERVER_PID=$(cat "$RESULTS_DIR/server.pid")
        if kill -0 $SERVER_PID 2>/dev/null; then
            log_info "停止服务器 (PID: $SERVER_PID)..."
            kill $SERVER_PID
            
            # 等待进程结束
            local attempt=1
            while [ $attempt -le 10 ] && kill -0 $SERVER_PID 2>/dev/null; do
                sleep 1
                ((attempt++))
            done
            
            # 强制终止
            if kill -0 $SERVER_PID 2>/dev/null; then
                log_warning "强制终止服务器进程..."
                kill -9 $SERVER_PID 2>/dev/null || true
            fi
            
            log_success "服务器已停止"
        fi
        rm -f "$RESULTS_DIR/server.pid"
    fi
    
    # 清理可能残留的进程
    lsof -ti:$SERVER_PORT | xargs kill -9 2>/dev/null || true
}

# 运行测试
run_tests() {
    log_info "运行MCP客户端测试..."
    
    source venv/bin/activate
    
    local test_result_file="$RESULTS_DIR/test_results_${TIMESTAMP}.json"
    
    if python "$CLIENT_SCRIPT" --save-results "$test_result_file"; then
        log_success "测试执行完成"
        
        # 解析测试结果
        if [ -f "$test_result_file" ]; then
            local success_rate=$(python -c "
import json
try:
    with open('$test_result_file', 'r') as f:
        data = json.load(f)
    print(data.get('summary', {}).get('success_rate', '0%'))
except:
    print('0%')
")
            log_info "测试成功率: $success_rate"
            echo "$success_rate" > "$RESULTS_DIR/latest_success_rate.txt"
            
            return 0
        else
            log_error "测试结果文件未生成"
            return 1
        fi
    else
        log_error "测试执行失败"
        return 1
    fi
}

# 生成测试报告
generate_report() {
    log_info "生成测试报告..."
    
    local report_file="$RESULTS_DIR/test_report_${TIMESTAMP}.md"
    
    cat > "$report_file" << EOF
# SOAR MCP 自动化测试报告

**测试时间**: $(date)
**测试ID**: $TIMESTAMP

## 测试环境

- 服务器脚本: $SERVER_SCRIPT
- 客户端脚本: $CLIENT_SCRIPT  
- 服务端口: $SERVER_PORT
- Python环境: $(python --version 2>&1)

## 测试结果

EOF

    # 添加成功率
    if [ -f "$RESULTS_DIR/latest_success_rate.txt" ]; then
        local success_rate=$(cat "$RESULTS_DIR/latest_success_rate.txt")
        echo "**总体成功率**: $success_rate" >> "$report_file"
        echo "" >> "$report_file"
    fi
    
    # 添加详细结果
    local test_result_file="$RESULTS_DIR/test_results_${TIMESTAMP}.json"
    if [ -f "$test_result_file" ]; then
        echo "### 详细测试结果" >> "$report_file"
        echo "" >> "$report_file"
        echo "\`\`\`json" >> "$report_file"
        cat "$test_result_file" >> "$report_file"
        echo "\`\`\`" >> "$report_file"
    fi
    
    # 添加服务器日志摘要
    local server_log="$RESULTS_DIR/server_${TIMESTAMP}.log"
    if [ -f "$server_log" ]; then
        echo "" >> "$report_file"
        echo "### 服务器日志摘要" >> "$report_file"
        echo "" >> "$report_file"
        echo "\`\`\`" >> "$report_file"
        tail -20 "$server_log" >> "$report_file"
        echo "\`\`\`" >> "$report_file"
    fi
    
    log_success "测试报告已生成: $report_file"
}

# 清理函数
cleanup() {
    log_info "清理测试环境..."
    stop_server
}

# 设置信号处理
trap cleanup EXIT INT TERM

# 主函数
main() {
    log_info "开始 SOAR MCP 自动化测试"
    log_info "测试ID: $TIMESTAMP"
    echo
    
    # 检查必要文件
    if [ ! -f "$SERVER_SCRIPT" ]; then
        log_error "服务器脚本不存在: $SERVER_SCRIPT"
        exit 1
    fi
    
    if [ ! -f "$CLIENT_SCRIPT" ]; then
        log_error "客户端脚本不存在: $CLIENT_SCRIPT"
        exit 1
    fi
    
    if [ ! -d "venv" ]; then
        log_error "虚拟环境不存在: venv/"
        exit 1
    fi
    
    # 检查端口
    if check_port; then
        log_warning "端口 $SERVER_PORT 已被占用，尝试清理..."
        lsof -ti:$SERVER_PORT | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # 启动服务器
    if ! start_server; then
        log_error "服务器启动失败"
        exit 1
    fi
    
    # 运行测试
    if ! run_tests; then
        log_error "测试执行失败"
        exit 1
    fi
    
    # 生成报告
    generate_report
    
    log_success "自动化测试完成！"
    
    # 显示结果摘要
    if [ -f "$RESULTS_DIR/latest_success_rate.txt" ]; then
        local success_rate=$(cat "$RESULTS_DIR/latest_success_rate.txt")
        echo
        log_info "测试成功率: $success_rate"
        
        # 根据成功率设置退出码
        if [[ "$success_rate" == "100.0%" ]]; then
            exit 0
        else
            exit 1
        fi
    fi
}

# 帮助信息
show_help() {
    cat << EOF
SOAR MCP 自动化测试脚本

用法: $0 [选项]

选项:
  -h, --help     显示此帮助信息
  -p, --port     指定服务器端口 (默认: 12345)
  -t, --timeout  测试超时时间 (默认: 30秒)
  --clean        清理测试结果目录

示例:
  $0                    # 运行完整测试
  $0 -p 8080           # 使用端口8080
  $0 --clean           # 清理测试结果
EOF
}

# 参数解析
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -p|--port)
            SERVER_PORT="$2"
            shift 2
            ;;
        -t|--timeout)
            TEST_TIMEOUT="$2"
            shift 2
            ;;
        --clean)
            log_info "清理测试结果目录..."
            rm -rf "$RESULTS_DIR"
            log_success "清理完成"
            exit 0
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
done

# 运行主函数
main