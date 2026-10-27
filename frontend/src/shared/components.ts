// Names of frontend components. Mirrors django_crudlink/shared/components.py,
// kept in sync by django_crudlink/tests/test_shared.py.

/** Built-in cells of list columns. */
export const CellComponent = {
  Text: 'text',
  Bool: 'bool',
  Tags: 'tags',
} as const
export type CellComponentName = (typeof CellComponent)[keyof typeof CellComponent]

/** Inertia page components, equal to pages/<name>.vue file names. */
export const PageComponent = {
  List: 'BaseListPage',
} as const
export type PageComponentName = (typeof PageComponent)[keyof typeof PageComponent]
