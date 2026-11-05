import { mount } from '@vue/test-utils'
import Button from 'openvue/button'
import OpenVue from 'openvue/config'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import BaseDetail from '../components/BaseDetail.vue'
import { CellComponent, type DetailProps, LayoutType } from '../shared'
import { page } from '../testing/inertia'
import BaseDetailPage from './BaseDetailPage.vue'

vi.mock('@inertiajs/vue3', () => import('../testing/inertia'))

function detailProps(overrides: Partial<DetailProps> = {}): DetailProps {
  return {
    title: 'bob',
    fields: { username: { label: 'Username', cell: { component: CellComponent.Text, props: { text: 'bob' } } } },
    layout: {
      type: LayoutType.Layout,
      cols: 1,
      label: null,
      field: null,
      children: [{ type: LayoutType.Field, cols: 1, label: null, field: 'username', children: [] }],
    },
    listUrl: null,
    ...overrides,
  }
}

function mountPage(props: DetailProps) {
  return mount(BaseDetailPage, {
    props,
    global: { plugins: [[OpenVue, { unstyled: true }]] },
  })
}

describe('BaseDetailPage', () => {
  beforeEach(() => {
    page.props = {}
  })

  it('renders the title and passes the fields and layout to the field list', () => {
    const props = detailProps()
    const wrapper = mountPage(props)
    expect(wrapper.find('h1').text()).toBe('bob')
    expect(wrapper.getComponent(BaseDetail).props()).toEqual({ fields: props.fields, layout: props.layout })
    expect(wrapper.findComponent(Button).exists()).toBe(false)
  })

  it('shows a button per url, a link in the navigation mode', () => {
    const wrapper = mountPage(detailProps({ listUrl: '/users/' }))
    expect(wrapper.findAllComponents(Button).map((button) => button.props('label'))).toEqual(['Back to list'])
    const link = wrapper.get('a')
    expect(link.attributes('href')).toBe('/users/')
    expect(link.attributes('data-pc-name')).toBe('button')
    expect(link.attributes()).not.toHaveProperty('data-inertia-link')
    expect(link.text()).toBe('Back to list')

    page.props = { crudlink: { siteTitle: 'Crudlink', inertiaNavigation: true } }
    expect(
      mountPage(detailProps({ listUrl: '/users/' }))
        .get('a')
        .attributes(),
    ).toHaveProperty('data-inertia-link')
  })
})
