# Context Menu Implementation for Maya Outliner

## 概述

已成功为 Maya Outliner 实现了自定义右键菜单功能，完全模仿 Maya 原生 Outliner 的菜单结构和行为。

## 实现的文件

### 1. 类型定义

**`src/types/contextMenu.ts`**
- 定义了菜单项、分隔符、菜单位置等类型
- 支持嵌套子菜单
- 支持禁用状态和快捷键提示

### 2. Composable

**`src/composables/useContextMenu.ts`**
- 管理菜单的显示/隐藏状态
- 处理点击外部关闭菜单
- 处理 ESC 键关闭菜单
- 管理子菜单的激活状态

### 3. 组件

**`src/components/ContextMenu.vue`**
- 可复用的右键菜单组件
- 支持嵌套子菜单
- 自动调整位置防止超出视口
- Maya 风格的样式设计

### 4. 菜单配置

**`src/config/mayaContextMenu.ts`**
- 定义 Maya Outliner 的完整菜单结构
- 集成所有可用的 API 方法
- 根据节点状态动态禁用菜单项

### 5. 组件集成

**更新的组件:**
- `src/components/TreeNode.vue` - 添加右键菜单事件处理
- `src/components/OutlinerTree.vue` - 传递右键菜单事件
- `src/App.vue` - 集成菜单显示逻辑

## 菜单结构

实现了以下 Maya 原生菜单项：

1. **仅显示 DAG 对象** ✓
2. **形状** ✓
3. **显示选定项** ✓
4. **在大纲图中隐藏** ✓ (带子菜单)
5. **引用** (占位符)
6. **场景集合** (占位符)
7. **集** (占位符)
8. **资产** (占位符)
9. **展示** (占位符，带子菜单)
10. **显示** ✓ (带子菜单)
11. **渲染设定** (占位符)

## 使用方法

### 在 Maya 中测试

```python
from maya_integration import maya_outliner

# 创建 Outliner（默认禁用原生菜单）
outliner = maya_outliner.main()

# 在前端右键点击任意节点即可看到自定义菜单
```

### 前端使用

右键菜单会自动在节点上显示，无需额外配置。菜单项会根据节点状态自动启用/禁用。

## 特性

### 1. 自动位置调整
- 菜单会自动调整位置，确保不会超出视口边界
- 子菜单会显示在父菜单右侧

### 2. 智能禁用
- 根据节点当前状态禁用不适用的菜单项
- 例如：已显示的节点会禁用"显示"选项

### 3. 键盘支持
- ESC 键关闭菜单
- 点击菜单外部关闭菜单

### 4. Maya 风格设计
- 深色主题 (#2b2b2b 背景)
- 蓝色高亮 (#094771)
- 与 Maya UI 一致的字体和间距

## API 集成

菜单项调用以下 API 方法：

```typescript
// 基础 API
await auroraview.api.select_node(nodeName)
await auroraview.api.set_visibility(nodeName, visible)

// 扩展 API
await auroraview.api.show_only_dag_objects(nodeName)
await auroraview.api.show_shapes(nodeName)
await auroraview.api.show_selected(nodeName)
await auroraview.api.hide_in_outliner(nodeName)
await auroraview.api.delete_node(nodeName)
```

## 样式定制

菜单样式在 `ContextMenu.vue` 中定义，可以通过修改以下 CSS 变量来定制：

```css
.context-menu {
  background: #2b2b2b;        /* 菜单背景色 */
  border: 1px solid #3c3c3c;  /* 边框颜色 */
  border-radius: 4px;         /* 圆角 */
}

.context-menu-item:hover {
  background: #094771;        /* 悬停背景色 */
}
```

## 扩展菜单

要添加新的菜单项，编辑 `src/config/mayaContextMenu.ts`：

```typescript
items.push({
  label: '新菜单项',
  action: () => {
    // 执行操作
  },
  // 可选：添加子菜单
  submenu: [
    {
      label: '子菜单项',
      action: () => { /* ... */ }
    }
  ]
})
```

## 注意事项

1. 确保 Python 端已禁用原生菜单：`context_menu=False`
2. 某些菜单项需要对应的 Python API 支持
3. 占位符菜单项当前被禁用，需要实现对应的后端功能

## 下一步改进

- [ ] 添加键盘导航（方向键）
- [ ] 实现占位符菜单项的功能
- [ ] 添加菜单项图标
- [ ] 支持自定义快捷键
- [ ] 添加菜单动画效果

