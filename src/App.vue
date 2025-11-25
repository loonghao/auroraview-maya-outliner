<script setup lang="ts">
import { ref, onMounted, provide, watch } from 'vue'
import OutlinerTree from './components/OutlinerTree.vue'
import ContextMenu from './components/ContextMenu.vue'
import { useMayaIPC } from './composables/useMayaIPC'
import { useContextMenu } from './composables/useContextMenu'
import { useResponsiveScale } from './composables/useResponsiveScale'
import { getMayaContextMenuItems } from './config/mayaContextMenu'
import { EventDataAdapter } from './utils/eventAdapter'
import { storage } from './utils/storage'
import type { MayaNode } from './types'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'

const { getSceneHierarchy, selectNode, setVisibility, onMayaEvent, callAPI } = useMayaIPC()
const contextMenu = useContextMenu()

// Responsive scaling with intelligent auto-zoom
const { scaleStyle, updateDimensions } = useResponsiveScale({
  baseWidth: 800,   // Design base width
  baseHeight: 600,  // Design base height
  minScale: 0.5,    // Minimum 50% zoom
  maxScale: 1.5,    // Maximum 150% zoom
  smoothTransition: true,
  throttleDelay: 16 // ~60fps for balanced performance (avoid UI blocking)
})

const sceneData = ref<MayaNode[]>([])
const selectedNode = ref<string | null>(null)
const selectedNodes = ref<Set<string>>(new Set()) // Multi-selection support
const searchQuery = ref('')
const isConnected = ref(false)
const isUpdating = ref(false)

// Display filters
const showDAGOnly = ref(false) // Show DAG objects only (default: show all)
const showHidden = ref(true) // Show hidden objects (default: show all)

// Tree expansion state
const expandAllTrigger = ref(0)
const collapseAllTrigger = ref(0)

// Provide expansion triggers to child components
provide('expandAllTrigger', expandAllTrigger)
provide('collapseAllTrigger', collapseAllTrigger)

const expandAll = () => {
  expandAllTrigger.value++
}

const collapseAll = () => {
  collapseAllTrigger.value++
}

// Load preferences from IndexedDB
const loadPreferences = async () => {
  try {
    const prefs = await storage.getAll()

    if (prefs.showDAGOnly !== undefined) {
      showDAGOnly.value = prefs.showDAGOnly
    }
    if (prefs.showHidden !== undefined) {
      showHidden.value = prefs.showHidden
    }
    if (prefs.windowWidth && prefs.windowHeight) {
      // Notify Python backend to resize window
      try {
        await callAPI('resize_window', {
          width: prefs.windowWidth,
          height: prefs.windowHeight
        })
      } catch (error) {
        console.error('[App] Failed to restore window size:', error)
      }
    }
  } catch (error) {
    console.error('[App] Failed to load preferences:', error)
  }
}

// Save preferences to IndexedDB with debouncing
let saveTimeout: number | null = null
const savePreferences = () => {
  if (saveTimeout) {
    clearTimeout(saveTimeout)
  }

  saveTimeout = window.setTimeout(async () => {
    try {
      await storage.set('showDAGOnly', showDAGOnly.value)
      await storage.set('showHidden', showHidden.value)
    } catch (error) {
      console.error('[App] Failed to save preferences:', error)
    }
  }, 500) // Debounce 500ms
}

// Watch for preference changes and save them
watch([showDAGOnly, showHidden], () => {
  savePreferences()
})

// Save window size when it changes (debounced to avoid excessive IndexedDB writes)
let saveWindowSizeTimeout: number | null = null
const saveWindowSize = async (width: number, height: number) => {
  // Clear previous timeout
  if (saveWindowSizeTimeout) {
    clearTimeout(saveWindowSizeTimeout)
  }

  // Debounce IndexedDB writes (500ms after last resize)
  saveWindowSizeTimeout = window.setTimeout(async () => {
    try {
      await storage.set('windowWidth', width)
      await storage.set('windowHeight', height)
      console.log('[App] Window size saved to IndexedDB:', { width, height })
    } catch (error) {
      console.error('[App] Failed to save window size:', error)
    }
  }, 500)
}

onMounted(async () => {
  // Load saved preferences
  await loadPreferences()

  // Wait for AuroraView API to be ready
  const waitForAPI = async (maxAttempts = 50, interval = 100) => {
    for (let i = 0; i < maxAttempts; i++) {
      if (window.auroraview?.api) {
        return true
      }
      await new Promise(resolve => setTimeout(resolve, interval))
    }
    return false
  }

  const apiReady = await waitForAPI()
  if (!apiReady) {
    return
  }

  // Request initial scene data using modern API
  try {
    const hierarchy = await getSceneHierarchy()
    sceneData.value = hierarchy
    isConnected.value = true
  } catch (error) {
    console.error('[App] Failed to load scene hierarchy:', error)
  }

  // Listen for scene updates from Maya (push notifications)
  onMayaEvent('scene_updated', (data: unknown) => {
    isUpdating.value = true

    const nodes = EventDataAdapter.extractArray<MayaNode>(data, 'nodes', 'value', 'data')
    sceneData.value = nodes
    isConnected.value = true

    // Clear updating indicator after a short delay
    setTimeout(() => {
      isUpdating.value = false
    }, 300)
  })

  onMayaEvent('selection_changed', (data: unknown) => {
    const node = EventDataAdapter.extractString(data, 'node', 'name')
    selectedNode.value = node
  })

  // Listen for window resize events from backend
  let lastResizeEventTime = 0
  let resizeEventCount = 0

  onMayaEvent('window_resized', (data: any) => {
    const now = performance.now()
    const timeSinceLastEvent = now - lastResizeEventTime
    resizeEventCount++

    console.log(`[App.vue] window_resized #${resizeEventCount} (Δ${timeSinceLastEvent.toFixed(1)}ms):`, data)

    const width = data?.width
    const height = data?.height

    if (width && height) {
      const updateStart = performance.now()

      // Update responsive scale dimensions immediately for smooth animation
      // In embedded webview, window.innerWidth/innerHeight may not update correctly
      updateDimensions(width, height)

      const updateTime = performance.now() - updateStart
      console.log(`[App.vue] updateDimensions completed in ${updateTime.toFixed(2)}ms`)

      // Save window size to IndexedDB (debounced to avoid excessive writes)
      saveWindowSize(width, height)
    } else {
      console.warn('[App.vue] Invalid dimensions received:', { width, height })
    }

    lastResizeEventTime = now
  })

  // Keyboard shortcuts
  window.addEventListener('keydown', handleKeyDown)
})

const handleKeyDown = async (event: KeyboardEvent) => {
  // Ctrl+G: Group selected nodes
  if ((event.ctrlKey || event.metaKey) && event.key === 'g' && selectedNode.value) {
    event.preventDefault()
    try {
      await callAPI('group_nodes', { node_name: selectedNode.value })
      // Refresh scene
      const result = await getSceneHierarchy()
      if (result) {
        sceneData.value = result
      }
    } catch (error) {
      console.error('[App] Failed to group nodes:', error)
    }
    return
  }

  // Ctrl+Shift+G: Ungroup selected nodes
  if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'G' && selectedNode.value) {
    event.preventDefault()
    try {
      await callAPI('ungroup_nodes', { node_name: selectedNode.value })
      // Refresh scene
      const result = await getSceneHierarchy()
      if (result) {
        sceneData.value = result
      }
    } catch (error) {
      console.error('[App] Failed to ungroup nodes:', error)
    }
    return
  }

  // Ctrl+D: Duplicate selected node
  if ((event.ctrlKey || event.metaKey) && event.key === 'd' && selectedNode.value) {
    event.preventDefault()
    try {
      await callAPI('duplicate_node', { node_name: selectedNode.value })
      // Refresh scene
      const result = await getSceneHierarchy()
      if (result) {
        sceneData.value = result
      }
    } catch (error) {
      console.error('[App] Failed to duplicate node:', error)
    }
    return
  }

  // Ctrl+P: Parent to world
  if ((event.ctrlKey || event.metaKey) && event.key === 'p' && selectedNode.value) {
    event.preventDefault()
    try {
      await callAPI('parent_nodes', { child_name: selectedNode.value, parent_name: null })
      // Refresh scene
      const result = await getSceneHierarchy()
      if (result) {
        sceneData.value = result
      }
    } catch (error) {
      console.error('[App] Failed to parent to world:', error)
    }
    return
  }

  // Delete: Delete selected node(s)
  if (event.key === 'Delete' && selectedNode.value) {
    event.preventDefault()
    try {
      if (selectedNodes.value.size > 1) {
        // Delete multiple nodes
        for (const nodeName of selectedNodes.value) {
          await callAPI('delete_node', { node_name: nodeName })
        }
      } else {
        // Delete single node
        await callAPI('delete_node', { node_name: selectedNode.value })
      }
      // Refresh scene
      const result = await getSceneHierarchy()
      if (result) {
        sceneData.value = result
      }
      selectedNode.value = null
      selectedNodes.value.clear()
    } catch (error) {
      console.error('[App] Failed to delete node:', error)
    }
  }
}

const handleNodeSelect = async (nodeName: string, event?: MouseEvent) => {
  // Multi-selection support
  if (event?.ctrlKey || event?.metaKey) {
    // Ctrl/Cmd + Click: Toggle selection
    if (selectedNodes.value.has(nodeName)) {
      selectedNodes.value.delete(nodeName)
    } else {
      selectedNodes.value.add(nodeName)
    }
    selectedNode.value = nodeName // Keep last selected as primary
  } else if (event?.shiftKey && selectedNode.value) {
    // Shift + Click: Range selection (TODO: implement range logic)
    selectedNodes.value.add(selectedNode.value)
    selectedNodes.value.add(nodeName)
    selectedNode.value = nodeName
  } else {
    // Normal click: Single selection
    selectedNodes.value.clear()
    selectedNodes.value.add(nodeName)
    selectedNode.value = nodeName
  }

  try {
    // Select all nodes in Maya
    if (selectedNodes.value.size > 1) {
      await callAPI('select_multiple_nodes', {
        node_names: Array.from(selectedNodes.value)
      })
    } else {
      await selectNode(nodeName)
    }
  } catch (error) {
    console.error('[App] Failed to select node:', error)
  }
}

const handleNodeRename = async (oldName: string, newName: string) => {
  try {
    await callAPI('rename_node', { old_name: oldName, new_name: newName })
    // Refresh scene hierarchy after rename
    const result = await getSceneHierarchy()
    if (result) {
      sceneData.value = result
    }
  } catch (error) {
    console.error('[App] Failed to rename node:', error)
  }
}

const handleVisibilityToggle = async (nodeName: string, visible: boolean) => {
  try {
    await setVisibility(nodeName, visible)
  } catch (error) {
    console.error('[App] Failed to toggle visibility:', error)
  }
}

const handleNodeParent = async (childName: string, parentName: string | null) => {
  try {
    await callAPI('parent_nodes', { child_name: childName, parent_name: parentName })
    // Refresh scene hierarchy
    const result = await getSceneHierarchy()
    if (result) {
      sceneData.value = result
    }
  } catch (error) {
    console.error('[App] Failed to parent node:', error)
  }
}

const handleContextMenu = (event: MouseEvent, node: MayaNode) => {

  // Get extended API methods if available
  const api = {
    selectNode,
    setVisibility,
    showOnlyDagObjects: async (nodeName: string) => {
      return callAPI('show_only_dag_objects', { node_name: nodeName })
    },
    showShapes: async (nodeName: string) => {
      return callAPI('show_shapes', { node_name: nodeName })
    },
    showSelected: async (nodeName: string) => {
      return callAPI('show_selected', { node_name: nodeName })
    },
    hideInOutliner: async (nodeName: string) => {
      return callAPI('hide_in_outliner', { node_name: nodeName })
    },
    deleteNode: async (nodeName: string) => {
      return callAPI('delete_node', { node_name: nodeName })
    },
    groupNodes: async (nodeName: string) => {
      return callAPI('group_nodes', { node_name: nodeName })
    },
    ungroupNodes: async (nodeName: string) => {
      return callAPI('ungroup_nodes', { node_name: nodeName })
    },
    parentNodes: async (childName: string, parentName: string | null) => {
      return callAPI('parent_nodes', { child_name: childName, parent_name: parentName })
    },
    duplicateNode: async (nodeName: string) => {
      return callAPI('duplicate_node', { node_name: nodeName })
    },
    renameNode: async (oldName: string, newName: string) => {
      return callAPI('rename_node', { old_name: oldName, new_name: newName })
    },
    createQuickSelectSet: async (nodeName: string, setName: string | null) => {
      return callAPI('create_quick_select_set', { node_name: nodeName, set_name: setName })
    },
    expandAll,
    collapseAll,
  }

  const menuItems = getMayaContextMenuItems(node, api)
  contextMenu.show(event.clientX, event.clientY, menuItems)
}

</script>

<template>
  <div class="app-wrapper">
    <!-- Edge buffer zones to prevent WebView from capturing resize events -->
    <div class="edge-buffer edge-buffer-top"></div>
    <div class="edge-buffer edge-buffer-right"></div>
    <div class="edge-buffer edge-buffer-bottom"></div>
    <div class="edge-buffer edge-buffer-left"></div>
    <div class="edge-buffer edge-buffer-top-left"></div>
    <div class="edge-buffer edge-buffer-top-right"></div>
    <div class="edge-buffer edge-buffer-bottom-left"></div>
    <div class="edge-buffer edge-buffer-bottom-right"></div>

    <div class="app-container" :style="scaleStyle">
      <header class="app-header">
      <div class="app-header-inner">
        <div class="app-title-block">
          <h1 class="app-title">Maya Outliner</h1>
          <p class="app-subtitle">AuroraView scene hierarchy</p>
        </div>
        <div class="status-badges">
          <Badge
            :variant="isConnected ? 'default' : 'outline'"
            class="connection-status"
            :class="{ connected: isConnected }"
          >
            <span class="status-dot"></span>
            <span class="status-label">
              {{ isConnected ? 'Connected' : 'Disconnected' }}
            </span>
          </Badge>
          <Badge
            v-if="isUpdating"
            variant="secondary"
            class="updating-status"
          >
            <span class="updating-spinner"></span>
            <span class="status-label">Updating...</span>
          </Badge>
        </div>
      </div>
    </header>

    <div class="search-bar">
      <Input
        v-model="searchQuery"
        type="text"
        placeholder="Search nodes..."
        class="search-input"
      />
      <div class="filter-options">
        <label class="filter-checkbox">
          <input type="checkbox" v-model="showDAGOnly" />
          <span>DAG Objects Only</span>
        </label>
        <label class="filter-checkbox">
          <input type="checkbox" v-model="showHidden" />
          <span>Show Hidden</span>
        </label>
      </div>
    </div>

    <main class="app-main">
      <Card class="app-card">
        <CardContent class="app-card-content">
          <ScrollArea class="tree-scroll-area">
            <OutlinerTree
              :nodes="sceneData"
              :selected-node="selectedNode"
              :search-query="searchQuery"
              :show-dag-only="showDAGOnly"
              :show-hidden="showHidden"
              @node-select="handleNodeSelect"
              @node-rename="handleNodeRename"
              @visibility-toggle="handleVisibilityToggle"
              @context-menu="handleContextMenu"
              @node-parent="handleNodeParent"
            />
          </ScrollArea>
        </CardContent>
      </Card>
    </main>

    <footer class="app-footer">
      <p>AuroraView Maya Outliner Example</p>
      <p class="stats">
        Nodes: {{ sceneData.length }} | Selected: {{ selectedNode || 'None' }}
      </p>
    </footer>

    <!-- Context Menu -->
    <ContextMenu
      :visible="contextMenu.visible.value"
      :x="contextMenu.position.value.x"
      :y="contextMenu.position.value.y"
      :items="contextMenu.items.value"
      @close="contextMenu.hide"
    />
    </div>
  </div>
</template>

<style scoped>
/* Wrapper for scaling - fills entire viewport */
.app-wrapper {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  position: relative;
  background: #020617;
  /* Eliminate white edges */
  margin: 0;
  padding: 0;
  border: none;
  outline: none;
  /* Force full coverage */
  box-sizing: border-box;
  /* Add subtle border to indicate resize area */
  box-shadow: inset 0 0 0 1px rgba(148, 163, 184, 0.1);
}

/* Edge buffer zones - transparent overlays that block WebView mouse events */
/* This allows Qt to handle window resize operations at the edges */
.edge-buffer {
  position: fixed;
  pointer-events: auto; /* Capture mouse events */
  z-index: 9999; /* Above all content */
  background: transparent; /* Invisible but interactive */

  /* Debug mode: uncomment to visualize buffer zones */
  /* background: rgba(255, 0, 0, 0.1); */
  /* border: 1px solid rgba(255, 0, 0, 0.3); */
}

/* Top edge */
.edge-buffer-top {
  top: 0;
  left: 0;
  right: 0;
  height: 12px;
}

/* Right edge */
.edge-buffer-right {
  top: 0;
  right: 0;
  bottom: 0;
  width: 12px;
}

/* Bottom edge */
.edge-buffer-bottom {
  bottom: 0;
  left: 0;
  right: 0;
  height: 12px;
}

/* Left edge */
.edge-buffer-left {
  top: 0;
  left: 0;
  bottom: 0;
  width: 12px;
}

/* Corner buffers - larger hit areas for easier corner resizing */
.edge-buffer-top-left {
  top: 0;
  left: 0;
  width: 24px;
  height: 24px;
}

.edge-buffer-top-right {
  top: 0;
  right: 0;
  width: 24px;
  height: 24px;
}

.edge-buffer-bottom-left {
  bottom: 0;
  left: 0;
  width: 24px;
  height: 24px;
}

.edge-buffer-bottom-right {
  bottom: 0;
  right: 0;
  width: 24px;
  height: 24px;
}

/* Container that gets scaled */
.app-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  padding: 0;
  background: #020617; /* Solid background to prevent white flash */
  color: #e5e7eb;
  /* GPU acceleration hints */
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  transform-style: preserve-3d;
  -webkit-transform-style: preserve-3d;
}

.app-header {
  border-radius: 0;
  padding: clamp(0.7rem, 0.55rem + 0.4vw, 1rem)
    clamp(1rem, 0.8rem + 1.2vw, 1.8rem);
  background: rgba(15, 23, 42, 0.98);
  border: none;
  border-bottom: 1px solid rgba(148, 163, 184, 0.55);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.85);
  margin: 0;
}

.app-header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: clamp(0.75rem, 0.5rem + 0.8vw, 1.5rem);
}

.app-title-block {
  display: flex;
  flex-direction: column;
  gap: clamp(0.15rem, 0.1rem + 0.2vw, 0.35rem);
}

.app-title {
  margin: 0;
  font-size: clamp(1.1rem, 0.95rem + 0.6vw, 1.6rem);
  font-weight: 600;
  letter-spacing: 0.02em;
}

.app-subtitle {
  margin: 0;
  font-size: clamp(0.7rem, 0.65rem + 0.2vw, 0.85rem);
  color: #94a3b8;
}

.connection-status {
  display: inline-flex;
  align-items: center;
  gap: clamp(0.35rem, 0.3rem + 0.1vw, 0.5rem);
  padding: clamp(0.35rem, 0.3rem + 0.1vw, 0.5rem)
    clamp(0.75rem, 0.6rem + 0.4vw, 1.2rem);
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.5);
  font-size: clamp(0.7rem, 0.65rem + 0.15vw, 0.85rem);
}

.status-dot {
  width: clamp(0.35rem, 0.3rem + 0.1vw, 0.5rem);
  height: clamp(0.35rem, 0.3rem + 0.1vw, 0.5rem);
  border-radius: 999px;
  background: #f97373;
  box-shadow: 0 0 0 1px rgba(15, 23, 42, 0.9);
}

.connection-status.connected .status-dot {
  background: #4ade80;
}

.status-label {
  white-space: nowrap;
}

.status-badges {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.updating-status {
  display: inline-flex;
  align-items: center;
  gap: clamp(0.35rem, 0.3rem + 0.1vw, 0.5rem);
  padding: clamp(0.35rem, 0.3rem + 0.1vw, 0.5rem)
    clamp(0.75rem, 0.6rem + 0.4vw, 1.2rem);
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  font-size: clamp(0.7rem, 0.65rem + 0.15vw, 0.85rem);
  color: #60a5fa;
}

.updating-spinner {
  width: clamp(0.35rem, 0.3rem + 0.1vw, 0.5rem);
  height: clamp(0.35rem, 0.3rem + 0.1vw, 0.5rem);
  border: 2px solid rgba(59, 130, 246, 0.3);
  border-top-color: #60a5fa;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.search-bar {
  margin: 0;
  padding: clamp(0.5rem, 0.35rem + 0.6vw, 1rem) clamp(1rem, 0.8rem + 1.2vw, 1.8rem);
  display: flex;
  flex-direction: column;
  gap: clamp(0.5rem, 0.4rem + 0.3vw, 0.8rem);
  background: rgba(15, 23, 42, 0.5);
  border-bottom: 1px solid rgba(148, 163, 184, 0.3);
}

.search-input {
  width: 100%;
  padding: clamp(0.55rem, 0.45rem + 0.3vw, 0.9rem)
    clamp(0.75rem, 0.6rem + 0.6vw, 1.4rem);
  background: rgba(15, 23, 42, 0.98);
  border: 1px solid rgba(51, 65, 85, 1);
  border-radius: clamp(0.55rem, 0.45rem + 0.3vw, 0.9rem);
  color: #e5e7eb;
  font-size: clamp(0.78rem, 0.72rem + 0.2vw, 0.9rem);
}

.search-input::placeholder {
  color: #64748b;
}

.search-input:focus {
  outline: none;
  border-color: #38bdf8;
  box-shadow: 0 0 0 1px rgba(56, 189, 248, 0.35);
}

.filter-options {
  display: flex;
  gap: clamp(1rem, 0.8rem + 0.5vw, 1.5rem);
  padding: clamp(0.4rem, 0.3rem + 0.2vw, 0.6rem) clamp(0.5rem, 0.4rem + 0.3vw, 0.8rem);
  background: rgba(15, 23, 42, 0.6);
  border-radius: clamp(0.4rem, 0.3rem + 0.2vw, 0.6rem);
}

.filter-checkbox {
  display: flex;
  align-items: center;
  gap: clamp(0.35rem, 0.3rem + 0.1vw, 0.5rem);
  font-size: clamp(0.75rem, 0.7rem + 0.15vw, 0.85rem);
  color: #cbd5e1;
  cursor: pointer;
  user-select: none;
}

.filter-checkbox input[type="checkbox"] {
  width: clamp(0.9rem, 0.8rem + 0.2vw, 1.1rem);
  height: clamp(0.9rem, 0.8rem + 0.2vw, 1.1rem);
  cursor: pointer;
  accent-color: #38bdf8;
}

.filter-checkbox:hover {
  color: #e5e7eb;
}

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin: 0;
  padding: clamp(0.6rem, 0.45rem + 0.5vw, 1rem) clamp(1rem, 0.8rem + 1.2vw, 1.8rem);
  min-height: 0; /* Critical for flex children to shrink */
}

.app-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-radius: 0;
  background: rgba(15, 23, 42, 0.98);
  border: none;
  box-shadow: none;
  padding: 0;
  overflow: hidden;
  min-height: 0; /* Critical for flex children to shrink */
}

.app-card-content {
  padding: 0 !important;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0; /* Critical for flex children to shrink */
}

.tree-scroll-area {
  flex: 1;
  min-height: 0; /* Critical for flex children to shrink */
}

.app-footer {
  margin: 0;
  padding: clamp(0.55rem, 0.45rem + 0.3vw, 0.85rem)
    clamp(0.8rem, 0.65rem + 0.7vw, 1.6rem);
  border-radius: 0;
  background: rgba(15, 23, 42, 0.98);
  border: none;
  border-top: 1px solid rgba(30, 64, 175, 0.6);
  font-size: clamp(0.7rem, 0.65rem + 0.15vw, 0.85rem);
  color: #94a3b8;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: clamp(0.35rem, 0.3rem + 0.2vw, 0.75rem);
}

.stats {
  margin: 0;
  color: #64748b;
}
</style>

