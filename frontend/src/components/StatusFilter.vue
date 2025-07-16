<template>
  <div class="status-filter">
    <label class="filter-label">Filter by Status:</label>
    <div class="filter-options">
      <button
        class="filter-btn"
        :class="{ active: selectedStatuses.size === 0 }"
        @click="showAll"
      >
        All ({{ totalCount }})
      </button>
      
      <button
        v-for="status in availableStatuses"
        :key="status.value"
        class="filter-btn"
        :class="{ 
          active: selectedStatuses.has(status.value),
          [status.value]: true 
        }"
        @click="toggleStatus(status.value)"
      >
        {{ status.label }} ({{ getStatusCount(status.value) }})
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Module } from '../stores/moduleStore'

interface Props {
  modules: Record<string, Module>
}

const props = defineProps<Props>()

const emit = defineEmits<{
  filterChange: [statuses: Set<Module['status']>]
}>()

const selectedStatuses = ref<Set<Module['status']>>(new Set())

const availableStatuses = [
  { value: 'implemented' as const, label: 'Implemented', color: '#27ae60' },
  { value: 'placeholder' as const, label: 'Placeholder', color: '#f39c12' },
  { value: 'error' as const, label: 'Error', color: '#e74c3c' }
]

const totalCount = computed(() => Object.keys(props.modules).length)

const getStatusCount = (status: Module['status']) => {
  return Object.values(props.modules).filter(module => module.status === status).length
}

const toggleStatus = (status: Module['status']) => {
  if (selectedStatuses.value.has(status)) {
    selectedStatuses.value.delete(status)
  } else {
    selectedStatuses.value.add(status)
  }
  emit('filterChange', new Set(selectedStatuses.value))
}

const showAll = () => {
  selectedStatuses.value.clear()
  emit('filterChange', new Set())
}
</script>

<style scoped>
.status-filter {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
}

.filter-label {
  font-weight: 500;
  color: #2c3e50;
  font-size: 14px;
  white-space: nowrap;
}

.filter-options {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 16px;
  background: white;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.filter-btn:hover {
  border-color: #4a90e2;
  color: #4a90e2;
}

.filter-btn.active {
  background: #4a90e2;
  border-color: #4a90e2;
  color: white;
}

.filter-btn.implemented.active {
  background: #27ae60;
  border-color: #27ae60;
}

.filter-btn.placeholder.active {
  background: #f39c12;
  border-color: #f39c12;
}

.filter-btn.error.active {
  background: #e74c3c;
  border-color: #e74c3c;
}

/* Responsive design */
@media (max-width: 768px) {
  .status-filter {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .filter-options {
    width: 100%;
  }
}
</style> 