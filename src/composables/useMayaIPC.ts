import { onBeforeUnmount } from 'vue'
import type { IPCEventHandler, MayaNode } from '../types'

interface AuroraBridge {
  call: <T = unknown>(method: string, params?: unknown) => Promise<T>
  on: (event: string, handler: IPCEventHandler) => () => void
  api?: Record<string, (...args: unknown[]) => Promise<unknown>>
}

declare global {
  interface Window {
    auroraview?: AuroraBridge
  }
}

/** One protocol: Promise-based RPC and AuroraView event subscriptions. */
export function useMayaIPC() {
  const subscriptions = new Map<string, Map<IPCEventHandler, () => void>>()

  const callAPI = async <T = unknown>(method: string, params?: unknown): Promise<T> => {
    const bridge = window.auroraview
    if (!bridge?.call) {
      throw new Error('Open this frontend inside Maya through AuroraView to use scene operations.')
    }
    return bridge.call<T>('api.' + method, params)
  }

  const offMayaEvent = (event: string, handler: IPCEventHandler) => {
    subscriptions.get(event)?.get(handler)?.()
    subscriptions.get(event)?.delete(handler)
  }

  const onMayaEvent = (event: string, handler: IPCEventHandler) => {
    if (!window.auroraview?.on) {
      throw new Error('AuroraView event bridge is not ready.')
    }
    if (!subscriptions.has(event)) subscriptions.set(event, new Map())
    offMayaEvent(event, handler)
    subscriptions.get(event)!.set(handler, window.auroraview.on(event, handler))
  }

  onBeforeUnmount(() => {
    subscriptions.forEach(handlers => handlers.forEach(unsubscribe => unsubscribe()))
    subscriptions.clear()
  })

  return {
    callAPI,
    getSceneHierarchy: () => callAPI<MayaNode[]>('get_scene_hierarchy'),
    selectNode: (nodeName: string) => callAPI('select_node', { node_name: nodeName }),
    setVisibility: (nodeName: string, visible: boolean) =>
      callAPI('set_visibility', { node_name: nodeName, visible }),
    onMayaEvent,
    offMayaEvent,
  }
}
