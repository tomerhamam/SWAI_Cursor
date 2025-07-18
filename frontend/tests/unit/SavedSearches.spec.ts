import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import SavedSearches from '@/components/SavedSearches.vue'
import { useModuleStore } from '@/stores/moduleStore'
import type { Module } from '@/stores/moduleStore'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})

describe('SavedSearches', () => {
  let store: ReturnType<typeof useModuleStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useModuleStore()
    
    // Clear localStorage mocks
    localStorageMock.getItem.mockClear()
    localStorageMock.setItem.mockClear()
    
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
      }
    } as Record<string, Module>
  })

  describe('Component Rendering', () => {
    it('renders without crashing', () => {
      const wrapper = mount(SavedSearches)
      expect(wrapper.find('.saved-searches').exists()).toBe(true)
    })

    it('shows empty state when no saved searches', () => {
      localStorageMock.getItem.mockReturnValue(null)
      
      const wrapper = mount(SavedSearches)
      expect(wrapper.find('.empty-state').exists()).toBe(true)
      expect(wrapper.text()).toContain('No saved searches yet')
    })

    it('disables save button when no active filters', () => {
      const wrapper = mount(SavedSearches)
      
      const saveButton = wrapper.find('.save-button')
      expect(saveButton.attributes('disabled')).toBeDefined()
    })

    it('enables save button when filters are active', async () => {
      const wrapper = mount(SavedSearches)
      
      // Apply some filters to enable save button
      store.setSearchQuery('test')
      await wrapper.vm.$nextTick()
      
      const saveButton = wrapper.find('.save-button')
      expect(saveButton.attributes('disabled')).toBeUndefined()
    })
  })

  describe('Search Management', () => {
    it('opens save dialog when save button is clicked', async () => {
      const wrapper = mount(SavedSearches)
      
      store.setSearchQuery('test query')
      await wrapper.vm.$nextTick()
      
      const saveButton = wrapper.find('.save-button')
      await saveButton.trigger('click')
      
      expect(wrapper.find('.modal').exists()).toBe(true)
      expect(wrapper.text()).toContain('Save Search')
    })

    it('generates appropriate default search name', async () => {
      const wrapper = mount(SavedSearches)
      
      store.setSearchQuery('authentication')
      store.setStatusFilters(new Set(['implemented']))
      await wrapper.vm.$nextTick()
      
      const saveButton = wrapper.find('.save-button')
      await saveButton.trigger('click')
      
      const nameInput = wrapper.find('.name-input')
      expect((nameInput.element as HTMLInputElement).value).toContain('authentication')
      expect((nameInput.element as HTMLInputElement).value).toContain('implemented')
    })

    it('shows search preview in save dialog', async () => {
      const wrapper = mount(SavedSearches)
      
      store.setSearchQuery('test query')
      store.setStatusFilters(new Set(['implemented', 'placeholder']))
      await wrapper.vm.$nextTick()
      
      const saveButton = wrapper.find('.save-button')
      await saveButton.trigger('click')
      
      const previewContent = wrapper.find('.preview-content')
      expect(previewContent.text()).toContain('test query')
      expect(previewContent.text()).toContain('implemented, placeholder')
    })
  })

  describe('Persistence', () => {
    it('loads saved searches from localStorage on mount', () => {
      const mockSavedSearches = JSON.stringify([
        {
          id: 'test1',
          name: 'Test Search',
          query: 'test',
          statusFilters: ['implemented'],
          searchFilters: [],
          resultCount: 1,
          createdAt: new Date().toISOString(),
          lastUsed: new Date().toISOString()
        }
      ])
      
      localStorageMock.getItem.mockReturnValue(mockSavedSearches)
      
      const wrapper = mount(SavedSearches)
      
      expect(localStorageMock.getItem).toHaveBeenCalledWith('moduleSavedSearches')
      expect(wrapper.find('.saved-search-item').exists()).toBe(true)
      expect(wrapper.text()).toContain('Test Search')
    })

    it('saves searches to localStorage', async () => {
      const wrapper = mount(SavedSearches)
      
      store.setSearchQuery('test query')
      await wrapper.vm.$nextTick()
      
      // Open save dialog
      const saveButton = wrapper.find('.save-button')
      await saveButton.trigger('click')
      
      // Enter name and save
      const nameInput = wrapper.find('.name-input')
      await nameInput.setValue('My Test Search')
      
      const confirmButton = wrapper.find('.action-button.primary')
      await confirmButton.trigger('click')
      
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'moduleSavedSearches',
        expect.stringContaining('My Test Search')
      )
    })
  })

  describe('Search Application', () => {
    it('applies saved search when clicked', async () => {
      // Mock existing saved search
      const mockSavedSearches = JSON.stringify([
        {
          id: 'test1',
          name: 'Test Search',
          query: 'authentication',
          statusFilters: ['implemented'],
          searchFilters: [],
          resultCount: 1,
          createdAt: new Date().toISOString(),
          lastUsed: new Date().toISOString()
        }
      ])
      
      localStorageMock.getItem.mockReturnValue(mockSavedSearches)
      
      const wrapper = mount(SavedSearches)
      
      // Click on the saved search
      const searchItem = wrapper.find('.search-info')
      await searchItem.trigger('click')
      
      // Verify the search was applied
      expect(store.searchQuery).toBe('authentication')
      expect(store.statusFilters.has('implemented')).toBe(true)
    })

    it('identifies current search correctly', async () => {
      // Apply some search filters
      store.setSearchQuery('test')
      store.setStatusFilters(new Set(['implemented']))
      
      // Mock saved search that matches current state
      const mockSavedSearches = JSON.stringify([
        {
          id: 'test1',
          name: 'Test Search',
          query: 'test',
          statusFilters: ['implemented'],
          searchFilters: [],
          resultCount: 1,
          createdAt: new Date().toISOString(),
          lastUsed: new Date().toISOString()
        }
      ])
      
      localStorageMock.getItem.mockReturnValue(mockSavedSearches)
      
      const wrapper = mount(SavedSearches)
      await wrapper.vm.$nextTick()
      
      // The matching search should be marked as active
      expect(wrapper.find('.saved-search-item.active').exists()).toBe(true)
    })
  })

  describe('Search Operations', () => {
    beforeEach(() => {
      const mockSavedSearches = JSON.stringify([
        {
          id: 'test1',
          name: 'Test Search',
          query: 'test',
          statusFilters: ['implemented'],
          searchFilters: [],
          resultCount: 1,
          createdAt: new Date().toISOString(),
          lastUsed: new Date().toISOString()
        }
      ])
      
      localStorageMock.getItem.mockReturnValue(mockSavedSearches)
    })

    it('opens edit dialog when edit button is clicked', async () => {
      const wrapper = mount(SavedSearches)
      
      const editButton = wrapper.find('.action-button.edit')
      await editButton.trigger('click')
      
      expect(wrapper.find('.modal').exists()).toBe(true)
      expect(wrapper.text()).toContain('Edit Search Name')
    })

    it('duplicates search when duplicate button is clicked', async () => {
      const wrapper = mount(SavedSearches)
      
      const duplicateButton = wrapper.find('.action-button.duplicate')
      await duplicateButton.trigger('click')
      
      expect(localStorageMock.setItem).toHaveBeenCalled()
      // Should have created a copy with "(Copy)" in the name
      const lastCall = localStorageMock.setItem.mock.calls[localStorageMock.setItem.mock.calls.length - 1]
      expect(lastCall[1]).toContain('Test Search (Copy)')
    })
  })

  describe('Date Formatting', () => {
    it('formats recent dates correctly', async () => {
      const recentDate = new Date()
      recentDate.setHours(recentDate.getHours() - 2) // 2 hours ago
      
      const mockSavedSearches = JSON.stringify([
        {
          id: 'test1',
          name: 'Recent Search',
          query: 'test',
          statusFilters: [],
          searchFilters: [],
          resultCount: 1,
          createdAt: recentDate.toISOString(),
          lastUsed: recentDate.toISOString()
        }
      ])
      
      localStorageMock.getItem.mockReturnValue(mockSavedSearches)
      
      const wrapper = mount(SavedSearches)
      
      expect(wrapper.text()).toContain('2h ago')
    })
  })
})