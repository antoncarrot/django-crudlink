"""Layout of form and detail pages: rows, columns and fieldsets of fields.

Example::

    layout = Layout(
        Row("username", "email"),
        Row(Span("first_name", cols=2), "last_name"),
        Fieldset("Permissions", Row("is_active", "is_staff"), "groups"),
    )

`cols` is a relative width of an element inside a `Row`.
"""

from dataclasses import dataclass
from typing import Union

from .shared import LayoutNode, LayoutType


@dataclass
class Span:
    field: str
    cols: int = 1

    def serialize(self) -> LayoutNode:
        return LayoutNode(type=LayoutType.FIELD, cols=self.cols, field=self.field)

    def field_names(self) -> list[str]:
        return [self.field]


Element = Union[str, Span, "Row", "Column", "Fieldset"]


def _wrap(element: Element) -> "Span | Row | Column | Fieldset":
    if isinstance(element, str):
        return Span(element)
    # a mistake (e.g. a tuple of names for a row) fails here, where the layout is defined, not on every request
    if not isinstance(element, (Span, _Container)):
        raise TypeError(f"A layout element is a field name, Span, Row, Column or Fieldset, not {element!r}.")
    return element


class _Container:
    layout_type: LayoutType  # sent as LayoutNode.type: which element the frontend renders

    def __init__(self, *elements: Element, cols: int = 1, label: str | None = None) -> None:
        self.elements = [_wrap(element) for element in elements]
        self.cols = cols
        self.label = label

    def serialize(self) -> LayoutNode:
        return LayoutNode(
            type=self.layout_type,
            cols=self.cols,
            label=self.label,
            children=[element.serialize() for element in self.elements],
        )

    def field_names(self) -> list[str]:
        return [name for element in self.elements for name in element.field_names()]


class Layout(_Container):
    layout_type = LayoutType.LAYOUT


class Row(_Container):
    layout_type = LayoutType.ROW


class Column(_Container):
    layout_type = LayoutType.COLUMN


class Fieldset(_Container):
    layout_type = LayoutType.FIELDSET

    def __init__(self, label: str, *elements: Element, cols: int = 1) -> None:
        if isinstance(label, (Span, _Container)):
            raise TypeError(f"The first argument of a Fieldset is its label, not {label!r}.")
        super().__init__(*elements, cols=cols, label=label)
