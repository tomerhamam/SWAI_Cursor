<template>
  <div v-if="show" class="bulk-operations-panel">
    <div class="panel-header">
      <div class="selection-info">
        <span class="selection-count">{{ selectedCount }} modules selected</span>
        <div class="selection-details" v-if="selectedCount > 0">
          <span v-for="status in selectedStatuses" :key="status" class="status-chip" :class="`status-${status}`">
            {{ getStatusCount(status) }} {{ status }}
          </span>
        </div>
      </div>
      
      <div class="panel-actions">
        <button 
          @click="selectAllVisible"
          class="action-button secondary"
          :disabled="isAllVisibleSelected"
          data-testid="select-all-visible"
        >
          {{ isAllVisibleSelected ? 'All Selected' : 'Select All Visible' }}
        </button>
        
        <button 
          @click="clearSelection"
          class="action-button secondary"
          :disabled="selectedCount === 0"
          data-testid="clear-selection"
        >
          Clear Selection
        </button>
        
        <button 
          @click="exitMultiSelect"
          class="action-button secondary"
          data-testid="exit-multi-select"
        >
          Exit Multi-Select
        </button>
      </div>
    </div>
    
    <div class="bulk-actions" v-if="selectedCount > 0">
      <div class="action-group">
        <label class="action-label">Update Status:</label>
        <div class="status-actions">
          <button 
            @click="updateStatus('implemented')"
            class="status-action implemented"
            :disabled="isUpdating"
            data-testid="status-implemented"
          >
            ✅ Implemented
          </button>
          <button 
            @click="updateStatus('placeholder')"
            class="status-action placeholder"
            :disabled="isUpdating"
            data-testid="status-placeholder"
          >
            ⚠️ Placeholder
          </button>
          <button 
            @click="updateStatus('error')"
            class="status-action error"
            :disabled="isUpdating"
            data-testid="status-error"
          >
            ❌ Error
          </button>
        </div>
      </div>
      
      <div class="action-group">
        <label class="action-label">Bulk Operations:</label>
        <div class="bulk-action-buttons">
          <button 
            @click="exportSelected"
            class="action-button primary"
            :disabled="isUpdating"
            data-testid="export-selected"
          >
            📤 Export Selected
          </button>
          
          <button 
            @click="duplicateSelected"
            class="action-button primary"
            :disabled="isUpdating || selectedCount !== 1"
            :title="selectedCount !== 1 ? 'Select exactly one module to duplicate' : ''"
            data-testid="duplicate-selected"
          >
            📋 Duplicate
          </button>
          
          <button 
            @click="showDeleteConfirm = true"
            class="action-button danger"
            :disabled="isUpdating"
            data-testid="delete-selected"
          >
            🗑️ Delete Selected
          </button>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirm" class="modal-overlay" @click="showDeleteConfirm = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Confirm Deletion</h3>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete {{ selectedCount }} module{{ selectedCount > 1 ? 's' : '' }}?</p>
          <ul class="modules-to-delete">
            <li v-for="module in selectedModules" :key="module.name">
              {{ module.name }} - {{ module.description }}
            </li>
          </ul>
          <p class="warning">This action cannot be undone.</p>
        </div>
        <div class="modal-actions">
          <button @click="showDeleteConfirm = false" class="action-button secondary">
            Cancel
          </button>
          <button @click="confirmDelete" class="action-button danger" :disabled="isUpdating">
            {{ isUpdating ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Loading Overlay -->
    <div v-if="isUpdating" class="loading-overlay">
      <div class="loading-spinner"></div>
      <span>{{ updateMessage }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useModuleStore } from '../stores/moduleStore'
import type { Module } from '../stores/moduleStore'

interface Props {
  show: boolean
}

const props = defineProps<Props>()
const moduleStore = useModuleStore()

// Local state
const isUpdating = ref(false)
const updateMessage = ref('')
const showDeleteConfirm = ref(false)

// Computed properties
const selectedCount = computed(() => moduleStore.selectedModuleCount)
const selectedModules = computed(() => moduleStore.selectedModules)
const selectedStatuses = computed(() => moduleStore.selectedModuleStatuses)
const filteredModulesCount = computed(() => moduleStore.searchResultsCount)

const isAllVisibleSelected = computed(() => {
  return selectedCount.value > 0 && selectedCount.value === filteredModulesCount.value
})

// Methods
const getStatusCount = (status: Module['status']) => {
  return selectedModules.value.filter(module => module.status === status).length
}

const selectAllVisible = () => {
  moduleStore.selectAllVisibleModules()
}

const clearSelection = () => {
  moduleStore.clearAllSelections()
}

const exitMultiSelect = () => {
  moduleStore.disableMultiSelectMode()
}

const updateStatus = async (newStatus: Module['status']) => {
  if (selectedCount.value === 0) return
  
  isUpdating.value = true
  updateMessage.value = `Updating ${selectedCount.value} module${selectedCount.value > 1 ? 's' : ''} to ${newStatus}...`
  
  try {
    await moduleStore.bulkUpdateStatus(newStatus)
    updateMessage.value = 'Update completed successfully!'
    setTimeout(() => {
      isUpdating.value = false
      updateMessage.value = ''
    }, 1500)
  } catch (error) {
    console.error('Bulk update failed:', error)
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred'
    updateMessage.value = `Update failed: ${errorMessage}. Please try again or contact support if the problem persists.`
    setTimeout(() => {
      isUpdating.value = false
      updateMessage.value = ''
    }, 5000) // Longer timeout for error messages
  }
}

const exportSelected = () => {
  const selectedData = selectedModules.value.map(module => ({
    name: module.name,
    description: module.description,
    status: module.status,
    version: module.version,
    inputs: module.inputs,
    outputs: module.outputs,
    dependencies: module.dependencies
  }))
  
  const dataStr = JSON.stringify(selectedData, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  
  const link = document.createElement('a')
  link.href = url
  link.download = `selected-modules-${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

const duplicateSelected = () => {
  if (selectedCount.value !== 1) return
  
  const module = selectedModules.value[0]
  const duplicatedModule = {
    ...module,
    name: `${module.name}_copy`,
    description: `Copy of ${module.description}`
  }
  
  emit('duplicateModule', duplicatedModule)
}

const confirmDelete = async () => {
  isUpdating.value = true
  updateMessage.value = `Deleting ${selectedCount.value} module${selectedCount.value > 1 ? 's' : ''}...`
  
  try {
    await moduleStore.bulkDeleteModules()
    showDeleteConfirm.value = false
    updateMessage.value = 'Deletion completed successfully!'
    setTimeout(() => {
      isUpdating.value = false
      updateMessage.value = ''
    }, 1500)
  } catch (error) {
    console.error('Bulk delete failed:', error)
    updateMessage.value = 'Deletion failed. Some modules may not have been deleted.'
    setTimeout(() => {
      isUpdating.value = false
      updateMessage.value = ''
    }, 3000)
  }
}

// Emits
const emit = defineEmits<{
  duplicateModule: [module: Omit<Module, 'name'> & { name: string }]
}>()

// Watch for selection changes to close delete modal
watch(() => selectedCount.value, (newCount) => {
  if (newCount === 0) {
    showDeleteConfirm.value = false
  }
})
</script>

<style scoped>
.bulk-operations-panel {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  border-top: 2px solid #e1e5e9;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-height: 300px;
  overflow-y: auto;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px 12px;
  border-bottom: 1px solid #f0f0f0;
}

.selection-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.selection-count {
  font-weight: 600;
  font-size: 16px;
  color: #333;
}

.selection-details {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.status-chip {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-chip.status-implemented {
  background: #e8f5e8;
  color: #2e7d32;
}

.status-chip.status-placeholder {
  background: #fff3e0;
  color: #f57c00;
}

.status-chip.status-error {
  background: #ffebee;
  color: #d32f2f;
}

.panel-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.bulk-actions {
  padding: 16px 24px;
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.action-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-label {
  font-weight: 600;
  font-size: 14px;
  color: #666;
}

.status-actions {
  display: flex;
  gap: 8px;
}

.status-action {
  padding: 8px 16px;
  border: 2px solid transparent;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.status-action.implemented {
  background: #e8f5e8;
  color: #2e7d32;
  border-color: #4caf50;
}

.status-action.implemented:hover:not(:disabled) {
  background: #4caf50;
  color: white;
}

.status-action.placeholder {
  background: #fff3e0;
  color: #f57c00;
  border-color: #ff9800;
}

.status-action.placeholder:hover:not(:disabled) {
  background: #ff9800;
  color: white;
}

.status-action.error {
  background: #ffebee;
  color: #d32f2f;
  border-color: #f44336;
}

.status-action.error:hover:not(:disabled) {
  background: #f44336;
  color: white;
}

.bulk-action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-button {
  padding: 8px 16px;
  border: 2px solid;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  background: transparent;
}

.action-button.primary {
  border-color: #4a90e2;
  color: #4a90e2;
}

.action-button.primary:hover:not(:disabled) {
  background: #4a90e2;
  color: white;
}

.action-button.secondary {
  border-color: #666;
  color: #666;
}

.action-button.secondary:hover:not(:disabled) {
  background: #666;
  color: white;
}

.action-button.danger {
  border-color: #f44336;
  color: #f44336;
}

.action-button.danger:hover:not(:disabled) {
  background: #f44336;
  color: white;
}

.action-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal {
  background: white;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  padding: 20px 24px 16px;
  border-bottom: 1px solid #e1e5e9;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.modal-body {
  padding: 20px 24px;
}

.modules-to-delete {
  max-height: 200px;
  overflow-y: auto;
  margin: 16px 0;
  padding: 0;
  list-style: none;
  background: #f8f9fa;
  border-radius: 4px;
  padding: 12px;
}

.modules-to-delete li {
  padding: 4px 0;
  font-size: 14px;
  color: #666;
}

.warning {
  color: #f44336;
  font-weight: 500;
  margin-top: 16px;
  margin-bottom: 0;
}

.modal-actions {
  padding: 16px 24px 20px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* Loading Overlay */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-weight: 500;
  color: #333;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f0f0f0;
  border-top: 3px solid #4a90e2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive Design */
@media (max-width: 768px) {
  .panel-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .bulk-actions {
    flex-direction: column;
    gap: 16px;
  }
  
  .status-actions, .bulk-action-buttons {
    flex-wrap: wrap;
  }
  
  .modal {
    margin: 20px;
    width: auto;
  }
}
</style>