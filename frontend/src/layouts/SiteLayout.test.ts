import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import { page } from '../testing/inertia'
import SiteLayout from './SiteLayout.vue'

vi.mock('@inertiajs/vue3', () => import('../testing/inertia'))

describe('SiteLayout', () => {
  it('shows the site title from the crudlink prop and renders the page', () => {
    page.props = { crudlink: { siteTitle: 'Back office' } }
    const wrapper = mount(SiteLayout, { slots: { default: '<p class="page">Users</p>' } })
    expect(wrapper.get('.site-layout__title').text()).toBe('Back office')
    expect(wrapper.get('.site-layout__main .page').text()).toBe('Users')
  })
})
