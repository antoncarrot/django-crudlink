import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import { Head } from '../testing/inertia'
import CrudPage from './CrudPage.vue'

vi.mock('@inertiajs/vue3', () => import('../testing/inertia'))

describe('CrudPage', () => {
  it('renders the title as the heading and the document title', () => {
    const wrapper = mount(CrudPage, { props: { title: 'Users' } })
    expect(wrapper.get('h1').text()).toBe('Users')
    expect(wrapper.findComponent(Head).vm.$attrs.title).toBe('Users')
  })

  it('renders the actions slot in the header, the content below', () => {
    const wrapper = mount(CrudPage, {
      props: { title: 'Users' },
      slots: { actions: '<button>Add</button>', default: '<p class="content">Table</p>' },
    })
    expect(wrapper.get('.crud-page__actions button').text()).toBe('Add')
    expect(wrapper.get('.crud-page > .content').text()).toBe('Table')
  })
})
