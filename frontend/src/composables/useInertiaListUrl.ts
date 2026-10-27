import { router } from '@inertiajs/vue3'

import { type ListData, ListParam } from '../shared'
import type { ListState } from '../types'

export interface InertiaListUrl {
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
 * All rows are here: an Inertia client-side visit (no request) changes the url and the state in
 * `data`. The deferred `data` is not loaded again: it is already in the page.
 */
export function useInertiaListUrl(): InertiaListUrl {
  function onChange(state: ListState): void {
    // Memory: Inertia keeps the page, with all rows, in `history.state`. Each replace copies it
    // again (and so does each scroll position save), one copy per history entry. Fine for the
    // few thousand rows this mode is meant for.
    router.replace({
      url: listUrl(state),
      preserveState: true,
      preserveScroll: true,
      props: (props) => {
        const data = props.data as ListData | undefined
        if (!data) return props
        const pagination = { ...data.pagination, page: state.page }
        return { ...props, data: { ...data, ordering: state.ordering, pagination } }
      },
    })
  }

  return { onChange }
}
