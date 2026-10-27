"""Resolve `list_display` names into value getters.

A name is looked up in order:
1. model field
2. model attribute or method
"""

from typing import Any, Protocol

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Field, Model
from django.forms.utils import pretty_name


class DataAttr(Protocol):
    name: str
    label: str
    order_field: str | None

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

    def get_value(self, obj: Model) -> Any:
        if self.field.many_to_many:
            return list(getattr(obj, self.name).all())
        if self.field.choices:
            return getattr(obj, f"get_{self.field.name}_display")()
        return getattr(obj, self.name)


class ModelAttr:
    """Model attribute or method (called without arguments)."""

    def __init__(self, model: type[Model], name: str, label: str | None = None) -> None:
        self.name = name
        self.label = str(label or pretty_name(name))
        self.order_field: str | None = None

    def get_value(self, obj: Model) -> Any:
        value = getattr(obj, self.name)
        return value() if callable(value) else value


def get_data_attr(model: type[Model], name: str) -> DataAttr:
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
    if hasattr(model, name):
        return ModelAttr(model, name)
    raise AttributeError(f"Unable to lookup '{name}' on {opts.object_name}")
