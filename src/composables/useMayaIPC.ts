import type { IPCEventHandler } from '../types'

// Declare auroraview global API
declare global {
  interface Window {
    auroraview?: {
      api?: Record<string, any>  // API methods are dynamically bound
      emit?: (event: string, data: any) => void
    }
  }
}

/**
 * Maya IPC communication composable
 *
 * This composable provides a bridge between the Vue frontend and Maya backend
 * using AuroraView's modern API system.
 *
 * Modern API (recommended):
 * - Call Python methods: await window.auroraview.api.method_name(args)
 * - Receive events: window.addEventListener(eventName, (e) => { ... e.detail ... })
 *
 * Legacy IPC (fallback):
 * - Send to Python: window.dispatchEvent(new CustomEvent(eventName, { detail: data }))
 * - Receive from Python: window.addEventListener(eventName, (e) => { ... e.detail ... })
 */
export function useMayaIPC() {
  // Event handlers registry
  const eventHandlers = new Map<string, Set<IPCEventHandler>>()

  /**
   * Call a Python API method (modern approach)
   *
   * AuroraView parameter passing rules:
   * - If params is a dict: Python receives **params (keyword arguments)
   * - If params is a list: Python receives *params (positional arguments)
   * - If params is a single value: Python receives params (single argument)
   */
  const callAPI = async <T = any>(method: string, params?: any): Promise<T> => {
    console.log('[MayaIPC] Calling API:', method, 'with params:', params)
    console.log('[MayaIPC] window.auroraview:', window.auroraview)
    console.log('[MayaIPC] window.auroraview?.api:', window.auroraview?.api)

    if (!window.auroraview?.api) {
      throw new Error('[MayaIPC] window.auroraview.api not available')
    }

    console.log('[MayaIPC] ✓ AuroraView API object found')
    console.log('[MayaIPC] Available API methods:', Object.keys(window.auroraview.api))

    const apiMethod = (window.auroraview.api as any)[method]
    console.log(`[MayaIPC] API method '${method}':`, apiMethod, 'type:', typeof apiMethod)

    if (typeof apiMethod !== 'function') {
      throw new Error(`[MayaIPC] Method '${method}' is not a function or not found on auroraview.api`)
    }

    try {
      console.log(`[MayaIPC] Calling ${method} with params:`, params)
      const result = params !== undefined ? await apiMethod(params) : await apiMethod()
      console.log('[MayaIPC] ✓ API result:', method, result)
      return result as T
    } catch (error) {
      console.error('[MayaIPC] ✗ API error:', method, error)
      throw error
    }
  }

  /**
   * Send a message to Maya using AuroraView IPC (legacy / compatibility path).
   *
   * Prefer auroraview.api.* where possible; this is only used as a fallback when
   * window.auroraview.api is not available.
   */
  const sendToMaya = (event: string, data: Record<string, unknown> = {}) => {
    const payload = data ?? {}
    console.log('[MayaIPC] Sending event:', event, payload)

    // 1) Preferred: high-level AuroraView bridge
    if ((window as any).auroraview && typeof (window as any).auroraview.send_event === 'function') {
      console.log('[MayaIPC] -> via auroraview.send_event')
      ;(window as any).auroraview.send_event(event, payload)
      return
    }

    // 2) Fallback: low-level window.ipc.postMessage (older AuroraView builds)
    if ((window as any).ipc && typeof (window as any).ipc.postMessage === 'function') {
      console.log('[MayaIPC] -> via window.ipc.postMessage')
      ;(window as any).ipc.postMessage(
        JSON.stringify({
          type: 'event',
          event,
          detail: payload,
        }),
      )
      return
    }

    // 3) Final fallback: local CustomEvent only (no Python backend)
    console.warn('[MayaIPC] No AuroraView IPC bridge detected, using window.dispatchEvent only')
    const customEvent = new CustomEvent(event, {
      detail: payload,
    })

    window.dispatchEvent(customEvent)
  }

  /**
   * Register an event handler for Maya events
   */
  const onMayaEvent = (event: string, handler: IPCEventHandler) => {
    if (!eventHandlers.has(event)) {
      eventHandlers.set(event, new Set())

      // Prefer AuroraView's high-level event API when available
      const dispatchToHandlers = (payload: unknown) => {
        console.log('[MayaIPC] Received event:', event, payload)
        const handlers = eventHandlers.get(event)
        if (handlers) {
          handlers.forEach((h) => h(payload))
        }
      }

      // Debug: Check what's available on window.auroraview
      console.log('[MayaIPC] Checking event registration for:', event)
      console.log('[MayaIPC] window.auroraview:', window.auroraview)
      console.log('[MayaIPC] window.auroraview.on:', (window.auroraview as any)?.on)
      console.log('[MayaIPC] typeof window.auroraview.on:', typeof (window.auroraview as any)?.on)

      if (window.auroraview && typeof (window.auroraview as any).on === 'function') {
        console.log('[MayaIPC] ✓ Registering handler via window.auroraview.on for event:', event)
        ;(window.auroraview as any).on(event, (payload: unknown) => {
          console.log('[MayaIPC] ✓ Event received via auroraview.on:', event, payload)
          dispatchToHandlers(payload)
        })
      } else {
        console.log('[MayaIPC] ⚠ window.auroraview.on not available, using window.addEventListener for event:', event)
        const eventListener = (e: Event) => {
          const customEvent = e as CustomEvent
          console.log('[MayaIPC] ✓ Event received via window.addEventListener:', event, customEvent.detail)
          dispatchToHandlers(customEvent.detail)
        }
        window.addEventListener(event, eventListener)
      }
    }

    eventHandlers.get(event)!.add(handler)
  }

  /**
   * Unregister an event handler
   */
  const offMayaEvent = (event: string, handler: IPCEventHandler) => {
    const handlers = eventHandlers.get(event)
    if (handlers) {
      handlers.delete(handler)
      if (handlers.size === 0) {
        eventHandlers.delete(event)
      }
    }
  }

  /**
   * Helper methods for common Maya operations
   */
  /**
   * Get scene hierarchy using the modern auroraview.api.get_scene_hierarchy API.
   *
   * We intentionally do not implement any legacy fallback here so that
   * debugging can focus purely on the modern Promise-based bridge.
   */
  const getSceneHierarchy = async () => {
    console.log('[MayaIPC] getSceneHierarchy: checking window.auroraview...')
    console.log('[MayaIPC] window.auroraview:', window.auroraview)
    console.log('[MayaIPC] window.auroraview?.api:', window.auroraview?.api)
    console.log('[MayaIPC] typeof window.auroraview?.api:', typeof window.auroraview?.api)

    if (!window.auroraview?.api) {
      throw new Error('[MayaIPC] window.auroraview.api is not available')
    }

    console.log('[MayaIPC] Accessing window.auroraview.api.get_scene_hierarchy...')
    const apiMethod = window.auroraview.api.get_scene_hierarchy
    console.log('[MayaIPC] apiMethod:', apiMethod)
    console.log('[MayaIPC] typeof apiMethod:', typeof apiMethod)

    if (typeof apiMethod !== 'function') {
      console.error('[MayaIPC] ✗ get_scene_hierarchy is not a function!')
      console.error('[MayaIPC] Available keys on window.auroraview.api:', Object.keys(window.auroraview.api))
      throw new Error('[MayaIPC] auroraview.api.get_scene_hierarchy is not available')
    }

    console.log('[MayaIPC] getSceneHierarchy: calling auroraview.api.get_scene_hierarchy()')
    const result = await apiMethod()
    console.log(
      '[MayaIPC] getSceneHierarchy: modern API returned',
      Array.isArray(result) ? result.length : 'unknown',
      'root nodes',
    )
    return result
  }

  const selectNode = async (nodeName: string) => {
    // Pass as named parameter object
    return callAPI<{ ok: boolean; message: string }>('select_node', { node_name: nodeName })
  }

  const setVisibility = async (nodeName: string, visible: boolean) => {
    // Pass as named parameter object
    return callAPI<{ ok: boolean; message: string }>('set_visibility', {
      node_name: nodeName,
      visible: visible,
    })
  }

  return {
    // Modern API
    callAPI,
    getSceneHierarchy,
    selectNode,
    setVisibility,
    // Legacy IPC
    sendToMaya,
    onMayaEvent,
    offMayaEvent,
  }
}

