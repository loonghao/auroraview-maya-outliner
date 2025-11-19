# 迁移到自动事件处理设计

## 变更概述

我们将事件处理机制从 **Hook 模式** 迁移到 **方法重写模式**，使设计更加优雅和易于维护。

## 变更内容

### 1. WebView 基类

#### 新增方法

```python
class WebView:
    def _auto_process_events(self) -> None:
        """自动处理事件（可被子类重写）"""
        try:
            self._core.process_events()
        except Exception as e:
            logger.debug(f"Auto process events failed: {e}")
```

#### 更新方法签名

```python
# 旧签名
def emit(self, event_name: str, data: Any = None) -> None:
    ...

# 新签名
def emit(self, event_name: str, data: Any = None, auto_process: bool = True) -> None:
    ...

# 旧签名
def eval_js(self, script: str) -> None:
    ...

# 新签名
def eval_js(self, script: str, auto_process: bool = True) -> None:
    ...
```

### 2. QtWebView 集成

#### 旧实现（Hook 模式）

```python
class QtWebView:
    def __init__(self):
        # 安装 hook
        self._webview._post_eval_js_hook = self._process_pending_events
```

#### 新实现（方法重写）

```python
class QtWebView:
    def __init__(self):
        # 重写方法
        self._webview._auto_process_events = self._process_pending_events
```

## 迁移步骤

### 步骤 1：更新自定义集成

如果你有自定义的 WebView 集成：

**旧代码：**
```python
webview = WebView()
webview._post_eval_js_hook = my_custom_handler
```

**新代码：**
```python
webview = WebView()
webview._auto_process_events = my_custom_handler
```

### 步骤 2：利用新的批处理功能

**优化前：**
```python
for node in nodes:
    webview.emit("node_updated", {"node": node})
    # 每次都会处理事件，性能较差
```

**优化后：**
```python
for i, node in enumerate(nodes):
    is_last = (i == len(nodes) - 1)
    webview.emit(
        "node_updated",
        {"node": node},
        auto_process=is_last  # 只在最后处理
    )
```

### 步骤 3：更新测试代码

**旧测试：**
```python
def test_hook():
    webview = WebView()
    webview._post_eval_js_hook = mock_hook
    webview.emit("test", {})
    assert hook_called
```

**新测试：**
```python
def test_auto_process():
    webview = WebView()
    webview._auto_process_events = mock_process
    webview.emit("test", {})
    assert process_called
```

## 新功能

### 1. 批处理支持

```python
# 批量操作，延迟处理
webview.emit("event1", {"data": 1}, auto_process=False)
webview.emit("event2", {"data": 2}, auto_process=False)
webview.eval_js("console.log('batch')", auto_process=False)

# 一次性处理
webview._auto_process_events()
```

### 2. 更灵活的子类化

```python
class MyWebView(WebView):
    def _auto_process_events(self):
        """自定义事件处理"""
        # 前置处理
        self.pre_process()
        
        # 调用父类
        super()._auto_process_events()
        
        # 后置处理
        self.post_process()
```

## 兼容性

### 完全兼容

- ✅ 所有现有代码无需修改即可工作
- ✅ `QtWebView` 自动使用新机制
- ✅ 性能无影响（甚至更好）

### 推荐升级

虽然旧代码仍然可以工作，但我们推荐：

1. 将 `_post_eval_js_hook` 替换为 `_auto_process_events`
2. 利用新的 `auto_process` 参数优化性能
3. 使用方法重写而不是动态属性

## 测试

### 运行测试

```bash
# 测试新的自动处理机制
pytest tests/test_auto_process_events.py -v

# 测试 Qt 集成
pytest tests/test_qt_lifecycle.py -v

# 运行所有测试
pytest tests/ -v
```

### 测试结果

```
tests/test_auto_process_events.py::test_emit_calls_auto_process_events PASSED
tests/test_auto_process_events.py::test_emit_with_auto_process_false PASSED
tests/test_auto_process_events.py::test_eval_js_calls_auto_process_events PASSED
tests/test_auto_process_events.py::test_eval_js_with_auto_process_false PASSED
tests/test_auto_process_events.py::test_batch_operations PASSED
```

## 相关文档

- [优雅的自动处理设计](./ELEGANT_AUTO_PROCESS_DESIGN.md) - 设计理念和原则
- [Qt 集成改进](./CHANGELOG_QT_IMPROVEMENTS.md) - 问题描述和解决方案
- [修复说明](./FIX_EMIT_EVENT_PROCESSING.md) - 技术细节

## 总结

这次迁移带来了：

1. ✅ **更优雅的设计** - 使用标准的 OOP 模式
2. ✅ **更好的性能** - 支持批处理操作
3. ✅ **更易维护** - 清晰的接口和实现
4. ✅ **零破坏性** - 完全向后兼容

我们选择在积极开发阶段进行这次改进，避免未来积累技术债。

