import type { ContextMenuItemOrSeparator } from '../types/contextMenu'
import type { MayaNode } from '../types'

/**
 * Get Maya Outliner context menu items for a node
 */
export function getMayaContextMenuItems(
  node: MayaNode,
  api: {
    selectNode: (nodeName: string) => Promise<any>
    setVisibility: (nodeName: string, visible: boolean) => Promise<any>
    showOnlyDagObjects?: (nodeName: string) => Promise<any>
    showShapes?: (nodeName: string) => Promise<any>
    showSelected?: (nodeName: string) => Promise<any>
    hideInOutliner?: (nodeName: string) => Promise<any>
    deleteNode?: (nodeName: string) => Promise<any>
    groupNodes?: (nodeName: string) => Promise<any>
    ungroupNodes?: (nodeName: string) => Promise<any>
    parentNodes?: (childName: string, parentName: string | null) => Promise<any>
    duplicateNode?: (nodeName: string) => Promise<any>
    renameNode?: (oldName: string, newName: string) => Promise<any>
    createQuickSelectSet?: (nodeName: string, setName: string | null) => Promise<any>
    expandAll?: () => void
    collapseAll?: () => void
  }
): ContextMenuItemOrSeparator[] {
  const items: ContextMenuItemOrSeparator[] = []

  // Check if API methods are available
  const hasExtendedAPI = !!(window as any).auroraview?.api

  // Show Only DAG Objects
  if (hasExtendedAPI && api.showOnlyDagObjects) {
    items.push({
      label: '仅显示 DAG 对象',
      action: () => api.showOnlyDagObjects!(node.name),
    })
  }

  // Shapes
  if (hasExtendedAPI && api.showShapes) {
    items.push({
      label: '形状',
      action: () => api.showShapes!(node.name),
    })
  }

  if (items.length > 0) {
    items.push({ type: 'separator' })
  }

  // Show Selected
  if (hasExtendedAPI && api.showSelected) {
    items.push({
      label: '显示选定项',
      action: () => api.showSelected!(node.name),
    })
  }

  // Hide in Outliner (with submenu)
  if (hasExtendedAPI && api.hideInOutliner) {
    items.push({
      label: '在大纲图中隐藏',
      submenu: [
        {
          label: '隐藏选定项',
          action: () => api.hideInOutliner!(node.name),
        },
      ],
    })
  }

  items.push({ type: 'separator' })

  // Group operations
  if (hasExtendedAPI && api.groupNodes) {
    items.push({
      label: '成组',
      action: () => api.groupNodes!(node.name),
    })
  }

  if (hasExtendedAPI && api.ungroupNodes) {
    items.push({
      label: '取消成组',
      action: () => api.ungroupNodes!(node.name),
    })
  }

  // Parent operations
  if (hasExtendedAPI && api.parentNodes) {
    items.push({
      label: '父级',
      submenu: [
        {
          label: '父级到世界',
          action: () => api.parentNodes!(node.name, null),
        },
      ],
    })
  }

  // Duplicate
  if (hasExtendedAPI && api.duplicateNode) {
    items.push({
      label: '复制',
      action: () => api.duplicateNode!(node.name),
    })
  }

  // Delete
  if (hasExtendedAPI && api.deleteNode) {
    items.push({
      label: '删除',
      action: () => api.deleteNode!(node.name),
    })
  }

  items.push({ type: 'separator' })

  // Reference (placeholder)
  items.push({
    label: '引用',
    submenu: [
      {
        label: '创建引用',
        action: () => {},
        disabled: true,
      },
    ],
  })

  // Scene Assembly (placeholder)
  items.push({
    label: '场景集合',
    submenu: [
      {
        label: '添加到新集合',
        action: () => {},
        disabled: true,
      },
    ],
  })

  // Sets
  items.push({
    label: '集',
    submenu: [
      {
        label: '创建快速选择集',
        action: hasExtendedAPI && api.createQuickSelectSet
          ? () => api.createQuickSelectSet!(node.name, null)
          : () => {},
        disabled: !(hasExtendedAPI && api.createQuickSelectSet),
      },
    ],
  })

  // Assets (placeholder)
  items.push({
    label: '资产',
    submenu: [
      {
        label: '分配新材质',
        action: () => {},
        disabled: true,
      },
    ],
  })

  items.push({ type: 'separator' })

  // Display
  items.push({
    label: '展示',
    submenu: [
      {
        label: '展开所有',
        action: api.expandAll || (() => {}),
        disabled: !api.expandAll,
      },
      {
        label: '折叠所有',
        action: api.collapseAll || (() => {}),
        disabled: !api.collapseAll,
      },
    ],
  })

  // Visibility
  items.push({
    label: '显示',
    submenu: [
      {
        label: '显示',
        action: () => api.setVisibility(node.name, true),
        disabled: node.visible,
      },
      {
        label: '隐藏',
        action: () => api.setVisibility(node.name, false),
        disabled: !node.visible,
      },
    ],
  })

  // Render Settings (placeholder)
  items.push({
    label: '渲染设定',
    submenu: [
      {
        label: '可渲染',
        action: () => {},
        disabled: true,
      },
    ],
  })

  return items
}

