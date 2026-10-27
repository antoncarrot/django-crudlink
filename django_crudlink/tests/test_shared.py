"""Python and TypeScript sides of the shared contract must stay in sync."""

import dataclasses
import json
import re
from pathlib import Path
from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from django.test import SimpleTestCase

from django_crudlink.json import CrudlinkJSONEncoder
from django_crudlink.shared import CamelCaseJSON, Cell, CellComponent, ListParam, PageComponent, RowData
from django_crudlink.shared import props as props_module
from django_crudlink.shared.props import to_camel

if TYPE_CHECKING:
    from enum import StrEnum

FRONTEND = Path(__file__).resolve().parents[2] / "frontend" / "src"


def ts_const_values(name: str, module: str = "components") -> set[str]:
    """Values of `export const <name> = { Key: 'value', ... } as const` in shared/<module>.ts."""
    source = (FRONTEND / "shared" / f"{module}.ts").read_text()
    block = re.search(rf"export const {name} = \{{(.*?)\}} as const", source, re.DOTALL)
    assert block is not None, f"{name} is missing in shared/{module}.ts"
    return set(re.findall(r":\s*'([^']+)'", block.group(1)))


def ts_interface_fields() -> dict[str, set[str]]:
    """Field names of each `export interface <Name> { ... }` in shared/props.ts."""
    source = (FRONTEND / "shared" / "props.ts").read_text()
    return {
        name: set(re.findall(r"^  (\w+)\??:", body, re.MULTILINE))
        for name, body in re.findall(r"export interface (\w+) \{\n(.*?)\n\}", source, re.DOTALL)
    }


class SharedComponentsTest(SimpleTestCase):
    def test_enums_match_typescript(self) -> None:
        enums: list[type[StrEnum]] = [CellComponent, PageComponent]
        for enum in enums:
            with self.subTest(enum=enum.__name__):
                self.assertEqual(ts_const_values(enum.__name__), {member.value for member in enum})

    def test_params_match_typescript(self) -> None:
        self.assertEqual(ts_const_values("ListParam", "params"), {member.value for member in ListParam})


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

    def test_only_field_names_are_camel_case(self) -> None:
        # dict keys are data: column names here, they must match `ColumnSchema.name`
        row = RowData(pk="1", cells={"full_name": Cell.text("Bob")}, values={"full_name": "Bob"})
        self.assertEqual(
            json.loads(json.dumps(row, cls=CrudlinkJSONEncoder)),
            {
                "pk": "1",
                "cells": {"full_name": {"component": "text", "props": {"text": "Bob"}}},
                "values": {"full_name": "Bob"},
            },
        )
        self.assertEqual(to_camel("page_size"), "pageSize")

    def test_model_is_its_str(self) -> None:
        # not inertia-django's model_to_dict(): every field, the password hash too
        user = User(username="bob", password="pbkdf2_sha256$hash")  # noqa: S106 - a fake hash
        self.assertEqual(json.loads(json.dumps({"value": user}, cls=CrudlinkJSONEncoder)), {"value": "bob"})
