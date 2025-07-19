import { onMounted, onUnmounted } from 'vue'
import { useModuleStore } from '../stores/moduleStore'

export function useKeyboardShortcuts() {
  const moduleStore = useModuleStore()

  const handleKeydown = async (event: KeyboardEvent) => {
    // Don't trigger shortcuts when user is typing in inputs
    const activeElement = document.activeElement
    if (activeElement && (
      activeElement.tagName === 'INPUT' || 
      activeElement.tagName === 'TEXTAREA' || 
      activeElement.contentEditable === 'true'
    )) {
      return
    }

    const isCtrl = event.ctrlKey || event.metaKey // Support both Ctrl and Cmd
    const key = event.key.toLowerCase()

    try {
      switch (true) {
        // Undo/Redo
        case isCtrl && key === 'z' && !event.shiftKey:
          event.preventDefault()
          if (moduleStore.canUndo) {
            await moduleStore.undo()
          }
          break

        case isCtrl && (key === 'y' || (key === 'z' && event.shiftKey)):
          event.preventDefault()
          if (moduleStore.canRedo) {
            await moduleStore.redo()
          }
          break

        // Select All (multi-select mode)
        case isCtrl && key === 'a':
          event.preventDefault()
          if (!moduleStore.isMultiSelectMode) {
            moduleStore.enableMultiSelectMode()
          }
          moduleStore.selectAllVisibleModules()
          break

        // Delete selected modules
        case key === 'delete' || key === 'backspace':
          event.preventDefault()
          await handleDelete()
          break

        // Toggle multi-select mode
        case key === 'm' && !isCtrl:
          event.preventDefault()
          moduleStore.toggleMultiSelectMode()
          break

        // Escape - Clear selections and exit modes
        case key === 'escape':
          event.preventDefault()
          if (moduleStore.isMultiSelectMode) {
            moduleStore.clearAllSelections()
          } else if (moduleStore.selectedModuleId) {
            moduleStore.clearSelection()
          }
          break

        // Copy selection info (for debugging/export)
        case isCtrl && key === 'c':
          event.preventDefault()
          await handleCopy()
          break
      }
    } catch (error) {
      console.error('Keyboard shortcut error:', error)
      moduleStore.setError('Keyboard shortcut failed: ' + (error instanceof Error ? error.message : 'Unknown error'))
    }
  }

  const handleDelete = async () => {
    if (moduleStore.isMultiSelectMode && moduleStore.selectedModuleCount > 0) {
      // Multi-select: Delete multiple modules
      const selectedCount = moduleStore.selectedModuleCount
      const moduleNames = moduleStore.selectedModules.map(m => m.name).join(', ')
      
      if (confirm(`Delete ${selectedCount} selected module${selectedCount > 1 ? 's' : ''}?\n\n${moduleNames}\n\nThis action can be undone.`)) {
        await moduleStore.bulkDeleteModules()
      }
    } else if (moduleStore.selectedModuleId) {
      // Single select: Delete one module
      const moduleName = moduleStore.selectedModuleId
      if (confirm(`Delete module "${moduleName}"?\n\nThis action can be undone.`)) {
        await moduleStore.deleteModule(moduleName)
      }
    }
  }

  const handleCopy = async () => {
    let copyData = ''
    
    if (moduleStore.isMultiSelectMode && moduleStore.selectedModuleCount > 0) {
      // Copy selected modules info
      const modules = moduleStore.selectedModules
      copyData = modules.map(m => `${m.name}: ${m.description} (${m.status})`).join('\n')
    } else if (moduleStore.selectedModuleId) {
      // Copy single module info
      const module = moduleStore.selectedModule
      if (module) {
        copyData = `${module.name}: ${module.description} (${module.status})`
      }
    }

    if (copyData) {
      try {
        await navigator.clipboard.writeText(copyData)
        // Successfully copied to clipboard
      } catch (error) {
        // Clipboard operation failed - user will need to copy manually
        moduleStore.setError('Failed to copy to clipboard. Please copy the information manually.')
      }
    }
  }

  onMounted(() => {
    document.addEventListener('keydown', handleKeydown)
  })

  onUnmounted(() => {
    document.removeEventListener('keydown', handleKeydown)
  })

  return {
    // Expose handler for testing or manual use
    handleKeydown
  }
}