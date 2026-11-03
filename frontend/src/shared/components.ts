// Names of frontend components. Mirrors django_crudlink/shared/components.py,
// kept in sync by django_crudlink/tests/test_shared.py.

/** Built-in cells of list columns and detail fields. */
export const CellComponent = {
  Text: 'text',
  Link: 'link',
  Bool: 'bool',
  Tags: 'tags',
} as const
export type CellComponentName = (typeof CellComponent)[keyof typeof CellComponent]

/** Layout node types of form and detail pages (`LayoutNode.type`). */
export const LayoutType = {
  Layout: 'layout',
  Row: 'row',
  Column: 'column',
  Fieldset: 'fieldset',
  Field: 'field',
} as const
export type LayoutTypeName = (typeof LayoutType)[keyof typeof LayoutType]

/** Inertia page components, equal to pages/<name>.vue file names. */
export const PageComponent = {
  List: 'BaseListPage',
  Detail: 'BaseDetailPage',
} as const
export type PageComponentName = (typeof PageComponent)[keyof typeof PageComponent]
