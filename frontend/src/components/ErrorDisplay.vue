<template>
  <transition name="error" @enter="onEnter" @leave="onLeave">
    <div v-if="error" class="error-container" :class="variant">
      <div class="error-content">
        <div class="error-icon-wrapper">
          <div class="error-icon" :class="{ 'shake': shake }">
            {{ getIcon() }}
          </div>
        </div>
        
        <div class="error-details">
          <h3 class="error-title">{{ title || getDefaultTitle() }}</h3>
          <p class="error-message">{{ error }}</p>
          
          <div v-if="showActions" class="error-actions">
            <button 
              v-if="onRetry" 
              @click="handleRetry" 
              class="error-button retry"
              :disabled="isRetrying"
            >
              {{ isRetrying ? 'Retrying...' : 'Try Again' }}
            </button>
            <button 
              v-if="onDismiss" 
              @click="onDismiss" 
              class="error-button dismiss"
            >
              Dismiss
            </button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  error: string | null
  title?: string
  variant?: 'inline' | 'overlay' | 'toast'
  showActions?: boolean
  onRetry?: () => Promise<void> | void
  onDismiss?: () => void
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'inline',
  showActions: true
})

const shake = ref(false)
const isRetrying = ref(false)

const getIcon = () => {
  switch (props.variant) {
    case 'toast':
      return '⚠️'
    case 'overlay':
      return '❌'
    default:
      return '⚠️'
  }
}

const getDefaultTitle = () => {
  switch (props.variant) {
    case 'toast':
      return 'Warning'
    case 'overlay':
      return 'Error Occurred'
    default:
      return 'Something went wrong'
  }
}

const handleRetry = async () => {
  if (!props.onRetry || isRetrying.value) return
  
  isRetrying.value = true
  try {
    await props.onRetry()
  } finally {
    isRetrying.value = false
  }
}

const onEnter = (el: Element) => {
  shake.value = true
  setTimeout(() => {
    shake.value = false
  }, 500)
}

const onLeave = () => {
  shake.value = false
}

// Trigger shake animation when error changes
watch(() => props.error, (newError, oldError) => {
  if (newError && newError !== oldError) {
    shake.value = true
    setTimeout(() => {
      shake.value = false
    }, 500)
  }
})
</script>

<style scoped>
.error-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.error-container.inline {
  background: #ffebee;
  border-radius: 8px;
  border: 1px solid #ffcdd2;
}

.error-container.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(4px);
  z-index: 100;
}

.error-container.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  max-width: 400px;
  z-index: 1000;
}

.error-content {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  text-align: left;
}

.error-icon-wrapper {
  flex-shrink: 0;
}

.error-icon {
  font-size: 32px;
  line-height: 1;
  animation: fadeIn 0.3s ease-out;
}

.error-icon.shake {
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.error-details {
  flex: 1;
}

.error-title {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #d32f2f;
}

.error-message {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.error-actions {
  display: flex;
  gap: 8px;
}

.error-button {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.error-button.retry {
  background: #f44336;
  color: white;
}

.error-button.retry:hover:not(:disabled) {
  background: #d32f2f;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(244, 67, 54, 0.3);
}

.error-button.retry:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-button.dismiss {
  background: #f5f5f5;
  color: #666;
}

.error-button.dismiss:hover {
  background: #e0e0e0;
}

/* Transition animations */
.error-enter-active,
.error-leave-active {
  transition: all 0.3s ease;
}

.error-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.error-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* Toast specific animations */
.error-container.toast.error-enter-from {
  transform: translateX(100%);
}

.error-container.toast.error-leave-to {
  transform: translateX(100%);
}

/* Responsive design */
@media (max-width: 768px) {
  .error-container.toast {
    left: 20px;
    right: 20px;
    max-width: none;
  }
}
</style>