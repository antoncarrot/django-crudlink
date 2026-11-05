// BaseDetail outside an Inertia app: no `vi.mock('@inertiajs/vue3')`, so there is no Inertia page.

import { mount } from '@vue/test-utils'
import OpenVue from 'openvue/config'
import { describe, expect, it } from 'vitest'
import { CellComponent, type LayoutNode, LayoutType } from '../shared'
import BaseDetail from './BaseDetail.vue'

function node(
  type: LayoutNode['type'],
  fieldName: string | null,
  children: LayoutNode[] = [],
  label: string | null = null,
  cols = 1,
): LayoutNode {
  return { type, cols, label, field: fieldName, children }
}

describe('BaseDetail', () => {
  it('renders the fields in the layout, links as plain links, without the missing ones', () => {
    const wrapper = mount(BaseDetail, {
      props: {
        fields: {
          username: { label: 'Username', cell: { component: CellComponent.Text, props: { text: 'bob' } } },
          email: { label: 'Email', cell: { component: CellComponent.Text, props: { text: 'bob@example.com' } } },
          group: {
            label: 'Group',
            cell: { component: CellComponent.Link, props: { text: 'staff', href: '/groups/1/' } },
          },
        },
        layout: node(LayoutType.Layout, null, [
          // Span('email', cols=2); `missing` has no field: no column for it
          node(LayoutType.Row, null, [
            node(LayoutType.Field, 'email', [], null, 2),
            node(LayoutType.Field, 'missing'),
            node(LayoutType.Field, 'username'),
          ]),
          node(
            LayoutType.Fieldset,
            null,
            [node(LayoutType.Field, 'group'), node(LayoutType.Field, 'missing')],
            'Access',
          ),
          // no field in it: no fieldset; "constructor" is not Object.prototype.constructor
          node(
            LayoutType.Fieldset,
            null,
            [node(LayoutType.Field, 'missing'), node(LayoutType.Field, 'constructor')],
            'Empty',
          ),
        ]),
      },
      global: { plugins: [[OpenVue, { unstyled: true }]] },
    })
    expect(wrapper.findAll('.crud-detail-field__label').map((label) => label.text())).toEqual([
      'Email',
      'Username',
      'Group',
    ])
    const row = wrapper.get('.layout-row')
    expect(row.text()).toBe('Emailbob@example.comUsernamebob')
    expect((row.element as HTMLElement).style.gridTemplateColumns).toBe('minmax(0, 2fr) minmax(0, 1fr)')
    expect(row.findAll(':scope > .crud-detail-field')).toHaveLength(2)
    expect(wrapper.findAll('fieldset').map((fieldset) => fieldset.find('legend').text())).toEqual(['Access'])
    expect(wrapper.get('fieldset a').attributes('href')).toBe('/groups/1/')
  })
})
