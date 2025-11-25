# EventTimer Integration for Smooth Window Dragging

## 问题描述

在 Qt 窗口拖动或调整大小时，WebView 的渲染会出现卡顿或停止更新。这是因为：

1. **Qt 事件循环被阻塞**：在拖动窗口时，Qt 的主事件循环会被阻塞
2. **WebView 事件无法处理**：WebView 的 `process_events()` 无法被调用
3. **渲染停止**：WebView 的渲染引擎无法更新画面

## 解决方案：EventTimer

使用 AuroraView 的 `EventTimer` 来确保在窗口操作期间持续处理 WebView 事件。

### 工作原理

```
Qt 窗口拖动
    ↓
Qt 事件循环被阻塞
    ↓
EventTimer (Qt QTimer) 仍在运行
    ↓
定期调用 webview.process_events()
    ↓
WebView 保持响应
```

### 实现细节

#### 1. 初始化 EventTimer

```python
def _setup_event_timer(self):
    """Setup EventTimer for continuous WebView updates."""
    # Get the underlying WebView instance
    webview_core = getattr(self.webview, '_webview', None)
    
    # Create EventTimer with 16ms interval (60 FPS)
    self._event_timer = EventTimer(webview_core, interval_ms=16)
    
    # Start the timer (auto-selects Qt QTimer backend in Maya)
    self._event_timer.start()
```

#### 2. 在 show() 中启动

```python
def show(self, url=None, use_local=False):
    # ... 其他初始化代码 ...
    
    # Setup EventTimer for smooth window dragging
    self._setup_event_timer()
    
    # Show dialog
    self.dialog.show()
```

#### 3. 在 close() 中停止

```python
def close(self):
    # Stop EventTimer
    if self._event_timer is not None:
        self._event_timer.stop()
        self._event_timer = None
    
    # ... 其他清理代码 ...
```

## EventTimer 后端选择

EventTimer 会自动选择最佳后端（优先级顺序）：

1. **Qt QTimer** ✅ - 在 Maya 中使用，最精确
2. **Maya scriptJob** - Maya 特定
3. **Blender timer** - Blender 特定
4. **Thread-based** - 后备方案

在 Maya 中，EventTimer 会自动使用 Qt QTimer，确保：
- 高精度定时（16ms = 60 FPS）
- 与 Qt 事件循环集成
- 即使在窗口拖动时也能运行

## 效果对比

### 没有 EventTimer
```
拖动窗口 → Qt 事件循环阻塞 → WebView 停止渲染 → 画面卡住
```

### 有 EventTimer
```
拖动窗口 → Qt 事件循环阻塞 → EventTimer 继续运行 → WebView 保持流畅
```

## 测试方法

运行测试脚本：

```python
# 在 Maya Script Editor 中运行
import test_event_timer_integration
outliner = test_event_timer_integration.test_event_timer()

# 测试步骤：
# 1. 拖动窗口 - WebView 应该保持响应
# 2. 调整窗口大小 - 内容应该实时更新
# 3. 在拖动时创建/删除 Maya 对象 - Outliner 应该实时更新
```

## 性能影响

- **CPU 使用**：轻微增加（60 FPS 的定时器）
- **内存使用**：几乎无影响
- **用户体验**：显著提升（窗口操作流畅）

## 参考文档

- [AuroraView EventTimer 文档](https://github.com/longhao-li/auroraview/blob/main/docs/event_timer.md)
- [Timer Architecture](https://github.com/longhao-li/auroraview/blob/main/docs/TIMER_ARCHITECTURE.md)

