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

export const useModuleStore = defineStore('module', () => {
  // State
  const modules = ref<Record<string, Module>>({})
  const selectedModuleId = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const connectionStatus = ref<'connected' | 'disconnected' | 'loading'>('loading')
  
  // Search and filter state
  const searchQuery = ref('')
  const searchFilters = ref<SearchFilter[]>([])
  const statusFilters = ref<Set<Module['status']>>(new Set())

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

  async function updateModule(moduleId: string, updates: Partial<Module>) {
    try {
      const updatedModule = await apiService.updateModule(moduleId, updates)
      modules.value[moduleId] = updatedModule
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

  async function createModule(module: Omit<Module, 'name'> & { name: string }) {
    try {
      const newModule = await apiService.createModule(module)
      modules.value[module.name] = newModule
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

  async function deleteModule(moduleId: string) {
    try {
      await apiService.deleteModule(moduleId)
      delete modules.value[moduleId]
      if (selectedModuleId.value === moduleId) {
        clearSelection()
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
    // Getters
    selectedModule,
    moduleList,
    moduleCount,
    getModulesByStatus,
    filteredModules,
    filteredModulesMap,
    searchResultsCount,
    hasActiveFilters,
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
    updateSearch
  }
}) 