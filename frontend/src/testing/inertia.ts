// Stand-in for '@inertiajs/vue3' in tests: vi.mock('@inertiajs/vue3', () => import('../testing/inertia'))
import { vi } from 'vitest'
import { defineComponent, h, reactive } from 'vue'

export const page = reactive({
  props: {} as Record<string, unknown>,
})

/** Records the options `createCrudlinkApp()` passes, and starts no app. */
export const createInertiaApp = vi.fn()

export const router = {
  visit: vi.fn(),
  replace: vi.fn(),
  get: vi.fn(),
}

export const usePage = () => page

/** Renders an <a data-inertia-link> so tests can tell it from a plain <a>. */
export const Link = defineComponent({
  props: { href: { type: String, required: true } },
  setup(props, { slots }) {
    return () => h('a', { href: props.href, 'data-inertia-link': '' }, slots.default?.())
  },
})

export const Head = defineComponent({ setup: () => () => null })
