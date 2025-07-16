<template>
  <div class="module-panel">
    <div class="panel-header">
      <h3>{{ module.name }}</h3>
      <button @click="$emit('close')" class="close-button" aria-label="Close panel">
        ×
      </button>
    </div>
    
    <div class="panel-content">
      <div class="module-info">
        <div class="info-item">
          <label>Status:</label>
          <span class="status-badge" :class="module.status">
            {{ module.status }}
          </span>
        </div>
        
        <div v-if="module.version" class="info-item">
          <label>Version:</label>
          <span>{{ module.version }}</span>
        </div>
        
        <div class="info-item">
          <label>Description:</label>
          <p class="description">{{ module.description }}</p>
        </div>
        
        <div v-if="module.file_path" class="info-item">
          <label>File Path:</label>
          <span class="file-path">{{ module.file_path }}</span>
        </div>
      </div>
      
      <div v-if="module.inputs && module.inputs.length" class="section">
        <h4>Inputs</h4>
        <ul class="list">
          <li v-for="input in module.inputs" :key="input">{{ input }}</li>
        </ul>
      </div>
      
      <div v-if="module.outputs && module.outputs.length" class="section">
        <h4>Outputs</h4>
        <ul class="list">
          <li v-for="output in module.outputs" :key="output">{{ output }}</li>
        </ul>
      </div>
      
      <div v-if="module.dependencies && module.dependencies.length" class="section">
        <h4>Dependencies</h4>
        <ul class="list">
          <li v-for="dep in module.dependencies" :key="dep" class="dependency-item">
            <button @click="selectDependency(dep)" class="dependency-link">
              {{ dep }}
            </button>
          </li>
        </ul>
      </div>
      
      <div class="section">
        <h4>Actions</h4>
        <div class="action-buttons">
          <button @click="editModule" class="action-button edit">
            Edit
          </button>
          <button @click="duplicateModule" class="action-button duplicate">
            Duplicate
          </button>
          <button @click="deleteModule" class="action-button delete" :disabled="isDeleting">
            {{ isDeleting ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Module } from '../stores/moduleStore'
import { useModuleStore } from '../stores/moduleStore'

interface Props {
  module: Module
}

const props = defineProps<Props>()
defineEmits<{
  close: []
}>()

const moduleStore = useModuleStore()
const isDeleting = ref(false)

const selectDependency = (depName: string) => {
  moduleStore.selectModule(depName)
}

const editModule = () => {
  // Future: Open edit modal or inline editing
  console.log('Edit module functionality coming soon')
}

const duplicateModule = () => {
  // Future: Duplicate module functionality
  console.log('Duplicate module functionality coming soon')
}

const deleteModule = async () => {
  if (!confirm(`Are you sure you want to delete the module "${props.module.name}"?`)) {
    return
  }
  
  isDeleting.value = true
  try {
    await moduleStore.deleteModule(props.module.name)
  } catch (error) {
    console.error('Failed to delete module:', error)
    // Error is handled by the store
  } finally {
    isDeleting.value = false
  }
}
</script>

<style scoped>
.module-panel {
  position: absolute;
  top: 0;
  right: 0;
  width: 350px;
  height: 100%;
  background: white;
  border-left: 1px solid #ddd;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  z-index: 20;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #eee;
  background: #f8f9fa;
}

.panel-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #2c3e50;
  font-weight: 600;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  color: #666;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.close-button:hover {
  background: #e9ecef;
  color: #333;
}

.panel-content {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
}

.module-info {
  margin-bottom: 1.5rem;
}

.info-item {
  margin-bottom: 1rem;
}

.info-item label {
  display: block;
  font-weight: 600;
  color: #555;
  margin-bottom: 0.25rem;
  font-size: 0.875rem;
}

.info-item span,
.info-item p {
  margin: 0;
  color: #333;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.implemented {
  background: #d4edda;
  color: #155724;
}

.status-badge.placeholder {
  background: #fff3cd;
  color: #856404;
}

.status-badge.error {
  background: #f8d7da;
  color: #721c24;
}

.description {
  line-height: 1.5;
  color: #666;
}

.file-path {
  font-family: monospace;
  font-size: 0.875rem;
  color: #666;
  background: #f8f9fa;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.section {
  margin-bottom: 1.5rem;
}

.section h4 {
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
  color: #2c3e50;
  font-weight: 600;
}

.list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.list li {
  padding: 0.5rem;
  border: 1px solid #eee;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  background: #f8f9fa;
}

.dependency-item {
  padding: 0 !important;
  background: none !important;
  border: none !important;
}

.dependency-link {
  display: block;
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #eee;
  border-radius: 4px;
  background: #f8f9fa;
  color: #3498db;
  text-decoration: none;
  cursor: pointer;
  text-align: left;
  font-family: inherit;
  font-size: inherit;
}

.dependency-link:hover {
  background: #e3f2fd;
  border-color: #3498db;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.action-button.edit {
  background: #3498db;
  color: white;
}

.action-button.edit:hover {
  background: #2980b9;
}

.action-button.duplicate {
  background: #95a5a6;
  color: white;
}

.action-button.duplicate:hover {
  background: #7f8c8d;
}

.action-button.delete {
  background: #e74c3c;
  color: white;
}

.action-button.delete:hover:not(:disabled) {
  background: #c0392b;
}

.action-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style> 