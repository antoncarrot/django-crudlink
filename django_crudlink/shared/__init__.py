"""Contract between backend and frontend: page props.

Everything here has a TypeScript twin in `frontend/src/shared/`, kept in sync
by `tests/test_shared.py`.
"""

from .props import CamelCaseJSON, CrudlinkSharedProps

__all__ = ("CamelCaseJSON", "CrudlinkSharedProps")
