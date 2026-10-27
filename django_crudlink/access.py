"""Which rows of a model a user gets and what they may do with them.

Views ask one `ModelAccess`: `ModelPermissions` of their queryset or model.
"""

from typing import Protocol

from django.db.models import Model, QuerySet
from django.http import HttpRequest

from .helpers.permissions import has_model_perm


class ModelAccess(Protocol):
    def get_queryset(self, request: HttpRequest) -> QuerySet: ...

    def has_add_permission(self, request: HttpRequest) -> bool: ...

    def has_view_permission(self, request: HttpRequest, obj: Model | None = None) -> bool: ...

    def has_change_permission(self, request: HttpRequest, obj: Model | None = None) -> bool: ...

    def has_delete_permission(self, request: HttpRequest, obj: Model | None = None) -> bool: ...


class ModelPermissions:
    """All rows of `queryset` (or of `model`), Django model permissions with object-level backends.

    `model` and `queryset` are class attributes or passed in.
    """

    model: type[Model]
    queryset: QuerySet | None = None

    def __init__(self, model: type[Model] | None = None, queryset: QuerySet | None = None) -> None:
        if model is not None:
            self.model = model
        if queryset is not None:
            self.queryset = queryset

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        # TODO is this method needed?
        if self.queryset is not None:
            return self.queryset.all()
        return self.model._default_manager.all()

    def has_add_permission(self, request: HttpRequest) -> bool:
        return has_model_perm(request.user, self.model, "add")

    def has_view_permission(self, request: HttpRequest, obj: Model | None = None) -> bool:
        return has_model_perm(request.user, self.model, "view", obj) or self.has_change_permission(request, obj)

    def has_change_permission(self, request: HttpRequest, obj: Model | None = None) -> bool:
        return has_model_perm(request.user, self.model, "change", obj)

    def has_delete_permission(self, request: HttpRequest, obj: Model | None = None) -> bool:
        return has_model_perm(request.user, self.model, "delete", obj)
