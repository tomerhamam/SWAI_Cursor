import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Temporary config with dynamic ports
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': '/src'
    }
  },
  server: {
    port: 3001,
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true
      }
    }
  }
})
