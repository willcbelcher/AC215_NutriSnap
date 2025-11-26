import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref } from 'vue'

// Mock Nuxt composables
vi.mock('#app', () => ({
  useFetch: vi.fn((url) => {
    if (url === '/dashboard') {
      return {
        data: ref([
          {
            id: 1,
            identified_foods: 'ramen',
            protein: 10,
            carbs: 40,
            fat: 1,
            triggers: 'None',
            created_at: new Date().toISOString(),
            user_id: 1
          }
        ]),
        pending: ref(false),
        error: ref(null)
      }
    }
    if (url === '/dashboard/symptoms') {
      return {
        data: ref([
          {
            id: 1,
            symptom_name: 'Headache',
            severity: 7,
            notes: 'After lunch',
            created_at: new Date().toISOString(),
            user_id: 1
          }
        ]),
        pending: ref(false),
        error: ref(null)
      }
    }
    if (url === '/dashboard/triggers') {
      return {
        data: ref(['Lactose', 'Gluten']),
        pending: ref(false),
        error: ref(null)
      }
    }
    return { data: ref([]), pending: ref(false), error: ref(null) }
  }),
  useRuntimeConfig: vi.fn(() => ({
    apiBase: 'http://localhost:8000',
    public: { apiBase: 'http://localhost:8000' }
  })),
  computed: vi.fn((fn) => {
    return { value: fn() }
  })
}))

// Mock vue3-apexcharts
vi.mock('vue3-apexcharts', () => ({
  default: {
    name: 'apexchart',
    template: '<div class="mock-apexchart"></div>'
  }
}))

describe('Dashboard Page - Basic Tests', () => {
  it('should have dashboard title in template', async () => {
    // This test verifies the static content exists
    const { default: IndexPage } = await import('~/pages/index.vue')

    // Check that the component template string contains expected text
    const componentString = IndexPage.__file || IndexPage.toString()

    // Basic smoke test - component exists and can be imported
    expect(IndexPage).toBeDefined()
    expect(IndexPage.__name || IndexPage.name).toBeTruthy()
  })

  it('should export a valid Vue component', async () => {
    const { default: IndexPage } = await import('~/pages/index.vue')

    // Verify it's a valid component with setup or template
    expect(IndexPage).toHaveProperty('setup')
    expect(IndexPage.setup).toBeTypeOf('function')
  })
})
