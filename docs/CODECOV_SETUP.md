# Codecov 集成设置指南

本文档说明如何为 AuroraView 项目配置 Codecov 代码覆盖率报告。

## 📋 前置要求

1. GitHub 仓库已启用
2. 拥有仓库的管理员权限
3. Codecov 账号（使用 GitHub 登录）

## 🔧 设置步骤

### 1. 在 Codecov 上启用仓库

1. 访问 [Codecov](https://codecov.io/)
2. 使用 GitHub 账号登录
3. 点击 "Add new repository"
4. 找到 `loonghao/auroraview` 并启用

### 2. 获取 Codecov Token

1. 在 Codecov 仓库页面，点击 "Settings"
2. 复制 "Repository Upload Token"

### 3. 配置 GitHub Secrets

1. 访问 GitHub 仓库设置：`https://github.com/loonghao/auroraview/settings/secrets/actions`
2. 点击 "New repository secret"
3. 添加以下 secret：
   - **Name**: `CODECOV_TOKEN`
   - **Value**: 粘贴从 Codecov 复制的 token

### 4. 验证配置

1. 创建一个 PR 或推送到 main 分支
2. 等待 CI 完成
3. 检查 Codecov 仓库页面是否显示覆盖率数据

## 📊 覆盖率报告

### 自动上传的覆盖率类型

我们的 CI 配置会自动上传以下覆盖率数据：

1. **Python 单元测试覆盖率**
   - 文件：`coverage.xml`
   - Flags：`python`, `unit`, `py{version}`, `{os}`
   - 触发：所有 Python 测试

2. **Rust 代码覆盖率**
   - 文件：`lcov.info`
   - Flags：`rust`
   - 触发：Rust 测试（使用 cargo-llvm-cov）

3. **Qt 集成测试覆盖率**
   - 文件：`coverage.xml`
   - Flags：`python`, `qt`, `windows`
   - 触发：Qt 测试（Windows）

### 覆盖率目标

根据 `codecov.yml` 配置：

- **项目整体覆盖率目标**: 70%
- **新代码覆盖率目标**: 80%
- **允许下降阈值**: 2%

## 🎯 Codecov 功能

### 1. PR 评论

Codecov 会自动在 PR 中添加评论，显示：
- 覆盖率变化
- 受影响的文件
- 未覆盖的代码行

### 2. 覆盖率徽章

README 中的徽章会自动更新：

```markdown
[![Codecov](https://codecov.io/gh/loonghao/auroraview/branch/main/graph/badge.svg)](https://codecov.io/gh/loonghao/auroraview)
```

### 3. 组件覆盖率

我们配置了以下组件：
- **Python Core**: `python/auroraview/*.py`
- **Rust Core**: `src/**/*.rs`
- **Qt Integration**: `python/auroraview/qt_integration.py`

## 🔍 查看覆盖率报告

### 在 Codecov 网站上

1. 访问：`https://codecov.io/gh/loonghao/auroraview`
2. 查看：
   - 整体覆盖率趋势
   - 文件级别覆盖率
   - 未覆盖的代码行
   - 历史覆盖率变化

### 在本地

运行测试并生成覆盖率报告：

```bash
# Python 覆盖率
just ci-test-python
# 查看 HTML 报告
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux

# Rust 覆盖率
cargo llvm-cov --html
open target/llvm-cov/html/index.html
```

## 🛠️ 故障排除

### Token 无效

如果看到 "Invalid token" 错误：
1. 确认 GitHub Secret 名称为 `CODECOV_TOKEN`
2. 重新从 Codecov 复制 token
3. 更新 GitHub Secret

### 覆盖率未上传

检查 CI 日志：
1. 确认 `coverage.xml` 或 `lcov.info` 文件已生成
2. 检查 Codecov action 的输出
3. 确认网络连接正常

### 覆盖率数据不准确

1. 确保测试运行时启用了覆盖率收集
2. 检查 `.coveragerc` 或 `codecov.yml` 配置
3. 验证忽略路径配置正确

## 📚 相关文档

- [Codecov 官方文档](https://docs.codecov.com/)
- [codecov.yml 配置参考](https://docs.codecov.com/docs/codecov-yaml)
- [GitHub Actions 集成](https://docs.codecov.com/docs/github-actions)

## ✅ 检查清单

- [ ] Codecov 仓库已启用
- [ ] `CODECOV_TOKEN` secret 已配置
- [ ] CI 成功运行并上传覆盖率
- [ ] Codecov 网站显示覆盖率数据
- [ ] PR 中显示 Codecov 评论
- [ ] README 徽章正常显示

