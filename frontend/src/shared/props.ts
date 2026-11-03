// Page props. Mirrors django_crudlink/shared/props.py: the Python dataclass fields in camelCase (`CamelCaseJSON`).

import type { CellComponentName, LayoutTypeName } from './components'

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
  /** Column name -> plain value the frontend sorts (and later filters) by; null when the backend does it. */
  values: Record<string, PlainValue> | null
}

export interface Pagination {
  page: number
  pageSize: number
  /** null when the rows are not counted (`ListMode.SERVER_UNCOUNTED`). */
  total: number | null
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
  /**
   * false - all rows are sent, the frontend sorts and pages; true - the backend does (a server `ListMode`),
   * the table reloads `data`.
   */
  hugeTable: boolean
}

// Layout of form and detail pages

/** Serialized layout element. */
export interface LayoutNode {
  type: LayoutTypeName
  /** Relative width inside a row. */
  cols: number
  /** Fieldset legend. */
  label: string | null
  /** Field name of a `field` node. */
  field: string | null
  children: LayoutNode[]
}

// Detail

export interface DetailField {
  label: string
  cell: Cell
}

export interface DetailProps {
  title: string
  /** Field name -> field, arranged by `layout`. */
  fields: Record<string, DetailField>
  layout: LayoutNode
  listUrl: string | null
}

// Every page

/** The `crudlink` prop every Inertia page gets (`CrudlinkMiddleware.get_shared_props`). */
export interface CrudlinkSharedProps {
  siteTitle: string
}
