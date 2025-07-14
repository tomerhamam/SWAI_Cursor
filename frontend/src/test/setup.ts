import { vi } from 'vitest'

// Mock vis-network for testing
vi.mock('vis-network', () => ({
  Network: vi.fn(),
  DataSet: vi.fn(),
  Node: vi.fn(),
  Edge: vi.fn(),
}))

// Mock console methods in tests
global.console = {
  ...console,
  log: vi.fn(),
  debug: vi.fn(),
  info: vi.fn(),
  warn: vi.fn(),
  error: vi.fn(),
}

// Setup global test utilities
beforeEach(() => {
  // Reset all mocks before each test
  vi.clearAllMocks()
}) 