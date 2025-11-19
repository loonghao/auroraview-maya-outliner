# 调试：Maya 创建物体后前端不刷新

## 问题描述

在 Maya 中创建物体（如 `cmds.polySphere()`）后，前端 Outliner 没有自动刷新显示新物体。

## 诊断步骤

### 步骤 1：验证初始加载是否成功

**检查前端控制台（F12）：**

```
✅ 应该看到：
[App] ✓ Scene hierarchy loaded: 4 root nodes
[MayaIPC] Registering handler via window.auroraview.on for event: scene_updated
[AuroraView] Registered handler for event: scene_updated

❌ 如果没看到：
- WebView 没有正确初始化
- 检查 Maya Script Editor 是否有错误
```

### 步骤 2：测试直接发送事件

在 Maya Script Editor 中运行：

```python
# 假设 outliner 已经创建
from maya_integration import test_direct_emit

# 测试 1：直接发送事件（绕过回调）
test_direct_emit.test_direct_emit(outliner)
```

**期望结果：**

**Maya 控制台：**
```
[TEST] ✓ WebView exists
[TEST] Current hierarchy: 4 root nodes
[TEST] Attempting to emit scene_updated event...
[TEST] ✓ emit() call succeeded
[TEST] ✓ Event processor: QtEventProcessor
```

**前端控制台：**
```
[EventAdapter] Extracted array from key 'value' (length: 4)
[App] ✓ Scene updated: 4 root nodes
```

**如果成功：** 说明事件发送机制正常，问题在于回调没有触发
**如果失败：** 说明事件发送机制有问题

### 步骤 3：测试回调是否触发

在 Maya Script Editor 中运行：

```python
from maya_integration import test_direct_emit

# 测试 2：创建物体并手动触发
test_direct_emit.test_create_object_and_emit(outliner)
```

**期望结果：**

**Maya 控制台：**
```
[TEST] Creating polySphere...
[TEST] ✓ Created: test_sphere
[TEST] Manually calling send_scene_update()
[MayaOutliner] send_scene_update: sending 5 root nodes
[MayaOutliner] ✓ Scene update emitted and processed automatically
```

**前端控制台：**
```
[EventAdapter] Extracted array from key 'value' (length: 5)
[App] ✓ Scene updated: 5 root nodes
```

**如果成功：** 说明 `send_scene_update()` 正常，问题在于回调没有自动触发
**如果失败：** 说明 `send_scene_update()` 有问题

### 步骤 4：验证回调注册

在 Maya Script Editor 中运行：

```python
from maya_integration import test_direct_emit

# 测试 3：验证回调注册
test_direct_emit.test_callback_registration(outliner)
```

**期望结果：**

**Maya 控制台：**
```
[TEST] ✓ Found 8 registered callbacks
[TEST] Creating polySphere to trigger callbacks...
[TEST] ✓ Created: callback_test_sphere

# 应该看到回调触发的消息：
================================================================================
[MayaOutliner] ✓ Callback triggered: Scene changed
[MayaOutliner] Args: (...)
[MayaOutliner] Updating hierarchy...
================================================================================
[MayaOutliner] send_scene_update: sending 6 root nodes
[MayaOutliner] ✓ Scene update emitted and processed automatically
================================================================================
```

**如果看到回调消息：** 回调正常工作
**如果没看到回调消息：** 回调没有被触发

## 常见问题和解决方案

### 问题 1：回调没有触发

**症状：**
- 创建物体后，Maya 控制台没有显示 `[MayaOutliner] ✓ Callback triggered`
- 前端没有刷新

**可能原因：**
1. Maya 版本不支持某些回调
2. 回调注册失败
3. 回调被其他插件覆盖

**解决方案：**

```python
# 检查 Maya 版本
import maya.cmds as cmds
print(cmds.about(version=True))

# 重新注册回调
outliner.run()  # 重新运行会重新注册回调
```

### 问题 2：回调触发但事件没发送

**症状：**
- Maya 控制台显示 `[MayaOutliner] ✓ Callback triggered`
- 但前端没有刷新

**可能原因：**
1. `webview` 对象为 None
2. `emit()` 调用失败
3. 事件处理器没有正确设置

**解决方案：**

```python
# 检查 webview
print(f"webview exists: {outliner.webview is not None}")

# 检查事件处理器
if hasattr(outliner.webview, '_webview'):
    print(f"_webview exists: {outliner.webview._webview is not None}")
    if hasattr(outliner.webview._webview, '_event_processor'):
        print(f"_event_processor: {outliner.webview._webview._event_processor}")
```

### 问题 3：事件发送但前端没收到

**症状：**
- Maya 控制台显示 `[MayaOutliner] ✓ Scene update emitted`
- 但前端控制台没有显示 `[EventAdapter] Extracted array`

**可能原因：**
1. 事件监听器没有注册
2. 事件名称不匹配
3. WebView 消息队列没有处理

**解决方案：**

```python
# 在前端控制台运行：
window.addEventListener('scene_updated', (e) => {
  console.log('[DEBUG] Received scene_updated:', e)
})

# 然后在 Maya 中手动发送：
outliner.webview.emit("scene_updated", {"value": [{"name": "test", "type": "transform", "children": []}]})
```

## 快速修复

### 方法 1：手动刷新

```python
# 在 Maya 中创建物体后，手动刷新
import maya.cmds as cmds
cmds.polySphere()

# 手动触发更新
outliner.send_scene_update()
```

### 方法 2：重新加载 Outliner

```python
# 关闭当前 Outliner
if outliner and outliner.webview:
    outliner.webview.close()

# 重新创建
import sys
sys.path.insert(0, r'c:\github\auroraview-maya-outliner')
from maya_integration import maya_outliner
outliner = maya_outliner.main()
```

### 方法 3：使用 scriptJob（临时方案）

如果回调不工作，可以使用 Maya 的 scriptJob：

```python
import maya.cmds as cmds

# 创建 scriptJob
job_id = cmds.scriptJob(
    event=["DagObjectCreated", lambda: outliner.send_scene_update()],
    protected=True
)

print(f"Created scriptJob: {job_id}")

# 清理
# cmds.scriptJob(kill=job_id)
```

## 调试检查清单

- [ ] 前端初始加载成功（看到 4 root nodes）
- [ ] 事件监听器已注册（看到 "Registered handler for event: scene_updated"）
- [ ] 直接 emit 测试成功（test_direct_emit）
- [ ] 手动调用 send_scene_update 成功（test_create_object_and_emit）
- [ ] 回调已注册（看到 "Found X registered callbacks"）
- [ ] 回调被触发（创建物体后看到 "Callback triggered"）
- [ ] Maya 控制台显示 "Scene update emitted"
- [ ] 前端控制台显示 "Extracted array from key 'value'"
- [ ] 前端控制台显示 "Scene updated: X root nodes"
- [ ] 新物体出现在前端 Outliner 中

## 下一步

如果所有测试都通过但问题仍然存在，请提供：

1. **Maya 版本：** `cmds.about(version=True)`
2. **Maya 控制台完整输出**
3. **前端控制台完整输出**
4. **测试脚本的输出**

这将帮助我们进一步诊断问题。

