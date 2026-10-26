"""Props sent to the frontend pages. Mirrored in `frontend/src/shared/props.ts`."""

import dataclasses
import functools
from dataclasses import dataclass
from typing import Any


def to_camel(name: str) -> str:
    """Return the camelCase form of a snake_case name: `site_title` -> `siteTitle`."""
    first, *rest = name.split("_")
    return first + "".join(word.capitalize() for word in rest)


@functools.cache
def _json_names(cls: type) -> tuple[tuple[str, str], ...]:
    return tuple((field.name, to_camel(field.name)) for field in dataclasses.fields(cls))


class CamelCaseJSON:
    """Base of the dataclasses sent to the frontend: field names go out in camelCase (`site_title` -> `siteTitle`).

    Only the field names: dict keys are data and stay as they are.
    """

    def to_json(self) -> dict[str, Any]:
        return {json_name: getattr(self, name) for name, json_name in _json_names(type(self))}


# Every page


@dataclass
class CrudlinkSharedProps(CamelCaseJSON):
    """The `crudlink` prop every Inertia page gets (`CrudlinkMiddleware.get_shared_props`)."""

    site_title: str
