<template>
  <div 
    v-if="visible" 
    class="context-menu"
    role="menu"
    :aria-label="`Context menu for ${contextType === 'node' && nodeId ? nodeId : 'canvas'}`"
    :style="{ left: position.x + 'px', top: position.y + 'px' }"
    @click.stop
    @keydown="handleKeyDown"
    tabindex="-1"
    ref="menuElement"
  >
    <div 
      v-for="(item, index) in menuItems" 
      :key="item.id"
      :class="['menu-item', { 'menu-separator': item.text === '---', 'menu-item-disabled': item.enabled === false }]"
      :role="item.text === '---' ? 'separator' : 'menuitem'"
      :tabindex="item.text === '---' || item.enabled === false ? -1 : 0"
      :aria-disabled="item.enabled === false"
      :aria-label="item.text"
      :data-index="index"
      @click="handleMenuClick(item)"
      @keydown.enter="handleMenuClick(item)"
      @keydown.space.prevent="handleMenuClick(item)"
      @focus="currentFocusIndex = index"
      ref="menuItemElements"
    >
      <span class="menu-icon" v-if="item.icon && item.text !== '---'" :aria-hidden="true">{{ item.icon }}</span>
      <span class="menu-text">{{ item.text }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'

export interface ContextMenuItem {
  id: string
  text: string
  icon?: string
  action: string
  enabled?: boolean
}

interface Props {
  visible: boolean
  position: { x: number; y: number }
  contextType: 'empty' | 'node'
  nodeId?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  menuAction: [action: string, nodeId?: string]
  close: []
}>()

// Accessibility state
const menuElement = ref<HTMLElement>()
const menuItemElements = ref<HTMLElement[]>([])
const currentFocusIndex = ref(0)

// Define menu items based on context
const menuItems = computed(() => {
  if (props.contextType === 'empty') {
    return [
      { id: 'add-module', text: 'Add Module', icon: '➕', action: 'add-module' },
      { id: 'toggle-dependency-mode', text: 'Dependency Mode', icon: '🔗', action: 'toggle-dependency-mode' },
      { id: 'paste', text: 'Paste', icon: '📋', action: 'paste', enabled: false },
    ]
  } else {
    // Node context menu
    return [
      { id: 'edit-module', text: 'Edit Module', icon: '✏️', action: 'edit-module' },
      { id: 'duplicate', text: 'Duplicate', icon: '📄', action: 'duplicate-module' },
      { id: 'delete', text: 'Delete', icon: '🗑️', action: 'delete-module' },
      { id: 'separator', text: '---', icon: '', action: '' },
      { id: 'start-dependency', text: 'Start Dependency', icon: '🔗', action: 'start-dependency' },
      { id: 'view-details', text: 'View Details', icon: '📊', action: 'view-details' },
    ]
  }
})

const handleMenuClick = (item: ContextMenuItem) => {
  if (item.enabled === false || item.action === '') return
  
  emit('menuAction', item.action, props.nodeId)
  emit('close')
}

const handleKeyDown = (event: KeyboardEvent) => {
  const focusableIndexes = menuItems.value
    .map((item, index) => ({ item, index }))
    .filter(({ item }) => item.text !== '---' && item.enabled !== false)
    .map(({ index }) => index)

  if (focusableIndexes.length === 0) return

  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      navigateToNext(focusableIndexes)
      break
    case 'ArrowUp':
      event.preventDefault()
      navigateToPrevious(focusableIndexes)
      break
    case 'Home':
      event.preventDefault()
      focusItem(focusableIndexes[0])
      break
    case 'End':
      event.preventDefault()
      focusItem(focusableIndexes[focusableIndexes.length - 1])
      break
    case 'Escape':
      event.preventDefault()
      emit('close')
      break
  }
}

const navigateToNext = (focusableIndexes: number[]) => {
  const currentIndex = focusableIndexes.indexOf(currentFocusIndex.value)
  const nextIndex = currentIndex === -1 ? 0 : (currentIndex + 1) % focusableIndexes.length
  focusItem(focusableIndexes[nextIndex])
}

const navigateToPrevious = (focusableIndexes: number[]) => {
  const currentIndex = focusableIndexes.indexOf(currentFocusIndex.value)
  const prevIndex = currentIndex === -1 ? 
    focusableIndexes.length - 1 : 
    (currentIndex - 1 + focusableIndexes.length) % focusableIndexes.length
  focusItem(focusableIndexes[prevIndex])
}

const focusItem = (index: number) => {
  currentFocusIndex.value = index
  nextTick(() => {
    const element = menuItemElements.value[index]
    if (element) {
      element.focus()
    }
  })
}

// Focus management when menu becomes visible
watch(() => props.visible, (isVisible) => {
  if (isVisible) {
    nextTick(() => {
      // Focus the menu container and first focusable item
      if (menuElement.value) {
        menuElement.value.focus()
      }
      
      const firstFocusableIndex = menuItems.value.findIndex(
        item => item.text !== '---' && item.enabled !== false
      )
      
      if (firstFocusableIndex !== -1) {
        focusItem(firstFocusableIndex)
      }
    })
  }
})
</script>

<style scoped>
.context-menu {
  position: fixed;
  background: white;
  border: 1px solid #ccc;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 4px 0;
  min-width: 160px;
  z-index: 1000;
  font-size: 14px;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  user-select: none;
  transition: background-color 0.1s;
}

.menu-item:hover {
  background-color: #f5f5f5;
}

.menu-item-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.menu-item:focus {
  background-color: #e3f2fd;
  outline: 2px solid #1976d2;
  outline-offset: -2px;
}

.menu-separator {
  height: 1px;
  background-color: #eee;
  margin: 4px 0;
  padding: 0;
  pointer-events: none;
}

.menu-separator .menu-text {
  display: none;
}

.menu-icon {
  margin-right: 8px;
  width: 16px;
  text-align: center;
}

.menu-text {
  flex: 1;
}
</style> 