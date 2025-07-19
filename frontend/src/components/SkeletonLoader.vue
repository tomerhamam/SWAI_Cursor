<template>
  <div class="skeleton-container">
    <div 
      v-for="i in rows" 
      :key="i" 
      class="skeleton-row"
      :style="{ animationDelay: `${i * 0.05}s` }"
    >
      <!-- Avatar skeleton -->
      <div v-if="showAvatar" class="skeleton-avatar skeleton-pulse"></div>
      
      <!-- Content skeleton -->
      <div class="skeleton-content">
        <div 
          v-if="showTitle" 
          class="skeleton-title skeleton-pulse"
          :style="{ width: `${60 + Math.random() * 30}%` }"
        ></div>
        
        <div v-if="showText" class="skeleton-text-group">
          <div 
            class="skeleton-text skeleton-pulse"
            :style="{ width: `${70 + Math.random() * 30}%` }"
          ></div>
          <div 
            class="skeleton-text skeleton-pulse"
            :style="{ width: `${60 + Math.random() * 20}%` }"
          ></div>
        </div>
        
        <div v-if="showActions" class="skeleton-actions">
          <div class="skeleton-button skeleton-pulse"></div>
          <div class="skeleton-button skeleton-pulse"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  rows?: number
  showAvatar?: boolean
  showTitle?: boolean
  showText?: boolean
  showActions?: boolean
}

withDefaults(defineProps<Props>(), {
  rows: 3,
  showAvatar: false,
  showTitle: true,
  showText: true,
  showActions: false
})
</script>

<style scoped>
.skeleton-container {
  padding: 16px 0;
}

.skeleton-row {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  animation: fadeIn 0.6s ease-out both;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.skeleton-avatar {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #e0e0e0;
}

.skeleton-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-title {
  height: 20px;
  background: #e0e0e0;
  border-radius: 4px;
}

.skeleton-text-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-text {
  height: 14px;
  background: #e0e0e0;
  border-radius: 4px;
}

.skeleton-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.skeleton-button {
  width: 80px;
  height: 32px;
  background: #e0e0e0;
  border-radius: 6px;
}

/* Pulse animation for all skeleton elements */
.skeleton-pulse {
  position: relative;
  overflow: hidden;
}

.skeleton-pulse::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.4),
    transparent
  );
  animation: skeleton-shimmer 1.5s infinite;
}

@keyframes skeleton-shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .skeleton-avatar {
    width: 40px;
    height: 40px;
  }
  
  .skeleton-row {
    gap: 12px;
  }
}
</style>