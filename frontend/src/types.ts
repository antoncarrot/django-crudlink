// Frontend-only types. Types shared with the backend are in ./shared.

import type { DetailProps, ListProps } from './shared'

/** Table state: the page and the sort column (`-` prefix for descending), kept in the url as `?page=2&o=-name`. */
export interface ListState {
  page: number
  ordering: string | null
}

/** Props of the `BaseList` table: the list page props without the page chrome. */
export interface BaseListProps extends Pick<ListProps, 'columns' | 'data'> {
  /** The backend sorts and pages (`ListProps.hugeTable`). Default false. */
  isHugeTable?: boolean
  /** A reload of `data` is running (huge table). */
  isLoading?: boolean
}

/** Props of the `BaseDetail` field list: the detail page props without the page chrome. */
export interface BaseDetailProps extends Pick<DetailProps, 'fields' | 'layout'> {}
