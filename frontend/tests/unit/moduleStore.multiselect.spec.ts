import { describe, it, expect, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useModuleStore } from '@/stores/moduleStore'
import type { Module } from '@/stores/moduleStore'

describe('ModuleStore Multi-Select Functionality', () => {
  let store: ReturnType<typeof useModuleStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useModuleStore()
    
    // Set up test modules
    store.modules = {
      auth: {
        name: 'UserAuthentication',
        description: 'Handles user login and authentication',
        status: 'implemented',
        version: '1.0.0',
        inputs: ['username', 'password'],
        outputs: ['authToken'],
        dependencies: ['Database', 'Encryption']
      },
      processor: {
        name: 'DataProcessor',
        description: 'Processes incoming data streams',
        status: 'placeholder',
        version: '2.0.0',
        inputs: ['rawData'],
        outputs: ['processedData'],
        dependencies: ['Database']
      },
      logger: {
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

  describe('Multi-Select Mode Toggle', () => {
    it('toggles multi-select mode', () => {
      expect(store.isMultiSelectMode).toBe(false)
      
      store.toggleMultiSelectMode()
      expect(store.isMultiSelectMode).toBe(true)
      
      store.toggleMultiSelectMode()
      expect(store.isMultiSelectMode).toBe(false)
    })

    it('enables multi-select mode', () => {
      store.enableMultiSelectMode()
      expect(store.isMultiSelectMode).toBe(true)
    })

    it('disables multi-select mode and clears selections', () => {
      store.enableMultiSelectMode()
      store.toggleModuleSelection('auth')
      
      expect(store.selectedModuleIds.has('auth')).toBe(true)
      
      store.disableMultiSelectMode()
      expect(store.isMultiSelectMode).toBe(false)
      expect(store.selectedModuleIds.size).toBe(0)
    })

    it('clears selections when exiting multi-select mode', () => {
      store.enableMultiSelectMode()
      store.toggleModuleSelection('auth')
      store.toggleModuleSelection('processor')
      
      expect(store.selectedModuleCount).toBe(2)
      
      store.toggleMultiSelectMode() // Turn off
      expect(store.selectedModuleCount).toBe(0)
    })
  })

  describe('Module Selection', () => {
    beforeEach(() => {
      store.enableMultiSelectMode()
    })

    it('toggles module selection', () => {
      expect(store.isModuleSelected('auth')).toBe(false)
      
      store.toggleModuleSelection('auth')
      expect(store.isModuleSelected('auth')).toBe(true)
      
      store.toggleModuleSelection('auth')
      expect(store.isModuleSelected('auth')).toBe(false)
    })

    it('selects multiple modules', () => {
      store.toggleModuleSelection('auth')
      store.toggleModuleSelection('processor')
      
      expect(store.selectedModuleCount).toBe(2)
      expect(store.isModuleSelected('auth')).toBe(true)
      expect(store.isModuleSelected('processor')).toBe(true)
    })

    it('selects all visible modules', () => {
      store.selectAllVisibleModules()
      
      expect(store.selectedModuleCount).toBe(3)
      expect(store.isModuleSelected('UserAuthentication')).toBe(true)
      expect(store.isModuleSelected('DataProcessor')).toBe(true)
      expect(store.isModuleSelected('ErrorHandler')).toBe(true)
    })

    it('selects all modules with filtering', () => {
      // Filter to only show implemented modules
      store.setStatusFilters(new Set(['implemented']))
      
      store.selectAllVisibleModules()
      
      expect(store.selectedModuleCount).toBe(1)
      expect(store.isModuleSelected('UserAuthentication')).toBe(true)
      expect(store.isModuleSelected('DataProcessor')).toBe(false)
    })

    it('clears all selections', () => {
      store.toggleModuleSelection('auth')
      store.toggleModuleSelection('processor')
      
      expect(store.selectedModuleCount).toBe(2)
      
      store.clearAllSelections()
      expect(store.selectedModuleCount).toBe(0)
    })
  })

  describe('Selection State Getters', () => {
    beforeEach(() => {
      store.enableMultiSelectMode()
    })

    it('returns selected modules', () => {
      store.toggleModuleSelection('auth')
      store.toggleModuleSelection('processor')
      
      const selectedModules = store.selectedModules
      expect(selectedModules).toHaveLength(2)
      expect(selectedModules.find(m => m.name === 'UserAuthentication')).toBeDefined()
      expect(selectedModules.find(m => m.name === 'DataProcessor')).toBeDefined()
    })

    it('returns selected module count', () => {
      expect(store.selectedModuleCount).toBe(0)
      
      store.toggleModuleSelection('auth')
      expect(store.selectedModuleCount).toBe(1)
      
      store.toggleModuleSelection('processor')
      expect(store.selectedModuleCount).toBe(2)
    })

    it('calculates bulk update capability', () => {
      expect(store.canBulkUpdateStatus).toBe(false)
      
      store.toggleModuleSelection('auth')
      expect(store.canBulkUpdateStatus).toBe(true)
      
      store.disableMultiSelectMode()
      expect(store.canBulkUpdateStatus).toBe(false)
    })

    it('returns selected module statuses', () => {
      store.toggleModuleSelection('auth') // implemented
      store.toggleModuleSelection('processor') // placeholder
      
      const statuses = store.selectedModuleStatuses
      expect(statuses.has('implemented')).toBe(true)
      expect(statuses.has('placeholder')).toBe(true)
      expect(statuses.has('error')).toBe(false)
    })
  })

  describe('Integration with Single Select', () => {
    it('updates single selection when toggling in single-select mode', () => {
      store.disableMultiSelectMode()
      
      store.toggleModuleSelection('auth')
      expect(store.selectedModuleId).toBe('auth')
      expect(store.isModuleSelected('auth')).toBe(true)
    })

    it('preserves single selection when entering multi-select mode', () => {
      store.selectModule('auth')
      expect(store.selectedModuleId).toBe('auth')
      
      store.enableMultiSelectMode()
      expect(store.selectedModuleId).toBe('auth') // Still set
    })
  })

  describe('Selection Persistence Across Filters', () => {
    beforeEach(() => {
      store.enableMultiSelectMode()
      store.toggleModuleSelection('auth')
      store.toggleModuleSelection('processor')
      store.toggleModuleSelection('logger')
    })

    it('maintains selections when applying filters', () => {
      expect(store.selectedModuleCount).toBe(3)
      
      // Apply filter that hides some modules
      store.setStatusFilters(new Set(['implemented']))
      
      // Selections should still be maintained
      expect(store.selectedModuleCount).toBe(3)
      expect(store.isModuleSelected('auth')).toBe(true)
      expect(store.isModuleSelected('processor')).toBe(true)
      expect(store.isModuleSelected('logger')).toBe(true)
    })

    it('selectAllVisibleModules only selects filtered modules', () => {
      store.clearAllSelections()
      
      // Filter to show only placeholder modules
      store.setStatusFilters(new Set(['placeholder']))
      
      store.selectAllVisibleModules()
      
      expect(store.selectedModuleCount).toBe(1)
      expect(store.isModuleSelected('DataProcessor')).toBe(true)
      expect(store.isModuleSelected('UserAuthentication')).toBe(false)
      expect(store.isModuleSelected('ErrorHandler')).toBe(false)
    })
  })

  describe('Error Handling', () => {
    it('handles non-existent module selection gracefully', () => {
      store.enableMultiSelectMode()
      
      expect(() => {
        store.toggleModuleSelection('nonexistent')
      }).not.toThrow()
      
      expect(store.isModuleSelected('nonexistent')).toBe(true) // Added to selection set
      expect(store.selectedModules).toHaveLength(0) // But not in actual modules
    })

    it('handles bulk operations with invalid selections', () => {
      store.enableMultiSelectMode()
      store.toggleModuleSelection('nonexistent')
      
      expect(store.canBulkUpdateStatus).toBe(true) // Has selections
      expect(store.selectedModules).toHaveLength(0) // But no actual modules
    })
  })
})