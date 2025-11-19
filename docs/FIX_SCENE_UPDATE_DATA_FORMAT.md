# 修复：场景更新数据格式不匹配

## 问题描述

在 Maya 中创建物体时，`scene_updated` 事件被正确发送到前端，但前端没有显示更新的数据。

## 根本原因

**数据格式不匹配！**

### Python 侧发送的格式

```python
# maya_integration/maya_outliner.py
self.webview.emit("scene_updated", {"nodes": hierarchy})
```

发送的数据结构：
```json
{
  "nodes": [
    {"name": "pSphere1", "type": "transform", "children": []},
    ...
  ]
}
```

### 前端期望的格式

```typescript
// src/App.vue lines 69-73
const nodes = Array.isArray(payload)
  ? payload
  : payload && Array.isArray((payload as any).value)
    ? (payload as any).value
    : []
```

前端期望的数据结构：
1. **直接是数组**：`[{...}, {...}]`
2. **或者包含 `value` 字段**：`{"value": [{...}, {...}]}`

但我们发送的是 `{"nodes": [...]}` ❌

## 解决方案

修改 Python 侧发送的数据格式，使用 `value` 字段而不是 `nodes`：

```python
# 修改前
self.webview.emit("scene_updated", {"nodes": hierarchy})

# 修改后
self.webview.emit("scene_updated", {"value": hierarchy})
```

## 修改的文件

- `maya_integration/maya_outliner.py` - `send_scene_update()` 方法

## 验证步骤

1. **在 Maya 中重新加载 Maya Outliner**

```python
import sys
sys.path.insert(0, r'c:\github\auroraview-maya-outliner')

from maya_integration import maya_outliner
outliner = maya_outliner.main()
```

2. **创建一个物体**

```python
import maya.cmds as cmds
cmds.polySphere()
```

3. **检查前端控制台** (F12)

你应该看到：

```
[App] scene_updated raw payload: {value: Array(X)}
[App] Scene updated: X root nodes
```

4. **检查前端界面**

新创建的物体应该立即出现在 Outliner 树中！

## 为什么测试脚本能工作？

测试脚本 (`test_event_processing.py`) 发送的是简单的字符串数据：

```python
webview.emit("test_event", {"message": "Hello from Python!", "timestamp": "test"})
```

前端只是简单地显示 `JSON.stringify(e.detail)`，所以任何格式都能显示。

但 Maya Outliner 的前端代码有特定的数据格式要求，需要从 `payload.value` 中提取数组。

## 经验教训

1. **前后端数据格式必须匹配** - 这是最常见的集成问题
2. **仔细阅读前端代码** - 了解前端期望的数据结构
3. **添加数据格式文档** - 在 API 文档中明确说明数据格式
4. **使用 TypeScript 类型** - 可以帮助发现格式不匹配问题

## 后续改进建议

### 1. 统一数据格式约定

在项目中建立统一的数据格式约定：

```python
# 推荐格式：直接发送数组（如果数据是数组）
self.webview.emit("scene_updated", hierarchy)

# 或者：使用统一的包装格式
self.webview.emit("scene_updated", {"data": hierarchy})
```

### 2. 添加数据验证

在前端添加数据验证和错误提示：

```typescript
onMayaEvent('scene_updated', (data: unknown) => {
  console.log('[App] scene_updated raw payload:', data)
  
  // 验证数据格式
  if (!data || (typeof data !== 'object')) {
    console.error('[App] Invalid scene_updated payload:', data)
    return
  }
  
  // 提取数据
  const payload = data as any
  const nodes = Array.isArray(payload)
    ? payload
    : Array.isArray(payload.value)
      ? payload.value
      : Array.isArray(payload.nodes)  // 兼容旧格式
        ? payload.nodes
        : []
  
  if (nodes.length === 0) {
    console.warn('[App] No nodes in scene_updated payload')
  }
  
  sceneData.value = nodes as MayaNode[]
})
```

### 3. 创建 API 文档

创建一个文档说明所有事件的数据格式：

```markdown
# Maya Outliner API

## Events (Python → JavaScript)

### scene_updated
更新场景层级数据

**数据格式：**
```json
{
  "value": [
    {
      "name": "pSphere1",
      "type": "transform",
      "children": []
    }
  ]
}
```

### selection_changed
选择改变

**数据格式：**
```json
{
  "node": "pSphere1"
}
```
```

## 总结

这个问题的根本原因是**数据格式不匹配**，而不是事件处理机制的问题。

✅ 事件处理链正常工作（测试脚本验证）  
✅ 分层架构正常工作（QtEventProcessor 正确设置）  
✅ Maya 回调正常触发（日志显示）  
❌ 数据格式不匹配（`nodes` vs `value`）  

修复后，Maya Outliner 应该能正常工作了！

