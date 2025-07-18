<template>
  <div class="global-search">
    <div class="search-input-container">
      <div class="search-input-wrapper">
        <input
          ref="searchInput"
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="Search modules..."
          @input="handleSearchInput"
          @keydown="handleKeyDown"
          @focus="showSuggestions = true"
          @blur="handleBlur"
        />
        <div class="search-icon">
          <span v-if="!searchQuery">🔍</span>
          <button 
            v-else 
            @click="clearSearch" 
            class="clear-button"
            aria-label="Clear search"
          >
            ×
          </button>
        </div>
      </div>
      
      <!-- Search suggestions dropdown -->
      <div 
        v-if="showSuggestions && (searchSuggestions.length > 0 || recentSearches.length > 0)"
        class="search-suggestions"
        role="listbox"
        aria-label="Search suggestions"
      >
        <!-- Recent searches -->
        <div v-if="!searchQuery && recentSearches.length > 0" class="suggestion-section">
          <div class="suggestion-header">Recent Searches</div>
          <div
            v-for="recent in recentSearches"
            :key="'recent-' + recent"
            class="suggestion-item recent-search"
            role="option"
          >
            <button
              class="suggestion-button"
              @click="selectSuggestion(recent)"
            >
              <span class="suggestion-icon">🕒</span>
              <span class="suggestion-text">{{ recent }}</span>
            </button>
            <button 
              @click.stop="removeRecentSearch(recent)"
              class="remove-recent"
              aria-label="Remove from recent searches"
            >
              ×
            </button>
          </div>
        </div>
        
        <!-- Search suggestions -->
        <div v-if="searchSuggestions.length > 0" class="suggestion-section">
          <div v-if="!searchQuery" class="suggestion-header">Suggestions</div>
          <button
            v-for="(suggestion, index) in searchSuggestions"
            :key="suggestion.id"
            :class="['suggestion-item', { highlighted: index === highlightedIndex }]"
            @click="selectSuggestion(suggestion.text)"
            role="option"
            :aria-selected="index === highlightedIndex"
          >
            <span class="suggestion-icon">{{ suggestion.icon }}</span>
            <span class="suggestion-text" v-html="suggestion.highlightedText"></span>
            <span class="suggestion-type">{{ suggestion.type }}</span>
          </button>
        </div>
        
        <!-- No results -->
        <div v-if="searchQuery && searchSuggestions.length === 0" class="no-results">
          <span class="suggestion-icon">🔍</span>
          <span>No results found for "{{ searchQuery }}"</span>
        </div>
      </div>
    </div>
    
    <!-- Search filters -->
    <div v-if="searchQuery" class="search-filters">
      <div class="filter-chips">
        <button
          v-for="filter in activeFilters"
          :key="filter.type + '-' + filter.value"
          class="filter-chip"
          @click="removeFilter(filter)"
        >
          {{ filter.label }}
          <span class="chip-remove">×</span>
        </button>
      </div>
      
      <div class="search-stats">
        <span class="results-count">
          {{ filteredModulesCount }} of {{ totalModulesCount }} modules
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useModuleStore } from '../stores/moduleStore'
import type { Module } from '../stores/moduleStore'

interface SearchSuggestion {
  id: string
  text: string
  highlightedText: string
  type: 'module' | 'description' | 'dependency'
  icon: string
  module?: Module
}

interface SearchFilter {
  type: 'status' | 'dependency' | 'version'
  value: string
  label: string
}

const moduleStore = useModuleStore()

// Reactive refs
const searchQuery = ref('')
const searchInput = ref<HTMLInputElement>()
const showSuggestions = ref(false)
const highlightedIndex = ref(-1)
const recentSearches = ref<string[]>([])
const activeFilters = ref<SearchFilter[]>([])

// Debounced search
let searchTimeout: NodeJS.Timeout | null = null

// Computed properties
const totalModulesCount = computed(() => Object.keys(moduleStore.modules).length)

const searchSuggestions = computed(() => {
  if (!searchQuery.value || searchQuery.value.length < 2) {
    // Show popular modules or recent modules when no search
    return Object.values(moduleStore.modules)
      .slice(0, 5)
      .map(module => ({
        id: module.name,
        text: module.name,
        highlightedText: module.name,
        type: 'module' as const,
        icon: getModuleIcon(module.status),
        module
      }))
  }

  const query = searchQuery.value.toLowerCase()
  const suggestions: SearchSuggestion[] = []
  
  // Search in module names
  Object.values(moduleStore.modules).forEach(module => {
    if (module.name.toLowerCase().includes(query)) {
      suggestions.push({
        id: `module-${module.name}`,
        text: module.name,
        highlightedText: highlightText(module.name, query),
        type: 'module',
        icon: getModuleIcon(module.status),
        module
      })
    }
    
    // Search in descriptions
    if (module.description.toLowerCase().includes(query)) {
      suggestions.push({
        id: `desc-${module.name}`,
        text: module.description,
        highlightedText: highlightText(module.description, query),
        type: 'description',
        icon: '📝',
        module
      })
    }
    
    // Search in dependencies
    module.dependencies?.forEach(dep => {
      if (dep.toLowerCase().includes(query)) {
        suggestions.push({
          id: `dep-${module.name}-${dep}`,
          text: dep,
          highlightedText: highlightText(dep, query),
          type: 'dependency',
          icon: '🔗',
          module
        })
      }
    })
  })
  
  // Remove duplicates and limit results
  const uniqueSuggestions = suggestions.filter((suggestion, index, self) => 
    index === self.findIndex(s => s.text === suggestion.text && s.type === suggestion.type)
  )
  
  return uniqueSuggestions.slice(0, 8)
})

const filteredModulesCount = computed(() => {
  if (!searchQuery.value && activeFilters.value.length === 0) {
    return totalModulesCount.value
  }
  
  return Object.values(moduleStore.modules).filter(module => {
    // Apply search query
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      const matchesQuery = 
        module.name.toLowerCase().includes(query) ||
        module.description.toLowerCase().includes(query) ||
        module.dependencies?.some(dep => dep.toLowerCase().includes(query))
      
      if (!matchesQuery) return false
    }
    
    // Apply active filters
    return activeFilters.value.every(filter => {
      switch (filter.type) {
        case 'status':
          return module.status === filter.value
        case 'dependency':
          return module.dependencies?.includes(filter.value)
        case 'version':
          return module.version === filter.value
        default:
          return true
      }
    })
  }).length
})

// Methods
const handleSearchInput = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  
  searchTimeout = setTimeout(() => {
    emitSearchChange()
  }, 300) // 300ms debounce
}

const handleKeyDown = (event: KeyboardEvent) => {
  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      highlightedIndex.value = Math.min(
        highlightedIndex.value + 1,
        searchSuggestions.value.length - 1
      )
      break
    case 'ArrowUp':
      event.preventDefault()
      highlightedIndex.value = Math.max(highlightedIndex.value - 1, -1)
      break
    case 'Enter':
      event.preventDefault()
      if (highlightedIndex.value >= 0) {
        selectSuggestion(searchSuggestions.value[highlightedIndex.value].text)
      } else if (searchQuery.value) {
        performSearch()
      }
      break
    case 'Escape':
      showSuggestions.value = false
      searchInput.value?.blur()
      break
  }
}

const handleBlur = () => {
  // Delay hiding suggestions to allow clicking
  setTimeout(() => {
    showSuggestions.value = false
  }, 200)
}

const selectSuggestion = (text: string) => {
  searchQuery.value = text
  showSuggestions.value = false
  addToRecentSearches(text)
  performSearch()
}

const clearSearch = () => {
  searchQuery.value = ''
  activeFilters.value = []
  emitSearchChange()
  searchInput.value?.focus()
}

const performSearch = () => {
  if (searchQuery.value) {
    addToRecentSearches(searchQuery.value)
  }
  emitSearchChange()
}

const addToRecentSearches = (query: string) => {
  if (!query.trim()) return
  
  // Remove if already exists
  const filtered = recentSearches.value.filter(search => search !== query)
  // Add to beginning
  recentSearches.value = [query, ...filtered].slice(0, 5)
  
  // Save to localStorage
  localStorage.setItem('moduleSearchHistory', JSON.stringify(recentSearches.value))
}

const removeRecentSearch = (query: string) => {
  recentSearches.value = recentSearches.value.filter(search => search !== query)
  localStorage.setItem('moduleSearchHistory', JSON.stringify(recentSearches.value))
}

const removeFilter = (filter: SearchFilter) => {
  activeFilters.value = activeFilters.value.filter(f => 
    f.type !== filter.type || f.value !== filter.value
  )
  emitSearchChange()
}

const highlightText = (text: string, query: string): string => {
  if (!query) return text
  
  const regex = new RegExp(`(${query})`, 'gi')
  return text.replace(regex, '<strong>$1</strong>')
}

const getModuleIcon = (status: Module['status']): string => {
  switch (status) {
    case 'implemented': return '✅'
    case 'placeholder': return '⚠️'
    case 'error': return '❌'
    default: return '📦'
  }
}

const emitSearchChange = () => {
  emit('searchChange', {
    query: searchQuery.value,
    filters: activeFilters.value
  })
}

// Emits
const emit = defineEmits<{
  searchChange: [data: { query: string, filters: SearchFilter[] }]
}>()

// Lifecycle
onMounted(() => {
  // Load recent searches from localStorage
  try {
    const saved = localStorage.getItem('moduleSearchHistory')
    if (saved) {
      recentSearches.value = JSON.parse(saved)
    }
  } catch (error) {
    console.warn('Failed to load search history:', error)
  }
})

onUnmounted(() => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
})

// Watch for changes in search query
watch(searchQuery, () => {
  highlightedIndex.value = -1
})

// Expose methods for parent component
defineExpose({
  focus: () => searchInput.value?.focus(),
  clear: clearSearch
})
</script>

<style scoped>
.global-search {
  position: relative;
  width: 100%;
  max-width: 400px;
}

.search-input-container {
  position: relative;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input {
  width: 100%;
  padding: 10px 40px 10px 12px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

.search-icon {
  position: absolute;
  right: 12px;
  color: #666;
  pointer-events: none;
}

.clear-button {
  background: none;
  border: none;
  font-size: 18px;
  color: #666;
  cursor: pointer;
  padding: 0;
  pointer-events: auto;
  line-height: 1;
}

.clear-button:hover {
  color: #333;
}

.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-height: 300px;
  overflow-y: auto;
  margin-top: 4px;
}

.suggestion-section {
  padding: 8px 0;
}

.suggestion-section:not(:last-child) {
  border-bottom: 1px solid #f0f0f0;
}

.suggestion-header {
  padding: 8px 16px 4px;
  font-size: 12px;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
}

.suggestion-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 8px 16px;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  transition: background-color 0.2s;
}

.suggestion-item:hover,
.suggestion-item.highlighted {
  background-color: #f8f9fa;
}

.suggestion-icon {
  margin-right: 8px;
  font-size: 14px;
}

.suggestion-text {
  flex: 1;
  font-size: 14px;
  color: #333;
}

.suggestion-text :deep(strong) {
  background-color: #fff3cd;
  padding: 1px 2px;
  border-radius: 2px;
}

.suggestion-type {
  font-size: 12px;
  color: #666;
  margin-left: 8px;
  text-transform: capitalize;
}

.recent-search {
  color: #666;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0;
}

.suggestion-button {
  flex: 1;
  display: flex;
  align-items: center;
  background: none;
  border: none;
  padding: 8px 16px;
  cursor: pointer;
  text-align: left;
  color: inherit;
  font-family: inherit;
  font-size: inherit;
}

.suggestion-button:hover {
  background-color: #f8f9fa;
}

.remove-recent {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 0 4px;
  margin-left: 8px;
  font-size: 16px;
  line-height: 1;
}

.remove-recent:hover {
  color: #666;
}

.no-results {
  display: flex;
  align-items: center;
  padding: 16px;
  color: #666;
  font-style: italic;
}

.search-filters {
  margin-top: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.filter-chips {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.filter-chip {
  display: flex;
  align-items: center;
  padding: 4px 8px;
  background: #e3f2fd;
  border: 1px solid #90caf9;
  border-radius: 16px;
  font-size: 12px;
  color: #1976d2;
  cursor: pointer;
  transition: background-color 0.2s;
}

.filter-chip:hover {
  background: #bbdefb;
}

.chip-remove {
  margin-left: 4px;
  font-size: 14px;
  line-height: 1;
}

.search-stats {
  font-size: 12px;
  color: #666;
  white-space: nowrap;
}

.results-count {
  font-weight: 500;
}

/* Responsive design */
@media (max-width: 768px) {
  .global-search {
    max-width: none;
  }
  
  .search-filters {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>