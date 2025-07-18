import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

const app = createApp(App)
const pinia = createPinia()

// Global error handling
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue Error:', err)
  console.error('Component:', instance)
  console.error('Error Info:', info)
  
  // In a production app, you would send this to an error reporting service
  // For now, we'll just log it and show a user-friendly message
  if (err instanceof Error) {
    // You could show a toast notification or error modal here
    console.error('Application Error:', err.message)
  }
}

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', event => {
  console.error('Unhandled Promise Rejection:', event.reason)
  event.preventDefault() // Prevent the default browser error handling
})

app.use(pinia)
app.mount('#app') 