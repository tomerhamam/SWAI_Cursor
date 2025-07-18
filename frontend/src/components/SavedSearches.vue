<template>
  <div class="saved-searches">
    <div class="saved-searches-header">
      <h3>Saved Searches</h3>
      <button 
        @click="saveCurrentSearch"
        class="save-button"
        :disabled="!canSaveCurrentSearch"
        title="Save current search and filters"
      >
        💾 Save Current
      </button>
    </div>
    
    <div v-if="savedSearches.length === 0" class="empty-state">
      <p>No saved searches yet</p>
      <p class="help-text">Apply some filters and search terms, then click "Save Current" to bookmark them.</p>
    </div>
    
    <div v-else class="saved-searches-list">
      <div 
        v-for="search in savedSearches" 
        :key="search.id"
        class="saved-search-item"
        :class="{ active: isCurrentSearch(search) }"
      >
        <div class="search-info" @click="applySearch(search)">
          <div class="search-name">{{ search.name }}</div>
          <div class="search-description">
            <span v-if="search.query" class="search-query">
              "{{ search.query }}"
            </span>
            <span v-if="search.statusFilters.length > 0" class="status-filters">
              {{ search.statusFilters.join(', ') }}
            </span>
            <span v-if="search.searchFilters.length > 0" class="search-filters">
              {{ search.searchFilters.length }} filter{{ search.searchFilters.length > 1 ? 's' : '' }}
            </span>
          </div>
          <div class="search-meta">
            <span class="search-date">{{ formatDate(search.createdAt) }}</span>
            <span class="search-results">{{ search.resultCount }} results</span>
          </div>
        </div>
        
        <div class="search-actions">
          <button 
            @click.stop="editSearch(search)"
            class="action-button edit"
            title="Edit search name"
          >
            ✏️
          </button>
          <button 
            @click.stop="duplicateSearch(search)"
            class="action-button duplicate"
            title="Duplicate search"
          >
            📋
          </button>
          <button 
            @click.stop="deleteSearch(search.id)"
            class="action-button delete"
            title="Delete search"
          >
            🗑️
          </button>
        </div>
      </div>
    </div>
    
    <!-- Edit Dialog -->
    <div v-if="editingSearch" class="modal-overlay" @click="cancelEdit">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Edit Search Name</h3>
        </div>
        <div class="modal-body">
          <input 
            ref="editInput"
            v-model="editedName"
            type="text"
            class="name-input"
            placeholder="Enter search name"
            @keyup.enter="saveEdit"
            @keyup.escape="cancelEdit"
          />
        </div>
        <div class="modal-actions">
          <button @click="cancelEdit" class="action-button secondary">
            Cancel
          </button>
          <button @click="saveEdit" class="action-button primary" :disabled="!editedName.trim()">
            Save
          </button>
        </div>
      </div>
    </div>
    
    <!-- Save Dialog -->
    <div v-if="showSaveDialog" class="modal-overlay" @click="cancelSave">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Save Search</h3>
        </div>
        <div class="modal-body">
          <label class="input-label">Search Name:</label>
          <input 
            ref="saveInput"
            v-model="newSearchName"
            type="text"
            class="name-input"
            placeholder="Enter a name for this search"
            @keyup.enter="confirmSave"
            @keyup.escape="cancelSave"
          />
          
          <div class="search-preview">
            <div class="preview-label">Search Preview:</div>
            <div class="preview-content">
              <div v-if="currentSearchQuery" class="preview-item">
                <strong>Query:</strong> "{{ currentSearchQuery }}"
              </div>
              <div v-if="currentStatusFilters.length > 0" class="preview-item">
                <strong>Status:</strong> {{ currentStatusFilters.join(', ') }}
              </div>
              <div v-if="currentSearchFilters.length > 0" class="preview-item">
                <strong>Filters:</strong> {{ currentSearchFilters.length }} additional filter{{ currentSearchFilters.length > 1 ? 's' : '' }}
              </div>
              <div class="preview-item">
                <strong>Results:</strong> {{ currentResultCount }} modules
              </div>
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="cancelSave" class="action-button secondary">
            Cancel
          </button>
          <button @click="confirmSave" class="action-button primary" :disabled="!newSearchName.trim()">
            Save Search
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useModuleStore } from '../stores/moduleStore'
import type { SearchFilter } from '../stores/moduleStore'

interface SavedSearch {
  id: string
  name: string
  query: string
  statusFilters: string[]
  searchFilters: SearchFilter[]
  resultCount: number
  createdAt: Date
  lastUsed: Date
}

interface SavedSearchData {
  id: string
  name: string
  query: string
  statusFilters: string[]
  searchFilters: SearchFilter[]
  resultCount: number
  createdAt: string // ISO string when stored
  lastUsed: string   // ISO string when stored
}

const moduleStore = useModuleStore()

// Reactive state
const savedSearches = ref<SavedSearch[]>([])
const showSaveDialog = ref(false)
const newSearchName = ref('')
const editingSearch = ref<SavedSearch | null>(null)
const editedName = ref('')

// Refs for inputs
const saveInput = ref<HTMLInputElement>()
const editInput = ref<HTMLInputElement>()

// Computed properties
const canSaveCurrentSearch = computed(() => {
  return moduleStore.hasActiveFilters
})

const currentSearchQuery = computed(() => moduleStore.searchQuery)
const currentStatusFilters = computed(() => Array.from(moduleStore.statusFilters))
const currentSearchFilters = computed(() => moduleStore.searchFilters)
const currentResultCount = computed(() => moduleStore.searchResultsCount)

// Methods
const saveCurrentSearch = () => {
  if (!canSaveCurrentSearch.value) return
  
  // Generate default name based on current search
  const defaultName = generateDefaultSearchName()
  newSearchName.value = defaultName
  showSaveDialog.value = true
  
  nextTick(() => {
    saveInput.value?.focus()
    saveInput.value?.select()
  })
}

const generateDefaultSearchName = (): string => {
  const parts: string[] = []
  
  if (currentSearchQuery.value) {
    parts.push(`"${currentSearchQuery.value}"`)
  }
  
  if (currentStatusFilters.value.length > 0) {
    parts.push(currentStatusFilters.value.join(', '))
  }
  
  if (currentSearchFilters.value.length > 0) {
    parts.push(`${currentSearchFilters.value.length} filters`)
  }
  
  if (parts.length === 0) {
    return 'All Modules'
  }
  
  return parts.join(' + ')
}

const confirmSave = () => {
  if (!newSearchName.value.trim()) return
  
  const newSearch: SavedSearch = {
    id: generateId(),
    name: newSearchName.value.trim(),
    query: currentSearchQuery.value,
    statusFilters: [...currentStatusFilters.value],
    searchFilters: [...currentSearchFilters.value],
    resultCount: currentResultCount.value,
    createdAt: new Date(),
    lastUsed: new Date()
  }
  
  savedSearches.value.unshift(newSearch)
  saveToPersistentStorage()
  
  cancelSave()
}

const cancelSave = () => {
  showSaveDialog.value = false
  newSearchName.value = ''
}

const applySearch = (search: SavedSearch) => {
  // Update last used
  search.lastUsed = new Date()
  saveToPersistentStorage()
  
  // Apply the search filters
  moduleStore.setSearchQuery(search.query)
  moduleStore.setStatusFilters(new Set(search.statusFilters))
  
  // Clear existing search filters and add saved ones
  moduleStore.clearSearchFilters()
  search.searchFilters.forEach(filter => {
    moduleStore.addSearchFilter(filter)
  })
}

const isCurrentSearch = (search: SavedSearch): boolean => {
  const queryMatches = moduleStore.searchQuery === search.query
  const statusMatches = arraysEqual(Array.from(moduleStore.statusFilters).sort(), search.statusFilters.sort())
  const filtersMatch = searchFiltersEqual(moduleStore.searchFilters, search.searchFilters)
  
  return queryMatches && statusMatches && filtersMatch
}

const editSearch = (search: SavedSearch) => {
  editingSearch.value = search
  editedName.value = search.name
  
  nextTick(() => {
    editInput.value?.focus()
    editInput.value?.select()
  })
}

const saveEdit = () => {
  if (!editingSearch.value || !editedName.value.trim()) return
  
  editingSearch.value.name = editedName.value.trim()
  saveToPersistentStorage()
  cancelEdit()
}

const cancelEdit = () => {
  editingSearch.value = null
  editedName.value = ''
}

const duplicateSearch = (search: SavedSearch) => {
  const duplicate: SavedSearch = {
    ...search,
    id: generateId(),
    name: `${search.name} (Copy)`,
    createdAt: new Date(),
    lastUsed: new Date()
  }
  
  savedSearches.value.unshift(duplicate)
  saveToPersistentStorage()
}

const deleteSearch = (searchId: string) => {
  if (confirm('Are you sure you want to delete this saved search?')) {
    savedSearches.value = savedSearches.value.filter(s => s.id !== searchId)
    saveToPersistentStorage()
  }
}

const formatDate = (date: Date): string => {
  const now = new Date()
  const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)
  
  if (diffInHours < 1) {
    return 'Just now'
  } else if (diffInHours < 24) {
    return `${Math.floor(diffInHours)}h ago`
  } else if (diffInHours < 24 * 7) {
    return `${Math.floor(diffInHours / 24)}d ago`
  } else {
    return date.toLocaleDateString()
  }
}

// Utility functions
const generateId = (): string => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

const arraysEqual = <T>(a: T[], b: T[]): boolean => {
  return a.length === b.length && a.every((val, i) => val === b[i])
}

const searchFiltersEqual = (a: SearchFilter[], b: SearchFilter[]): boolean => {
  if (a.length !== b.length) return false
  
  const sortedA = [...a].sort((x, y) => `${x.type}${x.value}`.localeCompare(`${y.type}${y.value}`))
  const sortedB = [...b].sort((x, y) => `${x.type}${x.value}`.localeCompare(`${y.type}${y.value}`))
  
  return sortedA.every((filter, i) => 
    filter.type === sortedB[i].type && 
    filter.value === sortedB[i].value
  )
}

const saveToPersistentStorage = () => {
  try {
    localStorage.setItem('moduleSavedSearches', JSON.stringify(savedSearches.value))
  } catch (error) {
    console.warn('Failed to save searches to localStorage:', error)
  }
}

const loadFromPersistentStorage = () => {
  try {
    const saved = localStorage.getItem('moduleSavedSearches')
    if (saved) {
      const parsed = JSON.parse(saved)
      savedSearches.value = parsed.map((search: SavedSearchData) => ({
        ...search,
        createdAt: new Date(search.createdAt),
        lastUsed: new Date(search.lastUsed)
      }))
    }
  } catch (error) {
    console.warn('Failed to load saved searches:', error)
  }
}

// Lifecycle
onMounted(() => {
  loadFromPersistentStorage()
})
</script>

<style scoped>
.saved-searches {
  background: white;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  max-height: 400px;
  overflow-y: auto;
}

.saved-searches-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 12px;
  border-bottom: 1px solid #f0f0f0;
  background: #f8f9fa;
  border-radius: 8px 8px 0 0;
}

.saved-searches-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.save-button {
  padding: 6px 12px;
  border: 2px solid #4a90e2;
  border-radius: 6px;
  background: white;
  color: #4a90e2;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.save-button:hover:not(:disabled) {
  background: #4a90e2;
  color: white;
}

.save-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  border-color: #ccc;
  color: #ccc;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: #666;
}

.help-text {
  font-size: 14px;
  margin-top: 8px;
  color: #888;
}

.saved-searches-list {
  padding: 8px 0;
}

.saved-search-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.saved-search-item:hover {
  background: #f8f9fa;
}

.saved-search-item.active {
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
}

.saved-search-item:last-child {
  border-bottom: none;
}

.search-info {
  flex: 1;
  cursor: pointer;
}

.search-name {
  font-weight: 600;
  font-size: 14px;
  color: #333;
  margin-bottom: 4px;
}

.search-description {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.search-query {
  color: #4a90e2;
  font-style: italic;
}

.status-filters {
  color: #f39c12;
}

.search-filters {
  color: #9b59b6;
}

.search-meta {
  font-size: 11px;
  color: #888;
  display: flex;
  gap: 12px;
}

.search-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.saved-search-item:hover .search-actions {
  opacity: 1;
}

.action-button {
  padding: 4px 8px;
  border: 1px solid transparent;
  border-radius: 4px;
  background: transparent;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.action-button.edit:hover {
  background: #fff3cd;
  border-color: #ffc107;
}

.action-button.duplicate:hover {
  background: #d1ecf1;
  border-color: #17a2b8;
}

.action-button.delete:hover {
  background: #f8d7da;
  border-color: #dc3545;
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

.input-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.name-input {
  width: 100%;
  padding: 12px;
  border: 2px solid #e1e5e9;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.name-input:focus {
  outline: none;
  border-color: #4a90e2;
}

.search-preview {
  margin-top: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
}

.preview-label {
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.preview-item {
  font-size: 14px;
  color: #666;
}

.preview-item strong {
  color: #333;
}

.modal-actions {
  padding: 16px 24px 20px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.action-button.primary {
  background: #4a90e2;
  color: white;
  border: 2px solid #4a90e2;
}

.action-button.primary:hover:not(:disabled) {
  background: #357abd;
  border-color: #357abd;
}

.action-button.secondary {
  background: white;
  color: #666;
  border: 2px solid #e1e5e9;
}

.action-button.secondary:hover {
  background: #f8f9fa;
  border-color: #ccc;
}

.action-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Responsive Design */
@media (max-width: 768px) {
  .saved-searches-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .search-description {
    flex-direction: column;
    gap: 4px;
  }
  
  .search-meta {
    flex-direction: column;
    gap: 2px;
  }
  
  .modal {
    margin: 20px;
    width: auto;
  }
}
</style>