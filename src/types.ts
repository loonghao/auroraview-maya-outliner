/**
 * Maya node types
 */
export type MayaNodeType =
  | 'transform'
  | 'mesh'
  | 'camera'
  | 'light'
  | 'group'
  | 'joint'
  | 'locator'
  | 'objectSet'
  | 'displayLayer'
  | 'renderLayer'
  | 'animLayer'
  | 'controller'
  | 'constraint'
  | 'ikHandle'
  | 'ikSolver'
  | 'cluster'
  | 'blendShape'
  | 'skinCluster'
  | 'shader'
  | 'lambert'
  | 'blinn'
  | 'phong'
  | 'file'
  | 'place2dTexture'
  | 'particleCloud'
  | 'nurbsCurve'
  | 'nurbsSurface'
  | 'curve'
  | 'unknown'

/**
 * Node type enum for better type safety (matches new design)
 */
export enum NodeType {
  TRANSFORM = 'transform',
  MESH = 'mesh',
  CAMERA = 'camera',
  LIGHT = 'light',
  JOINT = 'joint',
  CURVE = 'curve',
  GROUP = 'group',
}

/**
 * Maya scene node
 */
export interface MayaNode {
  /** Node name */
  name: string

  /** Node type */
  type: MayaNodeType

  /** Full DAG path */
  path: string

  /** Parent node name (null for root nodes) */
  parent: string | null

  /** Child nodes */
  children: MayaNode[]

  /** Visibility state */
  visible: boolean

  /** Selection state */
  selected: boolean
}

/**
 * Context menu item definition
 */
export interface ContextMenuItem {
  /** Menu item label */
  label: string
  /** Action callback */
  action: () => void
  /** Optional keyboard shortcut display */
  shortcut?: string
  /** Whether this is a separator */
  separator?: boolean
}

/**
 * Context menu state
 */
export interface ContextMenuState {
  visible: boolean
  x: number
  y: number
  targetNode: MayaNode | null
}

/**
 * Selection state for multi-selection support
 */
export interface SelectionState {
  ids: Set<string>
  lastSelectedId: string | null
}

/**
 * Drag item for drag and drop
 */
export interface DragItem {
  id: string
  type: 'NODE'
}

/**
 * IPC message from frontend to Maya
 */
export interface IPCMessage {
  /** Event name */
  event: string

  /** Event data */
  data: Record<string, unknown>
}

/**
 * IPC event handler
 */
export type IPCEventHandler = (data: unknown) => void

/**
 * Maya IPC interface
 */
export interface MayaIPC {
  /** Send message to Maya */
  sendToMaya: (event: string, data: Record<string, unknown>) => void

  /** Register event handler */
  onMayaEvent: (event: string, handler: IPCEventHandler) => void

  /** Unregister event handler */
  offMayaEvent: (event: string, handler: IPCEventHandler) => void
}

