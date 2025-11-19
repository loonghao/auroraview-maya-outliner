/**
 * Context menu types for Maya Outliner
 */

export interface ContextMenuItem {
  /** Menu item label */
  label: string

  /** Menu item action */
  action?: () => void | Promise<void>

  /** Submenu items */
  submenu?: ContextMenuItem[]

  /** Whether the item is disabled */
  disabled?: boolean

  /** Icon for the menu item (optional) */
  icon?: string

  /** Keyboard shortcut hint (optional) */
  shortcut?: string
}

export interface ContextMenuSeparator {
  type: 'separator'
}

export type ContextMenuItemOrSeparator = ContextMenuItem | ContextMenuSeparator

export interface ContextMenuPosition {
  x: number
  y: number
}

export interface ContextMenuState {
  visible: boolean
  position: ContextMenuPosition
  items: ContextMenuItemOrSeparator[]
  activeSubmenuIndex: number | null
}

