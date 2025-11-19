<script setup lang="ts">
import { computed } from 'vue'
import type { MayaNode } from '../types'
import TreeNode from './TreeNode.vue'

interface Props {
  nodes: MayaNode[]
  selectedNode: string | null
  searchQuery: string
}

interface Emits {
  (e: 'node-select', nodeName: string): void
  (e: 'visibility-toggle', nodeName: string, visible: boolean): void
  (e: 'context-menu', event: MouseEvent, node: MayaNode): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Debug: 监听 props.nodes 的变化
console.log('[OutlinerTree] props.nodes:', props.nodes)
console.log('[OutlinerTree] props.nodes length:', props.nodes?.length)

// Filter nodes based on search query
const filteredNodes = computed(() => {
  console.log('[OutlinerTree] Computing filteredNodes, nodes:', props.nodes)
  console.log('[OutlinerTree] searchQuery:', props.searchQuery)

  if (!props.searchQuery) {
    return props.nodes
  }

  const query = props.searchQuery.toLowerCase()
  const filterNode = (node: MayaNode): MayaNode | null => {
    const matches = node.name.toLowerCase().includes(query)
    const filteredChildren = node.children
      .map(filterNode)
      .filter((n): n is MayaNode => n !== null)

    if (matches || filteredChildren.length > 0) {
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

const handleNodeSelect = (nodeName: string) => {
  emit('node-select', nodeName)
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

