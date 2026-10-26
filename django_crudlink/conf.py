"""Crudlink settings with their defaults. Read on each call, so `override_settings` works."""

from django.conf import settings
from django.utils.translation import gettext_lazy

# Not a setting: rename the site with a translation of this msgid in your project's catalog (LOCALE_PATHS)
SITE_TITLE = gettext_lazy("crudlink:site_title")


def site_title() -> str:
    """Return the site title in the active language: the site layout header and the page `<title>`."""
    return str(SITE_TITLE)


def root_id() -> str:
    """`CRUDLINK_ROOT_ID`: id of the Inertia root element."""
    return str(getattr(settings, "CRUDLINK_ROOT_ID", "app"))
