import { test, expect } from '@playwright/test'

test.describe('Frontend E2E Setup', () => {
  test('has title', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveTitle(/Modular AI Architecture/)
  })

  test('should load without errors', async ({ page }) => {
    await page.goto('/')
    // Just check that the page loads without console errors
    const logs: string[] = []
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        logs.push(msg.text())
      }
    })
    
    await page.waitForLoadState('networkidle')
    expect(logs).toHaveLength(0)
  })
}) 