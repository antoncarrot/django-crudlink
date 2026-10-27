"""Turn column values into frontend cells (display) and plain values (frontend sorting)."""

import datetime
import decimal
from typing import Any

from django.utils import formats, timezone

from ..shared import Cell, PlainValue


def is_empty(value: Any) -> bool:
    """Whether a value is shown as the empty value display: `None` and `""`."""
    return value is None or value == ""


def to_text(value: Any, empty: str) -> str:
    """Localized text of a value, `empty` for `None` and `""`."""
    if is_empty(value):
        return empty
    if isinstance(value, datetime.datetime) and timezone.is_aware(value):
        value = timezone.localtime(value)
    if isinstance(value, (datetime.date, datetime.time, decimal.Decimal, float)):
        return str(formats.localize(value))
    return str(value)


def to_cell(value: Any, empty: str) -> Cell:
    """Choose a built-in cell for a value. Related objects are their text, lists of them tags."""
    if isinstance(value, bool):
        return Cell.boolean(value)
    if isinstance(value, (list, tuple)):
        return Cell.tags([str(item) for item in value])
    return Cell.text(to_text(value, empty))


def to_plain_value(value: Any) -> PlainValue:
    """Plain value of a column (`RowData.values`), the frontend sorts (and will filter) by it.

    Unlike `to_cell()` (display: localized text), it keeps the types, so the sort is
    right: numbers stay numbers, dates are ISO strings, `None` stays `None`.
    """
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, decimal.Decimal):
        return float(value)
    if isinstance(value, datetime.datetime) and timezone.is_aware(value):
        value = timezone.localtime(value)
    if isinstance(value, (datetime.date, datetime.time)):
        return value.isoformat()
    if isinstance(value, (list, tuple)):
        return ", ".join(str(item) for item in value)
    return str(value)


def to_cell_value(value: Any) -> PlainValue | list[PlainValue]:
    """Return the `value` prop of a custom cell: the plain value the frontend sorts by, a list stays a list of them."""
    if isinstance(value, (list, tuple)):
        return [to_plain_value(item) for item in value]
    return to_plain_value(value)
