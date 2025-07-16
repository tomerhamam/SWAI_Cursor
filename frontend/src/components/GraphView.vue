<template>
  <div class="graph-container">
    <!-- Status Filter -->
    <div class="filter-bar">
      <StatusFilter 
        :modules="moduleStore.modules"
        @filter-change="handleFilterChange"
      />
    </div>
    
    <!-- Graph View -->
    <div ref="graphContainer" class="graph-view" @contextmenu.prevent />
    
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>Loading modules...</p>
    </div>
    <div v-if="error" class="error-overlay">
      <p>{{ error }}</p>
      <button @click="retryLoad">Retry</button>
    </div>
    
    <!-- Context Menu -->
    <ContextMenu
      :visible="contextMenu.visible"
      :position="contextMenu.position"
      :context-type="contextMenu.type"
      :node-id="contextMenu.nodeId"
      @menu-action="handleContextMenuAction"
      @close="closeContextMenu"
    />
    
    <!-- Module Creation Dialog -->
    <ModuleCreationDialog
      :visible="showCreateDialog"
      @close="closeCreateDialog"
      @submit="handleCreateModule"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed, reactive } from 'vue'
import { Network } from 'vis-network/standalone/esm/vis-network'
import type { Data, Options, Node, Edge } from 'vis-network/standalone/esm/vis-network'
import { useModuleStore } from '../stores/moduleStore'
import type { Module } from '../stores/moduleStore'
import ContextMenu from './ContextMenu.vue'
import ModuleCreationDialog from './ModuleCreationDialog.vue'
import StatusFilter from './StatusFilter.vue'

const moduleStore = useModuleStore()
const graphContainer = ref<HTMLElement>()
let network: Network | null = null

const isLoading = computed(() => moduleStore.isLoading)
const error = computed(() => moduleStore.error)

// Context menu state
const contextMenu = reactive({
  visible: false,
  position: { x: 0, y: 0 },
  type: 'empty' as 'empty' | 'node',
  nodeId: undefined as string | undefined
})

// Dialog state
const showCreateDialog = ref(false)

// Filter state
const statusFilter = ref<Set<Module['status']>>(new Set())

// Convert modules to vis.js nodes
const createNodes = (modules: Record<string, Module>): Node[] => {
  return Object.entries(modules)
    .filter(([id, module]) => {
      // Apply status filter
      if (statusFilter.value.size === 0) return true
      return statusFilter.value.has(module.status)
    })
    .map(([id, module]) => ({
    id,
    label: module.name,
    title: `${module.name}\n${module.description}\nStatus: ${module.status}`,
    color: getNodeColor(module.status),
    font: {
      color: '#333',
      size: 14,
      face: 'Arial'
    },
    borderWidth: 2,
    borderWidthSelected: 3,
    shape: 'box',
    margin: 10,
    chosen: {
      node: (values: any) => {
        values.borderWidth = 4
        values.color = '#4a90e2'
      }
    }
  }))
}

// Convert dependencies to vis.js edges
const createEdges = (modules: Record<string, Module>): Edge[] => {
  const edges: Edge[] = []
  
  Object.entries(modules).forEach(([id, module]) => {
    if (module.dependencies) {
      module.dependencies.forEach(dep => {
        if (modules[dep]) {
          edges.push({
            from: dep,
            to: id,
            arrows: 'to',
            color: '#666',
            width: 2,
            smooth: {
              type: 'cubicBezier',
              forceDirection: 'horizontal',
              roundness: 0.4
            }
          })
        }
      })
    }
  })
  
  return edges
}

const getNodeColor = (status: Module['status']): string => {
  switch (status) {
    case 'implemented':
      return '#27ae60' // Green
    case 'placeholder':
      return '#f39c12' // Orange
    case 'error':
      return '#e74c3c' // Red
    default:
      return '#95a5a6' // Gray
  }
}

const initializeNetwork = () => {
  if (!graphContainer.value) return

  const modules = moduleStore.modules
  const nodes = createNodes(modules)
  const edges = createEdges(modules)

  const data: Data = { nodes, edges }
  
  const options: Options = {
    layout: {
      hierarchical: {
        enabled: true,
        direction: 'LR',
        sortMethod: 'directed',
        levelSeparation: 150,
        nodeSpacing: 100,
        treeSpacing: 200
      }
    },
    physics: {
      enabled: false
    },
    interaction: {
      dragNodes: true,
      dragView: true,
      zoomView: true,
      selectConnectedEdges: false
    },
    nodes: {
      borderWidth: 2,
      borderWidthSelected: 3,
      color: {
        border: '#2c3e50',
        background: '#ecf0f1',
        highlight: {
          border: '#4a90e2',
          background: '#e8f4fd'
        }
      },
      font: {
        size: 14,
        color: '#2c3e50'
      },
      shape: 'box',
      margin: 10
    },
    edges: {
      color: '#7f8c8d',
      width: 2,
      arrows: {
        to: {
          enabled: true,
          scaleFactor: 1
        }
      },
      smooth: {
        enabled: true,
        type: 'cubicBezier',
        roundness: 0.4
      }
    }
  }

  network = new Network(graphContainer.value, data, options)

  // Handle node selection
  network.on('click', (params) => {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0] as string
      moduleStore.selectModule(nodeId)
    } else {
      moduleStore.clearSelection()
    }
  })

  // Handle double click for future expansion
  network.on('doubleClick', (params) => {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0] as string
      console.log('Double clicked node:', nodeId)
      // Future: Expand/collapse or edit functionality
    }
  })

  // Handle right-click context menu
  network.on('oncontext', (params) => {
    // Get the canvas position
    const canvasPosition = network.canvasToDOM(params.pointer.canvas)
    
    contextMenu.position = {
      x: canvasPosition.x,
      y: canvasPosition.y
    }
    
    if (params.nodes.length > 0) {
      // Right-clicked on a node
      contextMenu.type = 'node'
      contextMenu.nodeId = params.nodes[0] as string
    } else {
      // Right-clicked on empty space
      contextMenu.type = 'empty'
      contextMenu.nodeId = undefined
    }
    
    contextMenu.visible = true
  })

  // Close context menu on any other click
  network.on('click', () => {
    closeContextMenu()
  })

  // Fit network to viewport
  setTimeout(() => {
    network?.fit()
  }, 100)
}

const updateNetwork = () => {
  if (!network) return

  const modules = moduleStore.modules
  const nodes = createNodes(modules)
  const edges = createEdges(modules)

  network.setData({ nodes, edges })
  
  // Maintain current view position
  const currentSelection = moduleStore.selectedModuleId
  if (currentSelection) {
    network.selectNodes([currentSelection])
  }
}

const retryLoad = () => {
  moduleStore.clearError()
  moduleStore.loadModules()
}

// Context menu handlers
const closeContextMenu = () => {
  contextMenu.visible = false
}

const handleContextMenuAction = async (action: string, nodeId?: string) => {
  switch (action) {
    case 'add-module':
      showCreateDialog.value = true
      break
    case 'edit-module':
      if (nodeId) {
        moduleStore.selectModule(nodeId)
      }
      break
    case 'delete-module':
      if (nodeId && confirm(`Delete module "${nodeId}"?`)) {
        try {
          await moduleStore.deleteModule(nodeId)
        } catch (error) {
          console.error('Failed to delete module:', error)
        }
      }
      break
    case 'view-details':
      if (nodeId) {
        moduleStore.selectModule(nodeId)
      }
      break
    default:
      console.log('Unhandled action:', action)
  }
}

// Dialog handlers
const closeCreateDialog = () => {
  showCreateDialog.value = false
}

const handleCreateModule = async (moduleData: Omit<Module, 'name'> & { name: string }) => {
  try {
    await moduleStore.createModule(moduleData)
    showCreateDialog.value = false
  } catch (error) {
    console.error('Failed to create module:', error)
  }
}

// Filter handlers
const handleFilterChange = (statuses: Set<Module['status']>) => {
  statusFilter.value = statuses
}

// Watch for module changes
watch(() => moduleStore.modules, updateNetwork, { deep: true })

// Watch for selection changes
watch(() => moduleStore.selectedModuleId, (selectedId) => {
  if (network && selectedId) {
    network.selectNodes([selectedId])
    network.focus(selectedId, {
      scale: 1.0,
      animation: {
        duration: 500,
        easingFunction: 'easeInOutQuad'
      }
    })
  } else if (network) {
    network.unselectAll()
  }
})

onMounted(() => {
  initializeNetwork()
})

onUnmounted(() => {
  if (network) {
    network.destroy()
    network = null
  }
})
</script>

<style scoped>
.graph-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.filter-bar {
  background: white;
  border-bottom: 1px solid #e0e0e0;
  padding: 12px 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.graph-view {
  flex: 1;
  width: 100%;
  position: relative;
  background: #f8f9fa;
}

.loading-overlay,
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: rgba(255, 255, 255, 0.9);
  z-index: 10;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-overlay p {
  color: #e74c3c;
  margin-bottom: 1rem;
  text-align: center;
}

.error-overlay button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  background: #3498db;
  color: white;
  cursor: pointer;
  font-size: 14px;
}

.error-overlay button:hover {
  background: #2980b9;
}
</style> 