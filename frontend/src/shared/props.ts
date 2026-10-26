// Page props. Mirrors django_crudlink/shared/props.py: the Python dataclass fields in camelCase (`CamelCaseJSON`).

// Every page

/** The `crudlink` prop every Inertia page gets (`CrudlinkMiddleware.get_shared_props`). */
export interface CrudlinkSharedProps {
  siteTitle: string
}
