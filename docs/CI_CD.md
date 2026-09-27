# CI/CD 流程说明

本项目使用 GitHub Actions 和 release-please 实现自动化的版本管理和发布流程。

## 工作流程概览

```
开发 → PR → 测试 → 合并到 main → 自动创建 Release PR → 合并 Release PR → 自动发布
```

## 1. PR 检查 (pr-checks.yml)

当创建或更新 Pull Request 时自动触发，确保代码质量：

### 检查项目

1. **Frontend Build & Lint**
   - 安装 Node.js 依赖
   - 构建前端代码
   - 上传构建产物

2. **Package Build Test**
   - 构建前端
   - 运行 `build_maya_package.py` 创建安装包
   - 验证包结构

3. **Installation Files Verification**
   - 验证所有必需文件存在
   - 检查 `.mod` 文件的 PYTHONPATH 配置
   - 确保 `userSetup.py` 没有占位符

4. **PR Ready Gate**
   - 所有检查必须通过才能合并

### 触发条件

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]
```

## 2. 自动发布 (release.yml)

使用 release-please 实现自动化版本管理和发布。

### 工作流程

#### 步骤 1: 合并 PR 到 main

当 PR 合并到 main 分支时，release-please 会：

1. 分析 commit 历史（基于 Conventional Commits）
2. 自动创建一个 **Release PR**
3. Release PR 包含：
   - 更新的版本号（在 `package.json`）
   - 自动生成的 CHANGELOG.md
   - 所有相关文件的版本更新

#### 步骤 2: 合并 Release PR

当 Release PR 被合并时，自动触发：

1. **创建 Git Tag**
   - 格式: `v0.1.1`, `v0.2.0` 等

2. **构建 Maya 包**
   - 构建前端
   - 运行 `build_maya_package.py`
   - 创建 `maya-outliner-{version}.zip`

3. **创建 GitHub Release**
   - 上传安装包
   - 生成详细的 changelog
   - 包含安装说明

### 版本号规则

基于 Conventional Commits 自动确定版本号：

| Commit 类型 | 版本变化 | 示例 |
|------------|---------|------|
| `feat:` | Minor (0.x.0) | `feat: add new feature` → 0.1.0 → 0.2.0 |
| `fix:` | Patch (0.0.x) | `fix: bug fix` → 0.1.0 → 0.1.1 |
| `BREAKING CHANGE:` | Major (x.0.0) | `feat!: breaking change` → 0.1.0 → 1.0.0 |
| `docs:`, `chore:`, `ci:` | 不触发发布 | 仅更新 Release PR |

## 3. Commit 规范

必须遵循 Conventional Commits 规范：

```bash
<type>(<scope>): <subject>

<body>

<footer>
```

### 常用类型

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试相关
- `ci`: CI/CD 配置
- `chore`: 其他杂项

### 示例

```bash
# 新功能 (触发 minor 版本)
git commit -m "feat: add shelf button auto-creation"

# Bug 修复 (触发 patch 版本)
git commit -m "fix: correct PYTHONPATH in mod file"

# 破坏性变更 (触发 major 版本)
git commit -m "feat!: redesign plugin architecture

BREAKING CHANGE: Plugin API has been completely redesigned"

# 文档更新 (不触发版本)
git commit -m "docs: update installation guide"
```

## 4. 配置文件

### release-please-config.json

```json
{
  "release-type": "node",
  "include-v-in-tag": true,
  "packages": {
    ".": {
      "package-name": "maya-outliner",
      "extra-files": [
        {
          "type": "json",
          "path": "package.json",
          "jsonpath": "$.version"
        }
      ]
    }
  }
}
```

### .release-please-manifest.json

```json
{
  ".": "0.1.0"
}
```

记录当前版本，由 release-please 自动更新。

## 5. 发布流程示例

### 场景 1: 修复 Bug

```bash
# 1. 创建分支
git checkout -b fix/mod-file-path

# 2. 修复代码
# ... 修改文件 ...

# 3. 提交 (使用 fix: 前缀)
git commit -m "fix: correct PYTHONPATH in mod file

Signed-off-by: longhao <hal.long@outlook.com>"

# 4. 推送并创建 PR
git push -u origin fix/mod-file-path

# 5. PR 检查通过后合并到 main

# 6. release-please 自动创建 Release PR
#    标题: "chore(main): release 0.1.1"
#    内容: 更新 package.json 版本为 0.1.1

# 7. 合并 Release PR

# 8. 自动发布 v0.1.1 到 GitHub Releases
```

### 场景 2: 添加新功能

```bash
# 1. 创建分支
git checkout -b feat/auto-shelf-button

# 2. 开发新功能
# ... 添加代码 ...

# 3. 提交 (使用 feat: 前缀)
git commit -m "feat: add automatic shelf button creation

Signed-off-by: longhao <hal.long@outlook.com>"

# 4. 推送并创建 PR
git push -u origin feat/auto-shelf-button

# 5. PR 检查通过后合并到 main

# 6. release-please 自动创建 Release PR
#    标题: "chore(main): release 0.2.0"
#    内容: 更新 package.json 版本为 0.2.0

# 7. 合并 Release PR

# 8. 自动发布 v0.2.0 到 GitHub Releases
```

## 6. 手动触发发布

如果需要手动触发发布流程：

1. 进入 GitHub Actions
2. 选择 "Release" workflow
3. 点击 "Run workflow"
4. 选择 main 分支
5. 点击 "Run workflow"

## 7. 故障排查

### PR 检查失败

1. 查看失败的步骤
2. 本地运行相同的命令：
   ```bash
   npm run build
   python build_maya_package.py --version 0.1.0-test
   ```
3. 修复问题后重新推送

### Release 失败

1. 检查 GitHub Actions 日志
2. 确认 `build_maya_package.py` 可以正常运行
3. 确认前端构建成功
4. 检查版本号格式是否正确

### Release PR 未创建

1. 确认 commit 使用了正确的 Conventional Commits 格式
2. 检查是否有 `feat:` 或 `fix:` 类型的 commit
3. 查看 release-please action 日志

## 8. 最佳实践

1. **始终使用 Conventional Commits**
   - 确保 commit message 格式正确
   - 使用正确的类型前缀

2. **小步提交**
   - 每个 commit 只做一件事
   - 便于生成清晰的 changelog

3. **及时合并 Release PR**
   - Release PR 创建后尽快审查和合并
   - 避免积累过多未发布的更改

4. **测试 PR 检查**
   - 确保所有 PR 检查通过
   - 本地测试打包流程

5. **版本号管理**
   - 让 release-please 自动管理版本号
   - 不要手动修改 package.json 的版本号

## 9. 相关链接

- [release-please 文档](https://github.com/googleapis/release-please)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)

