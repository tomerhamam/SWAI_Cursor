import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiService } from '../services/apiService'

export interface Module {
  name: string
  description: string
  status: 'implemented' | 'placeholder' | 'error'
  version?: string
  inputs?: string[]
  outputs?: string[]
  dependencies?: string[]
  file_path?: string
}

export interface SearchFilter {
  type: 'status' | 'dependency' | 'version' | 'name' | 'description'
  value: string
  label: string
}

export interface UndoCommand {
  id: string
  type: 'create' | 'update' | 'delete' | 'bulk_update' | 'bulk_delete'
  description: string
  timestamp: number
  undo: () => Promise<void>
  redo: () => Promise<void>
}

export const useModuleStore = defineStore('module', () => {
  // State
  const modules = ref<Record<string, Module>>({})
  const selectedModuleId = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const connectionStatus = ref<'connected' | 'disconnected' | 'loading'>('loading')
  
  // Multi-select state
  const selectedModuleIds = ref<Set<string>>(new Set())
  const isMultiSelectMode = ref(false)
  
  // Search and filter state
  const searchQuery = ref('')
  const searchFilters = ref<SearchFilter[]>([])
  const statusFilters = ref<Set<Module['status']>>(new Set())

  // Undo/Redo state
  const undoStack = ref<UndoCommand[]>([])
  const redoStack = ref<UndoCommand[]>([])
  const maxUndoSteps = ref(50)

  // Getters
  const selectedModule = computed(() => {
    return selectedModuleId.value ? modules.value[selectedModuleId.value] : null
  })

  const moduleList = computed(() => {
    return Object.values(modules.value)
  })

  const moduleCount = computed(() => {
    return Object.keys(modules.value).length
  })

  const getModulesByStatus = computed(() => {
    return (status: Module['status']) => {
      return Object.values(modules.value).filter(module => module.status === status)
    }
  })

  // Search and filter computed properties
  const filteredModules = computed(() => {
    let filtered = Object.values(modules.value)
    
    // Apply search query
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      filtered = filtered.filter(module => 
        module.name.toLowerCase().includes(query) ||
        module.description.toLowerCase().includes(query) ||
        module.dependencies?.some(dep => dep.toLowerCase().includes(query)) ||
        module.version?.toLowerCase().includes(query)
      )
    }
    
    // Apply status filters
    if (statusFilters.value.size > 0) {
      filtered = filtered.filter(module => statusFilters.value.has(module.status))
    }
    
    // Apply additional search filters
    filtered = filtered.filter(module => {
      return searchFilters.value.every(filter => {
        switch (filter.type) {
          case 'status':
            return module.status === filter.value
          case 'dependency':
            return module.dependencies?.includes(filter.value)
          case 'version':
            return module.version === filter.value
          case 'name':
            return module.name.toLowerCase().includes(filter.value.toLowerCase())
          case 'description':
            return module.description.toLowerCase().includes(filter.value.toLowerCase())
          default:
            return true
        }
      })
    })
    
    return filtered
  })

  const filteredModulesMap = computed(() => {
    const map: Record<string, Module> = {}
    filteredModules.value.forEach(module => {
      map[module.name] = module
    })
    return map
  })

  const searchResultsCount = computed(() => filteredModules.value.length)

  const hasActiveFilters = computed(() => 
    searchQuery.value.length > 0 || 
    searchFilters.value.length > 0 || 
    statusFilters.value.size > 0
  )

  // Multi-select computed properties
  const selectedModules = computed(() => {
    return Array.from(selectedModuleIds.value)
      .map(id => modules.value[id])
      .filter(Boolean)
  })

  const selectedModuleCount = computed(() => selectedModuleIds.value.size)

  const canBulkUpdateStatus = computed(() => 
    selectedModuleCount.value > 0 && isMultiSelectMode.value
  )

  const selectedModuleStatuses = computed(() => {
    const statuses = new Set<Module['status']>()
    selectedModules.value.forEach(module => {
      statuses.add(module.status)
    })
    return statuses
  })

  // Undo/Redo computed properties
  const canUndo = computed(() => undoStack.value.length > 0)
  const canRedo = computed(() => redoStack.value.length > 0)
  const lastUndoAction = computed(() => undoStack.value[undoStack.value.length - 1]?.description || '')
  const lastRedoAction = computed(() => redoStack.value[redoStack.value.length - 1]?.description || '')

  // Actions
  async function loadModules() {
    isLoading.value = true
    error.value = null
    connectionStatus.value = 'loading'
    
    try {
      const response = await apiService.getModules()
      modules.value = response
      connectionStatus.value = 'connected'
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load modules'
      connectionStatus.value = 'disconnected'
      // Log only in development
      if (import.meta.env.DEV) {
        console.error('Failed to load modules:', err)
      }
    } finally {
      isLoading.value = false
    }
  }

  function selectModule(moduleId: string) {
    selectedModuleId.value = moduleId
  }

  function clearSelection() {
    selectedModuleId.value = null
  }

  async function updateModule(moduleId: string, updates: Partial<Module>, skipUndo = false) {
    try {
      // Store the original module data before update for undo
      const originalModule = modules.value[moduleId]
      if (!originalModule) {
        throw new Error(`Module ${moduleId} not found`)
      }
      
      const updatedModule = await apiService.updateModule(moduleId, updates)
      modules.value[moduleId] = updatedModule
      
      // Add to undo stack
      if (!skipUndo) {
        const changedFields = Object.keys(updates).join(', ')
        const undoCommand: UndoCommand = {
          id: `update-${moduleId}-${Date.now()}`,
          type: 'update',
          description: `Update ${changedFields} in "${moduleId}"`,
          timestamp: Date.now(),
          undo: async () => {
            // Restore original values for the changed fields
            const revertUpdates: Partial<Module> = {}
            Object.keys(updates).forEach(key => {
              revertUpdates[key as keyof Module] = originalModule[key as keyof Module]
            })
            await updateModule(moduleId, revertUpdates, true) // Skip undo for the revert
          },
          redo: async () => {
            await updateModule(moduleId, updates, true) // Skip undo for the redo
          }
        }
        addToUndoStack(undoCommand)
      }
      
      return updatedModule
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update module'
      error.value = errorMessage
      
      // Log only in development
      if (import.meta.env.DEV) {
        console.error('Failed to update module:', err)
      }
      
      throw new Error(errorMessage)
    }
  }

  async function createModule(module: Omit<Module, 'name'> & { name: string }, skipUndo = false) {
    try {
      const newModule = await apiService.createModule(module)
      modules.value[module.name] = newModule
      
      // Add to undo stack
      if (!skipUndo) {
        const undoCommand: UndoCommand = {
          id: `create-${module.name}-${Date.now()}`,
          type: 'create',
          description: `Create module "${module.name}"`,
          timestamp: Date.now(),
          undo: async () => {
            await deleteModule(module.name, true) // Skip undo for the delete
          },
          redo: async () => {
            await createModule(module, true) // Skip undo for the create
          }
        }
        addToUndoStack(undoCommand)
      }
      
      return newModule
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create module'
      error.value = errorMessage
      
      // Log only in development
      if (import.meta.env.DEV) {
        console.error('Failed to create module:', err)
      }
      
      throw new Error(errorMessage)
    }
  }

  async function deleteModule(moduleId: string, skipUndo = false) {
    try {
      // Store the module data before deletion for undo
      const moduleToDelete = modules.value[moduleId]
      if (!moduleToDelete) {
        throw new Error(`Module ${moduleId} not found`)
      }
      
      await apiService.deleteModule(moduleId)
      delete modules.value[moduleId]
      if (selectedModuleId.value === moduleId) {
        clearSelection()
      }
      
      // Add to undo stack
      if (!skipUndo) {
        const undoCommand: UndoCommand = {
          id: `delete-${moduleId}-${Date.now()}`,
          type: 'delete',
          description: `Delete module "${moduleId}"`,
          timestamp: Date.now(),
          undo: async () => {
            await createModule({ ...moduleToDelete, name: moduleId }, true) // Skip undo for the create
          },
          redo: async () => {
            await deleteModule(moduleId, true) // Skip undo for the delete
          }
        }
        addToUndoStack(undoCommand)
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete module'
      error.value = errorMessage
      
      // Log only in development
      if (import.meta.env.DEV) {
        console.error('Failed to delete module:', err)
      }
      
      throw new Error(errorMessage)
    }
  }

  function clearError() {
    error.value = null
  }

  function setError(message: string) {
    error.value = message
  }

  // Undo/Redo actions
  function addToUndoStack(command: UndoCommand) {
    undoStack.value.push(command)
    
    // Clear redo stack when new action is performed
    redoStack.value = []
    
    // Limit undo stack size
    if (undoStack.value.length > maxUndoSteps.value) {
      undoStack.value.shift()
    }
  }

  async function undo() {
    if (!canUndo.value) return
    
    const command = undoStack.value.pop()
    if (command) {
      try {
        await command.undo()
        redoStack.value.push(command)
      } catch (err) {
        // If undo fails, put the command back
        undoStack.value.push(command)
        const errorMessage = err instanceof Error ? err.message : 'Undo failed'
        error.value = errorMessage
        throw new Error(errorMessage)
      }
    }
  }

  async function redo() {
    if (!canRedo.value) return
    
    const command = redoStack.value.pop()
    if (command) {
      try {
        await command.redo()
        undoStack.value.push(command)
      } catch (err) {
        // If redo fails, put the command back
        redoStack.value.push(command)
        const errorMessage = err instanceof Error ? err.message : 'Redo failed'
        error.value = errorMessage
        throw new Error(errorMessage)
      }
    }
  }

  function clearUndoHistory() {
    undoStack.value = []
    redoStack.value = []
  }

  // Search and filter actions
  function setSearchQuery(query: string) {
    searchQuery.value = query
  }

  function addSearchFilter(filter: SearchFilter) {
    // Remove existing filter of same type with same value
    searchFilters.value = searchFilters.value.filter(
      f => !(f.type === filter.type && f.value === filter.value)
    )
    searchFilters.value.push(filter)
  }

  function removeSearchFilter(filter: SearchFilter) {
    searchFilters.value = searchFilters.value.filter(
      f => !(f.type === filter.type && f.value === filter.value)
    )
  }

  function clearSearchFilters() {
    searchFilters.value = []
  }

  function setStatusFilters(statuses: Set<Module['status']>) {
    statusFilters.value = new Set(statuses)
  }

  function clearAllFilters() {
    searchQuery.value = ''
    searchFilters.value = []
    statusFilters.value = new Set()
  }

  function updateSearch(data: { query: string, filters: SearchFilter[] }) {
    searchQuery.value = data.query
    searchFilters.value = [...data.filters]
  }

  // Multi-select actions
  function toggleMultiSelectMode() {
    isMultiSelectMode.value = !isMultiSelectMode.value
    if (!isMultiSelectMode.value) {
      clearAllSelections()
    }
  }

  function enableMultiSelectMode() {
    isMultiSelectMode.value = true
  }

  function disableMultiSelectMode() {
    isMultiSelectMode.value = false
    clearAllSelections()
  }

  function toggleModuleSelection(moduleId: string) {
    if (selectedModuleIds.value.has(moduleId)) {
      selectedModuleIds.value.delete(moduleId)
      // Clear single selection when deselecting in single-select mode
      if (!isMultiSelectMode.value && selectedModuleId.value === moduleId) {
        selectedModuleId.value = null
      }
    } else {
      selectedModuleIds.value.add(moduleId)
      // Update single selection when not in multi-select mode
      if (!isMultiSelectMode.value) {
        selectedModuleId.value = moduleId
      }
    }
  }

  function selectAllModules() {
    filteredModules.value.forEach(module => {
      selectedModuleIds.value.add(module.name)
    })
  }

  function selectAllVisibleModules() {
    selectedModuleIds.value.clear()
    filteredModules.value.forEach(module => {
      selectedModuleIds.value.add(module.name)
    })
  }

  function clearAllSelections() {
    selectedModuleIds.value.clear()
    selectedModuleId.value = null
  }

  function isModuleSelected(moduleId: string): boolean {
    return selectedModuleIds.value.has(moduleId)
  }

  async function bulkUpdateStatus(newStatus: Module['status']) {
    if (!canBulkUpdateStatus.value) {
      throw new Error('Cannot perform bulk update: no modules selected')
    }

    const updatePromises = selectedModules.value.map(async (module) => {
      try {
        return await updateModule(module.name, { status: newStatus })
      } catch (err) {
        // Log individual failures but don't stop the batch
        if (import.meta.env.DEV) {
          console.error(`Failed to update module ${module.name}:`, err)
        }
        throw err
      }
    })

    const results = await Promise.allSettled(updatePromises)
    const failures = results.filter(result => result.status === 'rejected')
    
    if (failures.length > 0) {
      const failureCount = failures.length
      const successCount = results.length - failureCount
      const errorMessage = `${failureCount} of ${results.length} modules failed to update${successCount > 0 ? ` (${successCount} updated successfully)` : ''}`
      error.value = errorMessage
      
      // Only clear selections if at least some updates succeeded
      if (successCount > 0) {
        // Remove successfully updated modules from selection
        const failedModuleNames = failures.map((_, index) => {
          const originalIndex = results.findIndex(result => result === failures[index])
          return selectedModules.value[originalIndex]?.name
        }).filter(Boolean)
        
        // Keep only failed modules selected for retry
        selectedModuleIds.value = new Set(failedModuleNames)
      }
      
      throw new Error(errorMessage)
    }
    
    // All updates succeeded
    clearAllSelections()
    disableMultiSelectMode()
  }

  async function bulkDeleteModules() {
    if (!canBulkUpdateStatus.value) {
      throw new Error('Cannot perform bulk delete: no modules selected')
    }

    const modulesToDelete = [...selectedModules.value]
    const deletePromises = modulesToDelete.map(async (module) => {
      try {
        return await deleteModule(module.name)
      } catch (err) {
        if (import.meta.env.DEV) {
          console.error(`Failed to delete module ${module.name}:`, err)
        }
        throw err
      }
    })

    const results = await Promise.allSettled(deletePromises)
    const failures = results.filter(result => result.status === 'rejected')
    
    if (failures.length > 0) {
      const failureCount = failures.length
      const successCount = results.length - failureCount
      const errorMessage = `${failureCount} of ${results.length} modules failed to delete${successCount > 0 ? ` (${successCount} deleted successfully)` : ''}`
      error.value = errorMessage
      
      // Only clear selections if at least some deletions succeeded
      if (successCount > 0) {
        // Remove successfully deleted modules from selection
        const failedModuleNames = failures.map((_, index) => {
          const originalIndex = results.findIndex(result => result === failures[index])
          return modulesToDelete[originalIndex]?.name
        }).filter(Boolean)
        
        // Keep only failed modules selected for retry
        selectedModuleIds.value = new Set(failedModuleNames)
      }
      
      throw new Error(errorMessage)
    }
    
    // All deletions succeeded
    clearAllSelections()
    disableMultiSelectMode()
  }

  return {
    // State
    modules,
    selectedModuleId,
    isLoading,
    error,
    connectionStatus,
    searchQuery,
    searchFilters,
    statusFilters,
    // Multi-select state
    selectedModuleIds,
    isMultiSelectMode,
    // Getters
    selectedModule,
    moduleList,
    moduleCount,
    getModulesByStatus,
    filteredModules,
    filteredModulesMap,
    searchResultsCount,
    hasActiveFilters,
    // Multi-select getters
    selectedModules,
    selectedModuleCount,
    canBulkUpdateStatus,
    selectedModuleStatuses,
    // Undo/Redo getters
    canUndo,
    canRedo,
    lastUndoAction,
    lastRedoAction,
    // Actions
    loadModules,
    selectModule,
    clearSelection,
    updateModule,
    createModule,
    deleteModule,
    clearError,
    setError,
    // Search actions
    setSearchQuery,
    addSearchFilter,
    removeSearchFilter,
    clearSearchFilters,
    setStatusFilters,
    clearAllFilters,
    updateSearch,
    // Multi-select actions
    toggleMultiSelectMode,
    enableMultiSelectMode,
    disableMultiSelectMode,
    toggleModuleSelection,
    selectAllModules,
    selectAllVisibleModules,
    clearAllSelections,
    isModuleSelected,
    bulkUpdateStatus,
    bulkDeleteModules,
    // Undo/Redo actions
    undo,
    redo,
    clearUndoHistory
  }
}) 