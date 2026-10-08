import type { ContextMenuItemOrSeparator } from '../types/contextMenu'
import type { MayaNode } from '../types'

/** Only commands implemented by the tutorial backend are shown. */
export function getMayaContextMenuItems(
  node: MayaNode,
  api: {
    selectNode: (name: string) => Promise<unknown>
    setVisibility: (name: string, visible: boolean) => Promise<unknown>
    deleteNode?: (name: string) => Promise<unknown>
    groupNodes?: (name: string) => Promise<unknown>
    ungroupNodes?: (name: string) => Promise<unknown>
    parentNodes?: (child: string, parent: string | null) => Promise<unknown>
    duplicateNode?: (name: string) => Promise<unknown>
    renameNode?: (oldName: string, newName: string) => Promise<unknown>
    createQuickSelectSet?: (name: string, setName: string | null) => Promise<unknown>
    expandAll?: () => void
    collapseAll?: () => void
  }
): ContextMenuItemOrSeparator[] {
  const run = (operation: () => Promise<unknown>) => async (): Promise<void> => {
    await operation()
  }
  const items: ContextMenuItemOrSeparator[] = [
    { label: 'Select', action: run(() => api.selectNode(node.path)) },
    { label: node.visible ? 'Hide' : 'Show', action: run(() => api.setVisibility(node.path, !node.visible)) },
    { type: 'separator' },
  ]
  if (api.groupNodes) items.push({ label: 'Group', action: run(() => api.groupNodes!(node.path)) })
  if (api.ungroupNodes && node.children.length) {
    items.push({ label: 'Ungroup', action: run(() => api.ungroupNodes!(node.path)) })
  }
  if (api.parentNodes && node.parent) {
    items.push({ label: 'Parent to world', action: run(() => api.parentNodes!(node.path, null)) })
  }
  if (api.duplicateNode) items.push({ label: 'Duplicate', action: run(() => api.duplicateNode!(node.path)) })
  if (api.deleteNode) items.push({ label: 'Delete', action: run(() => api.deleteNode!(node.path)) })
  if (api.createQuickSelectSet) {
    items.push({ label: 'Create selection set', action: run(() => api.createQuickSelectSet!(node.path, null)) })
  }
  if (api.expandAll) items.push({ label: 'Expand all', action: api.expandAll })
  if (api.collapseAll) items.push({ label: 'Collapse all', action: api.collapseAll })
  return items
}
