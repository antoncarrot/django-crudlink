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
    const { loading, onChange } = useInertiaListUrl()
    onChange({ page: 1, ordering: '-name' })
    expect(loading.value).toBe(false)
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

  it('reloads data for a huge table, loading until the latest reload finishes', () => {
    const { loading, onChange } = useInertiaListUrl(() => true)
    onChange({ page: 2, ordering: null })
    expect(router.replace).not.toHaveBeenCalled()
    expect(router.get).toHaveBeenCalledWith(
      '/users/?keep=1&page=2',
      {},
      expect.objectContaining({ only: ['data'], replace: true, preserveState: true, preserveScroll: true }),
    )
    expect(loading.value).toBe(true)
    const onFinish = () => {
      const options = vi.mocked(router.get).mock.lastCall?.[2] as { onFinish: () => void }
      return options.onFinish
    }
    const first = onFinish()
    onChange({ page: 3, ordering: null })
    const latest = onFinish()

    first() // interrupted by the newer reload
    expect(loading.value).toBe(true)
    latest() // done, failed, or interrupted by another visit on the page
    expect(loading.value).toBe(false)
  })
})
