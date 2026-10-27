"""Contract between backend and frontend: page props, component names and url params.

Everything here has a TypeScript twin in `frontend/src/shared/`, kept in sync
by `tests/test_shared.py`.
"""

from .components import CellComponent, PageComponent
from .params import ListParam
from .props import (
    CamelCaseJSON,
    Cell,
    ColumnSchema,
    CrudlinkSharedProps,
    ListData,
    ListProps,
    Pagination,
    PlainValue,
    RowData,
)

__all__ = (
    "CamelCaseJSON",
    "Cell",
    "CellComponent",
    "ColumnSchema",
    "CrudlinkSharedProps",
    "ListData",
    "ListParam",
    "ListProps",
    "PageComponent",
    "Pagination",
    "PlainValue",
    "RowData",
)
