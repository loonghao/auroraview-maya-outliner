import { ref, provide, inject, type InjectionKey } from 'vue'

export interface TreeExpansionState {
  expandAll: () => void
  collapseAll: () => void
  isExpandAllActive: () => boolean
}

const TreeExpansionKey: InjectionKey<TreeExpansionState> = Symbol('TreeExpansion')

export function provideTreeExpansion() {
  const expandAllActive = ref(false)

  const expandAll = () => {
    expandAllActive.value = true
    // Reset after a short delay to allow components to react
    setTimeout(() => {
      expandAllActive.value = false
    }, 100)
  }

  const collapseAll = () => {
    expandAllActive.value = false
  }

  const isExpandAllActive = () => expandAllActive.value

  const state: TreeExpansionState = {
    expandAll,
    collapseAll,
    isExpandAllActive,
  }

  provide(TreeExpansionKey, state)

  return state
}

export function useTreeExpansion() {
  const state = inject(TreeExpansionKey)
  if (!state) {
    throw new Error('useTreeExpansion must be used within a component that calls provideTreeExpansion')
  }
  return state
}

