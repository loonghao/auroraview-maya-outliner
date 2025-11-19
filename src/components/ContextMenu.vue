<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import type { ContextMenuItemOrSeparator, ContextMenuItem } from '../types/contextMenu'

interface Props {
  visible: boolean
  x: number
  y: number
  items: ContextMenuItemOrSeparator[]
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'close'): void
}>()

const menuRef = ref<HTMLElement | null>(null)
const activeSubmenuIndex = ref<number | null>(null)
const submenuPosition = ref({ x: 0, y: 0 })
const adjustedPosition = ref({ x: props.x, y: props.y })

// Adjust menu position to stay within viewport
const menuStyle = computed(() => {
  if (!props.visible) return { display: 'none' }

  return {
    left: `${adjustedPosition.value.x}px`,
    top: `${adjustedPosition.value.y}px`,
    display: 'block',
    position: 'fixed',
  }
})

// Check if item is a separator
const isSeparator = (item: ContextMenuItemOrSeparator): item is { type: 'separator' } => {
  return 'type' in item && item.type === 'separator'
}

// Handle menu item click
const handleItemClick = async (item: ContextMenuItem, index: number) => {
  if (item.disabled) return

  if (item.submenu && item.submenu.length > 0) {
    // Toggle submenu
    if (activeSubmenuIndex.value === index) {
      activeSubmenuIndex.value = null
    } else {
      activeSubmenuIndex.value = index
      await nextTick()
      calculateSubmenuPosition(index)
    }
  } else if (item.action) {
    // Execute action and close menu
    await item.action()
    emit('close')
  }
}

// Handle submenu hover
const handleItemHover = async (index: number, hasSubmenu: boolean) => {
  if (hasSubmenu) {
    activeSubmenuIndex.value = index
    await nextTick()
    calculateSubmenuPosition(index)
  }
}

// Calculate submenu position (absolute positioning)
const calculateSubmenuPosition = (index: number) => {
  if (!menuRef.value) return

  const menuRect = menuRef.value.getBoundingClientRect()
  const itemElements = menuRef.value.querySelectorAll('.context-menu-item:not(.context-menu-separator)')
  const itemElement = itemElements[index] as HTMLElement

  if (itemElement) {
    const itemRect = itemElement.getBoundingClientRect()
    const viewportWidth = window.innerWidth
    const viewportHeight = window.innerHeight

    // Use estimated submenu dimensions (will be adjusted after render)
    const submenuWidth = 200
    const submenuHeight = 200

    // Default: position to the right of parent menu, aligned with the item
    let x = menuRect.right - 2
    let y = itemRect.top

    // If submenu would go off-screen to the right, position to the left
    if (x + submenuWidth > viewportWidth) {
      x = menuRect.left - submenuWidth + 2
    }

    // Ensure submenu doesn't go off-screen horizontally
    x = Math.max(0, Math.min(x, viewportWidth - submenuWidth))

    // If submenu would go off-screen at the bottom, adjust upward
    if (y + submenuHeight > viewportHeight) {
      y = Math.max(0, viewportHeight - submenuHeight - 10)
    }

    // Ensure submenu doesn't go off-screen vertically
    y = Math.max(0, y)

    submenuPosition.value = { x, y }
  }
}

// Adjust menu position to stay within viewport
const adjustMenuPosition = async () => {
  await nextTick()

  if (!menuRef.value) return

  const rect = menuRef.value.getBoundingClientRect()
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight

  let x = props.x
  let y = props.y

  console.log('[ContextMenu] Original position:', { x, y })
  console.log('[ContextMenu] Menu size:', { width: rect.width, height: rect.height })
  console.log('[ContextMenu] Viewport size:', { width: viewportWidth, height: viewportHeight })

  // Adjust horizontal position if menu would go off-screen
  if (x + rect.width > viewportWidth) {
    x = Math.max(0, viewportWidth - rect.width - 10)
    console.log('[ContextMenu] Adjusted X to:', x)
  }

  // Adjust vertical position if menu would go off-screen
  if (y + rect.height > viewportHeight) {
    y = Math.max(0, viewportHeight - rect.height - 10)
    console.log('[ContextMenu] Adjusted Y to:', y)
  }

  console.log('[ContextMenu] Final position:', { x, y })
  adjustedPosition.value = { x, y }
}

// Watch for visibility changes and adjust position
watch(
  () => props.visible,
  (visible) => {
    if (visible) {
      // Reset to original position first
      adjustedPosition.value = { x: props.x, y: props.y }
      // Then adjust after render
      adjustMenuPosition()
    } else {
      // Reset submenu when menu closes
      activeSubmenuIndex.value = null
    }
  },
  { immediate: true }
)

// Watch for position changes
watch(
  () => [props.x, props.y],
  () => {
    if (props.visible) {
      adjustedPosition.value = { x: props.x, y: props.y }
      adjustMenuPosition()
    }
  }
)
</script>

<template>
  <Teleport to="body">
    <div
      v-if="visible"
      ref="menuRef"
      class="context-menu"
      :style="menuStyle"
      @click.stop
    >
      <div
        v-for="(item, index) in items"
        :key="index"
        :class="[
          isSeparator(item) ? 'context-menu-separator' : 'context-menu-item',
          {
            'has-submenu': !isSeparator(item) && (item as ContextMenuItem).submenu,
            disabled: !isSeparator(item) && (item as ContextMenuItem).disabled,
            active: activeSubmenuIndex === index,
          },
        ]"
        @click="!isSeparator(item) && handleItemClick(item as ContextMenuItem, index)"
        @mouseenter="
          !isSeparator(item) &&
            handleItemHover(index, !!(item as ContextMenuItem).submenu)
        "
      >
        <template v-if="!isSeparator(item)">
          <span class="menu-item-label">{{ (item as ContextMenuItem).label }}</span>
          <span v-if="(item as ContextMenuItem).submenu" class="submenu-arrow">▶</span>
          <span
            v-if="(item as ContextMenuItem).shortcut"
            class="menu-item-shortcut"
          >
            {{ (item as ContextMenuItem).shortcut }}
          </span>

          <!-- Submenu -->
          <ContextMenu
            v-if="(item as ContextMenuItem).submenu && activeSubmenuIndex === index"
            :visible="true"
            :x="submenuPosition.x"
            :y="submenuPosition.y"
            :items="(item as ContextMenuItem).submenu!"
            class="submenu"
            @close="emit('close')"
          />
        </template>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.context-menu {
  position: fixed;
  background: #2b2b2b;
  border: 1px solid #3c3c3c;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  min-width: 180px;
  max-width: 280px;
  z-index: 9999;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 12px;
  padding: 4px 0;
  user-select: none;
}

.context-menu-item {
  padding: 6px 20px 6px 12px;
  cursor: pointer;
  color: #cccccc;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  transition: background-color 0.1s ease;
}

.context-menu-item:hover:not(.disabled) {
  background: #094771;
  color: #ffffff;
}

.context-menu-item.disabled {
  color: #666666;
  cursor: not-allowed;
  opacity: 0.5;
}

.context-menu-item.has-submenu {
  padding-right: 28px;
}

.context-menu-item.active {
  background: #094771;
  color: #ffffff;
}

.menu-item-label {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.submenu-arrow {
  position: absolute;
  right: 8px;
  font-size: 10px;
  color: #999999;
}

.context-menu-item:hover:not(.disabled) .submenu-arrow {
  color: #ffffff;
}

.menu-item-shortcut {
  margin-left: 16px;
  font-size: 11px;
  color: #999999;
}

.context-menu-separator {
  height: 1px;
  background: #3c3c3c;
  margin: 4px 8px;
}
</style>

