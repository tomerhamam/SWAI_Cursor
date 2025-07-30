/**
 * Utility functions for exporting module data to CSV format
 */

import type { Module } from '../stores/moduleStore'

interface ExportableModule {
  name: string
  description: string
  status: string
  version: string
  inputs?: string[]
  outputs?: string[]
  dependencies?: string[]
  file_path?: string
}

/**
 * Converts an array of modules to CSV format
 */
export function modulesToCSV(modules: ExportableModule[]): string {
  if (modules.length === 0) {
    return 'name,description,status,version,inputs,outputs,dependencies,file_path\n'
  }

  // CSV Header
  const headers = ['name', 'description', 'status', 'version', 'inputs', 'outputs', 'dependencies', 'file_path']
  const csvHeaders = headers.join(',')

  // CSV Rows
  const csvRows = modules.map(module => {
    // Escape CSV values (handle commas, quotes, and newlines)
    const escapeCSVValue = (value: unknown): string => {
      if (value == null) return ''
      
      let stringValue: string
      if (Array.isArray(value)) {
        stringValue = value.join('; ') // Use semicolon to separate array items
      } else {
        stringValue = String(value)
      }
      
      // If the value contains comma, quote, or newline, wrap in quotes and escape quotes
      if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n') || stringValue.includes('\r')) {
        stringValue = '"' + stringValue.replace(/"/g, '""') + '"'
      }
      
      return stringValue
    }

    return [
      escapeCSVValue(module.name),
      escapeCSVValue(module.description),
      escapeCSVValue(module.status),
      escapeCSVValue(module.version),
      escapeCSVValue(module.inputs),
      escapeCSVValue(module.outputs),
      escapeCSVValue(module.dependencies),
      escapeCSVValue(module.file_path)
    ].join(',')
  })

  return [csvHeaders, ...csvRows].join('\n')
}

/**
 * Downloads a CSV file with the given data
 */
export function downloadCSV(csvData: string, filename: string): void {
  const csvBlob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(csvBlob)
  
  const link = document.createElement('a')
  link.href = url
  link.download = filename.endsWith('.csv') ? filename : `${filename}.csv`
  link.setAttribute('style', 'display: none;')
  
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

/**
 * Downloads a JSON file with the given data
 */
export function downloadJSON(data: unknown, filename: string): void {
  const jsonString = JSON.stringify(data, null, 2)
  const jsonBlob = new Blob([jsonString], { type: 'application/json' })
  const url = URL.createObjectURL(jsonBlob)
  
  const link = document.createElement('a')
  link.href = url
  link.download = filename.endsWith('.json') ? filename : `${filename}.json`
  link.setAttribute('style', 'display: none;')
  
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

/**
 * Export modules data in the specified format
 */
export function exportModules(
  modules: ExportableModule[], 
  format: 'csv' | 'json', 
  baseFilename: string,
  additionalData?: Record<string, unknown>
): void {
  const timestamp = new Date().toISOString().split('T')[0]
  
  if (format === 'csv') {
    const csvData = modulesToCSV(modules)
    downloadCSV(csvData, `${baseFilename}-${timestamp}`)
  } else {
    const exportData = {
      exportedAt: new Date().toISOString(),
      totalResults: modules.length,
      ...additionalData,
      modules
    }
    downloadJSON(exportData, `${baseFilename}-${timestamp}`)
  }
}