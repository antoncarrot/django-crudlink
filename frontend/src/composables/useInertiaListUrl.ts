import { router } from '@inertiajs/vue3'
import { type MaybeRefOrGetter, type Ref, ref, toValue } from 'vue'

import { type ListData, ListParam } from '../shared'
import type { ListState } from '../types'

export interface InertiaListUrl {
  /** A reload of `data` is running (huge table). */
  loading: Ref<boolean>
  /** Handler of the `BaseList` `change` event. */
  onChange: (state: ListState) => void
}

/** Current url with the table state, other query params are kept. */
function listUrl(state: ListState): string {
  const url = new URL(window.location.href)
  url.searchParams.delete(ListParam.Page)
  url.searchParams.delete(ListParam.Ordering)
  if (state.page > 1) url.searchParams.set(ListParam.Page, String(state.page))
  if (state.ordering) url.searchParams.set(ListParam.Ordering, state.ordering)
  return url.pathname + url.search
}

/**
 * Keep the url and the `data` prop of an Inertia list page (`ListModelView`) in step with the
 * `BaseList` table state, so a reload or browser back/forward shows the same view.
 *
 * - Huge table: the backend sorts and pages, so `data` is reloaded from the new url
 *   (an Inertia partial reload).
 * - Otherwise all rows are here: an Inertia client-side visit (no request) changes the url and
 *   the state in `data`. The deferred `data` is not loaded again: it is already in the page.
 */
export function useInertiaListUrl(hugeTable: MaybeRefOrGetter<boolean> = false): InertiaListUrl {
  const loading = ref(false)
  /** Id of the last reload started here. */
  let latest = 0

  function onChange(state: ListState): void {
    const url = listUrl(state)
    if (!toValue(hugeTable)) {
      // Memory: Inertia keeps the page, with all rows, in `history.state`. Each replace copies it
      // again (and so does each scroll position save), one copy per history entry. Fine for the
      // few thousand rows this mode is meant for; a huge table keeps only one page there.
      router.replace({
        url,
        preserveState: true,
        preserveScroll: true,
        props: (props) => {
          const data = props.data as ListData | undefined
          if (!data) return props
          const pagination = { ...data.pagination, page: state.page }
          return { ...props, data: { ...data, ordering: state.ordering, pagination } }
        },
      })
      return
    }
    // before router.get(): it interrupts the previous reload, which then finishes with an older id
    const visit = ++latest
    loading.value = true
    router.get(
      url,
      {},
      {
        only: ['data'],
        replace: true,
        preserveState: true,
        preserveScroll: true,
        // a newer reload of ours keeps loading; otherwise this one ends it, whether it loaded the data,
        // failed, or another visit on the page interrupted it
        onFinish: () => {
          if (visit === latest) loading.value = false
        },
      },
    )
  }

  return { loading, onChange }
}
