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
    // no sorting before the data, by mouse or keyboard: the table would sort by itself, out of step with the url
    await wrapper.get('th').trigger('click')
    await wrapper.get('th').trigger('keydown', { code: 'Enter' })

    await wrapper.setProps({ data: listData() })
    expect(table.props('loading')).toBe(false)
    expect(table.props('paginator')).toBe(true)
    expect(wrapper.findAll('tbody tr').map((tr) => tr.text())).toEqual(['bob', 'alice'])
    expect(wrapper.emitted('change')).toBeUndefined()
    await wrapper.get('th').trigger('click')
    expect(wrapper.emitted('change')).toEqual([[{ page: 1, ordering: 'name' }]])
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

    table.vm.$emit('sort', { sortField: 'values.name', sortOrder: -1 })
    table.vm.$emit('page', { page: 1 })
    expect(wrapper.emitted('change')).toEqual([[{ page: 1, ordering: '-name' }], [{ page: 2, ordering: 'name' }]])
    await wrapper.vm.$nextTick()
    expect(table.props('sortOrder')).toBe(1)
    expect(table.props('first')).toBe(0)
  })

  it('sorts rows in the table itself, by the plain values', () => {
    // rows arrive as bob, alice; the table sorts them itself by values.name
    const wrapper = mountList(listProps({ data: listData({ ordering: 'name' }) }))
    const table = wrapper.getComponent(DataTable)
    expect(table.props('sortField')).toBe('values.name')
    expect(wrapper.getComponent(Column).props('sortField')).toBe('values.name')
    expect(wrapper.findAll('tbody tr').map((tr) => tr.text())).toEqual(['alice', 'bob'])
  })
})
