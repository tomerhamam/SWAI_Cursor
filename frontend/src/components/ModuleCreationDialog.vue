<template>
  <div v-if="visible" class="dialog-overlay" @click="closeDialog">
    <div class="dialog" @click.stop>
      <div class="dialog-header">
        <h3>Create New Module</h3>
        <button class="close-btn" @click="closeDialog">×</button>
      </div>
      
      <form @submit.prevent="handleSubmit" class="dialog-content">
        <div class="form-group">
          <label for="module-name">Module Name *</label>
          <input
            id="module-name"
            v-model="formData.name"
            type="text"
            placeholder="Enter module name (e.g., DataProcessor)"
            required
            pattern="[a-zA-Z][a-zA-Z0-9_]*"
            title="Must start with a letter and contain only letters, numbers, and underscores"
            :class="{ 'error': errors.name }"
          />
          <span v-if="errors.name" class="error-text">{{ errors.name }}</span>
        </div>

        <div class="form-group">
          <label for="module-description">Description *</label>
          <textarea
            id="module-description"
            v-model="formData.description"
            placeholder="Describe what this module does"
            required
            rows="3"
            :class="{ 'error': errors.description }"
          ></textarea>
          <span v-if="errors.description" class="error-text">{{ errors.description }}</span>
        </div>

        <div class="form-group">
          <label for="module-status">Status</label>
          <select id="module-status" v-model="formData.status">
            <option value="placeholder">Placeholder</option>
            <option value="implemented">Implemented</option>
            <option value="error">Error</option>
          </select>
        </div>

        <div class="form-group">
          <label for="module-version">Version</label>
          <input
            id="module-version"
            v-model="formData.version"
            type="text"
            placeholder="1.0.0"
          />
        </div>

        <div class="form-group">
          <label for="module-dependencies">Dependencies</label>
          <input
            id="module-dependencies"
            v-model="dependenciesText"
            type="text"
            placeholder="Enter comma-separated module names"
          />
          <small class="help-text">Comma-separated list of module names this module depends on</small>
        </div>

        <div class="dialog-actions">
          <button type="button" class="btn btn-secondary" @click="closeDialog">Cancel</button>
          <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
            {{ isSubmitting ? 'Creating...' : 'Create Module' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import type { Module } from '../stores/moduleStore'

interface Props {
  visible: boolean
  position?: { x: number; y: number }
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  submit: [moduleData: Omit<Module, 'name'> & { name: string }]
}>()

const isSubmitting = ref(false)

const formData = reactive({
  name: '',
  description: '',
  status: 'placeholder' as Module['status'],
  version: '1.0.0'
})

const dependenciesText = ref('')

const errors = reactive({
  name: '',
  description: ''
})

// Computed dependencies array
const dependencies = computed(() => {
  if (!dependenciesText.value.trim()) return []
  return dependenciesText.value
    .split(',')
    .map(dep => dep.trim())
    .filter(dep => dep.length > 0)
})

// Reset form when dialog closes
watch(() => props.visible, (visible) => {
  if (!visible) {
    resetForm()
  }
})

const resetForm = () => {
  formData.name = ''
  formData.description = ''
  formData.status = 'placeholder'
  formData.version = '1.0.0'
  dependenciesText.value = ''
  errors.name = ''
  errors.description = ''
  isSubmitting.value = false
}

const validateForm = () => {
  errors.name = ''
  errors.description = ''
  
  if (!formData.name.trim()) {
    errors.name = 'Module name is required'
    return false
  }
  
  if (!/^[a-zA-Z][a-zA-Z0-9_]*$/.test(formData.name)) {
    errors.name = 'Module name must start with a letter and contain only letters, numbers, and underscores'
    return false
  }
  
  if (!formData.description.trim()) {
    errors.description = 'Description is required'
    return false
  }
  
  return true
}

const handleSubmit = async () => {
  if (!validateForm()) return
  
  isSubmitting.value = true
  
  try {
    const moduleData = {
      name: formData.name.trim(),
      description: formData.description.trim(),
      status: formData.status,
      version: formData.version || '1.0.0',
      dependencies: dependencies.value
    }
    
    emit('submit', moduleData)
  } catch (error) {
    console.error('Form submission error:', error)
  } finally {
    isSubmitting.value = false
  }
}

const closeDialog = () => {
  emit('close')
}
</script>

<style scoped>
.dialog-overlay {
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

.dialog {
  background: white;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px 0;
  border-bottom: 1px solid #eee;
  margin-bottom: 20px;
}

.dialog-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
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

.close-btn:hover {
  background-color: #f5f5f5;
  color: #333;
}

.dialog-content {
  padding: 0 24px 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #2c3e50;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.1);
}

.form-group input.error,
.form-group textarea.error {
  border-color: #e74c3c;
}

.error-text {
  color: #e74c3c;
  font-size: 12px;
  margin-top: 4px;
  display: block;
}

.help-text {
  color: #666;
  font-size: 12px;
  margin-top: 4px;
  display: block;
}

.dialog-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background: #f8f9fa;
  color: #666;
  border: 1px solid #ddd;
}

.btn-secondary:hover {
  background: #e9ecef;
}

.btn-primary {
  background: #4a90e2;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #357abd;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style> 