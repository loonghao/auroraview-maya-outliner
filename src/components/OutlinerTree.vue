<script setup lang="ts">
import { computed } from 'vue'
import type { MayaNode } from '../types'
import TreeNode from './TreeNode.vue'

interface Props {
  nodes: MayaNode[]
  selectedNode: string | null
  searchQuery: string
  showDagOnly?: boolean
  showHidden?: boolean
}

interface Emits {
  (e: 'node-select', nodeName: string, event?: MouseEvent): void
  (e: 'node-rename', oldName: string, newName: string): void
  (e: 'visibility-toggle', nodeName: string, visible: boolean): void
  (e: 'context-menu', event: MouseEvent, node: MayaNode): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// DAG node types (visible when showDagOnly is true)
const DAG_NODE_TYPES = new Set([
  'transform', 'mesh', 'camera', 'light', 'group', 'joint', 'locator',
  'nurbsCurve', 'nurbsSurface', 'ikHandle', 'particleCloud'
])

// Filter nodes based on search query and display options
const filteredNodes = computed(() => {
  const query = props.searchQuery?.toLowerCase() || ''

  const filterNode = (node: MayaNode): MayaNode | null => {
    // Filter by DAG type
    if (props.showDagOnly && !DAG_NODE_TYPES.has(node.type)) {
      return null
    }

    // Filter by visibility
    if (!props.showHidden && !node.visible) {
      return null
    }

    // Filter by search query
    const matchesSearch = !query || node.name.toLowerCase().includes(query)

    // Recursively filter children
    const filteredChildren = node.children
      .map(filterNode)
      .filter((n): n is MayaNode => n !== null)

    // Include node if it matches or has matching children
    if (matchesSearch || filteredChildren.length > 0) {
      return {
        ...node,
        children: filteredChildren,
      }
    }

    return null
  }

  return props.nodes
    .map(filterNode)
    .filter((n): n is MayaNode => n !== null)
})

const handleNodeSelect = (nodeName: string, event?: MouseEvent) => {
  emit('node-select', nodeName, event)
}

const handleNodeRename = (oldName: string, newName: string) => {
  emit('node-rename', oldName, newName)
}

const handleVisibilityToggle = (nodeName: string, visible: boolean) => {
  emit('visibility-toggle', nodeName, visible)
}

const handleContextMenu = (event: MouseEvent, node: MayaNode) => {
  emit('context-menu', event, node)
}
</script>

<template>
  <div class="outliner-tree">
    <div v-if="filteredNodes.length === 0" class="empty-state">
      <p v-if="searchQuery">No nodes match "{{ searchQuery }}"</p>
      <p v-else>No nodes in scene</p>
    </div>

    <div v-else class="tree-container">
      <TreeNode
        v-for="node in filteredNodes"
        :key="node.path"
        :node="node"
        :selected-node="selectedNode"
        :level="0"
        @node-select="handleNodeSelect"
        @node-rename="handleNodeRename"
        @visibility-toggle="handleVisibilityToggle"
        @context-menu="handleContextMenu"
      />
    </div>
  </div>
</template>

<style scoped>
.outliner-tree {
  width: 100%;
  height: 100%;
  overflow: auto;
}

.tree-container {
  padding: clamp(0.25rem, 0.2rem + 0.3vw, 0.75rem) 0;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: clamp(8rem, 6rem + 5vw, 12rem);
  color: #64748b;
  font-size: clamp(0.78rem, 0.72rem + 0.2vw, 0.9rem);
}
</style>

