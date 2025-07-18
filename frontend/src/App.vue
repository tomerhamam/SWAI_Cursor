<template>
  <div id="app">
    <header class="app-header">
      <h1>Modular AI Architecture</h1>
      <div class="header-controls">
        <span class="status">{{ connectionStatus }}</span>
      </div>
    </header>
    
    <main class="app-main">
      <ModulePalette />
      
      <div class="graph-container">
        <GraphView />
      </div>
      
      <ModulePanel 
        v-if="selectedModule"
        :module="selectedModule"
        @close="clearSelection"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import GraphView from './components/GraphView.vue'
import ModulePanel from './components/ModulePanel.vue'
import ModulePalette from './components/ModulePalette.vue'
import { useModuleStore } from './stores/moduleStore'

const moduleStore = useModuleStore()

const selectedModule = computed(() => moduleStore.selectedModule)
const connectionStatus = computed(() => moduleStore.connectionStatus)

const clearSelection = () => {
  moduleStore.clearSelection()
}

// Initialize the store
moduleStore.loadModules()
</script>

<style scoped>
#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: #2c3e50;
  color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.app-header h1 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  background: #27ae60;
  color: white;
}

.app-main {
  flex: 1;
  display: flex;
  position: relative;
  overflow: hidden;
}

.graph-container {
  flex: 1;
  position: relative;
}
</style> 