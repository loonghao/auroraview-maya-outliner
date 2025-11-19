# 调试 Maya 事件处理问题

## 问题描述

在 Maya 中创建物体时，`scene_updated` 事件没有发送到前端显示。

## 诊断步骤

### 1. 运行测试脚本

在 Maya Script Editor 中运行：

```python
import sys
sys.path.insert(0, r'c:\github\auroraview-maya-outliner')

from maya_integration import test_event_processing
webview = test_event_processing.run_test()
```

这个脚本会：
1. 创建一个简单的 QtWebView
2. 检查 QtEventProcessor 是否正确设置
3. 发送一个测试事件
4. 在 WebView 控制台中显示结果

### 2. 检查控制台输出

#### Python 侧（Maya Script Editor）

你应该看到：

```
[TEST] ✓ QtWebView created
[TEST] ✓ Event processor found: QtEventProcessor
[TEST] ✓ Event processor has process() method
[TEST] Emitting test event...
[TEST] ✓ emit() called
```

#### JavaScript 侧（WebView DevTools - F12）

你应该看到：

```
[JS] Page loaded
[JS] Event listener registered
[JS] ✓ Received test_event: {message: "Hello from Python!", timestamp: "test"}
```

### 3. 可能的问题

#### 问题 A: Event Processor 未设置

**症状：**
```
[TEST] ✗ Event processor is None!
```

**原因：** QtWebView 没有正确设置 QtEventProcessor

**解决方案：** 检查 `python/auroraview/qt_integration.py` 中的 `QtWebView.__init__`

#### 问题 B: emit() 调用但事件未到达

**症状：**
- Python 侧显示 `✓ emit() called`
- JavaScript 侧没有收到事件

**原因：** 事件处理链中某个环节失败

**调试步骤：**

1. **检查 WebView._auto_process_events() 是否被调用**

   在 `python/auroraview/webview.py` 的 `emit()` 方法中添加日志：
   
   ```python
   def emit(self, event_name: str, data: Any = None, auto_process: bool = True) -> None:
       print(f"[WebView.emit] Event: {event_name}, auto_process: {auto_process}")
       core.emit(event_name, data)
       
       if auto_process:
           print("[WebView.emit] Calling _auto_process_events()...")
           self._auto_process_events()
           print("[WebView.emit] _auto_process_events() completed")
   ```

2. **检查 QtEventProcessor.process() 是否被调用**

   在 `python/auroraview/qt_integration.py` 的 `QtEventProcessor.process()` 中添加日志：
   
   ```python
   def process(self) -> None:
       self._process_count += 1
       print(f"[QtEventProcessor.process] Called (count: {self._process_count})")
       
       try:
           from qtpy.QtCore import QCoreApplication
           
           print("[QtEventProcessor.process] Processing Qt events...")
           QCoreApplication.processEvents()
           
           print("[QtEventProcessor.process] Processing WebView events...")
           self._webview._core.process_events()
           
           print("[QtEventProcessor.process] Completed")
       except Exception as e:
           print(f"[QtEventProcessor.process] ERROR: {e}")
   ```

3. **检查 Rust Core 是否处理了消息队列**

   这需要在 Rust 侧添加日志（如果可能）。

#### 问题 C: Maya 回调未触发

**症状：**
- 创建物体时没有看到 `[MayaOutliner] ✓ Callback triggered: Scene changed`

**原因：** Maya 回调没有正确注册

**解决方案：**

1. 检查 `setup_maya_callbacks()` 是否被调用
2. 检查回调是否成功注册（没有异常）
3. 尝试手动触发回调：

```python
# 在 Maya Script Editor 中
outliner.send_scene_update()
```

如果手动调用有效，说明问题在回调注册上。

### 4. 完整的事件流程

```
Maya 创建物体
    ↓
Maya API 触发 DagObjectCreated 事件
    ↓
on_scene_changed() 回调被调用
    ↓
send_scene_update() 被调用
    ↓
webview.emit("scene_updated", data)
    ↓
WebView.emit() 调用 _auto_process_events()
    ↓
QtEventProcessor.process() 被调用
    ↓
QCoreApplication.processEvents() - 处理 Qt 事件
    ↓
webview._core.process_events() - 处理 WebView 消息队列
    ↓
Rust Core 执行 JavaScript
    ↓
JavaScript 接收 'scene_updated' 事件
```

### 5. 快速验证

在 Maya Script Editor 中运行：

```python
# 假设 outliner 已经创建
outliner.send_scene_update()
```

如果这个调用能让前端更新，说明：
- ✅ 事件处理链正常
- ❌ Maya 回调有问题

如果这个调用也不能让前端更新，说明：
- ❌ 事件处理链有问题
- 需要按照上面的步骤 3.B 进行调试

## 下一步

根据测试结果，我们可以确定问题的具体位置并进行修复。

