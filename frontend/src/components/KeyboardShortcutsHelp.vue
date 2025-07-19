<template>
  <div class="shortcuts-help">
    <button 
      @click="showHelp = !showHelp"
      class="help-toggle"
      :class="{ active: showHelp }"
      title="Keyboard shortcuts"
      aria-label="Show keyboard shortcuts"
    >
      ⌨️
    </button>
    
    <div v-if="showHelp" class="shortcuts-modal-overlay" @click="showHelp = false">
      <div class="shortcuts-modal" @click.stop>
        <div class="modal-header">
          <h3>Keyboard Shortcuts</h3>
          <button @click="showHelp = false" class="close-btn" aria-label="Close">×</button>
        </div>
        
        <div class="shortcuts-content">
          <div class="shortcut-section">
            <h4>General</h4>
            <div class="shortcut-list">
              <div class="shortcut-item">
                <kbd>Ctrl</kbd> + <kbd>Z</kbd>
                <span>Undo last action</span>
              </div>
              <div class="shortcut-item">
                <kbd>Ctrl</kbd> + <kbd>Y</kbd>
                <span>Redo last undone action</span>
              </div>
              <div class="shortcut-item">
                <kbd>Escape</kbd>
                <span>Clear selection / Exit modes</span>
              </div>
            </div>
          </div>
          
          <div class="shortcut-section">
            <h4>Selection</h4>
            <div class="shortcut-list">
              <div class="shortcut-item">
                <kbd>M</kbd>
                <span>Toggle multi-select mode</span>
              </div>
              <div class="shortcut-item">
                <kbd>Ctrl</kbd> + <kbd>A</kbd>
                <span>Select all visible modules</span>
              </div>
              <div class="shortcut-item">
                <kbd>Ctrl</kbd> + <kbd>C</kbd>
                <span>Copy selection info</span>
              </div>
            </div>
          </div>
          
          <div class="shortcut-section">
            <h4>Actions</h4>
            <div class="shortcut-list">
              <div class="shortcut-item">
                <kbd>Delete</kbd>
                <span>Delete selected module(s)</span>
              </div>
              <div class="shortcut-item">
                <kbd>Backspace</kbd>
                <span>Delete selected module(s)</span>
              </div>
            </div>
          </div>
          
          <div class="shortcut-section">
            <h4>Navigation</h4>
            <div class="shortcut-list">
              <div class="shortcut-item">
                <kbd>Arrow Keys</kbd>
                <span>Navigate between modules</span>
              </div>
              <div class="shortcut-item">
                <kbd>Enter</kbd>
                <span>Select focused module</span>
              </div>
              <div class="shortcut-item">
                <kbd>Space</kbd>
                <span>Open context menu</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <p class="note">💡 Shortcuts work when not typing in input fields</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const showHelp = ref(false)
</script>

<style scoped>
.shortcuts-help {
  position: relative;
}

.help-toggle {
  padding: 6px 8px;
  border: 2px solid #e1e5e9;
  border-radius: 6px;
  background: white;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.help-toggle:hover {
  border-color: #4a90e2;
  color: #4a90e2;
  background: #f8f9fa;
}

.help-toggle.active {
  border-color: #4a90e2;
  color: #4a90e2;
  background: #e3f2fd;
}

.shortcuts-modal-overlay {
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

.shortcuts-modal {
  background: white;
  border-radius: 8px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e1e5e9;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
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
  background: #f5f5f5;
  color: #333;
}

.shortcuts-content {
  padding: 20px 24px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.shortcut-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #4a90e2;
  border-bottom: 2px solid #e3f2fd;
  padding-bottom: 4px;
}

.shortcut-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.shortcut-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.shortcut-item:last-child {
  border-bottom: none;
}

.shortcut-item span {
  color: #666;
  font-size: 14px;
  flex: 1;
  margin-left: 12px;
}

kbd {
  background: #f5f5f5;
  border: 1px solid #ccc;
  border-radius: 3px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  color: #333;
  display: inline-block;
  font-family: monospace;
  font-size: 12px;
  font-weight: 600;
  line-height: 1;
  padding: 4px 6px;
  white-space: nowrap;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #e1e5e9;
  background: #f8f9fa;
  border-radius: 0 0 8px 8px;
}

.note {
  margin: 0;
  font-size: 13px;
  color: #666;
  text-align: center;
}

/* Responsive design */
@media (max-width: 768px) {
  .shortcuts-content {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .shortcuts-modal {
    margin: 20px;
    width: auto;
  }
}
</style>