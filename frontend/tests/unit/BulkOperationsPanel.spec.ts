import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import BulkOperationsPanel from '@/components/BulkOperationsPanel.vue'
import { useModuleStore } from '@/stores/moduleStore'
import type { Module } from '@/stores/moduleStore'

// Mock URL.createObjectURL and related APIs
Object.defineProperty(window.URL, 'createObjectURL', {
  value: vi.fn(() => 'mock-url'),
  writable: true
})

Object.defineProperty(window.URL, 'revokeObjectURL', {
  value: vi.fn(),
  writable: true
})

describe('BulkOperationsPanel', () => {
  let store: ReturnType<typeof useModuleStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useModuleStore()
    
    // Set up test modules
    store.modules = {
      UserAuthentication: {
        name: 'UserAuthentication',
        description: 'Handles user login and authentication',
        status: 'implemented',
        version: '1.0.0',
        inputs: ['username', 'password'],
        outputs: ['authToken'],
        dependencies: ['Database']
      },
      DataProcessor: {
        name: 'DataProcessor',
        description: 'Processes incoming data streams',
        status: 'placeholder',
        version: '2.0.0',
        inputs: ['rawData'],
        outputs: ['processedData'],
        dependencies: ['Database']
      },
      ErrorHandler: {
        name: 'ErrorHandler',
        description: 'Central error handling and logging',
        status: 'error',
        version: '1.1.0',
        inputs: ['errorData'],
        outputs: ['logEntry'],
        dependencies: []
      }
    } as Record<string, Module>

    store.enableMultiSelectMode()
  })

  describe('Visibility', () => {
    it('shows when show prop is true', () => {
      const wrapper = mount(BulkOperationsPanel, { props: { show: true } })
      expect(wrapper.find('.bulk-operations-panel').exists()).toBe(true)
    })

    it('hides when show prop is false', () => {
      const wrapper = mount(BulkOperationsPanel, { props: { show: false } })
      expect(wrapper.find('.bulk-operations-panel').exists()).toBe(false)
    })
  })

  describe('Selection Display', () => {
    it('displays selection count', async () => {
      const wrapper = mount(BulkOperationsPanel, { props: { show: true } })
      
      store.toggleModuleSelection('UserAuthentication')
      store.toggleModuleSelection('DataProcessor')

      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.selection-count').text()).toContain('2 modules selected')
    })

    it('shows status breakdown for selected modules', async () => {
      const wrapper = mount(BulkOperationsPanel, { props: { show: true } })
      
      store.toggleModuleSelection('UserAuthentication') // implemented
      store.toggleModuleSelection('DataProcessor') // placeholder

      await wrapper.vm.$nextTick()
      
      const statusChips = wrapper.findAll('.status-chip')
      expect(statusChips.length).toBeGreaterThan(0)
    })
  })

  describe('Selection Actions', () => {
    it('selects all visible modules', async () => {
      const wrapper = mount(BulkOperationsPanel, { props: { show: true } })
      
      const selectAllButton = wrapper.find('[data-testid="select-all-visible"]')
      expect(selectAllButton.exists()).toBe(true)
      
      await selectAllButton.trigger('click')
      
      expect(store.selectedModuleCount).toBe(3)
    })

    it('clears selection', async () => {
      const wrapper = mount(BulkOperationsPanel, { props: { show: true } })
      
      store.toggleModuleSelection('UserAuthentication')
      store.toggleModuleSelection('DataProcessor')

      await wrapper.vm.$nextTick()
      
      const clearButton = wrapper.find('[data-testid="clear-selection"]')
      await clearButton.trigger('click')
      
      expect(store.selectedModuleCount).toBe(0)
    })

    it('exits multi-select mode', async () => {
      const wrapper = mount(BulkOperationsPanel, { props: { show: true } })
      
      const exitButton = wrapper.find('[data-testid="exit-multi-select"]')
      await exitButton.trigger('click')
      
      expect(store.isMultiSelectMode).toBe(false)
    })
  })

  describe('Status Updates', () => {
    it('updates selected modules to implemented status', async () => {
      const wrapper = mount(BulkOperationsPanel, { props: { show: true } })
      
      store.toggleModuleSelection('UserAuthentication')
      store.toggleModuleSelection('DataProcessor')
      
      await wrapper.vm.$nextTick()

      vi.spyOn(store, 'bulkUpdateStatus').mockResolvedValue()
      
      const implementedButton = wrapper.find('[data-testid="status-implemented"]')
      expect(implementedButton.exists()).toBe(true)
      
      await implementedButton.trigger('click')
      
      expect(store.bulkUpdateStatus).toHaveBeenCalledWith('implemented')
    })

    it('disables status buttons when no modules selected', async () => {
      const wrapper = mount(BulkOperationsPanel, { props: { show: true } })
      
      await wrapper.vm.$nextTick()
      
      // When no modules are selected, bulk actions section should not be visible
      expect(wrapper.find('.bulk-actions').exists()).toBe(false)
    })
  })

  describe('Export Functionality', () => {
    it('exports selected modules as JSON', async () => {
      const wrapper = mount(BulkOperationsPanel, { props: { show: true } })
      
      store.toggleModuleSelection('UserAuthentication')
      store.toggleModuleSelection('DataProcessor')
      
      await wrapper.vm.$nextTick()

      // Mock document methods
      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any)

      // Click the export button to open dropdown
      const exportButton = wrapper.find('[data-testid="export-selected"]')
      expect(exportButton.exists()).toBe(true)
      
      await exportButton.trigger('click')
      await wrapper.vm.$nextTick()
      
      // Find and click the JSON export option
      const jsonOption = wrapper.find('.export-option:first-child')
      expect(jsonOption.exists()).toBe(true)
      expect(jsonOption.text()).toContain('JSON')
      
      await jsonOption.trigger('click')
      
      expect(document.createElement).toHaveBeenCalledWith('a')
      expect(mockLink.click).toHaveBeenCalled()
      expect(mockLink.download).toMatch(/selected-modules-\d{4}-\d{2}-\d{2}\.json/)
    })

    it('exports selected modules as CSV', async () => {
      const wrapper = mount(BulkOperationsPanel, { props: { show: true } })
      
      store.toggleModuleSelection('UserAuthentication')
      store.toggleModuleSelection('DataProcessor')
      
      await wrapper.vm.$nextTick()

      // Mock document methods
      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any)

      // Click the export button to open dropdown
      const exportButton = wrapper.find('[data-testid="export-selected"]')
      expect(exportButton.exists()).toBe(true)
      
      await exportButton.trigger('click')
      await wrapper.vm.$nextTick()
      
      // Find and click the CSV export option
      const csvOption = wrapper.find('.export-option:last-child')
      expect(csvOption.exists()).toBe(true)
      expect(csvOption.text()).toContain('CSV')
      
      await csvOption.trigger('click')
      
      expect(document.createElement).toHaveBeenCalledWith('a')
      expect(mockLink.click).toHaveBeenCalled()
      expect(mockLink.download).toMatch(/selected-modules-\d{4}-\d{2}-\d{2}\.csv/)
    })
  })

  describe('Duplicate Functionality', () => {
    it('enables duplicate when exactly one module is selected', async () => {
      const wrapper = mount(BulkOperationsPanel, { props: { show: true } })
      
      store.toggleModuleSelection('UserAuthentication')
      
      await wrapper.vm.$nextTick()
      
      const duplicateButton = wrapper.find('[data-testid="duplicate-selected"]')
      expect(duplicateButton.exists()).toBe(true)
      expect(duplicateButton.attributes('disabled')).toBeUndefined()
    })

    it('disables duplicate when multiple modules are selected', async () => {
      const wrapper = mount(BulkOperationsPanel, { props: { show: true } })
      
      store.toggleModuleSelection('UserAuthentication')
      store.toggleModuleSelection('DataProcessor')
      
      await wrapper.vm.$nextTick()
      
      const duplicateButton = wrapper.find('[data-testid="duplicate-selected"]')
      expect(duplicateButton.exists()).toBe(true)
      expect(duplicateButton.attributes('disabled')).toBeDefined()
    })

    it('emits duplicate event with module data', async () => {
      const wrapper = mount(BulkOperationsPanel, { props: { show: true } })
      
      store.toggleModuleSelection('UserAuthentication')
      
      await wrapper.vm.$nextTick()
      
      const duplicateButton = wrapper.find('[data-testid="duplicate-selected"]')
      await duplicateButton.trigger('click')
      
      const emittedEvents = wrapper.emitted('duplicateModule')
      expect(emittedEvents).toBeTruthy()
      expect(emittedEvents![0][0]).toMatchObject({
        name: 'UserAuthentication_copy',
        description: 'Copy of Handles user login and authentication'
      })
    })
  })

  describe('Delete Functionality', () => {
    it('shows delete confirmation modal', async () => {
      const wrapper = mount(BulkOperationsPanel, { props: { show: true } })
      
      store.toggleModuleSelection('UserAuthentication')
      store.toggleModuleSelection('DataProcessor')
      
      await wrapper.vm.$nextTick()
      
      const deleteButton = wrapper.find('[data-testid="delete-selected"]')
      await deleteButton.trigger('click')
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.modal').exists()).toBe(true)
      expect(wrapper.text()).toContain('Are you sure you want to delete 2 modules?')
    })

    it('lists modules to be deleted in confirmation', async () => {
      const wrapper = mount(BulkOperationsPanel, { props: { show: true } })
      
      store.toggleModuleSelection('UserAuthentication')
      store.toggleModuleSelection('DataProcessor')
      
      await wrapper.vm.$nextTick()
      
      const deleteButton = wrapper.find('[data-testid="delete-selected"]')
      await deleteButton.trigger('click')
      
      await wrapper.vm.$nextTick()
      
      const modulesList = wrapper.find('.modules-to-delete')
      expect(modulesList.text()).toContain('UserAuthentication')
      expect(modulesList.text()).toContain('DataProcessor')
    })
  })

  describe('Component Integration', () => {
    it('properly integrates with module store state', async () => {
      const wrapper = mount(BulkOperationsPanel, { props: { show: true } })
      
      // Initially no selections
      expect(wrapper.find('.bulk-actions').exists()).toBe(false)
      
      // Select some modules
      store.toggleModuleSelection('UserAuthentication')
      await wrapper.vm.$nextTick()
      
      // Now bulk actions should be visible
      expect(wrapper.find('.bulk-actions').exists()).toBe(true)
      expect(wrapper.find('.selection-count').text()).toContain('1 modules selected')
    })

    it('responds to store state changes', async () => {
      const wrapper = mount(BulkOperationsPanel, { props: { show: true } })
      
      store.toggleModuleSelection('UserAuthentication')
      store.toggleModuleSelection('DataProcessor')
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.selection-count').text()).toContain('2 modules selected')
      
      // Clear selections from store
      store.clearAllSelections()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.selection-count').text()).toContain('0 modules selected')
    })
  })
})