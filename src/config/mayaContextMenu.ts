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

  // Sets (placeholder)
  items.push({
    label: '集',
    submenu: [
      {
        label: '创建快速选择集',
        action: () => {},
        disabled: true,
      },
    ],
  })

  // Assets (placeholder)
  items.push({
    label: '资产',
    submenu: [
      {
        label: '分配新资产',
        action: () => {},
        disabled: true,
      },
    ],
  })

  items.push({ type: 'separator' })

  // Display (placeholder)
  items.push({
    label: '展示',
    submenu: [
      {
        label: '展开所有',
        action: () => {},
        disabled: true,
      },
      {
        label: '折叠所有',
        action: () => {},
        disabled: true,
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

