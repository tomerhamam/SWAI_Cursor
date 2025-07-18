import { describe, it, expect, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useModuleStore } from '@/stores/moduleStore'
import type { Module, SearchFilter } from '@/stores/moduleStore'

describe('ModuleStore Search Functionality', () => {
  let store: ReturnType<typeof useModuleStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useModuleStore()
    
    // Set up test modules
    store.modules = {
      module1: {
        name: 'UserAuthentication',
        description: 'Handles user login and authentication',
        status: 'implemented',
        version: '1.0.0',
        inputs: ['username', 'password'],
        outputs: ['authToken'],
        dependencies: ['Database', 'Encryption']
      },
      module2: {
        name: 'DataProcessor',
        description: 'Processes incoming data streams',
        status: 'placeholder',
        version: '2.0.0',
        inputs: ['rawData'],
        outputs: ['processedData'],
        dependencies: ['Database']
      },
      module3: {
        name: 'ErrorHandler',
        description: 'Central error handling and logging',
        status: 'error',
        version: '1.1.0',
        inputs: ['errorData'],
        outputs: ['logEntry'],
        dependencies: []
      }
    } as Record<string, Module>
  })

  describe('Search Query', () => {
    it('filters modules by name', () => {
      store.setSearchQuery('authentication')
      
      const filtered = store.filteredModules
      expect(filtered).toHaveLength(1)
      expect(filtered[0].name).toBe('UserAuthentication')
    })

    it('filters modules by description', () => {
      store.setSearchQuery('streams')
      
      const filtered = store.filteredModules
      expect(filtered).toHaveLength(1)
      expect(filtered[0].name).toBe('DataProcessor')
    })

    it('filters modules by dependencies', () => {
      store.setSearchQuery('encryption')
      
      const filtered = store.filteredModules
      expect(filtered).toHaveLength(1)
      expect(filtered[0].name).toBe('UserAuthentication')
    })

    it('filters modules by version', () => {
      store.setSearchQuery('2.0')
      
      const filtered = store.filteredModules
      expect(filtered).toHaveLength(1)
      expect(filtered[0].name).toBe('DataProcessor')
    })

    it('returns all modules when search query is empty', () => {
      store.setSearchQuery('')
      
      const filtered = store.filteredModules
      expect(filtered).toHaveLength(3)
    })

    it('is case insensitive', () => {
      store.setSearchQuery('AUTHENTICATION')
      
      const filtered = store.filteredModules
      expect(filtered).toHaveLength(1)
      expect(filtered[0].name).toBe('UserAuthentication')
    })

    it('returns empty array when no matches found', () => {
      store.setSearchQuery('nonexistent')
      
      const filtered = store.filteredModules
      expect(filtered).toHaveLength(0)
    })
  })

  describe('Status Filters', () => {
    it('filters modules by single status', () => {
      store.setStatusFilters(new Set(['implemented']))
      
      const filtered = store.filteredModules
      expect(filtered).toHaveLength(1)
      expect(filtered[0].status).toBe('implemented')
    })

    it('filters modules by multiple statuses', () => {
      store.setStatusFilters(new Set(['implemented', 'placeholder']))
      
      const filtered = store.filteredModules
      expect(filtered).toHaveLength(2)
    })

    it('returns all modules when no status filters set', () => {
      store.setStatusFilters(new Set())
      
      const filtered = store.filteredModules
      expect(filtered).toHaveLength(3)
    })
  })

  describe('Search Filters', () => {
    it('adds search filter', () => {
      const filter: SearchFilter = {
        type: 'status',
        value: 'implemented',
        label: 'Implemented'
      }
      
      store.addSearchFilter(filter)
      
      expect(store.searchFilters).toContainEqual(filter)
    })

    it('removes duplicate filters when adding', () => {
      const filter: SearchFilter = {
        type: 'status',
        value: 'implemented',
        label: 'Implemented'
      }
      
      store.addSearchFilter(filter)
      store.addSearchFilter(filter) // Add same filter again
      
      expect(store.searchFilters).toHaveLength(1)
    })

    it('removes search filter', () => {
      const filter: SearchFilter = {
        type: 'status',
        value: 'implemented',
        label: 'Implemented'
      }
      
      store.addSearchFilter(filter)
      store.removeSearchFilter(filter)
      
      expect(store.searchFilters).not.toContainEqual(filter)
    })

    it('clears all search filters', () => {
      const filter1: SearchFilter = {
        type: 'status',
        value: 'implemented',
        label: 'Implemented'
      }
      const filter2: SearchFilter = {
        type: 'dependency',
        value: 'Database',
        label: 'Database'
      }
      
      store.addSearchFilter(filter1)
      store.addSearchFilter(filter2)
      store.clearSearchFilters()
      
      expect(store.searchFilters).toHaveLength(0)
    })

    it('filters modules by dependency filter', () => {
      const filter: SearchFilter = {
        type: 'dependency',
        value: 'Encryption',
        label: 'Encryption'
      }
      
      store.addSearchFilter(filter)
      
      const filtered = store.filteredModules
      expect(filtered).toHaveLength(1)
      expect(filtered[0].name).toBe('UserAuthentication')
    })

    it('filters modules by version filter', () => {
      const filter: SearchFilter = {
        type: 'version',
        value: '2.0.0',
        label: 'Version 2.0.0'
      }
      
      store.addSearchFilter(filter)
      
      const filtered = store.filteredModules
      expect(filtered).toHaveLength(1)
      expect(filtered[0].name).toBe('DataProcessor')
    })
  })

  describe('Combined Filtering', () => {
    it('combines search query and status filters', () => {
      store.setSearchQuery('login')
      store.setStatusFilters(new Set(['implemented']))
      
      const filtered = store.filteredModules
      expect(filtered).toHaveLength(1)
      expect(filtered[0].name).toBe('UserAuthentication')
    })

    it('returns empty when filters dont match', () => {
      store.setSearchQuery('login')
      store.setStatusFilters(new Set(['error']))
      
      const filtered = store.filteredModules
      expect(filtered).toHaveLength(0)
    })

    it('combines all filter types', () => {
      store.setSearchQuery('login')
      store.setStatusFilters(new Set(['implemented']))
      store.addSearchFilter({
        type: 'dependency',
        value: 'Encryption',
        label: 'Encryption'
      })
      
      const filtered = store.filteredModules
      expect(filtered).toHaveLength(1)
      expect(filtered[0].name).toBe('UserAuthentication')
    })
  })

  describe('Computed Properties', () => {
    it('calculates search results count', () => {
      store.setSearchQuery('authentication')
      
      expect(store.searchResultsCount).toBe(1)
    })

    it('detects active filters', () => {
      expect(store.hasActiveFilters).toBe(false)
      
      store.setSearchQuery('test')
      expect(store.hasActiveFilters).toBe(true)
      
      store.setSearchQuery('')
      store.setStatusFilters(new Set(['implemented']))
      expect(store.hasActiveFilters).toBe(true)
    })

    it('creates filtered modules map', () => {
      store.setSearchQuery('authentication')
      
      const filteredMap = store.filteredModulesMap
      expect(Object.keys(filteredMap)).toHaveLength(1)
      expect(filteredMap['UserAuthentication']).toBeDefined()
    })
  })

  describe('Clear All Filters', () => {
    it('clears all search state', () => {
      store.setSearchQuery('test')
      store.setStatusFilters(new Set(['implemented']))
      store.addSearchFilter({
        type: 'dependency',
        value: 'Database',
        label: 'Database'
      })
      
      store.clearAllFilters()
      
      expect(store.searchQuery).toBe('')
      expect(store.statusFilters.size).toBe(0)
      expect(store.searchFilters).toHaveLength(0)
      expect(store.hasActiveFilters).toBe(false)
    })
  })

  describe('Update Search', () => {
    it('updates search query and filters together', () => {
      const searchData = {
        query: 'test query',
        filters: [{
          type: 'status' as const,
          value: 'implemented',
          label: 'Implemented'
        }]
      }
      
      store.updateSearch(searchData)
      
      expect(store.searchQuery).toBe('test query')
      expect(store.searchFilters).toEqual(searchData.filters)
    })
  })
})