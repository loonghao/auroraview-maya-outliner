import type { IPCEventHandler } from '../types'

// Declare auroraview global API
declare global {
  interface Window {
    auroraview?: {
      api?: {
        get_scene_hierarchy?: () => Promise<any[]>
        select_node?: (node_name: string) => Promise<{ ok: boolean; message: string }>
        set_visibility?: (node_name: string, visible: boolean) => Promise<{ ok: boolean; message: string }>
      }
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

    // Check if modern API is available
    if (window.auroraview?.api) {
      console.log('[MayaIPC] ✓ AuroraView API object found')
      console.log('[MayaIPC] Available API methods:', Object.keys(window.auroraview.api))

      const apiMethod = (window.auroraview.api as any)[method]
      console.log(`[MayaIPC] API method '${method}':`, apiMethod, 'type:', typeof apiMethod)

      if (typeof apiMethod === 'function') {
        try {
          console.log(`[MayaIPC] Calling ${method} with params:`, params)
          // Call with params object - AuroraView will handle the conversion
          const result = params !== undefined ? await apiMethod(params) : await apiMethod()
          console.log('[MayaIPC] ✓ API result:', method, result)
          return result
        } catch (error) {
          console.error('[MayaIPC] ✗ API error:', method, error)
          throw error
        }
      } else {
        console.error(`[MayaIPC] ✗ Method '${method}' is not a function or not found`)
      }
    } else {
      console.error('[MayaIPC] ✗ window.auroraview.api not available')
    }

    // Fallback to legacy event-based IPC
    console.warn('[MayaIPC] Modern API not available, falling back to legacy IPC')
    return new Promise((resolve, reject) => {
      const responseEvent = `${method}_response`
      const timeout = setTimeout(() => {
        window.removeEventListener(responseEvent, handleResponse)
        reject(new Error(`API call timeout: ${method}`))
      }, 5000)

      const handleResponse = (e: Event) => {
        clearTimeout(timeout)
        window.removeEventListener(responseEvent, handleResponse)
        const customEvent = e as CustomEvent
        resolve(customEvent.detail)
      }

      window.addEventListener(responseEvent, handleResponse)
      sendToMaya(method, params)
    })
  }

  /**
   * Send a message to Maya using AuroraView's CustomEvent system (legacy)
   */
  const sendToMaya = (event: string, data: Record<string, unknown>) => {
    console.log('[MayaIPC] Sending event:', event, data)

    // AuroraView uses CustomEvent for IPC
    const customEvent = new CustomEvent(event, {
      detail: data,
    })

    window.dispatchEvent(customEvent)
  }

  /**
   * Register an event handler for Maya events
   */
  const onMayaEvent = (event: string, handler: IPCEventHandler) => {
    if (!eventHandlers.has(event)) {
      eventHandlers.set(event, new Set())

      // Register global event listener for CustomEvent
      const eventListener = (e: Event) => {
        const customEvent = e as CustomEvent
        console.log('[MayaIPC] Received event:', event, customEvent.detail)

        const handlers = eventHandlers.get(event)
        if (handlers) {
          handlers.forEach((h) => h(customEvent.detail))
        }
      }

      window.addEventListener(event, eventListener)
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
  const getSceneHierarchy = async () => {
    // No parameters needed for get_scene_hierarchy
    return callAPI<any[]>('get_scene_hierarchy')
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

