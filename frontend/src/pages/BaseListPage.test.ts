import { mount } from '@vue/test-utils'
import OpenVue from 'openvue/config'
import { describe, expect, it, vi } from 'vitest'

import BaseList from '../components/BaseList.vue'
import { CellComponent, type ListProps } from '../shared'
import { router } from '../testing/inertia'
import BaseListPage from './BaseListPage.vue'

vi.mock('@inertiajs/vue3', () => import('../testing/inertia'))

function listProps(overrides: Partial<ListProps> = {}): ListProps {
  return {
    title: 'Users',
    columns: [{ name: 'name', label: 'Name', sortable: true }],
    data: {
      rows: [
        {
          pk: '1',
          cells: { name: { component: CellComponent.Text, props: { text: 'bob' } } },
          values: { name: 'bob' },
        },
      ],
      pagination: { page: 1, pageSize: 25, total: 1, hasNext: false },
      ordering: null,
    },
    hugeTable: false,
    ...overrides,
  }
}

function mountPage(props: ListProps) {
  return mount(BaseListPage, {
    props,
    global: { plugins: [[OpenVue, { unstyled: true }]] },
  })
}

describe('BaseListPage', () => {
  it('renders the title and passes the list props to the table', () => {
    const props = listProps({ hugeTable: true })
    const wrapper = mountPage(props)
    expect(wrapper.find('h1').text()).toBe('Users')
    const table = wrapper.getComponent(BaseList)
    expect(table.props()).toEqual({ columns: props.columns, data: props.data, hugeTable: true, loading: false })
    expect(table.attributes('title')).toBeUndefined()
  })

  it('updates the url on a table change: a reload of data for a huge table', async () => {
    window.history.replaceState(null, '', '/users/')
    const huge = mountPage(listProps({ hugeTable: true })).getComponent(BaseList)
    huge.vm.$emit('change', { page: 2, ordering: null })
    expect(router.get).toHaveBeenCalledWith('/users/?page=2', {}, expect.objectContaining({ only: ['data'] }))
    await huge.vm.$nextTick()
    expect(huge.props('loading')).toBe(true)

    const table = mountPage(listProps()).getComponent(BaseList)
    table.vm.$emit('change', { page: 1, ordering: 'name' })
    expect(router.replace).toHaveBeenCalledWith(expect.objectContaining({ url: '/users/?o=name' }))
  })
})
