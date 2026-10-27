import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import CellRenderer from './components/CellRenderer.vue'
import { type Cell, CellComponent } from './shared'

function mountCell(cell: Cell) {
  return mount(CellRenderer, { props: { cell } })
}

describe('registry', () => {
  it('renders built-in components without a registry', () => {
    expect(mountCell({ component: CellComponent.Text, props: { text: 'bob' } }).text()).toBe('bob')
  })

  it('falls back to text and warns about unknown names', () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
    expect(mountCell({ component: 'nope', props: { text: 'bob' } }).text()).toBe('bob')
    // names of Object.prototype members are unknown too
    expect(mountCell({ component: 'constructor', props: { text: 'bob' } }).text()).toBe('bob')
    expect(warn).toHaveBeenCalledTimes(2)
  })
})
