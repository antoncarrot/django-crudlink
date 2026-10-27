from typing import Literal

from django.contrib.auth import get_permission_codename
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser
from django.db.models import Model

Action = Literal["add", "view", "change", "delete"]


def has_model_perm(
    user: AbstractBaseUser | AnonymousUser, model: type[Model], action: Action, obj: Model | None = None
) -> bool:
    """Django model permission, with object level backends support."""
    opts = model._meta
    perm = f"{opts.app_label}.{get_permission_codename(action, opts)}"
    return user.has_perm(perm) or (obj is not None and user.has_perm(perm, obj=obj))
