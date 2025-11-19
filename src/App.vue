<script setup lang="ts">
import { ref, onMounted } from 'vue'
import OutlinerTree from './components/OutlinerTree.vue'
import ContextMenu from './components/ContextMenu.vue'
import { useMayaIPC } from './composables/useMayaIPC'
import { useContextMenu } from './composables/useContextMenu'
import { getMayaContextMenuItems } from './config/mayaContextMenu'
import { EventDataAdapter } from './utils/eventAdapter'
import type { MayaNode } from './types'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'

const { getSceneHierarchy, selectNode, setVisibility, onMayaEvent, callAPI } = useMayaIPC()
const contextMenu = useContextMenu()
const sceneData = ref<MayaNode[]>([])
const selectedNode = ref<string | null>(null)
const searchQuery = ref('')
const isConnected = ref(false)
const isUpdating = ref(false)

onMounted(async () => {
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
})

const handleNodeSelect = async (nodeName: string) => {
  selectedNode.value = nodeName
  try {
    await selectNode(nodeName)
  } catch (error) {
    console.error('[App] Failed to select node:', error)
  }
}

const handleVisibilityToggle = async (nodeName: string, visible: boolean) => {
  try {
    await setVisibility(nodeName, visible)
  } catch (error) {
    console.error('[App] Failed to toggle visibility:', error)
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
  }

  const menuItems = getMayaContextMenuItems(node, api)
  contextMenu.show(event.clientX, event.clientY, menuItems)
}

</script>

<template>
  <div class="app-container">
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
    </div>

    <main class="app-main">
      <Card class="app-card">
        <CardContent class="app-card-content">
          <ScrollArea class="tree-scroll-area">
            <OutlinerTree
              :nodes="sceneData"
              :selected-node="selectedNode"
              :search-query="searchQuery"
              @node-select="handleNodeSelect"
              @visibility-toggle="handleVisibilityToggle"
              @context-menu="handleContextMenu"
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
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  padding: clamp(0.75rem, 0.5rem + 1vw, 1.5rem);
  background: radial-gradient(circle at top, #020617, #020617 40%, #020617 100%);
  color: #e5e7eb;
}

.app-header {
  border-radius: clamp(0.75rem, 0.6rem + 0.4vw, 1.1rem);
  padding: clamp(0.7rem, 0.55rem + 0.4vw, 1rem)
    clamp(1rem, 0.8rem + 1.2vw, 1.8rem);
  background: rgba(15, 23, 42, 0.98);
  border: 1px solid rgba(148, 163, 184, 0.55);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.85);
  margin-bottom: clamp(0.75rem, 0.5rem + 0.8vw, 1.3rem);
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
  margin-top: clamp(0.5rem, 0.35rem + 0.6vw, 1rem);
  margin-bottom: clamp(0.5rem, 0.35rem + 0.6vw, 1rem);
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

.app-main {
  flex: 1;
  overflow: hidden;
  padding: clamp(0.6rem, 0.45rem + 0.5vw, 1rem) 0;
}

.app-card {
  height: 100%;
  border-radius: clamp(0.75rem, 0.6rem + 0.4vw, 1.1rem);
  background: rgba(15, 23, 42, 0.98);
  border: 1px solid rgba(30, 64, 175, 0.65);
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.9);
  padding: clamp(0.4rem, 0.35rem + 0.4vw, 0.9rem)
    clamp(0.4rem, 0.35rem + 0.8vw, 1.2rem);
  overflow: hidden;
}

.app-footer {
  margin-top: clamp(0.6rem, 0.45rem + 0.5vw, 1rem);
  padding: clamp(0.55rem, 0.45rem + 0.3vw, 0.85rem)
    clamp(0.8rem, 0.65rem + 0.7vw, 1.6rem);
  border-radius: clamp(0.6rem, 0.5rem + 0.35vw, 1rem);
  background: radial-gradient(circle at top left, #020617, #020617);
  border: 1px solid rgba(30, 64, 175, 0.6);
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

