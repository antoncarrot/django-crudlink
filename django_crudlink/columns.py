"""`@column`: describe a computed list column."""

import functools
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypeVar

from django.utils.functional import Promise, cached_property

if TYPE_CHECKING:
    # only for annotations: `import django_crudlink` doesn't load the shared props and inertia
    from .shared import CellComponent

F = TypeVar("F", bound=Callable[..., Any])

# the function attribute `@column` keeps its `ColumnMeta` in
COLUMN_ATTR = "crudlink_column"


@dataclass(frozen=True)
class ColumnMeta:
    label: str | Promise | None = None
    order_field: str | None = None
    component: "CellComponent | str | None" = None


def column(
    label: str | Promise | None = None,
    order_field: str | None = None,
    component: "CellComponent | str | None" = None,
) -> Callable[[F], F]:
    """Describe a computed column.

    Example::

        from django.utils.translation import gettext_lazy as _

        @column(label=_("Full name"), order_field="last_name")
        def full_name(self, user):
            return user.get_full_name()

    Methods and properties of the view are columns only with `@column`, so its other attributes
    never clash with column names. A method is called as `method(obj)`, a property gives the same
    value in every row. Model methods and properties (cached ones too) need no decorator.

    Use `gettext_lazy` for labels: they are translated per request. Plain
    `gettext` runs once at import and is stuck in the startup language.

    `order_field` is what the server list modes sort the column by in the database.

    `component` renders the value with another frontend cell, which gets `{"value": value}`
    as props: the plain value the frontend sorts by (a list stays a list of them). An empty
    value (`None`, `""`) is the view's `empty_value_display` in a text cell instead.
    """

    def decorator(func: F) -> F:
        setattr(func, COLUMN_ATTR, ColumnMeta(label=label, order_field=order_field, component=component))
        return func

    return decorator


def unwrap(attr: Any) -> Any:
    """Return the function behind a property or a cached property, other attributes as they are."""
    if isinstance(attr, property):
        return attr.fget
    if isinstance(attr, cached_property):
        return attr.real_func
    if isinstance(attr, functools.cached_property):
        return attr.func
    return attr


def get_column(attr: Any) -> ColumnMeta | None:
    """Return the `@column` of a method, property or cached property, None if it has none."""
    return getattr(unwrap(attr), COLUMN_ATTR, None)
