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

export const useModuleStore = defineStore('module', () => {
  // State
  const modules = ref<Record<string, Module>>({})
  const selectedModuleId = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const connectionStatus = ref<'connected' | 'disconnected' | 'loading'>('loading')

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
      console.error('Failed to load modules:', err)
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

  async function updateModule(moduleId: string, updates: Partial<Module>) {
    try {
      const updatedModule = await apiService.updateModule(moduleId, updates)
      modules.value[moduleId] = updatedModule
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update module'
      throw err
    }
  }

  async function createModule(module: Omit<Module, 'name'> & { name: string }) {
    try {
      const newModule = await apiService.createModule(module)
      modules.value[module.name] = newModule
      return newModule
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create module'
      throw err
    }
  }

  async function deleteModule(moduleId: string) {
    try {
      await apiService.deleteModule(moduleId)
      delete modules.value[moduleId]
      if (selectedModuleId.value === moduleId) {
        clearSelection()
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete module'
      throw err
    }
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    modules,
    selectedModuleId,
    isLoading,
    error,
    connectionStatus,
    // Getters
    selectedModule,
    moduleList,
    moduleCount,
    getModulesByStatus,
    // Actions
    loadModules,
    selectModule,
    clearSelection,
    updateModule,
    createModule,
    deleteModule,
    clearError
  }
}) 