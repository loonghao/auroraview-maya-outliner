# 设计：类型安全的事件系统

## 问题背景

当前问题：前后端数据格式不匹配导致事件无法正确处理。

**根本原因：**
1. 缺乏类型约束 - Python 和 JavaScript 之间没有类型契约
2. 数据格式不统一 - 不同事件使用不同的数据结构
3. 缺乏运行时验证 - 错误的数据格式直到运行时才发现
4. 缺乏开发时提示 - IDE 无法提供类型提示和错误检查

## 设计目标

1. **类型安全** - 编译时/开发时发现类型错误
2. **自动验证** - 运行时自动验证数据格式
3. **统一协议** - 前后端使用相同的类型定义
4. **开发友好** - IDE 提供完整的类型提示和自动补全
5. **向后兼容** - 不破坏现有代码

## 解决方案

### 方案 1：使用 TypedDict + JSON Schema（推荐）

#### 1.1 定义共享的类型定义

创建 `python/auroraview/events.py`：

```python
"""
Event type definitions for AuroraView.

This module defines the data structures for all events exchanged between
Python and JavaScript. These definitions serve as the single source of truth
for event data formats.
"""

from typing import TypedDict, List, Any, Optional, Union
from typing_extensions import NotRequired


# ============================================================================
# Event Data Types
# ============================================================================

class MayaNode(TypedDict):
    """Maya scene node data structure."""
    name: str
    type: str
    children: List['MayaNode']
    visible: NotRequired[bool]
    selected: NotRequired[bool]


class SceneUpdateEvent(TypedDict):
    """Scene update event data (Python → JavaScript)."""
    nodes: List[MayaNode]


class SelectionChangedEvent(TypedDict):
    """Selection changed event data (Python → JavaScript)."""
    node: str


class RefreshSceneEvent(TypedDict):
    """Refresh scene event data (JavaScript → Python)."""
    timestamp: int


class SelectObjectEvent(TypedDict):
    """Select object event data (JavaScript → Python)."""
    node_name: str


# ============================================================================
# Event Registry
# ============================================================================

class EventRegistry:
    """Registry of all events and their data types."""
    
    # Python → JavaScript events
    SCENE_UPDATED = "scene_updated"
    SELECTION_CHANGED = "selection_changed"
    
    # JavaScript → Python events
    REFRESH_SCENE = "refresh_scene"
    SELECT_OBJECT = "select_object"
    
    # Event type mapping
    EVENT_TYPES = {
        SCENE_UPDATED: SceneUpdateEvent,
        SELECTION_CHANGED: SelectionChangedEvent,
        REFRESH_SCENE: RefreshSceneEvent,
        SELECT_OBJECT: SelectObjectEvent,
    }


# ============================================================================
# Helper Functions
# ============================================================================

def validate_event_data(event_name: str, data: Any) -> bool:
    """Validate event data against its type definition.
    
    Args:
        event_name: Name of the event
        data: Event data to validate
        
    Returns:
        True if valid, False otherwise
        
    Note:
        This is a basic validation. For production, consider using
        pydantic or jsonschema for more robust validation.
    """
    if event_name not in EventRegistry.EVENT_TYPES:
        print(f"[EventValidation] Warning: Unknown event '{event_name}'")
        return True  # Allow unknown events for flexibility
    
    expected_type = EventRegistry.EVENT_TYPES[event_name]
    
    # Basic type checking (can be enhanced with pydantic)
    if not isinstance(data, dict):
        print(f"[EventValidation] Error: Event '{event_name}' data must be a dict, got {type(data)}")
        return False
    
    # Check required fields
    required_fields = expected_type.__required_keys__ if hasattr(expected_type, '__required_keys__') else []
    for field in required_fields:
        if field not in data:
            print(f"[EventValidation] Error: Event '{event_name}' missing required field '{field}'")
            return False
    
    return True


def normalize_event_data(event_name: str, data: Any) -> Any:
    """Normalize event data to the expected format.
    
    This function handles common data format variations and converts them
    to the standard format expected by the frontend.
    
    Args:
        event_name: Name of the event
        data: Event data (may be in various formats)
        
    Returns:
        Normalized event data
        
    Examples:
        >>> # For scene_updated, accept both formats:
        >>> normalize_event_data("scene_updated", [node1, node2])
        {"nodes": [node1, node2]}
        
        >>> normalize_event_data("scene_updated", {"nodes": [node1, node2]})
        {"nodes": [node1, node2]}
    """
    if event_name == EventRegistry.SCENE_UPDATED:
        # Accept both array and dict formats
        if isinstance(data, list):
            return {"nodes": data}
        elif isinstance(data, dict):
            # Normalize different field names to "nodes"
            if "nodes" in data:
                return data
            elif "value" in data:
                return {"nodes": data["value"]}
            elif "data" in data:
                return {"nodes": data["data"]}
        return data
    
    return data
```

#### 1.2 修改 WebView.emit() 使用类型验证

```python
# python/auroraview/webview.py

from .events import validate_event_data, normalize_event_data

def emit(self, event_name: str, data: Any = None, auto_process: bool = True) -> None:
    """Emit an event to JavaScript with automatic validation and normalization.
    
    Args:
        event_name: Name of the event
        data: Event data (will be validated and normalized)
        auto_process: Automatically process message queue (default: True)
    """
    # Validate data format (development mode)
    if self._dev_mode:
        if not validate_event_data(event_name, data):
            logger.warning(f"Event '{event_name}' has invalid data format")
    
    # Normalize data to expected format
    normalized_data = normalize_event_data(event_name, data)
    
    # Emit the event
    core.emit(event_name, normalized_data)
    
    # Auto-process events
    if auto_process:
        self._auto_process_events()
```

#### 1.3 生成 TypeScript 类型定义

创建脚本 `scripts/generate_ts_types.py`：

```python
"""Generate TypeScript type definitions from Python event types."""

def generate_typescript_types():
    """Generate TypeScript types from Python TypedDict definitions."""
    
    ts_output = """
// Auto-generated from python/auroraview/events.py
// DO NOT EDIT MANUALLY

export interface MayaNode {
  name: string;
  type: string;
  children: MayaNode[];
  visible?: boolean;
  selected?: boolean;
}

export interface SceneUpdateEvent {
  nodes: MayaNode[];
}

export interface SelectionChangedEvent {
  node: string;
}

export interface RefreshSceneEvent {
  timestamp: number;
}

export interface SelectObjectEvent {
  node_name: string;
}

// Event type mapping
export const EventTypes = {
  SCENE_UPDATED: 'scene_updated',
  SELECTION_CHANGED: 'selection_changed',
  REFRESH_SCENE: 'refresh_scene',
  SELECT_OBJECT: 'select_object',
} as const;

export type EventName = typeof EventTypes[keyof typeof EventTypes];
"""
    
    with open("src/types/events.ts", "w") as f:
        f.write(ts_output)
    
    print("✓ TypeScript types generated: src/types/events.ts")

if __name__ == "__main__":
    generate_typescript_types()
```

#### 1.4 前端使用类型安全的事件

```typescript
// src/composables/useMayaIPC.ts
import type { SceneUpdateEvent, SelectionChangedEvent, EventName } from '@/types/events'

export function useMayaIPC() {
  // Type-safe event handler
  const onMayaEvent = <T = unknown>(event: EventName, handler: (data: T) => void) => {
    if (window.auroraview && typeof (window.auroraview as any).on === 'function') {
      ;(window.auroraview as any).on(event, handler)
    } else {
      window.addEventListener(event, (e: Event) => {
        const customEvent = e as CustomEvent<T>
        handler(customEvent.detail)
      })
    }
  }

  return { onMayaEvent }
}
```

```typescript
// src/App.vue
import { EventTypes } from '@/types/events'
import type { SceneUpdateEvent, SelectionChangedEvent } from '@/types/events'

// Type-safe event listeners
onMayaEvent<SceneUpdateEvent>(EventTypes.SCENE_UPDATED, (data) => {
  // TypeScript knows data.nodes is MayaNode[]
  sceneData.value = data.nodes
  console.log('[App] Scene updated:', data.nodes.length, 'root nodes')
})

onMayaEvent<SelectionChangedEvent>(EventTypes.SELECTION_CHANGED, (data) => {
  // TypeScript knows data.node is string
  selectedNode.value = data.node
  console.log('[App] Selection changed:', data.node)
})
```

### 方案 2：使用 Pydantic（更强大的验证）

```python
# python/auroraview/events.py
from pydantic import BaseModel, Field
from typing import List, Optional

class MayaNode(BaseModel):
    """Maya scene node."""
    name: str
    type: str
    children: List['MayaNode'] = Field(default_factory=list)
    visible: Optional[bool] = None
    selected: Optional[bool] = None

class SceneUpdateEvent(BaseModel):
    """Scene update event."""
    nodes: List[MayaNode]

    class Config:
        # Allow extra fields for forward compatibility
        extra = 'allow'

# Usage in WebView
def emit(self, event_name: str, data: Any = None, auto_process: bool = True) -> None:
    # Validate with Pydantic
    if event_name == "scene_updated":
        try:
            validated = SceneUpdateEvent(nodes=data if isinstance(data, list) else data.get("nodes", []))
            data = validated.dict()
        except Exception as e:
            logger.error(f"Event validation failed: {e}")
            return

    core.emit(event_name, data)
    if auto_process:
        self._auto_process_events()
```

### 方案 3：智能前端适配器（最灵活）

```typescript
// src/utils/eventAdapter.ts

/**
 * Smart event data adapter that handles multiple data formats
 */
export class EventDataAdapter {
  /**
   * Extract array data from various formats
   */
  static extractArray<T>(data: unknown, ...possibleKeys: string[]): T[] {
    // Direct array
    if (Array.isArray(data)) {
      return data as T[]
    }

    // Object with array field
    if (data && typeof data === 'object') {
      const obj = data as Record<string, unknown>

      // Try each possible key
      for (const key of possibleKeys) {
        if (key in obj && Array.isArray(obj[key])) {
          return obj[key] as T[]
        }
      }

      // Fallback: try common keys
      const commonKeys = ['value', 'data', 'items', 'nodes', 'list']
      for (const key of commonKeys) {
        if (key in obj && Array.isArray(obj[key])) {
          console.warn(`[EventAdapter] Using fallback key '${key}' for array data`)
          return obj[key] as T[]
        }
      }
    }

    console.error('[EventAdapter] Could not extract array from data:', data)
    return []
  }

  /**
   * Extract string value from various formats
   */
  static extractString(data: unknown, ...possibleKeys: string[]): string {
    // Direct string
    if (typeof data === 'string') {
      return data
    }

    // Object with string field
    if (data && typeof data === 'object') {
      const obj = data as Record<string, unknown>

      for (const key of possibleKeys) {
        if (key in obj && typeof obj[key] === 'string') {
          return obj[key] as string
        }
      }
    }

    return ''
  }
}
```

```typescript
// src/App.vue - 使用适配器
import { EventDataAdapter } from '@/utils/eventAdapter'

onMayaEvent('scene_updated', (data: unknown) => {
  // 自动适配多种格式：
  // - [node1, node2]
  // - {nodes: [node1, node2]}
  // - {value: [node1, node2]}
  // - {data: [node1, node2]}
  const nodes = EventDataAdapter.extractArray<MayaNode>(data, 'nodes', 'value', 'data')
  sceneData.value = nodes
  console.log('[App] Scene updated:', nodes.length, 'root nodes')
})

onMayaEvent('selection_changed', (data: unknown) => {
  // 自动适配：
  // - "pSphere1"
  // - {node: "pSphere1"}
  const node = EventDataAdapter.extractString(data, 'node', 'name')
  selectedNode.value = node
  console.log('[App] Selection changed:', node)
})
```

## 推荐实施方案

### 短期（立即实施）

✅ **方案 3：智能前端适配器**
- 优点：不需要修改现有 Python 代码，向后兼容
- 优点：立即解决数据格式不匹配问题
- 优点：提供更好的错误提示
- 缺点：只在前端做适配，Python 侧仍然可能发送错误格式

### 中期（1-2 周内）

✅ **方案 1：TypedDict + 数据规范化**
- 实施 `events.py` 定义所有事件类型
- 在 `WebView.emit()` 中添加数据规范化
- 生成 TypeScript 类型定义
- 更新文档说明数据格式

### 长期（未来版本）

✅ **方案 2：Pydantic 验证**
- 使用 Pydantic 进行严格的数据验证
- 自动生成 JSON Schema
- 开发模式下强制验证，生产模式下可选
- 提供更好的错误信息

## 实施优先级

1. **立即** - 实施智能前端适配器（1 小时）
2. **本周** - 创建事件类型定义文件（2 小时）
3. **本周** - 添加数据规范化函数（2 小时）
4. **下周** - 生成 TypeScript 类型（4 小时）
5. **未来** - 集成 Pydantic 验证（1 天）

## 收益

1. ✅ **避免数据格式错误** - 编译时和运行时双重保护
2. ✅ **更好的开发体验** - IDE 类型提示和自动补全
3. ✅ **自动化文档** - 类型定义即文档
4. ✅ **向后兼容** - 智能适配器处理旧格式
5. ✅ **易于维护** - 单一数据源，修改一处即可

