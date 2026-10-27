from collections.abc import Sequence
from typing import Any

from django.db.models import Model, QuerySet
from django.http import HttpRequest, HttpResponse
from django.utils.text import capfirst
from django.views import View
from inertia import defer

from ..helpers.cells import to_plain_value
from ..helpers.columns import DataAttr
from ..shared import ColumnSchema, ListData, ListParam, ListProps, PageComponent, Pagination, RowData
from .base import CrudViewMixin


def _page_number(requested: str | None, num_pages: int) -> int:
    """Return the requested page: at least 1 and at most the number of pages."""
    try:
        number = max(int(requested or 1), 1)
    except ValueError:
        number = 1
    return min(number, max(num_pages, 1))


def _all_rows(queryset: QuerySet, size: int | None, requested: str | None) -> tuple[list[Model], Pagination]:
    """All rows go to the frontend, the page number is only sent back. Without a size, they are one page."""
    objects = list(queryset)
    size = size or max(len(objects), 1)
    num_pages = -(-len(objects) // size)
    page = _page_number(requested, num_pages)
    return objects, Pagination(page=page, page_size=size, total=len(objects), has_next=page < num_pages)


class ListModelView(CrudViewMixin, View):
    """Paginated, sortable list of objects.

    Query params (`ListParam`): `page` - page number, `o` - the column to sort by,
    `-` prefix for descending order, e.g. `?o=-email`.

    The rows come in the deferred `data` prop, loaded right after the first render.
    All rows are sent, the frontend sorts and pages them: the requested page and
    sort column are only sent back.
    """

    component = PageComponent.LIST
    list_display: Sequence[str] = ("__str__",)
    ordering: Sequence[str] | None = None
    paginate_by: int | None = 25  # None or 0 - no paging, all rows on one page

    def get_list_display(self) -> Sequence[str]:
        return self.list_display

    def get_data_attrs(self) -> dict[str, DataAttr]:
        return {name: self.get_data_attr(name) for name in self.get_list_display()}

    def get_ordering(self, data_attrs: dict[str, DataAttr], queryset: QuerySet) -> tuple[str | None, list[Any]]:
        """Return (the requested sort key sent back to the page, queryset order_by).

        Any listed column is kept as the sort key, the frontend sorts by it. A column with
        an `order_field` is sorted by the database too. Without one, or without a sort column:
        `ordering`, else the queryset's own order (an `order_by()` in `get_queryset()`, or the
        model's `Meta.ordering`).
        """
        key = self.request.GET.get(ListParam.ORDERING, "")
        attr = data_attrs.get(key.removeprefix("-")) if key else None
        order_by: list[Any] = []
        if attr is None:
            key = ""
        elif attr.order_field is not None:
            field = attr.order_field
            if key.startswith("-"):
                field = field.removeprefix("-") if field.startswith("-") else f"-{field}"
            order_by.append(field)
        if not order_by:
            query = queryset.query
            default = query.get_meta().ordering if query.default_ordering else ()
            order_by = list(self.ordering or query.order_by or default)
        # stable order for pagination; every Django model has a pk
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
                    values={name: to_plain_value(value) for name, value in values.items()},
                )
            )
        return rows

    def get_title(self) -> str:
        return capfirst(str(self.get_model()._meta.verbose_name_plural))

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        """Filter the rows, e.g. by search and filter params in `self.request.GET`. No-op for now."""
        return queryset

    def paginate(self, queryset: QuerySet) -> tuple[list[Model], Pagination]:
        """Return the rows to send and their pagination."""
        return _all_rows(queryset, self.paginate_by, self.request.GET.get(ListParam.PAGE))

    def get_data(self, data_attrs: dict[str, DataAttr]) -> ListData:
        queryset = self.filter_queryset(self.get_queryset())
        ordering, order_by = self.get_ordering(data_attrs, queryset)
        objects, pagination = self.paginate(queryset.order_by(*order_by))
        return ListData(rows=self.get_rows(objects, data_attrs), pagination=pagination, ordering=ordering)

    def get_props(self) -> ListProps:
        data_attrs = self.get_data_attrs()
        return ListProps(
            title=self.get_title(),
            # the frontend sorts any column, by its plain value
            columns=[
                ColumnSchema(name=name, label=capfirst(attr.label), sortable=True) for name, attr in data_attrs.items()
            ],
            data=defer(lambda: self.get_data(data_attrs)),
        )

    def has_permission(self) -> bool:
        return self.access.has_view_permission(self.request)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return self.render(self.get_props())
