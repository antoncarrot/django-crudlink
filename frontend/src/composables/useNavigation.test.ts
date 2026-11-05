import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import CrudLink from '../components/CrudLink.vue'
import { page, router } from '../testing/inertia'
import { isSafeUrl, useNavigation } from './useNavigation'

vi.mock('@inertiajs/vue3', () => import('../testing/inertia'))

/** The `crudlink` prop of the current page (CrudlinkMiddleware); null - a page without it. */
function setInertiaNavigation(isInertiaNavigation: boolean | null): void {
  page.props =
    isInertiaNavigation === null ? {} : { crudlink: { siteTitle: 'Crudlink', inertiaNavigation: isInertiaNavigation } }
}

beforeEach(() => setInertiaNavigation(null))

describe('useNavigation', () => {
  it('does a full page load by default and without the crudlink prop', () => {
    const assign = vi.spyOn(window.location, 'assign').mockImplementation(() => {})
    for (const isInertiaNavigation of [null, false]) {
      setInertiaNavigation(isInertiaNavigation)
      const { isInertiaNavigation: mode, visit } = useNavigation()
      visit('/users/1/')
      expect(mode.value).toBe(false)
    }
    expect(assign.mock.calls).toEqual([['/users/1/'], ['/users/1/']])
    expect(router.visit).not.toHaveBeenCalled()
  })

  it('visits with Inertia when CRUDLINK_INERTIA_NAVIGATION is on', () => {
    const assign = vi.spyOn(window.location, 'assign').mockImplementation(() => {})
    setInertiaNavigation(true)
    const { isInertiaNavigation, visit } = useNavigation()
    visit('/users/1/')
    expect(router.visit).toHaveBeenCalledWith('/users/1/')
    expect(assign).not.toHaveBeenCalled()
    // follows the prop of the current page
    setInertiaNavigation(false)
    expect(isInertiaNavigation.value).toBe(false)
  })

  it('does not visit an unsafe url', () => {
    const assign = vi.spyOn(window.location, 'assign').mockImplementation(() => {})
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
    for (const isInertiaNavigation of [false, true]) {
      setInertiaNavigation(isInertiaNavigation)
      useNavigation().visit('javascript:alert(1)')
    }
    expect(assign).not.toHaveBeenCalled()
    expect(router.visit).not.toHaveBeenCalled()
    expect(warn).toHaveBeenCalledTimes(2)
  })
})

describe('isSafeUrl', () => {
  it('allows relative, http(s), mailto and tel urls, not code', () => {
    const safe = ['/users/1/', 'users/1/', '?page=2', '//example.com/', 'https://example.com/', 'HTTP://example.com/']
    for (const url of [...safe, 'mailto:bob@example.com', 'tel:+123']) {
      expect(isSafeUrl(url), url).toBe(true)
    }
    // the browser drops the leading space and the tab: these run as javascript: urls
    const unsafe = ['javascript:alert(1)', ' JavaScript:alert(1)', 'java\tscript:alert(1)', 'vbscript:msgbox(1)']
    for (const url of [...unsafe, 'data:text/html,<script>alert(1)</script>', 'http://[']) {
      expect(isSafeUrl(url), url).toBe(false)
    }
  })
})

describe('CrudLink', () => {
  function mountLink(href: string) {
    return mount(CrudLink, { props: { href }, attrs: { class: 'crud-link' }, slots: { default: 'bob' } })
  }

  it('renders a plain link by default', () => {
    const link = mountLink('/users/1/').get('a')
    expect(link.attributes('href')).toBe('/users/1/')
    expect(link.attributes()).not.toHaveProperty('data-inertia-link')
    expect(link.classes()).toContain('crud-link')
    expect(link.text()).toBe('bob')
  })

  it('renders an Inertia Link with Inertia navigation', () => {
    setInertiaNavigation(true)
    const link = mountLink('/users/1/').get('a')
    expect(link.attributes()).toHaveProperty('data-inertia-link')
    expect(link.classes()).toContain('crud-link')
  })

  it('shows an unsafe url as plain text', () => {
    for (const isInertiaNavigation of [false, true]) {
      setInertiaNavigation(isInertiaNavigation)
      const wrapper = mountLink('javascript:alert(1)')
      expect(wrapper.find('a').exists()).toBe(false)
      expect(wrapper.text()).toBe('bob')
      expect(wrapper.classes()).not.toContain('crud-link')
    }
  })
})
