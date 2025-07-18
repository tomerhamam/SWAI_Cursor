import axios from 'axios'
import type { Module } from '../stores/moduleStore'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for debugging
api.interceptors.request.use(request => {
  console.log('API Request:', request.method?.toUpperCase(), request.url)
  return request
})

// Response interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error.response?.status, error.response?.data)
    
    // Enhanced error handling with user-friendly messages
    if (error.code === 'ECONNABORTED') {
      error.message = 'Request timeout - please check your connection'
    } else if (error.response?.status === 404) {
      error.message = error.response.data?.error || 'Resource not found'
    } else if (error.response?.status === 409) {
      error.message = error.response.data?.error || 'Resource already exists'
    } else if (error.response?.status >= 500) {
      error.message = 'Server error - please try again later'
    } else if (error.response?.data?.error) {
      error.message = error.response.data.error
    } else if (!navigator.onLine) {
      error.message = 'No internet connection - please check your network'
    }
    
    return Promise.reject(error)
  }
)

export const apiService = {
  // Get all modules
  async getModules(): Promise<Record<string, Module>> {
    const response = await api.get('/modules')
    return response.data
  },

  // Get a specific module
  async getModule(moduleId: string): Promise<Module> {
    const response = await api.get(`/modules/${moduleId}`)
    return response.data
  },

  // Create a new module
  async createModule(module: Omit<Module, 'name'> & { name: string }): Promise<Module> {
    const response = await api.post('/modules', module)
    return response.data
  },

  // Update an existing module
  async updateModule(moduleId: string, updates: Partial<Module>): Promise<Module> {
    const response = await api.put(`/modules/${moduleId}`, updates)
    return response.data
  },

  // Delete a module
  async deleteModule(moduleId: string): Promise<void> {
    await api.delete(`/modules/${moduleId}`)
  },

  // Get available surrogates
  async getSurrogates(): Promise<string[]> {
    const response = await api.get('/surrogates')
    return response.data
  },

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await api.get('/health')
    return response.data
  }
} 