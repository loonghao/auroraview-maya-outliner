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
  (e: 'node-parent', childName: string, parentName: string | null): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const isExpanded = ref(true)
const hasChildren = computed(() => props.node.children.length > 0)
const isSelected = computed(() => props.node.name === props.selectedNode)

// Drag and drop state
const isDragging = ref(false)
const isDragOver = ref(false)
const dragOverPosition = ref<'top' | 'middle' | 'bottom' | null>(null)

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

// Get node icon class based on type
const nodeIconClass = computed(() => {
  switch (props.node.type) {
    // Geometry
    case 'mesh':
      return 'icon-mesh'
    case 'nurbsCurve':
      return 'icon-curve'
    case 'nurbsSurface':
      return 'icon-surface'

    // Cameras and Lights
    case 'camera':
      return 'icon-camera'
    case 'light':
      return 'icon-light'

    // Animation
    case 'joint':
      return 'icon-joint'
    case 'ikHandle':
      return 'icon-ik-handle'
    case 'ikSolver':
      return 'icon-ik-solver'
    case 'constraint':
      return 'icon-constraint'
    case 'controller':
      return 'icon-controller'

    // Deformers
    case 'cluster':
      return 'icon-cluster'
    case 'blendShape':
      return 'icon-blendshape'
    case 'skinCluster':
      return 'icon-skin'

    // Sets and Layers
    case 'objectSet':
      return 'icon-set'
    case 'displayLayer':
      return 'icon-layer'
    case 'renderLayer':
      return 'icon-render-layer'
    case 'animLayer':
      return 'icon-anim-layer'

    // Shaders and Textures
    case 'shader':
    case 'lambert':
    case 'blinn':
    case 'phong':
      return 'icon-shader'
    case 'file':
      return 'icon-texture'
    case 'place2dTexture':
      return 'icon-uv'

    // Particles
    case 'particleCloud':
      return 'icon-particle'

    // Hierarchy
    case 'group':
      return 'icon-group'
    case 'transform':
      return 'icon-transform'
    case 'locator':
      return 'icon-locator'

    default:
      return 'icon-default'
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

// Drag and drop handlers
const handleDragStart = (event: DragEvent) => {
  if (!event.dataTransfer) return

  isDragging.value = true
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', props.node.name)

  // Add a custom drag image (optional)
  if (event.target instanceof HTMLElement) {
    const dragImage = event.target.cloneNode(true) as HTMLElement
    dragImage.style.opacity = '0.5'
    event.dataTransfer.setDragImage(event.target, 0, 0)
  }
}

const handleDragEnd = () => {
  isDragging.value = false
}

const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
  if (!event.dataTransfer) return

  event.dataTransfer.dropEffect = 'move'
  isDragOver.value = true

  // Determine drop position based on mouse Y position
  const target = event.currentTarget as HTMLElement
  const rect = target.getBoundingClientRect()
  const y = event.clientY - rect.top
  const height = rect.height

  // Divide into three zones: top 25%, middle 50%, bottom 25%
  if (y < height * 0.25) {
    dragOverPosition.value = 'top'
  } else if (y > height * 0.75) {
    dragOverPosition.value = 'bottom'
  } else {
    // Middle zone - parent to this node (if it can have children)
    dragOverPosition.value = 'middle'
  }
}

const handleDragLeave = () => {
  isDragOver.value = false
  dragOverPosition.value = null
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  event.stopPropagation()

  if (!event.dataTransfer) return

  const draggedNodeName = event.dataTransfer.getData('text/plain')

  // Don't allow dropping on itself
  if (draggedNodeName === props.node.name) {
    isDragOver.value = false
    dragOverPosition.value = null
    return
  }

  // Don't allow dropping a parent onto its own child
  if (props.node.path.includes(draggedNodeName)) {
    isDragOver.value = false
    dragOverPosition.value = null
    return
  }

  // Determine the new parent based on drop position
  let newParent: string | null = null

  if (dragOverPosition.value === 'middle') {
    // Parent to this node
    newParent = props.node.name
  } else if (dragOverPosition.value === 'top' || dragOverPosition.value === 'bottom') {
    // Parent to this node's parent (sibling)
    newParent = props.node.parent || null
  }

  // Emit parent event
  emit('node-parent', draggedNodeName, newParent)

  isDragOver.value = false
  dragOverPosition.value = null
}
</script>

<template>
  <div class="tree-node">
    <div
      class="node-row"
      :class="{
        selected: isSelected,
        dragging: isDragging,
        'drag-over': isDragOver,
        'drag-over-top': isDragOver && dragOverPosition === 'top',
        'drag-over-middle': isDragOver && dragOverPosition === 'middle',
        'drag-over-bottom': isDragOver && dragOverPosition === 'bottom'
      }"
      :style="{ paddingLeft: `${level * 20 + 8}px` }"
      draggable="true"
      @click="handleClick"
      @dblclick="handleDoubleClick"
      @contextmenu="handleContextMenu"
      @dragstart="handleDragStart"
      @dragend="handleDragEnd"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @drop="handleDrop"
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

      <span class="node-icon" :class="nodeIconClass"></span>

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
        <span class="visibility-icon" :class="node.visible ? 'icon-visible' : 'icon-hidden'"></span>
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
        @node-parent="(childName, parentName) => emit('node-parent', childName, parentName)"
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
  background: linear-gradient(90deg, rgba(56, 189, 248, 0.35) 0%, rgba(56, 189, 248, 0.15) 100%),
    rgba(15, 23, 42, 0.95);
  border-left: 3px solid #38bdf8;
  box-shadow: inset 0 0 0 1px rgba(56, 189, 248, 0.3),
              0 2px 8px rgba(56, 189, 248, 0.2);
  transform: translateX(2px);
}

/* Drag and drop styles */
.node-row.dragging {
  opacity: 0.4;
  cursor: move;
}

.node-row.drag-over {
  position: relative;
}

.node-row.drag-over-top::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: #38bdf8;
  box-shadow: 0 0 4px rgba(56, 189, 248, 0.6);
}

.node-row.drag-over-middle {
  background: rgba(56, 189, 248, 0.2);
  border: 2px dashed #38bdf8;
  box-shadow: inset 0 0 8px rgba(56, 189, 248, 0.3);
}

.node-row.drag-over-bottom::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: #38bdf8;
  box-shadow: 0 0 4px rgba(56, 189, 248, 0.6);
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
  width: clamp(0.9rem, 0.85rem + 0.15vw, 1.1rem);
  height: clamp(0.9rem, 0.85rem + 0.15vw, 1.1rem);
  flex-shrink: 0;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
  opacity: 0.85;
}

/* Node type icons */
.icon-mesh { background-color: #60a5fa; mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M8 1l7 4v6l-7 4-7-4V5l7-4z' fill='none' stroke='currentColor' stroke-width='1.5'/%3E%3C/svg%3E"); }
.icon-camera { background-color: #a78bfa; mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Crect x='2' y='4' width='12' height='9' rx='1' fill='none' stroke='currentColor' stroke-width='1.5'/%3E%3Cpath d='M5 4L6 2h4l1 2' fill='none' stroke='currentColor' stroke-width='1.5'/%3E%3Ccircle cx='8' cy='8.5' r='2' fill='currentColor'/%3E%3C/svg%3E"); }
.icon-light { background-color: #fbbf24; mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Ccircle cx='8' cy='8' r='3' fill='currentColor'/%3E%3Cpath d='M8 1v2M8 13v2M15 8h-2M3 8H1M12.5 3.5l-1.4 1.4M4.9 11.1l-1.4 1.4M12.5 12.5l-1.4-1.4M4.9 4.9L3.5 3.5' stroke='currentColor' stroke-width='1.5'/%3E%3C/svg%3E"); }
.icon-joint { background-color: #f472b6; mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Ccircle cx='8' cy='8' r='2.5' fill='currentColor'/%3E%3Cpath d='M8 2v3.5M8 10.5V14M2 8h3.5M10.5 8H14' stroke='currentColor' stroke-width='1.5'/%3E%3C/svg%3E"); }
.icon-group { background-color: #fb923c; mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M3 2h10v10H3z' fill='none' stroke='currentColor' stroke-width='1.5'/%3E%3Cpath d='M5 5h6v6H5z' fill='none' stroke='currentColor' stroke-width='1.5'/%3E%3C/svg%3E"); }
.icon-transform { background-color: #fbbf24; mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M2 2h12v12H2z' fill='none' stroke='currentColor' stroke-width='1.5'/%3E%3C/svg%3E"); }
.icon-locator { background-color: #34d399; mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Ccircle cx='8' cy='8' r='1.5' fill='currentColor'/%3E%3Cpath d='M8 1v3M8 12v3M1 8h3M12 8h3' stroke='currentColor' stroke-width='1.5'/%3E%3C/svg%3E"); }
.icon-curve { background-color: #60a5fa; mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M2 12Q4 2 8 8T14 4' fill='none' stroke='currentColor' stroke-width='1.5'/%3E%3C/svg%3E"); }
.icon-surface { background-color: #60a5fa; mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M2 4Q8 2 14 4M2 8Q8 6 14 8M2 12Q8 10 14 12' fill='none' stroke='currentColor' stroke-width='1.5'/%3E%3C/svg%3E"); }
.icon-set { background-color: #a78bfa; mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Crect x='2' y='2' width='5' height='5' rx='1' fill='currentColor'/%3E%3Crect x='9' y='2' width='5' height='5' rx='1' fill='currentColor'/%3E%3Crect x='2' y='9' width='5' height='5' rx='1' fill='currentColor'/%3E%3Crect x='9' y='9' width='5' height='5' rx='1' fill='currentColor'/%3E%3C/svg%3E"); }
.icon-layer { background-color: #60a5fa; mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M2 4l6-2 6 2-6 2-6-2zM2 8l6 2 6-2M2 12l6 2 6-2' fill='none' stroke='currentColor' stroke-width='1.5'/%3E%3C/svg%3E"); }
.icon-shader { background-color: #f472b6; mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Ccircle cx='8' cy='8' r='5' fill='none' stroke='currentColor' stroke-width='1.5'/%3E%3Cpath d='M8 3v10M3 8h10' stroke='currentColor' stroke-width='1.5'/%3E%3C/svg%3E"); }
.icon-constraint { background-color: #fb923c; mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M4 6h8M4 10h8' stroke='currentColor' stroke-width='1.5'/%3E%3Ccircle cx='4' cy='6' r='1.5' fill='currentColor'/%3E%3Ccircle cx='12' cy='10' r='1.5' fill='currentColor'/%3E%3C/svg%3E"); }
.icon-ik-handle { background-color: #34d399; mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M3 3l5 5-5 5M8 8l5-5M8 8l5 5' fill='none' stroke='currentColor' stroke-width='1.5'/%3E%3C/svg%3E"); }
.icon-default { background-color: #94a3b8; mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Crect x='3' y='2' width='10' height='12' rx='1' fill='none' stroke='currentColor' stroke-width='1.5'/%3E%3Cpath d='M6 6h4M6 9h4' stroke='currentColor' stroke-width='1.5'/%3E%3C/svg%3E"); }

/* Add more icon types as needed */
.icon-cluster,
.icon-blendshape,
.icon-skin,
.icon-render-layer,
.icon-anim-layer,
.icon-texture,
.icon-uv,
.icon-particle,
.icon-controller,
.icon-ik-solver {
  background-color: #94a3b8;
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Ccircle cx='8' cy='8' r='4' fill='currentColor'/%3E%3C/svg%3E");
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
  width: clamp(1.1rem, 1rem + 0.3vw, 1.4rem);
  height: clamp(1.1rem, 1rem + 0.3vw, 1.4rem);
  padding: 0;
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.15s ease-out, transform 0.12s ease-out;
  display: flex;
  align-items: center;
  justify-content: center;
}

.visibility-btn:hover {
  opacity: 1;
  transform: scale(1.05);
}

.visibility-btn.hidden {
  opacity: 0.35;
}

.visibility-icon {
  width: 100%;
  height: 100%;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}

.icon-visible {
  background-color: #60a5fa;
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M8 3C4.5 3 1.5 6 1 8c.5 2 3.5 5 7 5s6.5-3 7-5c-.5-2-3.5-5-7-5z' fill='none' stroke='currentColor' stroke-width='1.5'/%3E%3Ccircle cx='8' cy='8' r='2' fill='currentColor'/%3E%3C/svg%3E");
}

.icon-hidden {
  background-color: #94a3b8;
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M1 1l14 14M4 4C2.5 5 1.5 6.5 1 8c.5 2 3.5 5 7 5 1 0 2-.3 3-.7M8 3c3.5 0 6.5 3 7 5-.3 1-1 2-2 3' fill='none' stroke='currentColor' stroke-width='1.5'/%3E%3C/svg%3E");
}

.node-children {
  margin-left: 0;
}
</style>

