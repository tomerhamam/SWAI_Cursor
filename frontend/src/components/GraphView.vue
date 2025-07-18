<template>
  <div class="graph-container">
    <!-- Search and Filter Bar -->
    <div class="filter-bar">
      <div class="search-section">
        <GlobalSearch 
          @search-change="handleSearchChange"
        />
      </div>
      <div class="filter-section">
        <StatusFilter 
          :modules="moduleStore.modules"
          @filter-change="handleStatusFilterChange"
        />
        <button 
          @click="toggleMultiSelect"
          :class="['multi-select-btn', { active: moduleStore.isMultiSelectMode }]"
          :title="moduleStore.isMultiSelectMode ? 'Exit multi-select mode' : 'Enable multi-select mode'"
        >
          {{ moduleStore.isMultiSelectMode ? '✓ Multi-Select' : '☐ Multi-Select' }}
        </button>
        
        <button 
          @click="cycleLayout"
          :class="['layout-toggle-btn', `layout-${layoutMode}`]"
          :title="getLayoutTooltip()"
        >
          {{ getLayoutLabel() }}
        </button>
        <div v-if="moduleStore.hasActiveFilters" class="filter-summary">
          <span class="results-summary">
            {{ moduleStore.searchResultsCount }} of {{ moduleStore.moduleCount }} modules
          </span>
          <button 
            @click="clearAllFilters" 
            class="clear-filters-btn"
            title="Clear all filters"
          >
            Clear All
          </button>
        </div>
      </div>
    </div>
    
    <!-- Graph View -->
    <div 
      ref="graphContainer" 
      class="graph-view" 
      :class="{ 'drop-active': dropZone.isActive, 'dependency-mode': dependencyMode.isActive }"
      :data-layout-mode="`${layoutMode} layout`"
      role="application"
      aria-label="Module dependency graph visualization"
      aria-describedby="graph-instructions"
      tabindex="0"
      @contextmenu.prevent 
      @dragover.prevent="handleDragOver"
      @drop.prevent="handleDrop"
      @dragleave="handleDragLeave"
      @keydown="handleKeyDown"
    />
    
    <!-- Screen reader instructions -->
    <div id="graph-instructions" class="sr-only">
      Interactive graph showing module dependencies in {{ layoutMode }} layout mode. 
      {{ layoutMode === 'manual' ? 'Nodes can be precisely positioned without physics.' : 
         layoutMode === 'physics' ? 'Nodes use dynamic physics-based positioning.' : 
         'Nodes are arranged in a hierarchical structure.' }}
      Use arrow keys to navigate between modules. Press Enter to select a module, Space to open context menu, or Tab to navigate to controls.
    </div>
    
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
    
    <!-- Bulk Operations Panel -->
    <BulkOperationsPanel
      :show="moduleStore.isMultiSelectMode"
      @duplicate-module="handleDuplicateModule"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed, reactive, nextTick } from 'vue'
import { Network } from 'vis-network/standalone/esm/vis-network'
import type { Data, Options, Node, Edge } from 'vis-network/standalone/esm/vis-network'
import { useModuleStore } from '../stores/moduleStore'
import type { Module } from '../stores/moduleStore'
import ContextMenu from './ContextMenu.vue'
import ModuleCreationDialog from './ModuleCreationDialog.vue'
import StatusFilter from './StatusFilter.vue'
import GlobalSearch from './GlobalSearch.vue'
import BulkOperationsPanel from './BulkOperationsPanel.vue'

// Type definitions for vis.js
interface VisNodeChosenValues {
  borderWidth: number
  color: string
}

interface PreviewLine {
  id: string
  from: string
  to: { x: number; y: number }
  color: { color: string }
  dashes: boolean
}

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

// Layout state
const layoutMode = ref<'manual' | 'physics' | 'hierarchical'>('physics')  // Start with physics layout

// Filter state is now managed in the store

// Drag & drop state
const dropZone = reactive({
  isActive: false,
  position: { x: 0, y: 0 }
})

// Dependency creation state
const dependencyMode = reactive({
  isActive: false,
  sourceNodeId: null as string | null,
  previewLine: null as PreviewLine | null
})

// Convert modules to vis.js nodes
const createNodes = (modules: Record<string, Module>): Node[] => {
  const searchTerm = moduleStore.searchQuery.toLowerCase()
  
  return Object.entries(modules)
    .map(([id, module]) => {
      // Check if this module matches the search query
      const isSearchMatch = searchTerm && (
        module.name.toLowerCase().includes(searchTerm) ||
        module.description.toLowerCase().includes(searchTerm) ||
        module.dependencies?.some(dep => dep.toLowerCase().includes(searchTerm))
      )
      
      // Check if this module is selected in multi-select mode
      const isSelected = moduleStore.isModuleSelected(id)
      
      // Create label with selection indicator in multi-select mode
      const label = moduleStore.isMultiSelectMode && isSelected 
        ? `✓ ${module.name}` 
        : module.name
      
      return {
        id,
        label,
        title: `${module.name}\n${module.description}\nStatus: ${module.status}${moduleStore.isMultiSelectMode && isSelected ? '\n✓ Selected' : ''}`,
        color: getNodeColor(module.status, isSearchMatch, isSelected),
        font: {
          color: isSelected ? '#1976d2' : (isSearchMatch ? '#2c3e50' : '#333'),
          size: isSearchMatch ? 16 : 14,
          face: 'Arial',
          bold: isSearchMatch || isSelected
        },
        borderWidth: isSelected ? 4 : (isSearchMatch ? 3 : 2),
        borderWidthSelected: 4,
        shape: 'box',
        margin: { top: 10, right: 10, bottom: 10, left: 10 },
        shadow: (isSearchMatch || isSelected) ? {
          enabled: true,
          color: isSelected ? '#1976d2' : '#4a90e2',
          size: isSelected ? 10 : 8,
          x: 0,
          y: 0
        } : false,
        chosen: {
          node: (values: VisNodeChosenValues) => {
            values.borderWidth = 4
            values.color = isSelected ? '#1976d2' : '#4a90e2'
          },
          label: false
        }
      }
    })
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
              enabled: true,
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

const getNodeColor = (status: Module['status'], isHighlighted: boolean = false, isSelected: boolean = false): string => {
  if (isSelected) {
    // Return selected state colors with blue accent
    switch (status) {
      case 'implemented':
        return { background: '#2196f3', border: '#1976d2', highlight: { background: '#42a5f5', border: '#1565c0' } }
      case 'placeholder':
        return { background: '#2196f3', border: '#1976d2', highlight: { background: '#42a5f5', border: '#1565c0' } }
      case 'error':
        return { background: '#2196f3', border: '#1976d2', highlight: { background: '#42a5f5', border: '#1565c0' } }
      default:
        return { background: '#2196f3', border: '#1976d2', highlight: { background: '#42a5f5', border: '#1565c0' } }
    }
  }
  
  if (isHighlighted) {
    // Return highlighted versions of the colors
    switch (status) {
      case 'implemented':
        return { background: '#2ecc71', border: '#27ae60', highlight: { background: '#58d68d', border: '#1e8449' } }
      case 'placeholder':
        return { background: '#f1c40f', border: '#f39c12', highlight: { background: '#f7dc6f', border: '#d68910' } }
      case 'error':
        return { background: '#e74c3c', border: '#c0392b', highlight: { background: '#ec7063', border: '#a93226' } }
      default:
        return { background: '#bdc3c7', border: '#95a5a6', highlight: { background: '#d5dbdb', border: '#7f8c8d' } }
    }
  }
  
  // Return normal colors
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
  if (!graphContainer.value) {
    moduleStore.setError('Graph container not found')
    return
  }

  // Ensure container has dimensions
  const containerRect = graphContainer.value.getBoundingClientRect()
  
  if (containerRect.width === 0 || containerRect.height === 0) {
    // Retry initialization if container has no dimensions yet
    setTimeout(initializeNetwork, 100)
    return
  }

  const modules = moduleStore.filteredModulesMap
  const nodes = createNodes(modules)
  const edges = createEdges(modules)

  const data: Data = { nodes, edges }
  
  const options: Options = {
    layout: {
      hierarchical: {
        enabled: layoutMode.value === 'hierarchical',
        direction: 'LR',
        sortMethod: 'directed',
        levelSeparation: 150,
        nodeSpacing: 100,
        treeSpacing: 200
      }
    },
    physics: {
      enabled: layoutMode.value === 'physics',
      stabilization: {
        enabled: true,
        iterations: layoutMode.value === 'hierarchical' ? 200 : (layoutMode.value === 'physics' ? 100 : 0),
        updateInterval: 25
      },
      solver: 'forceAtlas2Based',
      forceAtlas2Based: {
        gravitationalConstant: -50,
        centralGravity: 0.01,
        springLength: 200,
        springConstant: 0.08,
        damping: 0.4
      }
    },
    interaction: {
      dragNodes: true,
      dragView: true,
      zoomView: true,
      selectConnectedEdges: false,
      multiselect: false,
      tooltipDelay: 300
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
      margin: { top: 10, right: 10, bottom: 10, left: 10 }
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

  try {
    network = new Network(graphContainer.value, data, options)

    // Handle node selection
    network.on('click', (params) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0] as string
        
        // Handle dependency creation mode
        if (dependencyMode.isActive) {
          handleNodeClickForDependency(nodeId)
        } else if (moduleStore.isMultiSelectMode) {
          // Multi-select mode: toggle selection
          moduleStore.toggleModuleSelection(nodeId)
        } else {
          // Single select mode
          moduleStore.selectModule(nodeId)
        }
      } else {
        // Clicking empty space
        if (!moduleStore.isMultiSelectMode) {
          moduleStore.clearSelection()
        }
        // Exit dependency mode if clicking empty space
        if (dependencyMode.isActive) {
          dependencyMode.isActive = false
          dependencyMode.sourceNodeId = null
        }
      }
    })

    // Handle double click for future expansion
    network.on('doubleClick', (params) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0] as string
        // Future: Expand/collapse or edit functionality
      }
    })

    // Handle right-click context menu
    network.on('oncontext', (params) => {
      if (!network) return
      
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

    // Network stabilized event
    network.on('stabilized', () => {
      // Network has finished stabilizing
    })

    // Fit network to viewport with delay to ensure proper rendering
    setTimeout(() => {
      if (network) {
        network.fit({
          animation: {
            duration: 500,
            easingFunction: 'easeInOutQuad'
          }
        })
      }
    }, 100)

  } catch (error) {
    moduleStore.setError('Failed to initialize network visualization')
  }
}

const updateNetwork = () => {
  if (!network) return

  const modules = moduleStore.filteredModulesMap
  const nodes = createNodes(modules)
  const edges = createEdges(modules)

  network.setData({ nodes, edges })
  
      // Maintain current view position
    const currentSelection = moduleStore.selectedModuleId
    if (currentSelection && network) {
      network.selectNodes([currentSelection])
    }
}

const retryLoad = () => {
  moduleStore.clearError()
  moduleStore.loadModules()
}

// Keyboard navigation for accessibility
const handleKeyDown = (event: KeyboardEvent) => {
  if (!network) return

  const selectedNodes = network.getSelectedNodes()
  const allNodes = Object.keys(moduleStore.filteredModulesMap)
  
  switch (event.key) {
    case 'Enter':
      event.preventDefault()
      if (selectedNodes.length > 0) {
        moduleStore.selectModule(String(selectedNodes[0]))
      }
      break
    case ' ': // Space bar
      event.preventDefault()
      if (selectedNodes.length > 0) {
        const nodeId = String(selectedNodes[0])
        const nodePosition = network.getPositions([nodeId])[nodeId]
        if (nodePosition) {
          const canvasPosition = network.canvasToDOM(nodePosition)
          contextMenu.visible = true
          contextMenu.position = { x: canvasPosition.x, y: canvasPosition.y }
          contextMenu.type = 'node'
          contextMenu.nodeId = nodeId
        }
      }
      break
    case 'ArrowUp':
    case 'ArrowDown':
    case 'ArrowLeft':
    case 'ArrowRight':
      event.preventDefault()
      navigateWithKeyboard(event.key, selectedNodes.map(String), allNodes)
      break
    case 'Escape':
      event.preventDefault()
      if (network) {
        network.unselectAll()
      }
      closeContextMenu()
      break
  }
}

const navigateWithKeyboard = (key: string, selectedNodes: string[], allNodes: string[]) => {
  if (!network || allNodes.length === 0) return

  let targetNodeId: string
  
  if (selectedNodes.length === 0) {
    // No selection, select first node
    targetNodeId = allNodes[0]
  } else {
    // Navigate based on position relative to current selection
    const currentNodeId = selectedNodes[0]
    const currentIndex = allNodes.indexOf(currentNodeId)
    
    switch (key) {
      case 'ArrowUp':
      case 'ArrowLeft':
        targetNodeId = allNodes[(currentIndex - 1 + allNodes.length) % allNodes.length]
        break
      case 'ArrowDown':
      case 'ArrowRight':
        targetNodeId = allNodes[(currentIndex + 1) % allNodes.length]
        break
      default:
        return
    }
  }
  
  network.selectNodes([targetNodeId])
  network.focus(targetNodeId, {
    scale: 1.0,
    animation: {
      duration: 300,
      easingFunction: 'easeInOutQuad'
    }
  })
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
    case 'toggle-dependency-mode':
      toggleDependencyMode()
      break
    case 'start-dependency':
      if (nodeId) {
        dependencyMode.isActive = true
        dependencyMode.sourceNodeId = nodeId
      }
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
          moduleStore.setError('Failed to delete module')
        }
      }
      break
    case 'view-details':
      if (nodeId) {
        moduleStore.selectModule(nodeId)
      }
      break
    default:
      // Unhandled action
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
    moduleStore.setError('Failed to create module')
  }
}

// Search and filter handlers
const handleSearchChange = (data: { query: string, filters: any[] }) => {
  moduleStore.updateSearch(data)
}

const handleStatusFilterChange = (statuses: Set<Module['status']>) => {
  moduleStore.setStatusFilters(statuses)
}

const clearAllFilters = () => {
  moduleStore.clearAllFilters()
}

// Multi-select handlers
const toggleMultiSelect = () => {
  moduleStore.toggleMultiSelectMode()
}

const handleDuplicateModule = async (moduleData: Omit<Module, 'name'> & { name: string }) => {
  try {
    await moduleStore.createModule(moduleData)
  } catch (error) {
    console.error('Failed to duplicate module:', error)
  }
}

// Layout control handlers
const cycleLayout = () => {
  switch (layoutMode.value) {
    case 'manual':
      layoutMode.value = 'physics'
      break
    case 'physics':
      layoutMode.value = 'hierarchical'
      break
    case 'hierarchical':
      layoutMode.value = 'manual'
      break
  }
  
  // Reinitialize the network with new layout
  if (network) {
    initializeNetwork()
  }
}

const getLayoutLabel = () => {
  switch (layoutMode.value) {
    case 'manual':
      return '🎯 Manual'
    case 'physics':
      return '🌊 Physics'
    case 'hierarchical':
      return '📊 Hierarchical'
  }
}

const getLayoutTooltip = () => {
  switch (layoutMode.value) {
    case 'manual':
      return 'Switch to physics layout (dynamic positioning)'
    case 'physics':
      return 'Switch to hierarchical layout (structured positioning)'
    case 'hierarchical':
      return 'Switch to manual layout (precise positioning)'
  }
}

// Drag & drop handlers
const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
  dropZone.isActive = true
  
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'copy'
  }
}

const handleDragLeave = (event: DragEvent) => {
  // Only deactivate if leaving the graph container entirely
  const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
  if (
    event.clientX < rect.left || 
    event.clientX > rect.right || 
    event.clientY < rect.top || 
    event.clientY > rect.bottom
  ) {
    dropZone.isActive = false
  }
}

const handleDrop = async (event: DragEvent) => {
  event.preventDefault()
  dropZone.isActive = false
  
  if (!event.dataTransfer) return
  
  try {
    const templateData = JSON.parse(event.dataTransfer.getData('application/json'))
    
    // Generate a unique module name based on the template
    const timestamp = Date.now().toString().slice(-4)
    const moduleName = `${templateData.name.replace(/\s+/g, '')}${timestamp}`
    
    // Create module with template data
    const moduleData = {
      name: moduleName,
      description: templateData.description,
      status: templateData.defaultData.status,
      version: templateData.defaultData.version,
      dependencies: []
    }
    
    await moduleStore.createModule(moduleData)
    
    // If we have a network instance, try to position the new node
    if (network) {
      // Convert DOM coordinates to canvas coordinates
      const canvasPosition = network.DOMtoCanvas({
        x: event.offsetX,
        y: event.offsetY
      })
      
      // Position the node (this would require custom positioning logic)
      // Module will be positioned by the layout algorithm
    }
    
  } catch (error) {
    moduleStore.setError('Failed to create module from drop')
  }
}

// Dependency creation handlers
const toggleDependencyMode = () => {
  dependencyMode.isActive = !dependencyMode.isActive
  dependencyMode.sourceNodeId = null
  if (dependencyMode.previewLine) {
    // Clear any preview line
    dependencyMode.previewLine = null
  }
}

const handleNodeClickForDependency = (nodeId: string) => {
  if (!dependencyMode.isActive) return
  
  if (!dependencyMode.sourceNodeId) {
    // Select source node
    dependencyMode.sourceNodeId = nodeId
  } else if (dependencyMode.sourceNodeId !== nodeId) {
    // Create dependency between source and target
    createDependency(dependencyMode.sourceNodeId, nodeId)
    dependencyMode.sourceNodeId = null
  }
}

const createDependency = async (sourceId: string, targetId: string) => {
  try {
    // Get the target module and add the source as a dependency
    const targetModule = moduleStore.modules[targetId]
    if (targetModule) {
      const updatedDependencies = [...(targetModule.dependencies || []), sourceId]
      await moduleStore.updateModule(targetId, { 
        dependencies: updatedDependencies 
      })
    }
  } catch (error) {
    moduleStore.setError('Failed to create dependency')
  }
}

// Watch for module changes (including filtered results)
watch(() => moduleStore.filteredModulesMap, updateNetwork, { deep: true })

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
  // Ensure container is ready before initialization
  setTimeout(() => {
    // Wait for modules to be loaded before initializing network
    if (Object.keys(moduleStore.modules).length > 0) {
      initializeNetwork()
    } else {
      // Watch for first load
      const unwatch = watch(() => moduleStore.modules, (newModules) => {
        if (Object.keys(newModules).length > 0) {
          initializeNetwork()
          unwatch()
        }
      }, { immediate: true })
    }
  }, 50) // Small delay to ensure DOM is fully ready
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
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.search-section {
  display: flex;
  justify-content: flex-start;
}

.filter-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-summary {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: auto;
}

.results-summary {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.clear-filters-btn {
  padding: 6px 12px;
  border: 1px solid #e1e5e9;
  border-radius: 6px;
  background: white;
  color: #666;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.clear-filters-btn:hover {
  border-color: #4a90e2;
  color: #4a90e2;
  background: #f8f9fa;
}

.multi-select-btn {
  padding: 8px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 6px;
  background: white;
  color: #666;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.multi-select-btn:hover {
  border-color: #4a90e2;
  color: #4a90e2;
  background: #f8f9fa;
}

.multi-select-btn.active {
  border-color: #2196f3;
  color: #2196f3;
  background: #e3f2fd;
  font-weight: 600;
}

.multi-select-btn.active:hover {
  background: #bbdefb;
}

.layout-toggle-btn {
  padding: 8px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 6px;
  background: white;
  color: #666;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.layout-toggle-btn:hover {
  border-color: #4a90e2;
  color: #4a90e2;
  background: #f8f9fa;
}

.layout-toggle-btn.layout-manual {
  border-color: #6f42c1;
  color: #6f42c1;
  background: #f8f7ff;
}

.layout-toggle-btn.layout-manual:hover {
  background: #ede7ff;
}

.layout-toggle-btn.layout-physics {
  border-color: #17a2b8;
  color: #17a2b8;
  background: #f0feff;
}

.layout-toggle-btn.layout-physics:hover {
  background: #d6f8ff;
}

.layout-toggle-btn.layout-hierarchical {
  border-color: #28a745;
  color: #28a745;
  background: #f8fff9;
}

.layout-toggle-btn.layout-hierarchical:hover {
  background: #e8f5e9;
}

/* Responsive design for filter bar */
@media (max-width: 768px) {
  .filter-bar {
    padding: 8px 12px;
  }
  
  .filter-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .filter-summary {
    margin-left: 0;
    width: 100%;
    justify-content: space-between;
  }
}

.graph-view {
  flex: 1;
  width: 100%;
  height: 100%;
  min-height: 400px;
  position: relative;
  background: #f8f9fa;
  transition: all 0.2s ease;
  /* Add diagnostic styling to ensure visibility */
  border: 2px solid #e0e0e0;
  min-width: 300px;
}

/* Ensure vis.js canvas is visible */
.graph-view canvas {
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  z-index: 1 !important;
  width: 100% !important;
  height: 100% !important;
}

/* Ensure vis.js container div is visible */
.graph-view > div {
  width: 100% !important;
  height: 100% !important;
  position: relative !important;
}

/* Layout mode indicator */
.graph-view::before {
  content: attr(data-layout-mode);
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.1);
  color: #666;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  z-index: 10;
  pointer-events: none;
  text-transform: capitalize;
}

.graph-view.drop-active {
  background: #e8f5e8;
  border: 2px dashed #27ae60;
}

.graph-view.dependency-mode {
  background: #fff3cd;
  border: 2px dashed #ffc107;
  cursor: crosshair;
}

.graph-view.drop-active::after {
  content: "Drop module here";
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(39, 174, 96, 0.9);
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 16px;
  pointer-events: none;
  z-index: 100;
}

.graph-view.dependency-mode::after {
  content: "Dependency Mode: Click two nodes to connect them";
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 193, 7, 0.9);
  color: #856404;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
  font-size: 14px;
  pointer-events: none;
  z-index: 100;
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

/* Screen reader only content */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style> 