from collections.abc import Callable, Sequence
from enum import StrEnum
from functools import cached_property
from typing import Any

from django.core.paginator import Paginator
from django.db.models import Model, QuerySet
from django.http import HttpRequest, HttpResponse
from django.utils.text import capfirst
from django.views import View
from inertia import defer

from ..helpers.cells import to_plain_value
from ..helpers.columns import DataAttr
from ..shared import ColumnSchema, ListData, ListParam, ListProps, PageComponent, Pagination, RowData
from .base import CrudViewMixin


class ListMode(StrEnum):
    """Who sorts and pages the rows of a list."""

    CLIENT = "client"  # all rows are sent, the frontend sorts and pages them: up to a few thousand rows
    SERVER = "server"  # the database sorts and pages, the table reloads `data` for each page
    SERVER_UNCOUNTED = "server_uncounted"  # SERVER without COUNT(*): the pager only knows if there is a next page

    @property
    def server_side(self) -> bool:
        return self is not ListMode.CLIENT


def _page_number(requested: str | None, num_pages: int | None = None) -> int:
    """Return the requested page: at least 1 and, when the number of pages is known, at most that."""
    try:
        number = max(int(requested or 1), 1)
    except ValueError:
        number = 1
    return number if num_pages is None else min(number, max(num_pages, 1))


def _all_rows(queryset: QuerySet, size: int | None, requested: str | None) -> tuple[list[Model], Pagination]:
    """All rows go to the frontend, the page number is only sent back. Without a size, they are one page."""
    objects = list(queryset)
    size = size or max(len(objects), 1)
    num_pages = -(-len(objects) // size)
    page = _page_number(requested, num_pages)
    return objects, Pagination(page=page, page_size=size, total=len(objects), has_next=page < num_pages)


def _counted_page(queryset: QuerySet, size: int, requested: str | None) -> tuple[list[Model], Pagination]:
    """`SERVER`: one page, counted by Django's paginator."""
    page = Paginator(queryset, size).get_page(requested)
    pagination = Pagination(page=page.number, page_size=size, total=page.paginator.count, has_next=page.has_next())
    return list(page.object_list), pagination


def _uncounted_page(queryset: QuerySet, size: int, requested: str | None) -> tuple[list[Model], Pagination]:
    """`SERVER_UNCOUNTED`: one page without COUNT(*), one extra row tells whether there is a next page."""
    # the slice end, page * size + 1, must fit the database's 64-bit integers
    page = min(_page_number(requested), (2**63 - 2) // size)
    objects = list(queryset[(page - 1) * size : page * size + 1])
    return objects[:size], Pagination(page=page, page_size=size, total=None, has_next=len(objects) > size)


Paginate = Callable[[QuerySet, int, str | None], tuple[list[Model], Pagination]]
_PAGINATE: dict[ListMode, Paginate] = {
    ListMode.CLIENT: _all_rows,
    ListMode.SERVER: _counted_page,
    ListMode.SERVER_UNCOUNTED: _uncounted_page,
}


def _reverse(field: str) -> str:
    """Return the opposite order of an `order_by()` field: `name` <-> `-name`."""
    return field.removeprefix("-") if field.startswith("-") else f"-{field}"


class ListModelView(CrudViewMixin, View):
    """Paginated, sortable list of objects.

    Query params (`ListParam`): `page` - page number, `o` - the column to sort by,
    `-` prefix for descending order, e.g. `?o=-email`.

    The rows come in the deferred `data` prop, loaded right after the first render.
    `list_mode` decides who sorts and pages them, see `ListMode`. With the server
    modes the table reloads `data` for each page (an Inertia partial reload of the same url).
    """

    component = PageComponent.LIST
    list_display: Sequence[str] = ("__str__",)
    ordering: Sequence[str] | None = None
    paginate_by: int | None = 25  # None or 0 - no paging, all rows on one page (in every list_mode)
    list_mode: ListMode | str = ListMode.CLIENT  # a plain string ("server") works too

    def get_list_display(self) -> Sequence[str]:
        return self.list_display

    def get_list_mode(self) -> ListMode:
        return ListMode(self.list_mode)

    @cached_property
    def is_server_side(self) -> bool:
        """The database sorts and pages: a server `ListMode`. Once per request, a view lives for one."""
        return self.get_list_mode().server_side

    def get_data_attrs(self) -> dict[str, DataAttr]:
        return {name: self.get_data_attr(name) for name in self.get_list_display()}

    def get_ordering(self, data_attrs: dict[str, DataAttr], queryset: QuerySet) -> tuple[str | None, list[Any]]:
        """Return (the requested sort key sent back to the page, queryset order_by).

        In the server modes the database sorts by the column's `order_field`. A column without
        one (relations, choices, computed) can't be sorted there, so its key is dropped.

        `CLIENT` keeps any listed column as the sort key, the frontend sorts by it. The rows come
        in the base order whatever the sort key. The frontend sort keeps that order for equal
        values, so a page shows the same rows after a click on a column and after a reload.

        The base order: `ordering`, else the queryset's own order (an `order_by()` in
        `get_queryset()`, or the model's `Meta.ordering`).
        """
        key = self.request.GET.get(ListParam.ORDERING, "")
        attr = data_attrs.get(key.removeprefix("-"))
        field = attr.order_field if attr is not None and self.is_server_side else None
        if attr is None or (self.is_server_side and field is None):
            key = ""
        if field is not None:
            order_by: list[Any] = [_reverse(field) if key.startswith("-") else field]
        else:
            query = queryset.query
            default = query.get_meta().ordering if query.default_ordering else ()
            order_by = list(self.ordering or query.order_by or default)
        # a fixed order for pages and equal values; every Django model has a pk
        if "pk" not in order_by and "-pk" not in order_by:
            order_by.append("-pk" if not order_by else "pk")
        return key or None, order_by

    def get_rows(self, objects: Sequence[Model], data_attrs: dict[str, DataAttr]) -> list[RowData]:
        rows = []
        for obj in objects:
            values = {name: attr.get_value(obj) for name, attr in data_attrs.items()}
            rows.append(
                RowData(
                    pk=str(obj.pk),
                    cells={name: self.get_cell(obj, data_attrs[name], value) for name, value in values.items()},
                    # the database sorts in the server modes
                    values=None
                    if self.is_server_side
                    else {name: to_plain_value(value) for name, value in values.items()},
                )
            )
        return rows

    def get_title(self) -> str:
        return capfirst(str(self.get_model()._meta.verbose_name_plural))

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        """Filter the rows, e.g. by search and filter params in `self.request.GET`. No-op for now."""
        return queryset

    def paginate(self, queryset: QuerySet) -> tuple[list[Model], Pagination]:
        """Return the rows to send and their pagination, as `list_mode` says."""
        requested = self.request.GET.get(ListParam.PAGE)
        if not self.paginate_by:
            return _all_rows(queryset, None, requested)
        return _PAGINATE[self.get_list_mode()](queryset, self.paginate_by, requested)

    def get_data(self, data_attrs: dict[str, DataAttr]) -> ListData:
        queryset = self.filter_queryset(self.get_queryset())
        ordering, order_by = self.get_ordering(data_attrs, queryset)
        objects, pagination = self.paginate(queryset.order_by(*order_by))
        return ListData(rows=self.get_rows(objects, data_attrs), pagination=pagination, ordering=ordering)

    def get_props(self) -> ListProps:
        data_attrs = self.get_data_attrs()
        return ListProps(
            title=self.get_title(),
            columns=[
                ColumnSchema(
                    name=name,
                    label=capfirst(attr.label),
                    # the frontend sorts any column, by its plain value; the database only those with
                    # an order_field, which model fields have when they sort as shown
                    sortable=not self.is_server_side or attr.order_field is not None,
                )
                for name, attr in data_attrs.items()
            ],
            data=defer(lambda: self.get_data(data_attrs)),
            huge_table=self.is_server_side,
        )

    def has_permission(self) -> bool:
        return self.access.has_view_permission(self.request)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return self.render(self.get_props())
