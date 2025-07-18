<template>
  <div v-if="hasError" class="error-boundary">
    <div class="error-content">
      <h2>Something went wrong</h2>
      <p>{{ errorMessage }}</p>
      <button @click="resetError" class="retry-button">
        Try Again
      </button>
      <details v-if="isDevelopment" class="error-details">
        <summary>Error Details</summary>
        <pre>{{ errorStack }}</pre>
      </details>
    </div>
  </div>
  <slot v-else />
</template>

<script setup lang="ts">
import { ref, onErrorCaptured, computed } from 'vue'

const hasError = ref(false)
const errorMessage = ref('')
const errorStack = ref('')

const isDevelopment = computed(() => import.meta.env.DEV)

const resetError = () => {
  hasError.value = false
  errorMessage.value = ''
  errorStack.value = ''
  // Emit event to parent to handle reset if needed
  emit('reset')
}

const emit = defineEmits<{
  error: [error: Error]
  reset: []
}>()

onErrorCaptured((error: Error) => {
  hasError.value = true
  errorMessage.value = error.message || 'An unexpected error occurred'
  errorStack.value = error.stack || ''
  
  // Log error in development
  if (isDevelopment.value) {
    console.error('Error caught by boundary:', error)
  }
  
  // Emit error event for parent component handling
  emit('error', error)
  
  // Prevent error from propagating further
  return false
})

// Expose reset method for parent components
defineExpose({
  resetError
})
</script>

<style scoped>
.error-boundary {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  padding: 2rem;
  background-color: #f8f9fa;
}

.error-content {
  max-width: 600px;
  text-align: center;
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.error-content h2 {
  color: #e74c3c;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.error-content p {
  color: #666;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.retry-button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.retry-button:hover {
  background-color: #2980b9;
}

.retry-button:focus {
  outline: 2px solid #3498db;
  outline-offset: 2px;
}

.error-details {
  margin-top: 2rem;
  text-align: left;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 1rem;
  background-color: #f5f5f5;
}

.error-details summary {
  cursor: pointer;
  font-weight: 600;
  color: #666;
  margin-bottom: 0.5rem;
}

.error-details pre {
  margin: 0;
  padding: 1rem;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 0.875rem;
  line-height: 1.4;
  color: #e74c3c;
}
</style>