<script setup lang="ts">
import { ref, computed, inject, watch, nextTick, type Ref } from 'vue'
import type { MayaNode } from '../types'

interface Props {
  node: MayaNode
  selectedNode: string | null
  level: number
}

interface Emits {
  (e: 'node-select', nodeName: string, event?: MouseEvent): void
  (e: 'node-rename', nodeName: string, newName: string): void
  (e: 'visibility-toggle', nodeName: string, visible: boolean): void
  (e: 'context-menu', event: MouseEvent, node: MayaNode): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const isExpanded = ref(true)
const hasChildren = computed(() => props.node.children.length > 0)
const isSelected = computed(() => props.node.name === props.selectedNode)

// Inject expansion triggers
const expandAllTrigger = inject<Ref<number>>('expandAllTrigger', ref(0))
const collapseAllTrigger = inject<Ref<number>>('collapseAllTrigger', ref(0))

// Watch for expansion triggers
watch(expandAllTrigger, () => {
  if (hasChildren.value) {
    isExpanded.value = true
  }
})

watch(collapseAllTrigger, () => {
  if (hasChildren.value) {
    isExpanded.value = false
  }
})

const nodeIcon = computed(() => {
  switch (props.node.type) {
    // Geometry
    case 'mesh':
      return '🔷'
    case 'nurbsCurve':
      return '〰️'
    case 'nurbsSurface':
      return '🌊'

    // Cameras and Lights
    case 'camera':
      return '📷'
    case 'light':
      return '💡'

    // Animation
    case 'joint':
      return '🦴'
    case 'ikHandle':
      return '🔗'
    case 'ikSolver':
      return '⚙️'
    case 'constraint':
      return '🔒'
    case 'controller':
      return '🎮'

    // Deformers
    case 'cluster':
      return '🎯'
    case 'blendShape':
      return '🎭'
    case 'skinCluster':
      return '🦴'

    // Sets and Layers
    case 'objectSet':
      return '📦'
    case 'displayLayer':
      return '📋'
    case 'renderLayer':
      return '🎬'
    case 'animLayer':
      return '🎞️'

    // Shaders and Textures
    case 'shader':
    case 'lambert':
    case 'blinn':
    case 'phong':
      return '🌈'
    case 'file':
      return '🖼️'
    case 'place2dTexture':
      return '📐'

    // Particles
    case 'particleCloud':
      return '☁️'

    // Hierarchy
    case 'group':
      return '📦'
    case 'transform':
      return '📁'
    case 'locator':
      return '📍'

    default:
      return '📄'
  }
})

const toggleExpand = () => {
  if (hasChildren.value) {
    isExpanded.value = !isExpanded.value
  }
}

const isRenaming = ref(false)
const renamingValue = ref('')
const renameInput = ref<HTMLInputElement | null>(null)

const handleClick = (event: MouseEvent) => {
  emit('node-select', props.node.name, event)
}

const handleDoubleClick = async () => {
  isRenaming.value = true
  renamingValue.value = props.node.name
  await nextTick()
  renameInput.value?.focus()
  renameInput.value?.select()
}

const handleRename = () => {
  if (renamingValue.value && renamingValue.value !== props.node.name) {
    emit('node-rename', props.node.name, renamingValue.value)
  }
  isRenaming.value = false
}

const handleRenameKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter') {
    handleRename()
  } else if (event.key === 'Escape') {
    isRenaming.value = false
  }
}

const toggleVisibility = (event: Event) => {
  event.stopPropagation()
  emit('visibility-toggle', props.node.name, !props.node.visible)
}

const handleContextMenu = (event: MouseEvent) => {
  event.preventDefault()
  event.stopPropagation()
  emit('context-menu', event, props.node)
}
</script>

<template>
  <div class="tree-node">
    <div
      class="node-row"
      :class="{ selected: isSelected }"
      :style="{ paddingLeft: `${level * 20 + 8}px` }"
      @click="handleClick"
      @dblclick="handleDoubleClick"
      @contextmenu="handleContextMenu"
    >
      <button
        v-if="hasChildren"
        class="expand-btn"
        :class="{ expanded: isExpanded }"
        @click.stop="toggleExpand"
      >
        ▶
      </button>
      <span v-else class="expand-spacer"></span>

      <span class="node-icon">{{ nodeIcon }}</span>

      <!-- Rename input -->
      <input
        v-if="isRenaming"
        v-model="renamingValue"
        class="node-name-input"
        @blur="handleRename"
        @keydown="handleRenameKeydown"
        @click.stop
        ref="renameInput"
      />
      <span v-else class="node-name">{{ node.name }}</span>

      <span class="node-type">{{ node.type }}</span>

      <button
        class="visibility-btn"
        :class="{ hidden: !node.visible }"
        @click.stop="toggleVisibility"
        :title="node.visible ? 'Hide' : 'Show'"
      >
        {{ node.visible ? '👁️' : '🚫' }}
      </button>
    </div>

    <div v-if="hasChildren && isExpanded" class="node-children">
      <TreeNode
        v-for="child in node.children"
        :key="child.path"
        :node="child"
        :selected-node="selectedNode"
        :level="level + 1"
        @node-select="(nodeName, event) => emit('node-select', nodeName, event)"
        @node-rename="(oldName, newName) => emit('node-rename', oldName, newName)"
        @visibility-toggle="(nodeName, visible) => emit('visibility-toggle', nodeName, visible)"
        @context-menu="(event, node) => emit('context-menu', event, node)"
      />
    </div>
  </div>
</template>

<style scoped>
.tree-node {
  user-select: none;
}

.node-row {
  display: flex;
  align-items: center;
  gap: clamp(0.35rem, 0.3rem + 0.2vw, 0.75rem);
  padding: clamp(0.3rem, 0.25rem + 0.3vw, 0.7rem)
    clamp(0.5rem, 0.4rem + 0.5vw, 1rem);
  cursor: pointer;
  transition: background-color 0.12s ease-out, box-shadow 0.12s ease-out,
    border-color 0.12s ease-out;
  border-radius: clamp(0.35rem, 0.3rem + 0.2vw, 0.6rem);
  margin: clamp(0.05rem, 0.03rem + 0.1vw, 0.2rem) 0;
}

.node-row:hover {
  background-color: rgba(30, 64, 175, 0.35);
}

.node-row.selected {
  background: radial-gradient(circle at left, rgba(56, 189, 248, 0.28), transparent),
    rgba(15, 23, 42, 0.95);
  border-left: 2px solid #38bdf8;
}

.expand-btn {
  width: clamp(0.8rem, 0.72rem + 0.2vw, 1rem);
  height: clamp(0.8rem, 0.72rem + 0.2vw, 1rem);
  padding: 0;
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  transition: transform 0.18s ease-out, color 0.12s ease-out;
  font-size: clamp(0.6rem, 0.55rem + 0.15vw, 0.75rem);
}

.expand-btn.expanded {
  transform: rotate(90deg);
}

.expand-btn:hover {
  color: #e5e7eb;
}

.expand-spacer {
  width: clamp(0.8rem, 0.72rem + 0.2vw, 1rem);
}

.node-icon {
  font-size: clamp(0.85rem, 0.8rem + 0.15vw, 1rem);
  flex-shrink: 0;
}

.node-name {
  flex: 1;
  font-size: clamp(0.8rem, 0.75rem + 0.15vw, 0.95rem);
  color: #e5e7eb;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-name-input {
  flex: 1;
  font-size: clamp(0.8rem, 0.75rem + 0.15vw, 0.95rem);
  color: #e5e7eb;
  background: rgba(30, 41, 59, 0.95);
  border: 1px solid #38bdf8;
  border-radius: 4px;
  padding: 2px 6px;
  outline: none;
}

.node-type {
  font-size: clamp(0.65rem, 0.6rem + 0.15vw, 0.8rem);
  color: #9ca3af;
  padding: clamp(0.05rem, 0.03rem + 0.05vw, 0.15rem)
    clamp(0.35rem, 0.3rem + 0.2vw, 0.6rem);
  background: rgba(15, 23, 42, 0.98);
  border-radius: 999px;
  border: 1px solid rgba(51, 65, 85, 0.9);
}

.visibility-btn {
  width: clamp(1.25rem, 1.1rem + 0.5vw, 1.75rem);
  height: clamp(1.25rem, 1.1rem + 0.5vw, 1.75rem);
  padding: 0;
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.15s ease-out, transform 0.12s ease-out;
  font-size: clamp(0.85rem, 0.8rem + 0.2vw, 1.05rem);
}

.visibility-btn:hover {
  opacity: 1;
  transform: scale(1.05);
}

.visibility-btn.hidden {
  opacity: 0.35;
}

.node-children {
  margin-left: 0;
}
</style>

