"""Names of frontend components. Mirrored in `frontend/src/shared/components.ts`.

Values are sent to the frontend as plain strings (`StrEnum`). Custom cells registered
on the frontend (`createCrudlinkApp({ cells })`) are used by their string name too.
"""

from enum import StrEnum


class CellComponent(StrEnum):
    """Built-in cells of list columns and detail fields, see `Cell` constructors for their props."""

    TEXT = "text"
    LINK = "link"
    BOOL = "bool"
    TAGS = "tags"


class LayoutType(StrEnum):
    """Layout node types of form and detail pages (`LayoutNode.type`)."""

    LAYOUT = "layout"
    ROW = "row"
    COLUMN = "column"
    FIELDSET = "fieldset"
    FIELD = "field"


class PageComponent(StrEnum):
    """Inertia page components, equal to `frontend/src/pages/<name>.vue` file names."""

    LIST = "BaseListPage"
    DETAIL = "BaseDetailPage"
