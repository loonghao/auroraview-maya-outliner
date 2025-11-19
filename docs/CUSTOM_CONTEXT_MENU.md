# Custom Context Menu for Maya Outliner

This document explains how to implement custom context menus in the Maya Outliner using AuroraView's context menu configuration.

## Overview

The Maya Outliner now supports disabling the native browser context menu and implementing custom JavaScript-based menus. This allows you to create Maya-style context menus with full control over appearance and functionality.

## Python Configuration

### Disable Native Context Menu

```python
from maya_integration import maya_outliner

# Create outliner with custom context menu support
outliner = maya_outliner.main(context_menu=False)
```

### Available API Methods

The following methods are available via `auroraview.api.*` for context menu actions:

```javascript
// Selection
await auroraview.api.select_node(nodeName)

// Visibility
await auroraview.api.set_visibility(nodeName, visible)
await auroraview.api.show_only_dag_objects(nodeName)
await auroraview.api.show_shapes(nodeName)
await auroraview.api.show_selected(nodeName)
await auroraview.api.hide_in_outliner(nodeName)

// Node operations
await auroraview.api.delete_node(nodeName)
```

## Frontend Implementation

### Basic Context Menu Structure

```typescript
// React component example
const handleContextMenu = (e: React.MouseEvent, node: Node) => {
  e.preventDefault();
  
  // Show custom menu at cursor position
  showContextMenu({
    x: e.clientX,
    y: e.clientY,
    items: [
      {
        label: '仅显示 DAG 对象',
        action: () => auroraview.api.show_only_dag_objects(node.name)
      },
      {
        label: '形状',
        action: () => auroraview.api.show_shapes(node.name)
      },
      { type: 'separator' },
      {
        label: '显示选定项',
        action: () => auroraview.api.show_selected(node.name)
      }
    ]
  });
};
```

## Complete Menu Structure (Maya-style)

Based on Maya's native outliner, here's the complete menu structure:

```typescript
const mayaOutlinerContextMenu = [
  {
    label: '仅显示 DAG 对象',
    action: () => auroraview.api.show_only_dag_objects(node.name)
  },
  {
    label: '形状',
    action: () => auroraview.api.show_shapes(node.name)
  },
  { type: 'separator' },
  {
    label: '显示选定项',
    action: () => auroraview.api.show_selected(node.name)
  },
  {
    label: '在大纲图中隐藏',
    submenu: [
      {
        label: '隐藏选定项',
        action: () => auroraview.api.hide_in_outliner(node.name)
      }
    ]
  },
  { type: 'separator' },
  {
    label: '引用',
    submenu: [
      { label: '创建引用', action: () => {} }
    ]
  },
  {
    label: '场景集合',
    submenu: [
      { label: '添加到新集合', action: () => {} }
    ]
  },
  {
    label: '集',
    submenu: [
      { label: '创建快速选择集', action: () => {} }
    ]
  },
  {
    label: '资产',
    submenu: [
      { label: '分配新资产', action: () => {} }
    ]
  },
  { type: 'separator' },
  {
    label: '展示',
    submenu: [
      { label: '展开所有', action: () => {} },
      { label: '折叠所有', action: () => {} }
    ]
  },
  {
    label: '显示',
    submenu: [
      { label: '显示', action: () => auroraview.api.set_visibility(node.name, true) },
      { label: '隐藏', action: () => auroraview.api.set_visibility(node.name, false) }
    ]
  },
  {
    label: '渲染设定',
    submenu: [
      { label: '可渲染', action: () => {} }
    ]
  }
];
```

## Styling Example

```css
.context-menu {
  position: fixed;
  background: #2b2b2b;
  border: 1px solid #3c3c3c;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  min-width: 180px;
  z-index: 1000;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 12px;
}

.context-menu-item {
  padding: 6px 20px;
  cursor: pointer;
  color: #cccccc;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.context-menu-item:hover {
  background: #094771;
}

.context-menu-separator {
  height: 1px;
  background: #3c3c3c;
  margin: 4px 0;
}
```

## Best Practices

1. **Performance**: Cache menu items and only rebuild when necessary
2. **Accessibility**: Support keyboard navigation (Arrow keys, Enter, Escape)
3. **UX Consistency**: Match Maya's visual style and behavior
4. **Error Handling**: Show user-friendly messages when API calls fail
5. **Cleanup**: Remove menu from DOM when clicking outside

## Testing

```python
# In Maya Script Editor
from maya_integration import maya_outliner

# Create outliner with custom menu
outliner = maya_outliner.main(context_menu=False)
```
