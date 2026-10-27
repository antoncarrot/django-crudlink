// Page props. Mirrors django_crudlink/shared/props.py: the Python dataclass fields in camelCase (`CamelCaseJSON`).

import type { CellComponentName } from './components'

/** Built-in name, or a custom one. */
type CustomName = string & {}

// Cells

export interface Cell {
  component: CellComponentName | CustomName
  props: Record<string, unknown>
}

// List

export interface ColumnSchema {
  name: string
  label: string
  sortable: boolean
}

export type PlainValue = string | number | boolean | null

export interface RowData {
  pk: string
  cells: Record<string, Cell>
  /** Column name -> plain value the frontend sorts (and later filters) by. */
  values: Record<string, PlainValue>
}

export interface Pagination {
  page: number
  pageSize: number
  total: number
  hasNext: boolean
}

/** Table data: the deferred `data` prop of the list page. */
export interface ListData {
  rows: RowData[]
  pagination: Pagination
  /** Column name, "-" prefix for descending. */
  ordering: string | null
}

export interface ListProps {
  title: string
  columns: ColumnSchema[]
  /** Deferred: undefined until Inertia loads it, right after the first render. */
  data?: ListData
}

// Every page

/** The `crudlink` prop every Inertia page gets (`CrudlinkMiddleware.get_shared_props`). */
export interface CrudlinkSharedProps {
  siteTitle: string
}
