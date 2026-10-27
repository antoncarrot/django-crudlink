import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import { defineComponent, h, type Plugin } from 'vue'

import CellRenderer from './components/CellRenderer.vue'
import { crudlinkRegistry } from './registry'
import { type Cell, CellComponent } from './shared'

const Badge = defineComponent({ props: { value: Number }, setup: (props) => () => h('b', `badge ${props.value}`) })

function mountCell(cell: Cell, plugins: Plugin[] = []) {
  return mount(CellRenderer, { props: { cell }, global: { plugins } })
}

describe('registry', () => {
  it('renders built-in components without a registry', () => {
    expect(mountCell({ component: CellComponent.Text, props: { text: 'bob' } }).text()).toBe('bob')
  })

  it('renders the custom components of the app registry', () => {
    const registry = crudlinkRegistry({ cells: { badge: Badge } })
    expect(mountCell({ component: 'badge', props: { value: 3 } }, [registry]).text()).toBe('badge 3')
    // the built-in ones stay
    expect(mountCell({ component: CellComponent.Text, props: { text: 'bob' } }, [registry]).text()).toBe('bob')
  })

  it('falls back to the text or value and warns about unknown names', () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
    expect(mountCell({ component: 'nope', props: { text: 'bob' } }).text()).toBe('bob')
    // names of Object.prototype members are unknown too
    expect(mountCell({ component: 'constructor', props: { text: 'bob' } }).text()).toBe('bob')
    // a custom cell that isn't registered, e.g. in the prebuilt bundles, still shows its value
    expect(mountCell({ component: 'badge', props: { value: 3 } }).text()).toBe('3')
    expect(mountCell({ component: 'badge', props: { value: ['staff', 'editors'] } }).text()).toBe('staff, editors')
    expect(warn).toHaveBeenCalledTimes(4)
  })
})
