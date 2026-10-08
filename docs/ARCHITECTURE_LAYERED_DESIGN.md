> Historical design note from the original example. For the maintained runtime, commands and acceptance status, see the [current tutorial](../README.md) and [validation record](VALIDATION.md).

# AuroraView 分层架构设计

## 🎯 设计目标

1. **清晰的职责分离** - 每一层只负责自己的事情
2. **避免重复修改** - 底层解决问题，上层自动受益
3. **易于扩展** - 新的集成（如 Tkinter、wxPython）容易添加

## 📐 四层架构

```
┌─────────────────────────────────────────────────────────────┐
│                    应用层 (Application)                      │
│              maya_outliner.py, houdini_tool.py              │
│  职责：业务逻辑、DCC 特定功能                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓ uses
┌─────────────────────────────────────────────────────────────┐
│                  集成层 (Integration)                        │
│              QtWebView, TkWebView, WxWebView                │
│  职责：UI 框架集成、框架特定的事件循环处理                     │
└─────────────────────────────────────────────────────────────┘
                            ↓ inherits
┌─────────────────────────────────────────────────────────────┐
│                Python 抽象层 (Abstraction)                   │
│                       WebView                               │
│  职责：Python API、事件处理策略、生命周期管理                  │
└─────────────────────────────────────────────────────────────┘
                            ↓ wraps
┌─────────────────────────────────────────────────────────────┐
│                  Rust 核心层 (Core)                          │
│                     AuroraView                              │
│  职责：WebView 渲染、消息队列、平台窗口管理                    │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 各层职责

### 1. Rust 核心层 (AuroraView)

**职责：**
- WebView 渲染引擎封装
- 消息队列管理（JavaScript ↔ Rust）
- 平台窗口管理（Win32/X11/Cocoa）
- IPC 通信

**不负责：**
- 不知道 Python 的存在
- 不知道 Qt/Tk 等 UI 框架
- 不自动处理事件（只提供 `process_events()` 方法）

**关键方法：**
```rust
impl AuroraView {
    fn emit(&self, event_name: &str, data: &str);
    fn eval_js(&self, script: &str);
    fn process_events(&self) -> bool;  // 处理消息队列
}
```

### 2. Python 抽象层 (WebView)

**职责：**
- 提供 Pythonic API
- 定义事件处理策略（通过 `_auto_process_events`）
- 管理生命周期（show/close/wait）
- 提供默认的事件处理实现

**关键设计：**
```python
class WebView:
    def __init__(self):
        self._core = AuroraView(...)  # Rust 核心
        self._event_processor = None  # 事件处理器（策略模式）
    
    def set_event_processor(self, processor):
        """设置事件处理器（策略模式）"""
        self._event_processor = processor
    
    def _auto_process_events(self):
        """自动处理事件（可被重写或使用策略）"""
        if self._event_processor:
            self._event_processor.process()
        else:
            # 默认实现：直接调用 Rust
            self._core.process_events()
    
    def emit(self, event_name, data, auto_process=True):
        """发送事件"""
        self._core.emit(event_name, data)
        if auto_process:
            self._auto_process_events()
    
    def eval_js(self, script, auto_process=True):
        """执行 JavaScript"""
        self._core.eval_js(script)
        if auto_process:
            self._auto_process_events()
```

### 3. 集成层 (QtWebView, TkWebView, etc.)

**职责：**
- UI 框架特定的集成
- 处理框架的事件循环
- 提供框架特定的 API

**QtWebView 实现：**
```python
class QtEventProcessor:
    """Qt 事件处理器（策略模式）"""
    def __init__(self, webview):
        self._webview = webview
    
    def process(self):
        """处理 Qt 事件 + WebView 事件"""
        from qtpy.QtCore import QCoreApplication
        QCoreApplication.processEvents()  # Qt 事件
        self._webview._core.process_events()  # WebView 事件

class QtWebView(QWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        
        # 创建 WebView
        self._webview = WebView(**kwargs)
        
        # 设置 Qt 事件处理器
        processor = QtEventProcessor(self._webview)
        self._webview.set_event_processor(processor)
    
    def emit(self, event_name, data, auto_process=True):
        """委托给 WebView"""
        self._webview.emit(event_name, data, auto_process)
```

### 4. 应用层 (maya_outliner.py)

**职责：**
- 业务逻辑
- DCC 特定功能
- 用户交互

**使用方式：**
```python
# 应用层只需要使用，不需要关心底层实现
webview = QtWebView(parent=maya_window)
webview.emit("scene_updated", {"nodes": [...]})
# ✅ 事件自动处理，无需手动调用 process_events()
```

## 🎁 优势

### 1. 职责清晰

| 层次 | 职责 | 不负责 |
|------|------|--------|
| Rust | 渲染、消息队列 | UI 框架、事件循环 |
| Python WebView | API、策略 | UI 框架特定逻辑 |
| Qt/Tk 集成 | 框架集成 | 业务逻辑 |
| 应用 | 业务逻辑 | 底层实现 |

### 2. 避免重复修改

```python
# ✅ 底层修改一次，所有集成自动受益
class WebView:
    def emit(self, event_name, data, auto_process=True):
        self._core.emit(event_name, data)
        if auto_process:
            self._auto_process_events()  # 所有子类自动调用

# QtWebView、TkWebView、WxWebView 都自动获得这个行为
```

### 3. 易于扩展

```python
# 添加新的 UI 框架集成非常简单
class TkEventProcessor:
    def process(self):
        self._root.update()  # Tk 事件
        self._webview._core.process_events()  # WebView 事件

class TkWebView(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self._webview = WebView(**kwargs)
        processor = TkEventProcessor(self._webview, parent)
        self._webview.set_event_processor(processor)
```

## 🔄 事件处理流程

```
应用层调用
    ↓
webview.emit("event", data)
    ↓
WebView.emit()
    ↓
self._core.emit()  ← Rust 层：推送到消息队列
    ↓
self._auto_process_events()
    ↓
self._event_processor.process()  ← 策略模式
    ↓
QtEventProcessor.process()
    ├─ QCoreApplication.processEvents()  ← Qt 事件
    └─ self._webview._core.process_events()  ← WebView 消息队列
        ↓
        Rust 层：处理消息队列，执行 JavaScript
```

## 📝 实现计划

### Phase 1: 重构 WebView 基类
- [ ] 添加 `set_event_processor()` 方法
- [ ] 重构 `_auto_process_events()` 使用策略模式
- [ ] 保持向后兼容（支持直接重写 `_auto_process_events()`）

### Phase 2: 重构 QtWebView
- [ ] 创建 `QtEventProcessor` 类
- [ ] 在 `__init__` 中设置处理器
- [ ] 简化 `_process_pending_events()`

### Phase 3: 文档和测试
- [ ] 更新架构文档
- [ ] 添加集成测试
- [ ] 创建新集成的示例（TkWebView）

## 🎯 最终目标

```python
# 应用层代码保持简单
webview = QtWebView(parent=maya_window)
webview.emit("scene_updated", data)  # ✅ 自动处理

# 添加新集成也很简单
class MyFrameworkWebView:
    def __init__(self):
        self._webview = WebView()
        processor = MyFrameworkEventProcessor(self._webview)
        self._webview.set_event_processor(processor)
```

**核心原则：** 底层解决问题，上层自动受益，避免重复修改。
