import dataclasses
from typing import Any

from django.db.models import Model
from inertia.utils import InertiaJsonEncoder

from .shared import CamelCaseJSON


class CrudlinkJSONEncoder(InertiaJsonEncoder):
    """Inertia encoder that also knows about dataclasses, and sends model instances as `str(obj)`.

    Crudlink props (`CamelCaseJSON`) go out with camelCase field names, other dataclasses as they are.
    A model instance (e.g. the value of a custom cell) is its `str()`: inertia-django would send
    `model_to_dict()`, every field, a user's password hash included.

    Enable with `INERTIA_JSON_ENCODER = "django_crudlink.json.CrudlinkJSONEncoder"`
    or pass it as a class.
    """

    def default(self, o: Any) -> Any:
        if isinstance(o, CamelCaseJSON):
            return o.to_json()
        if dataclasses.is_dataclass(o) and not isinstance(o, type):
            return {field.name: getattr(o, field.name) for field in dataclasses.fields(o)}
        if isinstance(o, Model):
            return str(o)
        return super().default(o)
