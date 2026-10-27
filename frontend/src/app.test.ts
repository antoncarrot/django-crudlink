import { describe, expect, it, vi } from 'vitest'
import type { DefineComponent } from 'vue'

import { createCrudlinkApp } from './app'
import BaseListPage from './pages/BaseListPage.vue'
import { PageComponent } from './shared'
import { createInertiaApp } from './testing/inertia'

vi.mock('@inertiajs/vue3', () => import('./testing/inertia'))

/** The page resolver `createCrudlinkApp({ resolve })` gives Inertia. */
function pageResolver(resolve?: (name: string) => DefineComponent | undefined): (name: string) => unknown {
  createCrudlinkApp({ resolve })
  const [options] = vi.mocked(createInertiaApp).mock.lastCall as [{ resolve: (name: string) => unknown }]
  return options.resolve
}

describe('createCrudlinkApp', () => {
  it('resolves crudlink pages before the project ones', () => {
    const HostPage = {} as DefineComponent
    const resolve = pageResolver(() => HostPage)
    expect(resolve(PageComponent.List)).toBe(BaseListPage)
    expect(resolve('Dashboard')).toBe(HostPage)
    // names of Object.prototype members are project pages too
    expect(resolve('toString')).toBe(HostPage)
  })

  it('throws for a page nobody resolves', () => {
    const resolve = pageResolver()
    expect(() => resolve('Dashboard')).toThrow('Inertia page not found: Dashboard')
    expect(() => resolve('toString')).toThrow('Inertia page not found: toString')
  })
})
