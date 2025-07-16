<template>
  <div class="module-palette">
    <h3 class="palette-title">Module Palette</h3>
    <div class="palette-items">
      <div
        v-for="template in moduleTemplates"
        :key="template.id"
        class="palette-item"
        :class="{ dragging: dragState.isDragging && dragState.templateId === template.id }"
        draggable="true"
        @dragstart="handleDragStart($event, template)"
        @dragend="handleDragEnd"
      >
        <div class="item-icon" :style="{ background: template.color }">
          {{ template.icon }}
        </div>
        <div class="item-label">{{ template.name }}</div>
        <div class="item-description">{{ template.description }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

interface ModuleTemplate {
  id: string
  name: string
  description: string
  icon: string
  color: string
  defaultData: {
    status: 'implemented' | 'placeholder' | 'error'
    version: string
  }
}

const emit = defineEmits<{
  moduleDrop: [template: ModuleTemplate, position: { x: number; y: number }]
}>()

const dragState = reactive({
  isDragging: false,
  templateId: null as string | null
})

const moduleTemplates: ModuleTemplate[] = [
  {
    id: 'service',
    name: 'Service Module',
    description: 'Business logic service',
    icon: '⚙️',
    color: '#3498db',
    defaultData: { status: 'placeholder', version: '1.0.0' }
  },
  {
    id: 'data-processor',
    name: 'Data Processor',
    description: 'Data transformation module',
    icon: '📊',
    color: '#9b59b6',
    defaultData: { status: 'placeholder', version: '1.0.0' }
  },
  {
    id: 'api-gateway',
    name: 'API Gateway',
    description: 'External interface module',
    icon: '🌐',
    color: '#e67e22',
    defaultData: { status: 'placeholder', version: '1.0.0' }
  },
  {
    id: 'database',
    name: 'Database Module',
    description: 'Data storage interface',
    icon: '🗄️',
    color: '#27ae60',
    defaultData: { status: 'placeholder', version: '1.0.0' }
  },
  {
    id: 'ui-component',
    name: 'UI Component',
    description: 'User interface module',
    icon: '🎨',
    color: '#f39c12',
    defaultData: { status: 'placeholder', version: '1.0.0' }
  },
  {
    id: 'utility',
    name: 'Utility Module',
    description: 'Helper functions and tools',
    icon: '🔧',
    color: '#95a5a6',
    defaultData: { status: 'placeholder', version: '1.0.0' }
  }
]

const handleDragStart = (event: DragEvent, template: ModuleTemplate) => {
  dragState.isDragging = true
  dragState.templateId = template.id
  
  // Store template data in the drag event
  if (event.dataTransfer) {
    event.dataTransfer.setData('application/json', JSON.stringify(template))
    event.dataTransfer.effectAllowed = 'copy'
    
    // Create a custom drag image
    const dragElement = event.target as HTMLElement
    const rect = dragElement.getBoundingClientRect()
    event.dataTransfer.setDragImage(dragElement, rect.width / 2, rect.height / 2)
  }
}

const handleDragEnd = () => {
  dragState.isDragging = false
  dragState.templateId = null
}
</script>

<style scoped>
.module-palette {
  width: 250px;
  background: white;
  border-right: 1px solid #e0e0e0;
  padding: 16px;
  overflow-y: auto;
  max-height: 100%;
}

.palette-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 1px solid #ecf0f1;
  padding-bottom: 8px;
}

.palette-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.palette-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fafafa;
  cursor: grab;
  transition: all 0.2s;
  user-select: none;
}

.palette-item:hover {
  background: #f0f8ff;
  border-color: #4a90e2;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.palette-item:active,
.palette-item.dragging {
  cursor: grabbing;
  transform: rotate(2deg);
  opacity: 0.8;
}

.item-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: white;
  flex-shrink: 0;
}

.item-label {
  font-weight: 500;
  color: #2c3e50;
  font-size: 14px;
  line-height: 1.2;
}

.item-description {
  font-size: 12px;
  color: #666;
  line-height: 1.3;
}

/* Responsive design */
@media (max-width: 768px) {
  .module-palette {
    width: 200px;
    padding: 12px;
  }
  
  .palette-item {
    flex-direction: column;
    text-align: center;
    padding: 8px;
  }
  
  .item-icon {
    width: 28px;
    height: 28px;
    font-size: 14px;
  }
}
</style> 