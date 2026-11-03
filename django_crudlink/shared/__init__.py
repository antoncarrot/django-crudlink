"""Contract between backend and frontend: page props, component names and url params.

Everything here has a TypeScript twin in `frontend/src/shared/`, kept in sync
by `tests/test_shared.py`.
"""

from .components import CellComponent, LayoutType, PageComponent
from .params import ListParam
from .props import (
    CamelCaseJSON,
    Cell,
    ColumnSchema,
    CrudlinkSharedProps,
    DetailField,
    DetailProps,
    LayoutNode,
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
    "DetailField",
    "DetailProps",
    "LayoutNode",
    "LayoutType",
    "ListData",
    "ListParam",
    "ListProps",
    "PageComponent",
    "Pagination",
    "PlainValue",
    "RowData",
)
