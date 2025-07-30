<template>
  <div class="loading-container" :class="{ 'overlay': overlay }">
    <div class="loading-content">
      <div class="spinner-wrapper">
        <div class="spinner" :class="size">
          <div class="spinner-blade"></div>
          <div class="spinner-blade"></div>
          <div class="spinner-blade"></div>
          <div class="spinner-blade"></div>
          <div class="spinner-blade"></div>
          <div class="spinner-blade"></div>
          <div class="spinner-blade"></div>
          <div class="spinner-blade"></div>
        </div>
      </div>
      
      <div v-if="message" class="loading-message">
        <p class="primary-message">{{ message }}</p>
        <p v-if="submessage" class="sub-message">{{ submessage }}</p>
      </div>
      
      <div v-if="showProgress" class="progress-bar">
        <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  message?: string
  submessage?: string
  size?: 'small' | 'medium' | 'large'
  overlay?: boolean
  progress?: number
  showProgress?: boolean
}

withDefaults(defineProps<Props>(), {
  size: 'medium',
  overlay: false,
  progress: 0,
  showProgress: false
})
</script>

<style scoped>
.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.loading-container.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(2px);
  z-index: 100;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.loading-content {
  text-align: center;
  animation: slideUp 0.4s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.spinner-wrapper {
  display: inline-block;
  position: relative;
}

.spinner {
  position: relative;
  display: inline-block;
  animation: rotate 1.2s linear infinite;
}

.spinner.small {
  width: 24px;
  height: 24px;
}

.spinner.medium {
  width: 40px;
  height: 40px;
}

.spinner.large {
  width: 60px;
  height: 60px;
}

@keyframes rotate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.spinner-blade {
  position: absolute;
  width: 100%;
  height: 100%;
  opacity: 0;
  animation: fadeInOut 1.2s linear infinite;
}

.spinner-blade::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  width: 3px;
  height: 30%;
  background: linear-gradient(to bottom, #4a90e2, transparent);
  border-radius: 3px;
  transform: translateX(-50%);
}

.spinner.small .spinner-blade::before {
  width: 2px;
}

.spinner.large .spinner-blade::before {
  width: 4px;
}

.spinner-blade:nth-child(1) {
  transform: rotate(0deg);
  animation-delay: -1.05s;
}

.spinner-blade:nth-child(2) {
  transform: rotate(45deg);
  animation-delay: -0.9s;
}

.spinner-blade:nth-child(3) {
  transform: rotate(90deg);
  animation-delay: -0.75s;
}

.spinner-blade:nth-child(4) {
  transform: rotate(135deg);
  animation-delay: -0.6s;
}

.spinner-blade:nth-child(5) {
  transform: rotate(180deg);
  animation-delay: -0.45s;
}

.spinner-blade:nth-child(6) {
  transform: rotate(225deg);
  animation-delay: -0.3s;
}

.spinner-blade:nth-child(7) {
  transform: rotate(270deg);
  animation-delay: -0.15s;
}

.spinner-blade:nth-child(8) {
  transform: rotate(315deg);
  animation-delay: 0s;
}

@keyframes fadeInOut {
  0%, 100% {
    opacity: 0.2;
  }
  50% {
    opacity: 1;
  }
}

.loading-message {
  margin-top: 20px;
  animation: fadeIn 0.5s ease-out 0.2s both;
}

.primary-message {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.sub-message {
  margin: 4px 0 0;
  font-size: 14px;
  color: #666;
}

.progress-bar {
  margin-top: 16px;
  width: 200px;
  height: 4px;
  background: #e0e0e0;
  border-radius: 2px;
  overflow: hidden;
  animation: fadeIn 0.5s ease-out 0.3s both;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4a90e2, #5ca3f5);
  border-radius: 2px;
  transition: width 0.3s ease-out;
  position: relative;
  overflow: hidden;
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.3),
    transparent
  );
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .spinner.large {
    width: 48px;
    height: 48px;
  }
  
  .progress-bar {
    width: 160px;
  }
}
</style>