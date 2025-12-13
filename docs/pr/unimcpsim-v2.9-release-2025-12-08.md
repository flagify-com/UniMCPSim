# UniMCPSim v2.9 重磅发布：内置 Playground，一键测试任意 MCP Server！

## 🎉 两个月迭代十个版本，UniMCPSim 全面升级

还记得9月30日那场直播吗？我们发布了 UniMCPSim —— 一款能够模拟数百个网安产品 MCP Server 的神器。

两个多月过去了，我们一直在倾听用户反馈，持续迭代优化。今天，UniMCPSim **正式发布 v2.9.0 版本**，带来了一项杀手级功能：**MCP Playground**！

![MCP Playground](../images/screenshots/mcp-server-playground.png)

---

## 🚀 重磅功能：MCP Playground

### 不再需要外部客户端！

以前，测试 MCP Server 需要配置 Cherry Studio、Claude Desktop 或 Cline 等客户端。现在，**直接在 UniMCPSim 的 Web 界面**就能完成全部测试！

### 核心能力

| 功能 | 说明 |
|------|------|
| 📝 可视化配置 | 通过 Monaco 编辑器配置任意 MCP Server（JSON格式） |
| 🔗 一键测试连接 | 快速验证 MCP Server 并列出所有可用工具 |
| 💬 AI 对话交互 | 自然语言下达指令，大模型自动调用 MCP 工具 |
| 👁️ 实时可视化 | 完整展示工具调用过程和返回结果 |
| ✏️ 自定义提示词 | 可编辑系统提示词，控制 AI 行为 |

### 使用示例

```json
{
  "mcpServers": {
    "QAXFW": {
      "name": "奇安信防火墙",
      "type": "streamableHttp",
      "isActive": true,
      "baseUrl": "http://127.0.0.1:9090/Firewall/QAXFW?token=YOUR_TOKEN"
    }
  }
}
```

粘贴配置 → 测试连接 → 开始对话，三步搞定！

---

## 📊 十大版本更新速览

从 v2.0 到 v2.9，我们完成了 **10 个版本** 的迭代。以下是核心更新：

### v2.9.0 ⭐ MCP Playground（2025-12-08）
- 内置 MCP 测试工具，无需外部客户端
- AI 对话 + Function Calling 自动调用工具
- 左右分栏布局，配置与对话一体化

### v2.8.0 应用配置导入导出（2025-11-08）
- 一键导出全部或指定应用配置
- 导入前预览，自动识别同名应用
- 支持跨环境迁移和备份

### v2.7.0 完整回归测试套件（2025-10-17）
- 前端/后端/MCP 完整测试覆盖
- 自动化测试支持 CI/CD
- 详细的故障排查指南

### v2.6.0 Web 界面大模型配置（2025-10-17）
- 告别 `.env` 文件手动编辑
- 可视化配置 API Key、模型、Base URL
- 一键测试连接，实时生效

### v2.5.0 用户体验优化（2025-01-17）
- Toast 通知替代 alert 弹窗
- URL 安全字符验证
- 智能数据库初始化

### v2.4.0 增强日志系统（2025-09-30）
- 三级日志文件（all/error/debug）
- DEBUG 模式详细诊断
- 自动日志轮转

### v2.2.0 版本管理系统（2025-09-30）
- 全局版本号统一管理
- 健康检查接口显示版本
- 登录页版本展示

### v2.1.0 Token 权限管理增强（2025-09-30）
- 可视化权限配置弹窗
- 批量授权（全选/取消全选）
- 一键生成 MCP 配置

### v2.0.0 核心功能发布（2025-09-29）
- 9 款预置产品模拟器
- AI 智能响应生成
- Web 管理后台

---

## 🎯 核心应用场景

### 场景一：AI SOC 开发测试

在没有真实安全产品的情况下，模拟：
- VirusTotal 威胁情报查询
- 青藤云 HIDS 主机检测
- 深信服防火墙封禁 IP

```
1. 威胁检测（VirusTotal）
   ↓
2. 主机排查（青藤HIDS）
   ↓
3. 防火墙封禁（深信服）
   ↓
4. 工单记录（Jira）
```

### 场景二：SOAR 剧本编排验证

测试复杂的安全编排剧本，验证多产品联动：
- 无需购买真实产品
- 无需复杂部署
- 5 分钟搭建完整测试环境

### 场景三：MCP 协议学习

通过 Playground 直观了解：
- MCP 协议的工作方式
- Function Calling 的调用过程
- 工具参数和返回值格式

---

## 🛠️ 技术架构

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │◄──►│   UniMCPSim      │◄──►│   OpenAI API    │
│                 │    │                  │    │                 │
│ - Cherry Studio │    │ - MCP Server     │    │ - GPT-4o-mini   │
│ - Claude Code   │    │ - Web Admin      │    │ - 通义千问      │
│ - Playground    │    │ - Playground     │    │ - DeepSeek      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

**技术栈**：
- 后端：FastMCP + Flask + SQLAlchemy
- 前端：原生 JS + Monaco Editor
- AI：兼容 OpenAI API 的任意大模型
- 部署：Docker 一键部署

---

## 🚀 快速开始

### 方式一：Docker 部署（推荐）

```bash
docker pull wuzhi/unimcpsim:latest
docker run -d -p 9090:9090 -p 9091:9091 wuzhi/unimcpsim
```

### 方式二：源码运行

```bash
git clone https://github.com/wzfukui/UniMCPSim.git
cd UniMCPSim
pip install -r requirements.txt
python start_servers.py
```

访问：http://localhost:9091/admin/
默认账号：admin / admin123

---

## 💡 为什么选择 UniMCPSim？

| 特性 | UniMCPSim | 传统方式 |
|------|-----------|----------|
| 部署复杂度 | Docker 一键部署 | 需要采购/部署真实产品 |
| 测试成本 | 零成本 | 高昂的产品授权费 |
| 产品覆盖 | 无限扩展 | 受限于已有产品 |
| AI 响应 | 智能生成逼真数据 | 真实但有限的测试数据 |
| MCP 兼容 | 完整协议支持 | 需要各厂商单独适配 |

---

## 🔮 未来规划

- 更多预置产品模拟器（云安全、EDR、NDR 等）
- Playground 历史对话保存
- 多用户协作支持
- API 性能压测模式

---

## 📢 获取项目

**GitHub 开源地址**：
https://github.com/wzfukui/UniMCPSim

欢迎 Star ⭐ 和 Fork！

---

**雾帜智能** - 让安全更智能，让 AI 更安全

关注我们，获取更多 AI 安全和 MCP 生态的最新动态！

---

*如果您有兴趣了解更多雾帜智能的产品和服务，欢迎点击「阅读原文」*
