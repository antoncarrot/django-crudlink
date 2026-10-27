"""Resolve `list_display` names into value getters.

A name is looked up in order:
1. model field
2. `@column` method of the view (called as `method(obj)`) or property
3. model attribute or method
"""

from typing import Any, Protocol

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Field, Model
from django.forms.utils import pretty_name

from ..columns import ColumnMeta, get_column, unwrap
from ..shared import CellComponent


def _get_column_meta(attr: Any) -> ColumnMeta:
    """Return the `@column` of a model attribute, else its admin style `short_description` and `order_field`."""
    func = unwrap(attr)
    return get_column(func) or ColumnMeta(
        label=getattr(func, "short_description", None),
        order_field=getattr(func, "order_field", None),
    )


class DataAttr(Protocol):
    name: str
    label: str
    order_field: str | None
    component: CellComponent | str | None  # a frontend cell for the value, None - a built-in one by its type

    def get_value(self, obj: Model) -> Any: ...


class ModelField:
    """Value of a model field. Choices are displayed, relations returned as objects (lists of them).

    `order_field` is what the server list modes sort by in the database: the field itself when it
    sorts as shown. Relations (shown as their str()) and choices (shown as their labels) have none;
    a computed column can name a field that sorts as shown, e.g. `author__name`.
    """

    def __init__(self, name: str, field: Field) -> None:
        self.name = name
        self.field = field
        self.label = str(field.verbose_name)
        sorts_as_shown = field.concrete and not field.is_relation and not field.choices
        self.order_field: str | None = name if sorts_as_shown else None
        self.component: CellComponent | str | None = None

    def get_value(self, obj: Model) -> Any:
        if self.field.many_to_many:
            return list(getattr(obj, self.name).all())
        if self.field.choices:
            return getattr(obj, f"get_{self.field.name}_display")()
        return getattr(obj, self.name)


class ColumnAttr:
    """Base of the columns that aren't model fields. Without a label, the name is the label."""

    def __init__(self, name: str, label: str | None = None) -> None:
        self.name = name
        self.label = label or pretty_name(name)


class ModelAttr(ColumnAttr):
    """Model attribute or method (called without arguments), described by `@column` or admin style attributes."""

    def __init__(self, model: type[Model], name: str, label: str | None = None) -> None:
        meta = _get_column_meta(getattr(model, name, None))
        # str(): a lazy label is translated per request
        super().__init__(name, label or str(meta.label or ""))
        self.order_field = meta.order_field
        self.component = meta.component

    def get_value(self, obj: Model) -> Any:
        value = getattr(obj, self.name)
        return value() if callable(value) else value


class DataSourceAttr(ColumnAttr):
    """`@column` method or property of a data source outside the model, the view.

    A method is called as `method(obj)`, a property gives the same value in every row.
    """

    def __init__(self, source: object, name: str, meta: ColumnMeta) -> None:
        super().__init__(name, str(meta.label or ""))
        self.source = source
        self.order_field = meta.order_field
        self.component = meta.component

    def get_value(self, obj: Model) -> Any:
        value = getattr(self.source, self.name)
        return value(obj) if callable(value) else value


def get_data_attr(model: type[Model], name: str, sources: list[object]) -> DataAttr:
    opts = model._meta
    if name == "__str__":
        return ModelAttr(model, name, label=str(opts.verbose_name))
    try:
        field = opts.get_field(name)
    except FieldDoesNotExist:
        field = None
    # a reverse relation is not a Field: looked up like any other name
    if isinstance(field, Field):
        return ModelField(name, field)
    for source in sources:
        # looked up on the class: other attributes (e.g. the view's `render`) are not columns
        meta = get_column(getattr(type(source), name, None))
        if meta is not None:
            return DataSourceAttr(source, name, meta)
    if hasattr(model, name):
        return ModelAttr(model, name)
    raise AttributeError(f"Unable to lookup '{name}' on {opts.object_name}")
