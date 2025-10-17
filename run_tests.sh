#!/bin/bash
# 运行回归测试脚本

echo "============================================================"
echo "UniMCPSim 回归测试"
echo "============================================================"
echo ""

# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️ 未检测到虚拟环境，尝试激活..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo "✅ 虚拟环境已激活"
    else
        echo "❌ 未找到虚拟环境，请先创建: python3 -m venv venv"
        exit 1
    fi
fi

echo ""
echo "提示: 请确保服务器已启动"
echo "如果未启动，请在另一个终端运行: ./start_servers.sh"
echo ""
echo "按回车键继续测试，或按Ctrl+C取消..."
read

# 运行测试
python tests/run_all_tests.py

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "✅ 测试完成"
else
    echo "❌ 测试失败，请查看上述错误信息"
fi

exit $exit_code
