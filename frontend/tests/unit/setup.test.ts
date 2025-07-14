import { describe, it, expect } from 'vitest'

describe('Frontend Testing Setup', () => {
  it('should have working test environment', () => {
    expect(true).toBe(true)
  })

  it('should have access to DOM', () => {
    const element = document.createElement('div')
    element.innerHTML = 'test'
    expect(element.innerHTML).toBe('test')
  })
}) 