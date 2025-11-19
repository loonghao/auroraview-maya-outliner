# 快速参考：EventDataAdapter 使用指南

## 什么是 EventDataAdapter？

EventDataAdapter 是一个智能数据适配器，用于处理 Python 和 JavaScript 之间的数据格式差异。

## 为什么需要它？

**问题：** Python 和 JavaScript 之间传递数据时，格式可能不一致：
- Python 发送：`{"nodes": [...]}`
- 前端期望：`{"value": [...]}`
- 结果：数据无法正确提取 ❌

**解决：** EventDataAdapter 自动适配多种格式 ✅

## 快速开始

### 1. 导入

```typescript
import { EventDataAdapter } from '@/utils/eventAdapter'
```

### 2. 提取数组

```typescript
// 自动处理多种格式
const nodes = EventDataAdapter.extractArray<MayaNode>(data, 'nodes', 'value', 'data')

// 支持的格式：
// ✅ [node1, node2, ...]
// ✅ {nodes: [node1, node2, ...]}
// ✅ {value: [node1, node2, ...]}
// ✅ {data: [node1, node2, ...]}
```

### 3. 提取字符串

```typescript
// 自动处理多种格式
const name = EventDataAdapter.extractString(data, 'node', 'name', 'id')

// 支持的格式：
// ✅ "pSphere1"
// ✅ {node: "pSphere1"}
// ✅ {name: "pSphere1"}
// ✅ {id: "pSphere1"}
```

### 4. 提取对象

```typescript
// 自动处理多种格式
const config = EventDataAdapter.extractObject<Config>(data, 'config', 'settings')

// 支持的格式：
// ✅ {key: "value", ...}
// ✅ {config: {key: "value", ...}}
// ✅ {settings: {key: "value", ...}}
```

## 实际示例

### 示例 1：场景更新事件

```typescript
// src/App.vue
onMayaEvent('scene_updated', (data: unknown) => {
  // 旧代码（脆弱）：
  // const nodes = data?.nodes || data?.value || []
  
  // 新代码（健壮）：
  const nodes = EventDataAdapter.extractArray<MayaNode>(data, 'nodes', 'value')
  sceneData.value = nodes
})
```

**Python 侧可以发送任何格式：**
```python
# 格式 1
webview.emit("scene_updated", {"nodes": hierarchy})

# 格式 2
webview.emit("scene_updated", {"value": hierarchy})

# 格式 3
webview.emit("scene_updated", hierarchy)

# 所有格式都能正确处理！✅
```

### 示例 2：选择改变事件

```typescript
onMayaEvent('selection_changed', (data: unknown) => {
  // 旧代码（脆弱）：
  // const node = (data as any).node || ''
  
  // 新代码（健壮）：
  const node = EventDataAdapter.extractString(data, 'node', 'name')
  selectedNode.value = node
})
```

**Python 侧可以发送任何格式：**
```python
# 格式 1
webview.emit("selection_changed", {"node": "pSphere1"})

# 格式 2
webview.emit("selection_changed", {"name": "pSphere1"})

# 格式 3
webview.emit("selection_changed", "pSphere1")

# 所有格式都能正确处理！✅
```

## API 参考

### extractArray<T>()

```typescript
static extractArray<T>(
  data: unknown,
  ...possibleKeys: string[]
): T[]
```

**参数：**
- `data` - 原始数据（可以是数组或对象）
- `possibleKeys` - 可能的键名（按优先级顺序）

**返回：**
- 提取的数组，如果失败返回空数组 `[]`

**日志：**
- 成功：`[EventAdapter] Extracted array from key 'nodes' (length: 5)`
- 失败：`[EventAdapter] Could not find array in object. Available keys: ...`

### extractString()

```typescript
static extractString(
  data: unknown,
  ...possibleKeys: string[]
): string
```

**参数：**
- `data` - 原始数据（可以是字符串或对象）
- `possibleKeys` - 可能的键名（按优先级顺序）

**返回：**
- 提取的字符串，如果失败返回空字符串 `""`

**日志：**
- 成功：`[EventAdapter] Extracted string from key 'node': pSphere1`
- 失败：`[EventAdapter] Could not find string in object. Available keys: ...`

### extractObject<T>()

```typescript
static extractObject<T extends Record<string, unknown>>(
  data: unknown,
  ...possibleKeys: string[]
): T
```

**参数：**
- `data` - 原始数据
- `possibleKeys` - 可能的键名（按优先级顺序）

**返回：**
- 提取的对象，如果失败返回空对象 `{}`

## 调试技巧

### 1. 查看控制台日志

EventDataAdapter 会自动输出详细的日志：

```
[EventAdapter] Extracted array from key 'nodes' (length: 5)
```

或者警告：

```
[EventAdapter] Using fallback key 'value' for array data (consider using explicit key)
```

### 2. 检查数据格式

如果提取失败，会显示可用的键：

```
[EventAdapter] Could not find array in object. Available keys: ['foo', 'bar']
[EventAdapter] Object data: {foo: 123, bar: 456}
```

### 3. 添加自定义日志

```typescript
const nodes = EventDataAdapter.extractArray<MayaNode>(data, 'nodes')
console.log('[MyComponent] Extracted nodes:', nodes)
```

## 最佳实践

### ✅ 推荐

```typescript
// 1. 指定优先级顺序
const nodes = EventDataAdapter.extractArray<MayaNode>(data, 'nodes', 'value', 'data')

// 2. 使用类型参数
const nodes = EventDataAdapter.extractArray<MayaNode>(data, 'nodes')

// 3. 检查结果
const nodes = EventDataAdapter.extractArray<MayaNode>(data, 'nodes')
if (nodes.length === 0) {
  console.warn('No nodes received')
}
```

### ❌ 不推荐

```typescript
// 1. 不指定键名（依赖自动回退）
const nodes = EventDataAdapter.extractArray<MayaNode>(data)  // 可以工作，但不明确

// 2. 不使用类型参数
const nodes = EventDataAdapter.extractArray(data, 'nodes')  // 失去类型安全

// 3. 忽略空结果
const nodes = EventDataAdapter.extractArray<MayaNode>(data, 'nodes')
sceneData.value = nodes  // 可能是空数组，应该检查
```

## 常见问题

### Q: 为什么不直接统一数据格式？

A: 我们正在逐步统一，但 EventDataAdapter 提供了过渡期的兼容性：
- ✅ 支持旧代码
- ✅ 支持新代码
- ✅ 不破坏现有功能

### Q: 性能影响如何？

A: 几乎可以忽略：
- 简单的类型检查和键查找
- 没有复杂的转换逻辑
- 日志可以在生产环境关闭

### Q: 如何添加新的数据格式支持？

A: 修改 `src/utils/eventAdapter.ts`：

```typescript
// 添加新的回退键
const commonKeys = ['value', 'data', 'items', 'nodes', 'list', 'results', 'YOUR_NEW_KEY']
```

## 下一步

1. **阅读完整设计文档：** `docs/DESIGN_TYPE_SAFE_EVENTS.md`
2. **查看实施总结：** `docs/SUMMARY_TYPE_SAFE_SOLUTION.md`
3. **学习调试技巧：** `docs/DEBUG_MAYA_EVENT_PROCESSING.md`

