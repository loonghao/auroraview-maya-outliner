# AuroraView API Update Changelog

## 概述

本次更新将 `maya_outliner.py` 迁移到最新的 AuroraView API（2025版本）。

## 主要变化

### 1. WebView 创建方式

#### 之前（旧 API）
```python
self.webview = WebView(
    title="Maya Outliner",
    width=400,
    height=800,
    url=url,
    dev_tools=True,
    parent_hwnd=maya_hwnd,
    parent_mode="owner",
)
```

#### 现在（新 API）
```python
self.webview = WebView.create(
    title="Maya Outliner",
    url=url,
    width=400,
    height=800,
    parent=maya_hwnd,
    mode="auto",  # 自动选择 owner 模式
    debug=True,  # 替代 dev_tools
    auto_show=False,
    auto_timer=True,  # 自动启动 EventTimer
)
```

### 2. 参数名称变化

| 旧参数名 | 新参数名 | 说明 |
|---------|---------|------|
| `dev_tools` | `debug` | 开发者工具开关 |
| `decorations` | `frame` | 窗口边框 |
| `parent_hwnd` | `parent` | 父窗口句柄 |
| `parent_mode` | `mode` | 嵌入模式 |

### 3. EventTimer 自动管理

#### 之前（手动管理）
```python
# 手动创建和启动 EventTimer
self._event_timer = EventTimer(self.webview, interval_ms=16)
self._event_timer.start()

# 手动停止
self._event_timer.cleanup()
```

#### 现在（自动管理）
```python
# WebView.create() 自动创建和启动 EventTimer（当 auto_timer=True）
self.webview = WebView.create(..., auto_timer=True)

# 获取 EventTimer（如果需要）
timer = self._get_event_timer()

# WebView.close() 自动停止 EventTimer
self.webview.close()
```

### 4. 后端选择简化

#### 之前
```python
# 全局变量控制后端
USE_QT_BACKEND = True

# 复杂的后端检测和切换逻辑
if USE_QT_BACKEND:
    # Qt backend
else:
    # Native backend
```

#### 现在
```python
# 实例级别控制
def __init__(self, use_qt: bool = False):
    self._use_qt = use_qt

# 简化的后端选择
if self._use_qt:
    self.webview = QtWebView(...)
else:
    self.webview = WebView.create(...)
```

### 5. 清理逻辑简化

#### 之前
```python
def close(self):
    # 1. 停止 EventTimer
    self._stop_event_processing()
    # 2. 移除回调
    self.cleanup_callbacks()
    # 3. 关闭 WebView
    self.webview.close()
    # 4. 强制关闭（如果需要）
    # ... 复杂的 HWND 操作
```

#### 现在
```python
def close(self):
    # 1. 移除回调
    self.cleanup_callbacks()
    # 2. 关闭 WebView（自动停止 EventTimer）
    self.webview.close()
    # 简化！新 API 自动处理清理
```

## 新功能

### 1. Qt 后端选择
```python
# 使用 Native 后端（默认）
outliner = maya_outliner.main()

# 使用 Qt 后端
outliner = maya_outliner.main(use_qt=True)
```

### 2. 自动模式检测
```python
# mode="auto" 自动检测：
# - 有 parent → 使用 "owner" 模式（嵌入）
# - 无 parent → 使用独立模式
self.webview = WebView.create(..., mode="auto")
```

### 3. 改进的调试输出
```python
# 使用 ✓ ✗ ⚠ 符号提高可读性
print("[MayaOutliner] ✓ WebView created")
print("[MayaOutliner] ✗ Failed to import")
print("[MayaOutliner] ⚠ Warning message")
```

## 移除的代码

### 移除的方法
- `_start_event_processing()` - 由 `auto_timer=True` 替代
- `_stop_event_processing()` - 由 `WebView.close()` 自动处理

### 移除的全局变量
- `USE_QT_BACKEND` - 改为实例变量 `self._use_qt`

### 移除的实例变量
- `self._is_embedded` - 不再需要
- `self._event_timer` - 由 WebView 内部管理

## 兼容性

### 向后兼容
- `main()` 函数签名保持兼容，新增可选参数 `use_qt`
- 现有调用方式仍然有效：`maya_outliner.main()`

### 破坏性变化
- 无破坏性变化，所有现有功能保持不变

## 测试

运行测试脚本验证更新：
```python
# 在 Maya 中运行
import sys
sys.path.insert(0, r"C:\github\auroraview-maya-outliner")
exec(open(r"C:\github\auroraview-maya-outliner\test_api_update.py").read())
```

## 参考

- AuroraView 源码：`C:\Users\hallo\Documents\augment-projects\dcc_webview\python\auroraview\`
- WebView API：`webview.py`
- EventTimer API：`event_timer.py`
- Qt 集成：`qt_integration.py`

