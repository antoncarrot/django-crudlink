"""Python and TypeScript sides of the shared contract must stay in sync."""

import dataclasses
import json
import re
from pathlib import Path

from django.contrib.auth.models import User
from django.test import SimpleTestCase

from django_crudlink.json import CrudlinkJSONEncoder
from django_crudlink.shared import CamelCaseJSON
from django_crudlink.shared import props as props_module
from django_crudlink.shared.props import to_camel

FRONTEND = Path(__file__).resolve().parents[2] / "frontend" / "src"


def ts_interface_fields() -> dict[str, set[str]]:
    """Field names of each `export interface <Name> { ... }` in shared/props.ts."""
    source = (FRONTEND / "shared" / "props.ts").read_text()
    return {
        name: set(re.findall(r"^  (\w+)\??:", body, re.MULTILINE))
        for name, body in re.findall(r"export interface (\w+) \{\n(.*?)\n\}", source, re.DOTALL)
    }


class SharedPropsTest(SimpleTestCase):
    def test_props_match_typescript(self) -> None:
        interfaces = ts_interface_fields()
        classes = [
            obj
            for obj in vars(props_module).values()
            if dataclasses.is_dataclass(obj) and obj.__module__ == props_module.__name__
        ]
        self.assertTrue(classes)
        for cls in classes:
            with self.subTest(cls=cls.__name__):
                self.assertTrue(issubclass(cls, CamelCaseJSON))
                self.assertIn(cls.__name__, interfaces, f"{cls.__name__} is missing in shared/props.ts")
                self.assertEqual({to_camel(field.name) for field in dataclasses.fields(cls)}, interfaces[cls.__name__])

    def test_model_is_its_str(self) -> None:
        # not inertia-django's model_to_dict(): every field, the password hash too
        user = User(username="bob", password="pbkdf2_sha256$hash")  # noqa: S106 - a fake hash
        self.assertEqual(json.loads(json.dumps({"value": user}, cls=CrudlinkJSONEncoder)), {"value": "bob"})
