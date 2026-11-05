"""Crudlink settings with their defaults. Read on each call, so `override_settings` works."""

from django.conf import settings
from django.utils.translation import gettext_lazy

# Not a setting: rename the site with a translation of this msgid in your project's catalog (LOCALE_PATHS)
SITE_TITLE = gettext_lazy("crudlink:site_title")


def str2bool(value: str | bool) -> bool:  # noqa: FBT001 - the value to convert, not a flag
    """Boolean representation of a string or a bool.

    A string from the environment counts by its meaning, "False" and "0" are False
    (https://peps.python.org/pep-0632/#migration-advice). A bool setting is returned as it is.
    """
    if isinstance(value, bool):
        return value
    return bool(value and value.lower() in ("y", "yes", "on", "1", "true", "t"))


def site_title() -> str:
    """Return the site title in the active language: the site layout header and the page `<title>`."""
    return str(SITE_TITLE)


def root_id() -> str:
    """`CRUDLINK_ROOT_ID`: id of the Inertia root element."""
    return str(getattr(settings, "CRUDLINK_ROOT_ID", "app"))


def inertia_navigation() -> bool:
    """`CRUDLINK_INERTIA_NAVIGATION`.

    False (default) - moving to another page is a full page load, only same-page
    updates (table data) go through Inertia. True - SPA navigation.
    """
    return str2bool(getattr(settings, "CRUDLINK_INERTIA_NAVIGATION", False))
