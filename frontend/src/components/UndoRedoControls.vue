<template>
  <div class="undo-redo-controls">
    <button
      @click="handleUndo"
      :disabled="!moduleStore.canUndo"
      :title="undoTooltip"
      class="undo-btn control-btn"
      aria-label="Undo last action"
    >
      ↶ Undo
    </button>
    
    <button
      @click="handleRedo"
      :disabled="!moduleStore.canRedo"
      :title="redoTooltip"
      class="redo-btn control-btn"
      aria-label="Redo last undone action"
    >
      ↷ Redo
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useModuleStore } from '../stores/moduleStore'

const moduleStore = useModuleStore()

// Computed properties for tooltips
const undoTooltip = computed(() => {
  if (!moduleStore.canUndo) return 'Nothing to undo'
  return `Undo: ${moduleStore.lastUndoAction} (Ctrl+Z)`
})

const redoTooltip = computed(() => {
  if (!moduleStore.canRedo) return 'Nothing to redo'  
  return `Redo: ${moduleStore.lastRedoAction} (Ctrl+Y)`
})

// Action handlers
const handleUndo = async () => {
  try {
    await moduleStore.undo()
  } catch (error) {
    console.error('Undo failed:', error)
  }
}

const handleRedo = async () => {
  try {
    await moduleStore.redo()
  } catch (error) {
    console.error('Redo failed:', error)
  }
}
</script>

<style scoped>
.undo-redo-controls {
  display: flex;
  gap: 4px;
}

.control-btn {
  padding: 6px 12px;
  border: 2px solid #e1e5e9;
  border-radius: 6px;
  background: white;
  color: #666;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  min-width: 80px;
}

.control-btn:hover:not(:disabled) {
  border-color: #4a90e2;
  color: #4a90e2;
  background: #f8f9fa;
}

.control-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  color: #999;
  border-color: #ddd;
}

.undo-btn:hover:not(:disabled) {
  border-color: #17a2b8;
  color: #17a2b8;
}

.redo-btn:hover:not(:disabled) {
  border-color: #28a745;
  color: #28a745;
}

/* Responsive design */
@media (max-width: 768px) {
  .control-btn {
    padding: 4px 8px;
    font-size: 12px;
    min-width: 60px;
  }
}
</style>