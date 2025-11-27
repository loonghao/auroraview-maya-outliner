<script setup lang="ts">
import { Search, Plus, Trash2, ChevronDown, ChevronRight } from 'lucide-vue-next'

interface Props {
  filterText: string
  hasSelection: boolean
}

interface Emits {
  (e: 'update:filterText', value: string): void
  (e: 'add-node'): void
  (e: 'delete-selected'): void
  (e: 'expand-all'): void
  (e: 'collapse-all'): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

const handleFilterChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:filterText', target.value)
}
</script>

<template>
  <div class="toolbar">
    <div class="toolbar-main">
      <!-- Search Input -->
      <div class="search-container">
        <input
          type="text"
          placeholder="Search..."
          class="search-input"
          :value="filterText"
          @input="handleFilterChange"
        />
        <Search :size="12" class="search-icon" />
      </div>

      <!-- Action Buttons -->
      <button
        class="toolbar-btn"
        title="Create Group/Transform"
        @click="emit('add-node')"
      >
        <Plus :size="14" />
      </button>
      <button
        class="toolbar-btn toolbar-btn-danger"
        title="Delete Selected"
        :disabled="!hasSelection"
        @click="emit('delete-selected')"
      >
        <Trash2 :size="14" />
      </button>

      <div class="toolbar-divider"></div>

      <!-- Expand/Collapse -->
      <button
        class="toolbar-btn"
        title="Expand All"
        @click="emit('expand-all')"
      >
        <ChevronDown :size="14" />
      </button>
      <button
        class="toolbar-btn"
        title="Collapse All"
        @click="emit('collapse-all')"
      >
        <ChevronRight :size="14" />
      </button>
    </div>

    <!-- Display Options Bar -->
    <div class="display-bar">
      <span>Display</span>
      <span class="display-bar-item">Show</span>
      <span class="display-bar-item">Help</span>
    </div>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  flex-direction: column;
  background: var(--maya-panel, #1f1f1f);
  border-bottom: 1px solid var(--maya-border, #111111);
}

.toolbar-main {
  height: 32px;
  display: flex;
  align-items: center;
  padding: 0 8px;
  gap: 8px;
}

.search-container {
  flex: 1;
  position: relative;
}

.search-input {
  width: 100%;
  background: #111;
  color: #d1d5db;
  font-size: 12px;
  border: 1px solid #374151;
  border-radius: 4px;
  padding: 4px 8px 4px 28px;
  outline: none;
  transition: border-color 0.15s ease;
}

.search-input:focus {
  border-color: var(--maya-select, #5285a6);
}

.search-input::placeholder {
  color: #6b7280;
}

.search-icon {
  position: absolute;
  left: 8px;
  top: 50%;
  transform: translateY(-50%);
  color: #6b7280;
  pointer-events: none;
}

.toolbar-btn {
  padding: 4px;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: #9ca3af;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.toolbar-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.toolbar-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.toolbar-btn-danger:hover:not(:disabled) {
  color: #f87171;
}

.toolbar-divider {
  width: 1px;
  height: 16px;
  background: #374151;
  margin: 0 4px;
}

.display-bar {
  height: 24px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 8px;
  font-size: 10px;
  color: #6b7280;
  background: #2a2a2a;
  border-bottom: 1px solid #111;
}

.display-bar-item {
  margin-left: 8px;
}
</style>

