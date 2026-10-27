// Frontend-only types. Types shared with the backend are in ./shared.

import type { ListProps } from './shared'

/** Table state: the page and the sort column (`-` prefix for descending), kept in the url as `?page=2&o=-name`. */
export interface ListState {
  page: number
  ordering: string | null
}

/** Props of the `BaseList` table: the list page props without the page chrome. */
export interface BaseListProps extends Pick<ListProps, 'columns' | 'data'> {}
