// BaseList outside an Inertia app: no `vi.mock('@inertiajs/vue3')`, so there is no Inertia page.
import { mount } from '@vue/test-utils'
import OpenVue from 'openvue/config'
import DataTable from 'openvue/datatable'
import { describe, expect, it } from 'vitest'

import { CellComponent } from '../shared'
import BaseList from './BaseList.vue'

describe('BaseList without Inertia', () => {
  it('renders plain links and emits the table state', () => {
    const wrapper = mount(BaseList, {
      props: {
        columns: [{ name: 'name', label: 'Name', sortable: true }],
        data: {
          rows: [
            {
              pk: '1',
              cells: { name: { component: CellComponent.Link, props: { text: 'bob', href: '/users/1/' } } },
              values: null,
            },
          ],
          pagination: { page: 1, pageSize: 25, total: 1, hasNext: false },
          ordering: null,
        },
        isHugeTable: true,
      },
      global: { plugins: [[OpenVue, { unstyled: true }]] },
    })
    const link = wrapper.get('tbody a')
    expect(link.attributes('href')).toBe('/users/1/')
    expect(link.text()).toBe('bob')

    wrapper.getComponent(DataTable).vm.$emit('sort', { sortField: 'name', sortOrder: 1 })
    expect(wrapper.emitted('change')).toEqual([[{ page: 1, ordering: 'name' }]])
  })
})
