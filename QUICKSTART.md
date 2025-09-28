# UniMCPSim 快速启动指南

## 🚀 5分钟快速体验

### 第一步：环境准备

```bash
# 确保在项目目录中
cd UniMCPSim

# 设置环境变量（重要！）
unset HTTPS_PROXY
unset HTTP_PROXY

# 激活虚拟环境
source venv/bin/activate

# 确认依赖已安装
pip install -r requirements.txt
```

### ⚠️ 重要：配置.env文件

在启动前**必须**创建`.env`文件，这是必需步骤：

```bash
# 创建.env文件
cat > .env << 'EOF'
# OpenAI API配置（必需）
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_BASE_URL=https://api.openai.com/v1
EOF
```

**重要说明**：
- 请将`your_openai_api_key_here`替换为您的真实OpenAI API密钥
- 从v2.0开始，系统使用AI智能生成动作定义，必须配置OpenAI API
- 如果没有配置，新建应用功能将无法正常工作

### 第三步：一键启动服务

```bash
# 一键启动所有服务
python start_servers.py
```

看到以下输出表示启动成功：
```
==========================================================
UniMCPSim - Universal MCP Simulator
==========================================================

初始化默认模拟器...
✅ 已创建默认管理员用户

启动服务...
服务已启动:
----------------------------------------------------------
MCP服务器: http://localhost:8080/mcp
管理后台: http://localhost:8081/admin/
默认账号: admin / admin123
----------------------------------------------------------

按 Ctrl+C 停止服务
```

### 第四步：快速功能验证

#### 1. 测试核心功能

打开新终端，运行功能测试：

```bash
cd UniMCPSim
source venv/bin/activate
unset HTTPS_PROXY && unset HTTP_PROXY

# 运行核心功能测试
python tests/simple_test.py
```

期望输出：
```
############################################################
# UniMCPSim 功能验证测试
############################################################

============================================================
测试应用列表功能
============================================================
✅ 找到 9 个已启用的应用:
   - VirusTotal威胁情报 (/Security/VirusTotal)
   - 微步在线威胁情报 (/Security/ThreatBook)
   - 青藤云HIDS (/Security/QingTengHIDS)
   - 企业微信 (/IM/WeChat)
   - 腾讯会议 (/Meeting/TencentMeeting)
   - Jira工单系统 (/Ticket/Jira)
   - 华为交换机 (/Network/HuaweiSwitch)
   - Cisco路由器 (/Network/CiscoRouter)
   - 深信服防火墙 (/Firewall/Sangfor)

============================================================
UniMCPSim 核心功能测试
============================================================
✅ 使用Token: dbb02af0...a525

测试 1: 企业微信发送消息 ✅ 成功
测试 2: VirusTotal IP扫描 ✅ 成功
测试 3: Jira创建工单 ✅ 成功
测试 4: 深信服防火墙封禁IP ✅ 成功
测试 5: 华为交换机查看接口 ✅ 成功

============================================================
测试总结
============================================================
🎉 所有测试通过!
```

#### 2. 访问Web管理后台

浏览器访问：http://localhost:8081/admin/

- 用户名：`admin`
- 密码：`admin123`

可以查看：
- 📊 系统概览
- 🔧 应用管理
- 🎫 Token管理
- 📋 审计日志

#### 3. 测试MCP接口

```bash
# 获取Demo Token
curl -s "http://localhost:8081/admin/api/tokens" \
  -H "Authorization: Bearer admin-session" | grep -o '"token":"[^"]*"' | head -1

# 使用Token测试MCP初始化
curl "http://localhost:8080/mcp?token=<your-demo-token>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
      "protocolVersion": "0.1.0",
      "capabilities": {},
      "clientInfo": {"name": "test-client", "version": "1.0.0"}
    },
    "id": 1
  }'
```

## 📝 常用操作

### 重启服务
```bash
# 停止服务 (Ctrl+C)
# 重新启动
python start_servers.py
```

### 重置数据库
```bash
# 删除现有数据库
rm -f data/unimcp.db

# 重新初始化
python init_simulators.py
```

### 查看日志
```bash
# 服务启动时会显示实时日志
# Web管理后台可查看审计日志
```

## 🧪 完整测试流程

### 1. 基础功能测试
```bash
python tests/simple_test.py
```

### 2. MCP协议测试
```bash
# 确保服务正在运行
python tests/test_e2e.py
```

### 3. 手动API测试

#### 企业微信发送消息示例
```bash
# 1. 初始化会话
session_response=$(curl -s "http://localhost:8080/mcp?token=<token>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "0.1.0", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}, "id": 1}' \
  -D headers.tmp)

# 2. 提取会话ID
session_id=$(grep -i 'mcp-session-id:' headers.tmp | tr -d '\r' | cut -d' ' -f2-)

# 3. 调用企业微信发送消息
curl "http://localhost:8080/mcp?token=<token>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $session_id" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "execute_action",
      "arguments": {
        "token": "<token>",
        "category": "IM",
        "product": "WeChat",
        "action": "send_message",
        "parameters": {
          "to_user": "test_user",
          "text": "Hello from UniMCPSim!"
        }
      }
    },
    "id": 2
  }'
```

## ⚠️ 故障排除

### 问题1：端口被占用
```bash
# 检查端口占用
lsof -i :8080
lsof -i :8081

# 杀死占用进程
kill -9 <PID>
```

### 问题2：依赖安装失败
```bash
# 升级pip
pip install --upgrade pip

# 清除缓存重新安装
pip cache purge
pip install -r requirements.txt
```

### 问题3：数据库错误
```bash
# 完全重置
rm -rf data/
mkdir data
python init_simulators.py
```

### 问题4：网络代理干扰
```bash
# 确保取消代理设置
unset HTTPS_PROXY
unset HTTP_PROXY
unset http_proxy
unset https_proxy

# 验证
echo $HTTPS_PROXY  # 应该为空
```

## 🎯 成功标志

看到以下输出表示系统运行正常：

1. **服务启动成功**：
   - MCP服务器运行在8080端口
   - Web管理后台运行在8081端口
   - 无错误日志输出

2. **功能测试通过**：
   - `python tests/simple_test.py` 显示 "🎉 所有测试通过!"
   - 9个应用模拟器全部可用
   - Demo Token正常工作

3. **Web界面正常**：
   - 能够正常登录管理后台
   - 各个页面加载正常
   - 数据显示正确

## 📞 获取帮助

如果遇到问题：

1. 检查README.md中的详细说明
2. 确认所有前置条件已满足
3. 查看控制台错误输出
4. 验证网络和权限设置

---

**恭喜！UniMCPSim已经准备就绪！** 🎉

现在您可以：
- 🔌 通过MCP协议连接各种客户端
- 🌐 使用Web界面管理应用和Token
- 🧪 开发和测试需要多种API的应用
- 🔧 根据需要添加自定义模拟器