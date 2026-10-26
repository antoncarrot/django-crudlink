from collections.abc import Callable

from django.http import HttpRequest, HttpResponse
from inertia import share

from . import conf
from .shared import CrudlinkSharedProps


class CrudlinkMiddleware:
    """Share the `crudlink` prop with every Inertia page, your own pages too.

    The site layout (`SiteLayout`) reads it. Override `get_shared_props()` to change it.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # a callable: Inertia resolves it only for a response that sends it. Plain JSON data:
        # host pages are encoded with the host's INERTIA_JSON_ENCODER
        share(request, crudlink=lambda: self.get_shared_props(request).to_json())
        return self.get_response(request)

    def get_shared_props(self, request: HttpRequest) -> CrudlinkSharedProps:
        return CrudlinkSharedProps(site_title=conf.site_title())
