from collections.abc import Sequence
from typing import Any

from django.db.models import Model
from django.http import HttpRequest, HttpResponse
from django.utils.text import capfirst
from django.views import View

from ..helpers.columns import DataAttr
from ..layout import Layout
from ..shared import DetailField, DetailProps, PageComponent
from .base import CrudViewMixin


class DetailModelView(CrudViewMixin, View):
    """The fields of one object, by the `pk` url kwarg, arranged by `layout`.

    Fields are taken from `fields` or `layout`, in that order, else all model fields.
    """

    component = PageComponent.DETAIL
    # None - all model fields, except auto created. Names are resolved like
    # list columns: model field, `@column` method of the view, model attribute.
    fields: Sequence[str] | None = None
    layout: Layout | None = None  # None - the fields stacked in order
    object: Model  # set for the handlers; None in has_permission() when the pk isn't found

    def get_page_object(self) -> Model:
        return self.get_object()

    def has_permission(self) -> bool:
        return self.access.has_view_permission(self.request, self.object)

    def get_fields(self) -> list[DataAttr]:
        names = self.fields
        if names is None and self.layout is not None:
            names = self.layout.field_names()
        if names is None:
            opts = self.get_model()._meta
            names = [field.name for field in [*opts.fields, *opts.many_to_many] if not field.auto_created]
        return [self.get_data_attr(name) for name in names]

    def get_object_data(self, obj: Model) -> dict[str, DetailField]:
        return {
            attr.name: DetailField(label=capfirst(attr.label), cell=self.get_cell(obj, attr, attr.get_value(obj)))
            for attr in self.get_fields()
        }

    def get_layout(self, fields: dict[str, DetailField]) -> Layout:
        return self.layout or Layout(*fields)

    def get_title(self, obj: Model) -> str:
        return str(obj)

    def get_props(self, obj: Model) -> DetailProps:
        fields = self.get_object_data(obj)
        return DetailProps(
            title=self.get_title(obj),
            fields=fields,
            layout=self.get_layout(fields).serialize(),
            list_url=self.reverse("list"),
        )

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return self.render(self.get_props(self.object))
