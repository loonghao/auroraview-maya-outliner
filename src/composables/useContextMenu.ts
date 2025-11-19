import { ref, onMounted, onUnmounted } from 'vue'
import type { ContextMenuItemOrSeparator, ContextMenuPosition } from '../types/contextMenu'

export function useContextMenu() {
  const visible = ref(false)
  const position = ref<ContextMenuPosition>({ x: 0, y: 0 })
  const items = ref<ContextMenuItemOrSeparator[]>([])
  const activeSubmenuIndex = ref<number | null>(null)

  const show = (x: number, y: number, menuItems: ContextMenuItemOrSeparator[]) => {
    position.value = { x, y }
    items.value = menuItems
    visible.value = true
    activeSubmenuIndex.value = null
  }

  const hide = () => {
    visible.value = false
    activeSubmenuIndex.value = null
  }

  const handleClickOutside = (event: MouseEvent) => {
    const target = event.target as HTMLElement
    if (!target.closest('.context-menu')) {
      hide()
    }
  }

  const handleEscape = (event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      hide()
    }
  }

  onMounted(() => {
    document.addEventListener('click', handleClickOutside)
    document.addEventListener('keydown', handleEscape)
  })

  onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
    document.removeEventListener('keydown', handleEscape)
  })

  return {
    visible,
    position,
    items,
    activeSubmenuIndex,
    show,
    hide,
  }
}

