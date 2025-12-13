# UniMCPSim 测试套件

本目录包含UniMCPSim项目的完整回归测试套件，用于确保产品迭代过程中的质量稳定性。

## 测试结构

```
tests/
├── test_admin_frontend.py    # 前端管理界面测试
├── test_ai_backend.py         # 后端AI功能测试
├── test_mcp_client.py         # MCP客户端测试
├── run_all_tests.py           # 运行所有测试的脚本
└── README.md                  # 本文档
```

## 测试分类

### 1. 前端管理界面测试 (`test_admin_frontend.py`)

测试Admin Web界面的核心功能：

- **登录功能测试**
  - 正确用户名密码登录
  - 错误密码登录拒绝

- **密码修改测试**
  - 修改密码为 `admin456`
  - 使用新密码登录验证
  - 恢复密码为 `admin123`
  - 验证恢复后的密码

- **应用管理测试**
  - 创建测试应用
  - 获取应用列表验证
  - 更新应用信息
  - 验证更新结果
  - 删除应用
  - 验证删除结果

- **Token管理测试**
  - 创建测试Token
  - 设置Token应用权限
  - 验证Token权限
  - 删除Token
  - 清理测试数据

### 2. 后端AI功能测试 (`test_ai_backend.py`)

测试后端AI生成功能：

- **AI动作生成测试**
  - 使用提示词模板生成防火墙管理动作
  - 验证返回的JSON格式
  - 检查动作结构完整性

- **AI响应模拟测试**
  - 生成威胁情报查询响应
  - 生成企业微信消息发送响应
  - 验证响应格式和字段

- **配置重载测试**
  - 测试AI配置重载功能
  - 验证配置变更生效

- **默认响应测试**
  - 测试AI未启用时的默认响应生成
  - 验证回退机制

### 3. MCP客户端测试 (`test_mcp_client.py`)

测试MCP协议交互（StreamableHTTP模式）：

- **List Tools测试**
  - 获取可用工具列表
  - 验证工具数量和格式
  - 使用正确的应用路径（如 `/ThreatIntelligence/Threatbook`）

- **直接调用工具测试**
  - 测试在已知工具名称的情况下直接调用
  - 验证SSE格式响应
  - 处理权限错误

- **完整MCP流程测试**（精简版）
  - 只测试一个应用（ThreatBook）验证系统核心功能
  - 测试完整流程：`tools/list` → 选择工具 → `tools/call`
  - 一个应用测试通过即证明系统功能正常

- **Resources List测试（可选功能）**
  - 尝试获取资源列表
  - 如果未实现，标记为警告而非失败

## 使用方法

### 前置条件

1. **启动服务器**（必须）
   ```bash
   # 方式1: 使用启动脚本
   ./start_servers.sh

   # 方式2: 直接启动
   python start_servers.py
   ```

2. **确保服务运行正常**
   - MCP Server: http://localhost:9090
   - Admin Server: http://localhost:9091

3. **环境配置**（可选）
   - 如需测试AI功能，请配置 `.env` 文件或通过Web界面配置大模型
   - 确保数据库中存在可用的Token

### 运行测试

#### 方式1: 运行所有测试（推荐）

```bash
cd tests
python run_all_tests.py
```

这将按顺序运行所有测试套件，并在最后显示总结报告。

#### 方式2: 运行单个测试

```bash
# 前端测试
python tests/test_admin_frontend.py

# 后端AI测试
python tests/test_ai_backend.py

# MCP客户端测试
python tests/test_mcp_client.py
```

### 测试输出示例

```
############################################################
# UniMCPSim 回归测试套件
############################################################

============================================================
检查服务器状态
============================================================

检查MCP服务器 (http://localhost:9090)...
✅ MCP服务器运行正常

检查Admin服务器 (http://localhost:9091)...
✅ Admin服务器运行正常

✅ 服务器检查通过，开始测试...

============================================================
运行测试: 前端管理界面测试
============================================================

测试1: 登录功能
1.1 测试正确的用户名密码登录...
✅ 登录成功

[... 更多测试输出 ...]

============================================================
测试总结
============================================================
总测试数: 15
✅ 通过: 15
❌ 失败: 0

🎉 所有测试通过!
```

## 测试策略

### 高效测试原则

本测试套件采用**精简高效**的策略：

1. **前端测试**: 覆盖所有核心CRUD操作
   - 登录/密码管理
   - 应用管理（创建、更新、删除）
   - Token管理（创建、权限、删除）

2. **后端AI测试**: 验证AI集成功能
   - AI动作生成
   - AI响应模拟
   - 配置管理

3. **MCP客户端测试**: 只测试一个应用即可
   - ✅ **高效策略**: 测试一个应用（ThreatBook）证明系统功能
   - ❌ **避免**: 重复测试所有应用，浪费时间
   - 💡 **原理**: 一个成功 = 系统架构正常 = 其他应用也能正常工作

### 为什么只测试一个应用？

MCP测试的核心是验证：
- MCP协议实现是否正确
- SSE响应格式是否正确
- Token权限验证是否正常
- AI响应生成是否正常

这些都是**系统级功能**，不是应用特定的。因此：
- ✅ 一个应用测试通过 → 证明系统核心功能OK
- ❌ 测试所有10个应用 → 浪费时间，没有额外价值

## 重要说明

### 数据库中的实际应用名称

测试使用的应用路径必须与数据库中的实际名称匹配：

| 测试中使用 | 数据库实际名称 | 说明 |
|----------|-------------|-----|
| `/ThreatIntelligence/Threatbook` | ✅ 正确 | 注意是小写b |
| `/IM/WeWork` | ✅ 正确 | 企业微信 |
| `/Ticket/Jira` | ✅ 正确 | Jira工单系统 |
| `/Firewall/USGFirewall` | ✅ 正确 | 华为USG防火墙 |
| `/HIDS/QingTengYun-HIDS` | ✅ 正确 | 青藤云HIDS |
| `/Network/HuaweiSwitch` | ✅ 正确 | 华为交换机 |

**查看数据库中所有应用**:
```bash
sqlite3 data/unimcp.db "SELECT category, name, display_name FROM applications;"
```

### MCP StreamableHTTP 模式

**响应格式**: Server-Sent Events (SSE)
```
Content-Type: text/event-stream

event: message
data: {"jsonrpc": "2.0", "id": 1, "result": {...}}
```

**正确的测试流程**:
1. 先调用 `tools/list` 获取可用工具
2. 从返回的工具列表中找到实际的action名称
3. 使用实际名称调用 `tools/call`

## 测试注意事项

### 1. 服务器状态

- 测试前必须确保服务器已启动
- 如果服务器崩溃，测试会立即失败并提示

### 2. Token权限

- MCP测试需要数据库中存在启用的Token
- 如果Token没有相应应用权限，会显示权限警告但不影响测试通过
- 建议使用Admin界面创建一个拥有所有权限的测试Token

### 3. AI功能测试

- AI测试需要配置OpenAI API或兼容的API
- 如果未配置AI，相关测试会跳过而不是失败
- 配置方法：
  - Web界面: http://localhost:9091/admin/llm-config
  - 环境变量: `.env` 文件中设置 `OPENAI_API_KEY`

### 4. 数据库状态

- 测试会创建和删除临时数据（如测试应用、测试Token）
- 所有测试都会清理创建的测试数据
- 不会影响现有的生产数据

### 5. 密码重置

- 前端测试会临时修改admin密码，但最后会恢复为 `admin123`
- 如果测试中断，可能需要手动重置密码：
  ```bash
  python reset_admin_password.py
  ```

## 回归测试流程

### 定期回归测试

建议在以下情况下运行完整的回归测试：

1. **代码提交前**
   ```bash
   python tests/run_all_tests.py
   ```

2. **发布新版本前**
   ```bash
   # 确保服务器运行在默认端口
   ./start_servers.sh

   # 运行完整测试
   python tests/run_all_tests.py
   ```

3. **重大功能更新后**
   - 运行完整测试套件
   - 检查所有测试通过
   - 如有失败，分析原因并修复

### 快速验证测试

如果只需要快速验证核心功能：

```bash
# 只测试MCP功能
python tests/test_mcp_client.py

# 只测试前端功能
python tests/test_admin_frontend.py
```

## 故障排查

### 测试失败的常见原因

1. **服务器未启动**
   ```
   ❌ 无法连接到MCP服务器
   ```
   **解决方案**: 运行 `./start_servers.sh` 或 `python start_servers.py`

2. **端口被占用**
   ```
   Address already in use
   ```
   **解决方案**:
   ```bash
   # 查找占用端口的进程
   lsof -i :9090
   lsof -i :9091

   # 杀死进程
   kill -9 <PID>
   ```

3. **Token不存在**
   ```
   ❌ 未找到可用Token
   ```
   **解决方案**:
   - 访问 http://localhost:9091/admin/
   - 登录后创建Token
   - 为Token分配应用权限

4. **数据库锁定**
   ```
   database is locked
   ```
   **解决方案**:
   - 确保没有多个服务器实例运行
   - 重启服务器

5. **AI测试失败**
   ```
   ❌ AI generation failed
   ```
   **解决方案**:
   - 检查API Key配置
   - 访问 http://localhost:9091/admin/llm-config 配置
   - 或在 `.env` 中设置 `OPENAI_API_KEY`

## 测试扩展

### 添加新测试

1. **创建测试文件**
   ```python
   #!/usr/bin/env python3
   """
   新功能测试
   """
   import sys
   import os

   sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

   class MyTester:
       def __init__(self):
           self.passed_tests = 0
           self.failed_tests = 0

       def test_my_feature(self):
           # 测试逻辑
           pass

       def run_all_tests(self):
           self.test_my_feature()
           # 打印总结
           return self.failed_tests == 0

   def main():
       tester = MyTester()
       success = tester.run_all_tests()
       return 0 if success else 1

   if __name__ == "__main__":
       sys.exit(main())
   ```

2. **添加到测试套件**

   编辑 `run_all_tests.py`，在 `tests` 列表中添加：
   ```python
   tests = [
       ("test_admin_frontend.py", "前端管理界面测试"),
       ("test_ai_backend.py", "后端AI功能测试"),
       ("test_mcp_client.py", "MCP客户端测试"),
       ("test_my_new_feature.py", "新功能测试"),  # 新增
   ]
   ```

## 测试覆盖

当前测试覆盖的功能模块：

- ✅ Admin登录认证
- ✅ 密码修改
- ✅ 应用CRUD操作
- ✅ Token管理
- ✅ Token权限设置
- ✅ AI动作生成
- ✅ AI响应模拟
- ✅ MCP协议交互
- ✅ 多产品模拟
- ✅ 配置重载

未来可能添加的测试：

- ⏳ 提示词模板管理
- ⏳ 大模型配置管理
- ⏳ 审计日志查询
- ⏳ 并发请求测试
- ⏳ 性能基准测试

## 联系与反馈

如有测试相关问题，请：

1. 检查本文档的故障排查部分
2. 查看服务器日志
3. 提交Issue到项目仓库

---

**最后更新**: 2025-12-13
**测试套件版本**: v1.1.0
