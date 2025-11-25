# AuroraView Maya Outliner - Deployment Guide

[English](#english) | [中文](#中文)

---

## English

### Overview

AuroraView Maya Outliner supports two deployment modes:

1. **Development Mode** - Uses Vite dev server with hot-reload (default)
2. **Production Mode** - Uses pre-built static files from `dist/` directory

The mode is controlled by the `AURORAVIEW_ENV` environment variable.

### Environment Configuration

#### Development Mode (Default)

```bash
# Option 1: Don't set AURORAVIEW_ENV (defaults to development)
# Option 2: Explicitly set to development
set AURORAVIEW_ENV=development
# or
set AURORAVIEW_ENV=dev
```

**Requirements:**
- Vite dev server must be running: `npm run dev`
- Frontend accessible at `http://localhost:5173`

**Advantages:**
- ✅ Hot-reload for instant updates
- ✅ Better debugging with source maps
- ✅ Faster iteration during development

#### Production Mode

```bash
# Set environment variable to production
set AURORAVIEW_ENV=production
# or
set AURORAVIEW_ENV=prod
```

**Requirements:**
- Build static files first: `npm run build`
- Files will be in `dist/` directory

**Advantages:**
- ✅ No need to run dev server
- ✅ Faster load times
- ✅ Self-contained deployment
- ✅ Better for distribution

### Quick Start

#### 1. Development Workflow

```bash
# Terminal 1: Start Vite dev server
npm run dev

# Terminal 2: Launch Maya
# In Maya Script Editor (Python):
from maya_integration import main
main()  # Auto-detects development mode
```

#### 2. Production Workflow

```bash
# Step 1: Build frontend
npm run build

# Step 2: Set environment variable
set AURORAVIEW_ENV=production

# Step 3: Launch Maya
# In Maya Script Editor (Python):
from maya_integration import main
main()  # Auto-detects production mode
```

### Advanced Usage

#### Force Specific Mode

```python
from maya_integration import MayaOutliner

# Force production mode (use static files)
outliner = MayaOutliner()
outliner.run(use_local=True)

# Force development mode (use dev server)
import os
os.environ['AURORAVIEW_ENV'] = 'development'
outliner = MayaOutliner()
outliner.run()

# Use custom URL
outliner = MayaOutliner()
outliner.run(url="http://localhost:8080")
```

#### Check Current Configuration

```python
from maya_integration.config import get_environment_info

info = get_environment_info()
print(f"Environment: {info['env_value']}")
print(f"Mode: {'Production' if info['is_production'] else 'Development'}")
print(f"URL: {info['current_url']}")
print(f"Dist exists: {info['dist_exists']}")
```

### Quick Launch Scripts

For convenience, we provide launch scripts for both modes:

#### Windows Batch Scripts

```bash
# Launch in production mode
launch_production.bat

# Launch in development mode
launch_development.bat
```

#### PowerShell Scripts

```powershell
# Launch in production mode
.\launch_production.ps1

# Launch in development mode
.\launch_development.ps1
```

These scripts will:
- Set the appropriate environment variable
- Check if required files/server are available
- Launch Maya with the correct configuration

### Troubleshooting

#### Error: "Production mode requested but dist files not found"

**Solution:**
```bash
npm run build
```

#### Dev server not accessible

**Solution:**
```bash
# Make sure dev server is running
npm run dev

# Check if port 5173 is available
netstat -ano | findstr :5173
```

---

## 中文

### 概述

AuroraView Maya Outliner 支持两种部署模式:

1. **开发模式** - 使用 Vite 开发服务器,支持热重载(默认)
2. **生产模式** - 使用 `dist/` 目录中的预构建静态文件

模式通过 `AURORAVIEW_ENV` 环境变量控制。

### 环境配置

#### 开发模式(默认)

```bash
# 方式1: 不设置 AURORAVIEW_ENV (默认为开发模式)
# 方式2: 显式设置为开发模式
set AURORAVIEW_ENV=development
# 或
set AURORAVIEW_ENV=dev
```

**要求:**
- Vite 开发服务器必须运行: `npm run dev`
- 前端可通过 `http://localhost:5173` 访问

**优势:**
- ✅ 热重载,即时更新
- ✅ 更好的调试体验(source maps)
- ✅ 开发时迭代更快

#### 生产模式

```bash
# 设置环境变量为生产模式
set AURORAVIEW_ENV=production
# 或
set AURORAVIEW_ENV=prod
```

**要求:**
- 先构建静态文件: `npm run build`
- 文件将在 `dist/` 目录中

**优势:**
- ✅ 无需运行开发服务器
- ✅ 加载速度更快
- ✅ 自包含部署
- ✅ 更适合分发

### 快速开始

#### 1. 开发工作流

```bash
# 终端1: 启动 Vite 开发服务器
npm run dev

# 终端2: 启动 Maya
# 在 Maya 脚本编辑器(Python)中:
from maya_integration import main
main()  # 自动检测开发模式
```

#### 2. 生产工作流

```bash
# 步骤1: 构建前端
npm run build

# 步骤2: 设置环境变量
set AURORAVIEW_ENV=production

# 步骤3: 启动 Maya
# 在 Maya 脚本编辑器(Python)中:
from maya_integration import main
main()  # 自动检测生产模式
```

### 高级用法

#### 强制指定模式

```python
from maya_integration import MayaOutliner

# 强制生产模式(使用静态文件)
outliner = MayaOutliner()
outliner.run(use_local=True)

# 强制开发模式(使用开发服务器)
import os
os.environ['AURORAVIEW_ENV'] = 'development'
outliner = MayaOutliner()
outliner.run()

# 使用自定义 URL
outliner = MayaOutliner()
outliner.run(url="http://localhost:8080")
```

#### 检查当前配置

```python
from maya_integration.config import get_environment_info

info = get_environment_info()
print(f"环境: {info['env_value']}")
print(f"模式: {'生产' if info['is_production'] else '开发'}")
print(f"URL: {info['current_url']}")
print(f"Dist 存在: {info['dist_exists']}")
```

### 快速启动脚本

为了方便使用,我们提供了两种模式的启动脚本:

#### Windows 批处理脚本

```bash
# 以生产模式启动
launch_production.bat

# 以开发模式启动
launch_development.bat
```

#### PowerShell 脚本

```powershell
# 以生产模式启动
.\launch_production.ps1

# 以开发模式启动
.\launch_development.ps1
```

这些脚本会:
- 设置适当的环境变量
- 检查所需文件/服务器是否可用
- 使用正确的配置启动 Maya

### 故障排除

#### 错误: "Production mode requested but dist files not found"

**解决方案:**
```bash
npm run build
```

#### 开发服务器无法访问

**解决方案:**
```bash
# 确保开发服务器正在运行
npm run dev

# 检查端口 5173 是否可用
netstat -ano | findstr :5173
```

