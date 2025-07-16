<template>
  <div 
    v-if="visible" 
    class="context-menu"
    :style="{ left: position.x + 'px', top: position.y + 'px' }"
    @click.stop
  >
    <div class="menu-item" v-for="item in menuItems" :key="item.id" @click="handleMenuClick(item)">
      <span class="menu-icon" v-if="item.icon">{{ item.icon }}</span>
      <span class="menu-text">{{ item.text }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

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

.menu-item[data-enabled="false"] {
  opacity: 0.5;
  cursor: not-allowed;
}

.menu-icon {
  margin-right: 8px;
  width: 16px;
  text-align: center;
}

.menu-text {
  flex: 1;
}

.menu-item:has(.menu-text:contains("---")) {
  height: 1px;
  background-color: #eee;
  margin: 4px 0;
  padding: 0;
  pointer-events: none;
}
</style> 