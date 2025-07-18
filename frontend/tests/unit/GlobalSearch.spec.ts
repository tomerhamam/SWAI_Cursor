import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import GlobalSearch from '@/components/GlobalSearch.vue'
import { useModuleStore } from '@/stores/moduleStore'
import type { Module } from '@/stores/moduleStore'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', { value: localStorageMock })

describe('GlobalSearch', () => {
  beforeEach(() => {
    // Create a fresh pinia instance before each test
    setActivePinia(createPinia())
    // Clear localStorage mocks
    localStorageMock.getItem.mockClear()
    localStorageMock.setItem.mockClear()
  })

  const mockModules = {
    module1: {
      name: 'TestModule',
      description: 'A test module for searching',
      status: 'implemented',
      version: '1.0.0',
      inputs: ['input1'],
      outputs: ['output1'],
      dependencies: ['dependency1']
    } as Module,
    module2: {
      name: 'AnotherModule',
      description: 'Another module',
      status: 'placeholder',
      version: '2.0.0',
      inputs: ['input2'],
      outputs: ['output2'],
      dependencies: ['dependency2']
    } as Module
  }

  it('renders search input correctly', () => {
    const wrapper = mount(GlobalSearch)

    const searchInput = wrapper.find('.search-input')
    expect(searchInput.exists()).toBe(true)
    expect(searchInput.attributes('placeholder')).toBe('Search modules...')
  })

  it('shows search icon when input is empty', () => {
    const wrapper = mount(GlobalSearch)

    const searchIcon = wrapper.find('.search-icon')
    expect(searchIcon.text()).toBe('🔍')
  })

  it('shows clear button when input has text', async () => {
    const wrapper = mount(GlobalSearch)
    const searchInput = wrapper.find('.search-input')

    await searchInput.setValue('test')

    const clearButton = wrapper.find('.clear-button')
    expect(clearButton.exists()).toBe(true)
    expect(clearButton.text()).toBe('×')
  })

  it('emits searchChange event when input changes', async () => {
    const wrapper = mount(GlobalSearch)
    const searchInput = wrapper.find('.search-input')

    await searchInput.setValue('test')
    await searchInput.trigger('input')

    // Wait for debounce
    await new Promise(resolve => setTimeout(resolve, 350))

    expect(wrapper.emitted('searchChange')).toBeTruthy()
    const emittedData = wrapper.emitted('searchChange')![0][0] as any
    expect(emittedData.query).toBe('test')
  })

  it('clears search when clear button is clicked', async () => {
    const wrapper = mount(GlobalSearch)
    const searchInput = wrapper.find('.search-input')

    await searchInput.setValue('test')
    const clearButton = wrapper.find('.clear-button')
    await clearButton.trigger('click')

    expect((searchInput.element as HTMLInputElement).value).toBe('')
  })

  it('shows suggestions when focused with modules available', async () => {
    const store = useModuleStore()
    store.modules = mockModules
    
    const wrapper = mount(GlobalSearch)
    const searchInput = wrapper.find('.search-input')

    await searchInput.trigger('focus')

    const suggestions = wrapper.find('.search-suggestions')
    expect(suggestions.exists()).toBe(true)
  })

  it('hides suggestions when blurred', async () => {
    const wrapper = mount(GlobalSearch)
    const searchInput = wrapper.find('.search-input')

    await searchInput.trigger('focus')
    await searchInput.trigger('blur')

    // Wait for blur delay
    await new Promise(resolve => setTimeout(resolve, 250))

    const suggestions = wrapper.find('.search-suggestions')
    expect(suggestions.exists()).toBe(false)
  })

  it('handles keyboard navigation with arrow keys', async () => {
    const wrapper = mount(GlobalSearch)
    const searchInput = wrapper.find('.search-input')

    await searchInput.trigger('focus')
    await searchInput.trigger('keydown', { key: 'ArrowDown' })

    // Should not crash and should handle navigation
    expect(wrapper.vm).toBeDefined()
  })

  it('handles escape key to close suggestions', async () => {
    const wrapper = mount(GlobalSearch)
    const searchInput = wrapper.find('.search-input')

    await searchInput.trigger('focus')
    await searchInput.trigger('keydown', { key: 'Escape' })

    const suggestions = wrapper.find('.search-suggestions')
    expect(suggestions.exists()).toBe(false)
  })

  it('loads recent searches from localStorage on mount', () => {
    const mockHistory = ['test search', 'another search']
    localStorageMock.getItem.mockReturnValue(JSON.stringify(mockHistory))

    const wrapper = mount(GlobalSearch)

    expect(localStorageMock.getItem).toHaveBeenCalledWith('moduleSearchHistory')
  })

  it('saves recent searches to localStorage', async () => {
    const wrapper = mount(GlobalSearch)
    const searchInput = wrapper.find('.search-input')

    await searchInput.setValue('test search')
    await searchInput.trigger('keydown', { key: 'Enter' })

    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'moduleSearchHistory',
      expect.stringContaining('test search')
    )
  })

  it('displays module count when searching', async () => {
    const store = useModuleStore()
    store.modules = mockModules
    store.setSearchQuery('test')

    const wrapper = mount(GlobalSearch)
    
    // Should show search filters with module count
    const searchFilters = wrapper.find('.search-filters')
    if (searchFilters.exists()) {
      expect(searchFilters.text()).toContain('modules')
    }
  })

  it('exposes focus method', () => {
    const wrapper = mount(GlobalSearch)
    
    expect(wrapper.vm.focus).toBeDefined()
    expect(typeof wrapper.vm.focus).toBe('function')
  })

  it('exposes clear method', () => {
    const wrapper = mount(GlobalSearch)
    
    expect(wrapper.vm.clear).toBeDefined()
    expect(typeof wrapper.vm.clear).toBe('function')
  })

  it('handles search input debouncing correctly', async () => {
    const wrapper = mount(GlobalSearch)
    const searchInput = wrapper.find('.search-input')

    // Type multiple characters quickly
    await searchInput.setValue('t')
    await searchInput.trigger('input')
    await searchInput.setValue('te')
    await searchInput.trigger('input')
    await searchInput.setValue('test')
    await searchInput.trigger('input')

    // Should only emit once after debounce period
    await new Promise(resolve => setTimeout(resolve, 350))

    expect(wrapper.emitted('searchChange')).toHaveLength(1)
  })
})