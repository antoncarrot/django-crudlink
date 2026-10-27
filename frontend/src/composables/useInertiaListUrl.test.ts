import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { ListData } from '../shared'
import { router } from '../testing/inertia'
import { useInertiaListUrl } from './useInertiaListUrl'

vi.mock('@inertiajs/vue3', () => import('../testing/inertia'))

describe('useInertiaListUrl', () => {
  beforeEach(() => {
    window.history.replaceState(null, '', '/users/?keep=1&page=3')
  })

  it('changes the url and the state in data, without a request', () => {
    const { onChange } = useInertiaListUrl()
    onChange({ page: 1, ordering: '-name' })
    expect(router.get).not.toHaveBeenCalled()
    const options = vi.mocked(router.replace).mock.lastCall?.[0] as {
      url: string
      props: (props: Record<string, unknown>) => Record<string, unknown>
    }
    // other query params are kept, page 1 is left out
    expect(options).toMatchObject({ url: '/users/?keep=1&o=-name', preserveState: true, preserveScroll: true })

    const data: ListData = { rows: [], pagination: { page: 3, pageSize: 25, total: 80, hasNext: true }, ordering: null }
    expect(options.props({ title: 'Users', data })).toEqual({
      title: 'Users',
      data: { rows: [], pagination: { page: 1, pageSize: 25, total: 80, hasNext: true }, ordering: '-name' },
    })
    // before the deferred data, the props stay as they are
    expect(options.props({ title: 'Users' })).toEqual({ title: 'Users' })
  })
})
