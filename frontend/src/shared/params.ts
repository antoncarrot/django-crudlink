// Query params of crudlink urls. Mirrors django_crudlink/shared/params.py,
// kept in sync by django_crudlink/tests/test_shared.py.

/** List page url params, read by `ListModelView`. */
export const ListParam = {
  Page: 'page',
  /** Column name, "-" prefix for descending. */
  Ordering: 'o',
} as const
