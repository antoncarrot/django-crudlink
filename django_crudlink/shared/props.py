"""Props sent to the frontend pages. Mirrored in `frontend/src/shared/props.ts`."""

import dataclasses
import functools
from dataclasses import dataclass
from typing import Any

from inertia.prop_classes import DeferredProp

from .components import CellComponent


def to_camel(name: str) -> str:
    """Return the camelCase form of a snake_case name: `site_title` -> `siteTitle`."""
    first, *rest = name.split("_")
    return first + "".join(word.capitalize() for word in rest)


@functools.cache
def _json_names(cls: type) -> tuple[tuple[str, str], ...]:
    return tuple((field.name, to_camel(field.name)) for field in dataclasses.fields(cls))


class CamelCaseJSON:
    """Base of the dataclasses sent to the frontend: field names go out in camelCase (`site_title` -> `siteTitle`).

    Only the field names: dict keys are data (column names, cell props) and stay as they are.
    """

    def to_json(self) -> dict[str, Any]:
        return {json_name: getattr(self, name) for name, json_name in _json_names(type(self))}


# Cells


@dataclass
class Cell(CamelCaseJSON):
    """A value rendered by the frontend cell component registered under `component`.

    Use the constructors for built-in cells, they document the props::

        Cell.tags(["staff", "editors"])
    """

    component: CellComponent | str
    props: dict[str, Any]

    @classmethod
    def text(cls, text: str) -> "Cell":
        return cls(CellComponent.TEXT, {"text": text})

    @classmethod
    def tags(cls, items: list[str]) -> "Cell":
        return cls(CellComponent.TAGS, {"items": items})

    @classmethod
    def boolean(cls, value: bool) -> "Cell":  # noqa: FBT001
        return cls(CellComponent.BOOL, {"value": value})


# List


@dataclass
class ColumnSchema(CamelCaseJSON):
    name: str
    label: str
    sortable: bool


PlainValue = str | int | float | bool | None


@dataclass
class RowData(CamelCaseJSON):
    pk: str
    cells: dict[str, Cell]
    values: dict[str, PlainValue]  # column name -> plain value the frontend sorts (and later filters) by


@dataclass
class Pagination(CamelCaseJSON):
    page: int
    page_size: int
    total: int
    has_next: bool


@dataclass
class ListData(CamelCaseJSON):
    """Table data: the deferred `data` prop of the list page."""

    rows: list[RowData]
    pagination: Pagination
    ordering: str | None  # column name, "-" prefix for descending


@dataclass
class ListProps(CamelCaseJSON):
    title: str
    columns: list[ColumnSchema]
    data: ListData | DeferredProp  # deferred: loaded right after the first render


# Every page


@dataclass
class CrudlinkSharedProps(CamelCaseJSON):
    """The `crudlink` prop every Inertia page gets (`CrudlinkMiddleware.get_shared_props`)."""

    site_title: str
