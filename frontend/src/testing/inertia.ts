// Stand-in for '@inertiajs/vue3' in tests: vi.mock('@inertiajs/vue3', () => import('../testing/inertia'))
import { defineComponent, reactive } from 'vue'

export const page = reactive({
  props: {} as Record<string, unknown>,
})

export const usePage = () => page

export const Head = defineComponent({ setup: () => () => null })
