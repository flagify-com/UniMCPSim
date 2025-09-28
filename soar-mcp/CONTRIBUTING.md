# 贡献指南

欢迎为 SOAR MCP Server 项目贡献代码！

## 开发环境设置

### 1. Fork 项目

在 GitHub 上 fork 此仓库到你的账号下。

### 2. 克隆代码

```bash
git clone https://github.com/flagify-com/soar-mcp.git
cd soar-mcp
```

### 3. 设置开发环境

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖（如果有）
pip install -r requirements-dev.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的配置
```

## 开发流程

### 1. 创建功能分支

```bash
git checkout -b feature/your-feature-name
```

### 2. 进行开发

- 遵循现有的代码风格
- 添加必要的测试
- 更新相关文档

### 3. 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行 MCP 客户端测试
cd tests
python mcp_soar_client.py
```

### 4. 提交代码

```bash
git add .
git commit -m "feat: 添加新功能描述"
git push origin feature/your-feature-name
```

### 5. 创建 Pull Request

1. 访问 GitHub 上的原始仓库
2. 点击 "New Pull Request"
3. 选择你的分支
4. 填写详细的 PR 描述

## 代码规范

### Python 代码风格

- 遵循 PEP 8 标准
- 使用 4 个空格缩进
- 行长度限制为 88 字符
- 使用有意义的变量和函数名

### 提交信息格式

使用约定式提交（Conventional Commits）格式：

```
<类型>[可选的作用域]: <描述>

[可选的正文]

[可选的脚注]
```

类型包括：
- `feat`: 新功能
- `fix`: 修复问题
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构代码
- `test`: 添加或修改测试
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat: 添加剧本执行状态监控功能

- 实现剧本执行状态的实时查询
- 添加状态变更通知机制
- 优化执行日志存储格式

Closes #123
```

## 测试

### 运行测试

```bash
# 运行所有测试
python -m pytest

# 运行特定测试文件
python -m pytest tests/test_specific.py

# 运行并生成覆盖率报告
python -m pytest --cov=.
```

### 编写测试

- 为新功能编写单元测试
- 确保测试覆盖率不低于 80%
- 使用有意义的测试名称

## 文档

### 更新文档

如果你的更改涉及：
- API 接口变更
- 配置选项变更
- 新增功能

请相应更新：
- `README.md`
- API 文档
- 配置示例

### 文档风格

- 使用清晰简洁的语言
- 提供代码示例
- 保持中英文一致性

## 问题报告

### 报告 Bug

使用 [GitHub Issues](https://github.com/flagify-com/soar-mcp/issues) 报告问题，请包含：

1. **问题描述**：清晰描述遇到的问题
2. **复现步骤**：详细的复现步骤
3. **预期行为**：期望的正确行为
4. **实际行为**：实际发生的情况
5. **环境信息**：
   - 操作系统版本
   - Python 版本
   - 相关依赖版本
6. **日志信息**：相关的错误日志
7. **截图**：如果有界面问题，提供截图

### 功能请求

提交功能请求时，请包含：

1. **功能描述**：详细描述期望的功能
2. **使用场景**：说明这个功能的应用场景
3. **实现建议**：如果有实现想法，可以分享
4. **优先级**：说明这个功能的重要程度

## 代码审查

### 审查清单

提交 PR 前请确保：

- [ ] 代码遵循项目的编码规范
- [ ] 添加了必要的测试
- [ ] 测试全部通过
- [ ] 更新了相关文档
- [ ] 提交信息格式正确
- [ ] 没有引入破坏性变更（或在 PR 中明确说明）

### 审查过程

1. 自动化测试通过
2. 至少一个维护者审查代码
3. 解决所有审查意见
4. 合并到主分支

## 社区

### 交流渠道

- GitHub Issues：问题报告和功能请求
- GitHub Discussions：技术讨论和交流
- 邮件：code@wuzhi-ai.com

### 行为准则

我们致力于为所有参与者创造一个开放、友好、多元化和包容的环境。请遵循以下原则：

- 使用友好和包容的语言
- 尊重不同的观点和经验
- 接受建设性批评
- 专注于对社区最有利的事情
- 对其他社区成员表现出同理心

## 许可证

通过贡献代码，你同意你的贡献将在 MIT 许可证下授权。

## 致谢

感谢所有为项目做出贡献的开发者！你们的贡献让 SOAR MCP Server 变得更好。