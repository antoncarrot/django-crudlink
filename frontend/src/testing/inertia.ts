// Stand-in for '@inertiajs/vue3' in tests: vi.mock('@inertiajs/vue3', () => import('../testing/inertia'))
import { vi } from 'vitest'
import { defineComponent, reactive } from 'vue'

export const page = reactive({
  props: {} as Record<string, unknown>,
})

/** Records the options `createCrudlinkApp()` passes, and starts no app. */
export const createInertiaApp = vi.fn()

export const router = {
  replace: vi.fn(),
  get: vi.fn(),
}

export const usePage = () => page

export const Head = defineComponent({ setup: () => () => null })
