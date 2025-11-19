# API 调用修复说明

## 问题描述

在启动 Maya Outliner 时遇到错误：

```
Failed to load scene hierarchy: Error: [MayaIPC] auroraview.api.get_scene_hierarchy is not available
```

## 根本原因

### 错误的实现

之前的代码直接检查 `window.auroraview.api.get_scene_hierarchy` 是否存在：

```typescript
const getSceneHierarchy = async () => {
  if (!window.auroraview?.api?.get_scene_hierarchy) {
    throw new Error('[MayaIPC] auroraview.api.get_scene_hierarchy is not available')
  }
  
  const result = await window.auroraview.api.get_scene_hierarchy()
  return result
}
```

### 问题所在

AuroraView 的 API 方法不是直接作为函数属性存在的。根据 AuroraView 的工作原理：

1. Python 端通过 `bind_api(api, namespace="api")` 绑定 API 对象
2. JavaScript 端通过 `window.auroraview.call(method, params)` 调用方法
3. API 方法是动态绑定的，不能直接通过属性访问检查

## 解决方案

### 修复后的实现

使用 `callAPI` 辅助函数来调用 API 方法：

```typescript
const getSceneHierarchy = async () => {
  console.log('[MayaIPC] getSceneHierarchy: calling via callAPI')
  // Use callAPI without params for zero-parameter methods
  const result = await callAPI<any[]>('get_scene_hierarchy')
  console.log(
    '[MayaIPC] getSceneHierarchy: modern API returned',
    Array.isArray(result) ? result.length : 'unknown',
    'root nodes',
  )
  return result
}
```

### callAPI 的工作原理

```typescript
const callAPI = async <T = any>(method: string, params?: any): Promise<T> => {
  if (!window.auroraview?.api) {
    throw new Error('[MayaIPC] window.auroraview.api not available')
  }

  const apiMethod = (window.auroraview.api as any)[method]
  
  if (typeof apiMethod !== 'function') {
    throw new Error(`[MayaIPC] Method '${method}' is not a function`)
  }

  // Call with or without params
  const result = params !== undefined ? await apiMethod(params) : await apiMethod()
  return result as T
}
```

## AuroraView API 调用规则

根据 AuroraView 文档：

### 1. 无参数方法

```typescript
// Python
def get_scene_hierarchy(self):
    return [...]

// JavaScript - 不传递 params
await callAPI('get_scene_hierarchy')
```

### 2. 关键字参数

```typescript
// Python
def select_node(self, node_name: str):
    ...

// JavaScript - 传递对象
await callAPI('select_node', { node_name: 'pCube1' })
```

### 3. 位置参数

```typescript
// Python
def move(self, x, y):
    ...

// JavaScript - 传递数组
await callAPI('move', [10, 20])
```

### 4. 单个参数

```typescript
// Python
def delete_node(self, node_name: str):
    ...

// JavaScript - 传递单个值或对象
await callAPI('delete_node', { node_name: 'pCube1' })
```

## 类型定义更新

### 之前（错误）

```typescript
declare global {
  interface Window {
    auroraview?: {
      api?: {
        get_scene_hierarchy?: () => Promise<any[]>
        select_node?: (node_name: string) => Promise<...>
        // ...
      }
    }
  }
}
```

### 现在（正确）

```typescript
declare global {
  interface Window {
    auroraview?: {
      api?: Record<string, any>  // API methods are dynamically bound
      emit?: (event: string, data: any) => void
    }
  }
}
```

## 最佳实践

### ✅ 推荐

```typescript
// 使用 callAPI 辅助函数
const result = await callAPI('get_scene_hierarchy')
const result2 = await callAPI('select_node', { node_name: 'pCube1' })
```

### ❌ 避免

```typescript
// 不要直接访问 API 方法
const result = await window.auroraview.api.get_scene_hierarchy()

// 不要检查方法是否存在
if (window.auroraview?.api?.get_scene_hierarchy) {
  // 这个检查可能失败
}
```

## 验证修复

### 1. 启动 Maya Outliner

```python
from maya_integration import maya_outliner

outliner = maya_outliner.main()
```

### 2. 检查浏览器控制台

应该看到：

```
[MayaIPC] getSceneHierarchy: calling via callAPI
[MayaIPC] Calling API: get_scene_hierarchy with params: undefined
[MayaIPC] ✓ AuroraView API object found
[MayaIPC] Available API methods: [...]
[MayaIPC] ✓ API result: get_scene_hierarchy [...]
```

### 3. 验证场景加载

Outliner 应该显示 Maya 场景中的节点。

## 相关文件

- `src/composables/useMayaIPC.ts` - 修复的主要文件
- `maya_integration/maya_outliner.py` - Python API 定义
- `README.md` - AuroraView API 使用说明

## 总结

这个修复确保了前端正确使用 AuroraView 的动态 API 调用机制，而不是尝试直接访问不存在的函数属性。所有 API 调用现在都通过 `callAPI` 辅助函数进行，这是 AuroraView 推荐的方式。

