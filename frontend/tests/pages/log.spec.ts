import { describe, it, expect, vi } from 'vitest'
import { ref } from 'vue'

// Mock Nuxt composables
vi.mock('#app', () => ({
  useFetch: vi.fn(() => {
    return { data: ref([]), pending: ref(false), error: ref(null) }
  }),
  useRuntimeConfig: vi.fn(() => ({
    apiBase: 'http://localhost:8000',
    public: { apiBase: 'http://localhost:8000' }
  })),
}))

describe('Log Page', () => {
  it('should export a valid Vue component', async () => {
    const { default: LogPage } = await import('~/pages/log.vue')
    expect(LogPage).toBeDefined()
    expect(LogPage.setup).toBeTypeOf('function')
  })
})
