# Installation Guide

[English](#english) | [中文](#中文)

---

## English

### Quick Installation (Recommended)

#### For End Users

1. **Download the latest release**
   - Go to [Releases](https://github.com/loonghao/auroraview-maya-outliner/releases)
   - Download `maya-outliner-{version}.zip`

2. **Extract the archive**
   - Extract to any location (e.g., `C:\maya-tools\maya-outliner`)

3. **Run the installer**
   
   **Windows (Batch):**
   ```bash
   install.bat
   ```
   
   **Windows (PowerShell):**
   ```powershell
   .\install.ps1
   ```
   
   **Linux/macOS:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

4. **Restart Maya**

5. **Launch the Outliner**
   
   In Maya Script Editor (Python):
   ```python
   from maya_integration import main
   main()
   ```

### Development Installation

#### For Developers

1. **Clone the repository**
   ```bash
   git clone https://github.com/loonghao/auroraview-maya-outliner.git
   cd auroraview-maya-outliner
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Build the frontend**
   ```bash
   npm run build
   ```

4. **Run the installer**
   
   **Windows:**
   ```bash
   install.bat
   ```
   
   **Linux/macOS:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

5. **Restart Maya**

6. **For development with hot-reload**
   
   Terminal 1 - Start dev server:
   ```bash
   npm run dev
   ```
   
   Terminal 2 - Set environment and launch Maya:
   ```bash
   # Windows
   set AURORAVIEW_ENV=development
   
   # Linux/macOS
   export AURORAVIEW_ENV=development
   ```
   
   In Maya:
   ```python
   from maya_integration import main
   main()
   ```

### Manual Installation

If you prefer manual installation:

1. **Copy files to Maya modules directory**
   
   **Windows:**
   ```
   %USERPROFILE%\Documents\maya\modules\maya-outliner\
   ```
   
   **Linux/macOS:**
   ```
   ~/maya/modules/maya-outliner/
   ```

2. **Create module file**
   
   Create `maya-outliner.mod` in the modules directory:
   ```
   + maya-outliner 1.0.0 ./maya-outliner
   PYTHONPATH +:= maya_integration
   ```

3. **Restart Maya**

### Uninstallation

1. **Remove the module file**
   
   **Windows:**
   ```
   %USERPROFILE%\Documents\maya\modules\maya-outliner.mod
   ```
   
   **Linux/macOS:**
   ```
   ~/maya/modules/maya-outliner.mod
   ```

2. **Optionally remove the installation directory**

3. **Restart Maya**

### Troubleshooting

#### Module not found

- Make sure Maya modules directory exists
- Check that `.mod` file is in the correct location
- Verify PYTHONPATH in `.mod` file

#### Frontend not loading

- **Production mode**: Make sure `dist/index.html` exists (run `npm run build`)
- **Development mode**: Make sure Vite dev server is running (`npm run dev`)

#### Permission errors (Linux/macOS)

```bash
chmod +x install.sh
```

---

## 中文

### 快速安装(推荐)

#### 普通用户

1. **下载最新版本**
   - 访问 [Releases](https://github.com/loonghao/auroraview-maya-outliner/releases)
   - 下载 `maya-outliner-{version}.zip`

2. **解压文件**
   - 解压到任意位置(例如: `C:\maya-tools\maya-outliner`)

3. **运行安装程序**
   
   **Windows (批处理):**
   ```bash
   install.bat
   ```
   
   **Windows (PowerShell):**
   ```powershell
   .\install.ps1
   ```
   
   **Linux/macOS:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

4. **重启 Maya**

5. **启动 Outliner**
   
   在 Maya 脚本编辑器(Python)中:
   ```python
   from maya_integration import main
   main()
   ```

### 开发者安装

#### 开发者

1. **克隆仓库**
   ```bash
   git clone https://github.com/loonghao/auroraview-maya-outliner.git
   cd auroraview-maya-outliner
   ```

2. **安装依赖**
   ```bash
   npm install
   ```

3. **构建前端**
   ```bash
   npm run build
   ```

4. **运行安装程序**
   
   **Windows:**
   ```bash
   install.bat
   ```
   
   **Linux/macOS:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

5. **重启 Maya**

6. **开发模式(热重载)**
   
   终端1 - 启动开发服务器:
   ```bash
   npm run dev
   ```
   
   终端2 - 设置环境变量并启动 Maya:
   ```bash
   # Windows
   set AURORAVIEW_ENV=development
   
   # Linux/macOS
   export AURORAVIEW_ENV=development
   ```
   
   在 Maya 中:
   ```python
   from maya_integration import main
   main()
   ```

### 手动安装

如果你更喜欢手动安装:

1. **复制文件到 Maya 模块目录**
   
   **Windows:**
   ```
   %USERPROFILE%\Documents\maya\modules\maya-outliner\
   ```
   
   **Linux/macOS:**
   ```
   ~/maya/modules/maya-outliner/
   ```

2. **创建模块文件**
   
   在 modules 目录创建 `maya-outliner.mod`:
   ```
   + maya-outliner 1.0.0 ./maya-outliner
   PYTHONPATH +:= maya_integration
   ```

3. **重启 Maya**

### 卸载

1. **删除模块文件**
   
   **Windows:**
   ```
   %USERPROFILE%\Documents\maya\modules\maya-outliner.mod
   ```
   
   **Linux/macOS:**
   ```
   ~/maya/modules/maya-outliner.mod
   ```

2. **可选: 删除安装目录**

3. **重启 Maya**

### 故障排除

#### 找不到模块

- 确保 Maya modules 目录存在
- 检查 `.mod` 文件位置是否正确
- 验证 `.mod` 文件中的 PYTHONPATH

#### 前端无法加载

- **生产模式**: 确保 `dist/index.html` 存在(运行 `npm run build`)
- **开发模式**: 确保 Vite 开发服务器正在运行(`npm run dev`)

#### 权限错误 (Linux/macOS)

```bash
chmod +x install.sh
```

