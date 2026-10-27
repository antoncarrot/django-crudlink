import { mount } from '@vue/test-utils'
import Column from 'openvue/column'
import OpenVue from 'openvue/config'
import DataTable from 'openvue/datatable'
import { describe, expect, it } from 'vitest'

import { CellComponent, type ListData, type RowData } from '../shared'
import type { BaseListProps } from '../types'
import BaseList from './BaseList.vue'

function row(pk: number, name: string): RowData {
  return {
    pk: String(pk),
    cells: { name: { component: CellComponent.Text, props: { text: name } } },
    values: { name },
  }
}

function listData(overrides: Partial<ListData> = {}): ListData {
  return {
    rows: [row(1, 'bob'), row(2, 'alice')],
    pagination: { page: 1, pageSize: 25, total: 2, hasNext: false },
    ordering: null,
    ...overrides,
  }
}

function listProps(overrides: Partial<BaseListProps> = {}): BaseListProps {
  return {
    columns: [{ name: 'name', label: 'Name', sortable: true }],
    data: listData(),
    ...overrides,
  }
}

function mountList(props: BaseListProps) {
  return mount(BaseList, {
    props,
    global: { plugins: [[OpenVue, { unstyled: true }]] },
  })
}

describe('BaseList', () => {
  it('shows the loading state until the deferred data arrives', async () => {
    const wrapper = mountList(listProps({ data: undefined }))
    const table = wrapper.getComponent(DataTable)
    expect(table.props('loading')).toBe(true)
    expect(table.props('value')).toEqual([])
    expect(table.props('paginator')).toBe(false)
    expect(wrapper.find('tbody').text()).toBe('')

    await wrapper.setProps({ data: listData() })
    expect(table.props('loading')).toBe(false)
    expect(table.props('paginator')).toBe(true)
    expect(wrapper.findAll('tbody tr').map((tr) => tr.text())).toEqual(['bob', 'alice'])
    await wrapper.get('th').trigger('click')
    expect(wrapper.emitted('change')).toEqual([[{ page: 1, ordering: 'name' }]])
  })

  it('shows the loading state while the page reloads the data', () => {
    const wrapper = mountList(listProps({ loading: true }))
    expect(wrapper.getComponent(DataTable).props('loading')).toBe(true)
    // the rows stay until the new data comes
    expect(wrapper.findAll('tbody tr')).toHaveLength(2)
  })

  it('says so when there are no rows', () => {
    const wrapper = mountList(listProps({ data: listData({ rows: [] }) }))
    expect(wrapper.get('tbody').text()).toBe('No rows')
  })

  it('takes the state from the data', async () => {
    const data = listData({ pagination: { page: 2, pageSize: 25, total: 30, hasNext: false }, ordering: '-name' })
    const wrapper = mountList(listProps({ data }))
    const table = wrapper.getComponent(DataTable)
    expect(table.props('first')).toBe(25)
    expect(table.props('sortOrder')).toBe(-1)
    // new data (another visit, or browser back) brings its own state
    await wrapper.setProps({ data: listData({ ordering: 'name' }) })
    expect(table.props('first')).toBe(0)
    expect(table.props('sortOrder')).toBe(1)
  })

  it('only emits the new state: the page updates data', async () => {
    const wrapper = mountList(listProps({ data: listData({ ordering: 'name' }) }))
    const table = wrapper.getComponent(DataTable)

    // the DataTable sends its own sort along with a page change
    table.vm.$emit('sort', { sortField: 'values.name', sortOrder: -1 })
    table.vm.$emit('page', { page: 1, sortField: 'values.name', sortOrder: 1 })
    expect(wrapper.emitted('change')).toEqual([[{ page: 1, ordering: '-name' }], [{ page: 2, ordering: 'name' }]])
    await wrapper.vm.$nextTick()
    expect(table.props('sortOrder')).toBe(1)
    expect(table.props('first')).toBe(0)
  })

  it('pages with the sort the table shows, even before the data has it', () => {
    // a sort by -email is still loading: the data says name
    const wrapper = mountList(listProps({ hugeTable: true, loading: true, data: listData({ ordering: 'name' }) }))
    wrapper.getComponent(DataTable).vm.$emit('page', { page: 1, sortField: 'email', sortOrder: -1 })
    expect(wrapper.emitted('change')).toEqual([[{ page: 2, ordering: '-email' }]])
  })

  it('goes back to the page and sort in the data when a reload ends without new data', async () => {
    const data = listData({ pagination: { page: 1, pageSize: 25, total: 80, hasNext: true }, ordering: 'name' })
    const wrapper = mountList(listProps({ hugeTable: true, data }))
    const table = wrapper.getComponent(DataTable)
    // clicks: page 3, then a sort by -email; the page starts a reload
    table.vm.$emit('update:first', 50)
    table.vm.$emit('update:sortField', 'email')
    table.vm.$emit('update:sortOrder', -1)
    await wrapper.setProps({ loading: true })
    expect([table.props('first'), table.props('sortField'), table.props('sortOrder')]).toEqual([50, 'email', -1])

    // the reload failed: same data
    await wrapper.setProps({ loading: false })
    expect([table.props('first'), table.props('sortField'), table.props('sortOrder')]).toEqual([0, 'name', 1])
  })

  describe('frontend mode (hugeTable = false)', () => {
    it('sorts rows in the table itself, by the plain values', () => {
      // rows arrive as bob, alice; the table sorts them itself by values.name
      const wrapper = mountList(listProps({ data: listData({ ordering: 'name' }) }))
      const table = wrapper.getComponent(DataTable)
      expect(table.props('lazy')).toBe(false)
      expect(table.props('sortField')).toBe('values.name')
      expect(wrapper.getComponent(Column).props('sortField')).toBe('values.name')
      expect(wrapper.findAll('tbody tr').map((tr) => tr.text())).toEqual(['alice', 'bob'])
    })
  })

  describe('hugeTable mode', () => {
    it('lets the backend sort by column name', () => {
      // rows arrive as bob, alice and stay so: the backend sorted them
      const wrapper = mountList(listProps({ hugeTable: true, data: listData({ ordering: 'name' }) }))
      const table = wrapper.getComponent(DataTable)
      expect(table.props('lazy')).toBe(true)
      expect(table.props('sortField')).toBe('name')
      expect(wrapper.getComponent(Column).props('sortField')).toBe('name')
      expect(wrapper.findAll('tbody tr').map((tr) => tr.text())).toEqual(['bob', 'alice'])
      table.vm.$emit('sort', { sortField: 'name', sortOrder: -1 })
      expect(wrapper.emitted('change')).toEqual([[{ page: 1, ordering: '-name' }]])
    })

    it('pages without a row count', async () => {
      const rows = Array.from({ length: 25 }, (_, index) => row(index, `user${index}`))
      const data = listData({ rows, pagination: { page: 2, pageSize: 25, total: null, hasNext: true } })
      const wrapper = mountList(listProps({ hugeTable: true, data }))
      const table = wrapper.getComponent(DataTable)
      // 25 rows before, 25 on this page, one more so "next" is enabled
      expect(table.props('totalRecords')).toBe(51)
      expect(table.props('paginatorTemplate')).toBe('PrevPageLink CurrentPageReport NextPageLink')
      expect(wrapper.find('[data-pc-name="pcpaginator"]').text()).toBe('2')

      // a page past the end: still counted up to its end, or the paginator would jump back by itself
      const pagination = { page: 3, pageSize: 25, total: null, hasNext: false }
      await wrapper.setProps({ data: listData({ rows: [], pagination }) })
      expect(table.props('first')).toBe(50)
      expect(table.props('totalRecords')).toBe(75)
      expect(wrapper.emitted('change')).toBeUndefined()
    })
  })
})
