"""Template tags to mount crudlink into Django templates.

Mode 1, crud pages inside your own template (set it as INERTIA_LAYOUT)::

    {% extends "site/base.html" %}
    {% load crudlink %}
    {% block content %}{% crudlink_root %}{% crudlink_assets "crud" %}{% endblock %}

Mode 2, full site: ``INERTIA_LAYOUT = "django_crudlink/site.html"``.
"""

from typing import Any

from django import template
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.safestring import SafeString

from .. import conf

register = template.Library()


@register.inclusion_tag("django_crudlink/root.html", takes_context=True)
def crudlink_root(context: template.Context) -> dict[str, Any]:
    """Inertia root element with the initial page data. Id is `CRUDLINK_ROOT_ID`."""
    return {"page": context.get("page", ""), "root_id": conf.root_id()}


@register.simple_tag
def crudlink_site_title() -> str:
    """Return the site title in the active language, e.g. for the `<title>`."""
    return conf.site_title()


@register.simple_tag
def crudlink_assets(bundle: str) -> SafeString:
    """Prebuilt bundle: "crud" (pages only) or "site" (pages with layout)."""
    return format_html(
        '<link rel="stylesheet" href="{}"><script type="module" src="{}"></script>',
        static(f"django_crudlink/{bundle}.css"),
        static(f"django_crudlink/{bundle}.js"),
    )
