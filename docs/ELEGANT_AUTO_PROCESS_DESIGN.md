# 优雅的自动事件处理设计

## 设计理念

在积极开发阶段，我们选择**最优雅的设计**而不是过度考虑向后兼容，避免积累技术债。

## 旧设计（Hook 模式）

### 问题

```python
# 旧设计：使用 _post_eval_js_hook
class WebView:
    def emit(self, event_name, data):
        core.emit(event_name, data)
        # 检查 hook 是否存在
        if hasattr(self, "_post_eval_js_hook") and callable(self._post_eval_js_hook):
            self._post_eval_js_hook()

class QtWebView:
    def __init__(self):
        # 手动安装 hook
        self._webview._post_eval_js_hook = self._process_pending_events
```

### 缺点

1. **不够明确**：`_post_eval_js_hook` 是动态设置的"私有"属性
2. **重复代码**：`emit()` 和 `eval_js()` 都需要检查 hook 是否存在
3. **不够优雅**：使用 `hasattr()` 和 `callable()` 检查
4. **难以扩展**：子类需要知道 hook 的存在

## 新设计（方法重写模式）

### 核心思想

使用**模板方法模式**：基类定义算法骨架，子类重写特定步骤。

```python
class WebView:
    def _auto_process_events(self):
        """自动处理事件（可被子类重写）"""
        try:
            self._core.process_events()
        except Exception as e:
            logger.debug(f"Auto process events failed: {e}")
    
    def emit(self, event_name, data, auto_process=True):
        """发送事件"""
        core.emit(event_name, data)
        
        # 自动处理事件
        if auto_process:
            self._auto_process_events()
    
    def eval_js(self, script, auto_process=True):
        """执行 JavaScript"""
        core.eval_js(script)
        
        # 自动处理事件
        if auto_process:
            self._auto_process_events()
```

```python
class QtWebView:
    def __init__(self):
        # 重写方法（而不是设置 hook）
        self._webview._auto_process_events = self._process_pending_events
    
    def _process_pending_events(self):
        """Qt 特定的事件处理"""
        QCoreApplication.processEvents()  # 处理 Qt 事件
        self._webview._core.process_events()  # 处理 WebView 事件
```

### 优点

1. ✅ **明确的接口**：`_auto_process_events()` 是一个明确的方法
2. ✅ **简洁的代码**：不需要 `hasattr()` 和 `callable()` 检查
3. ✅ **易于扩展**：子类只需重写 `_auto_process_events()`
4. ✅ **支持批处理**：通过 `auto_process=False` 参数
5. ✅ **符合 OOP 原则**：使用继承和方法重写

## 使用示例

### 基本使用（自动处理）

```python
from auroraview import WebView

webview = WebView()

# 自动处理事件（默认行为）
webview.emit("scene_updated", {"nodes": [...]})
webview.eval_js("console.log('test')")
```

### 批处理（手动控制）

```python
# 批量操作，延迟处理
webview.emit("event1", {"data": 1}, auto_process=False)
webview.emit("event2", {"data": 2}, auto_process=False)
webview.eval_js("console.log('batch')", auto_process=False)

# 一次性处理所有事件
webview._auto_process_events()
```

### Qt 集成（自动增强）

```python
from auroraview import QtWebView

# QtWebView 自动重写 _auto_process_events
webview = QtWebView()

# 自动处理 Qt 事件 + WebView 事件
webview.emit("scene_updated", {"nodes": [...]})
# ↓ 内部调用
# QCoreApplication.processEvents()  # Qt 事件
# self._core.process_events()       # WebView 事件
```

### 自定义集成

```python
class CustomWebView(WebView):
    def _auto_process_events(self):
        """自定义事件处理"""
        # 1. 处理自定义逻辑
        self.my_custom_processing()
        
        # 2. 调用父类处理
        super()._auto_process_events()
        
        # 3. 后续处理
        self.post_processing()
```

## 性能优化

### 批处理示例

```python
# 场景更新：批量发送多个事件
def update_scene(nodes):
    for i, node in enumerate(nodes):
        is_last = (i == len(nodes) - 1)
        webview.emit(
            "node_updated",
            {"node": node},
            auto_process=is_last  # 只在最后一个事件时处理
        )
```

## 迁移指南

### 从旧设计迁移

**旧代码（Hook 模式）：**
```python
webview._post_eval_js_hook = my_custom_handler
```

**新代码（方法重写）：**
```python
webview._auto_process_events = my_custom_handler
```

### 完全兼容

新设计完全兼容旧代码，只需简单替换即可。

## 总结

| 特性 | 旧设计（Hook） | 新设计（方法重写） |
|------|---------------|-------------------|
| 代码清晰度 | ⚠️ 需要检查 hook | ✅ 明确的方法调用 |
| 扩展性 | ⚠️ 需要了解 hook | ✅ 标准的方法重写 |
| 性能控制 | ❌ 无法批处理 | ✅ 支持 `auto_process=False` |
| OOP 原则 | ⚠️ 动态属性 | ✅ 继承和多态 |
| 技术债 | ⚠️ 容易积累 | ✅ 清晰的设计 |

**结论：** 新设计更优雅、更易维护、更符合 OOP 原则，适合积极开发阶段的项目。

