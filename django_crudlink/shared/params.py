"""Query params of crudlink urls. Mirrored in `frontend/src/shared/params.ts`."""

from enum import StrEnum


class ListParam(StrEnum):
    """List page url params, read by `ListModelView`."""

    PAGE = "page"
    ORDERING = "o"  # column name, "-" prefix for descending
