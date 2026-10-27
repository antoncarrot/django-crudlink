"""Names of frontend components. Mirrored in `frontend/src/shared/components.ts`.

Values are sent to the frontend as plain strings (`StrEnum`).
"""

from enum import StrEnum


class CellComponent(StrEnum):
    """Built-in cells of list columns, see `Cell` constructors for their props."""

    TEXT = "text"
    BOOL = "bool"
    TAGS = "tags"


class PageComponent(StrEnum):
    """Inertia page components, equal to `frontend/src/pages/<name>.vue` file names."""

    LIST = "BaseListPage"
