from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db.models import Model, QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import NoReverseMatch, reverse
from django.utils.functional import cached_property
from inertia import InertiaResponse, location

from ..access import ModelAccess, ModelPermissions
from ..helpers import cells
from ..helpers.columns import DataAttr, get_data_attr
from ..json import CrudlinkJSONEncoder
from ..shared import CamelCaseJSON, Cell, PageComponent


class CrudlinkResponse(InertiaResponse):
    json_encoder = CrudlinkJSONEncoder


class CrudViewMixin(LoginRequiredMixin):
    """Common part of crudlink views.

    Rows and permissions come from `access`: Django model permissions of `get_model()`,
    the rows of `queryset`, else all rows of the model.

    Before the handler runs, `dispatch()` checks `has_permission()`.
    """

    # declared without a value, so not class attributes: View.setup() sets them on the instance
    request: HttpRequest
    kwargs: dict[str, Any]
    # options, overridden in subclasses or by as_view()
    component: PageComponent | str = ""
    model: type[Model] | None = None
    queryset: QuerySet | None = None
    url_namespace: str | None = None  # namespace of sibling urls ("list", "detail", ...), None - the current one
    empty_value_display: str = "—"

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        # anonymous users get the login redirect of LoginRequiredMixin, not a 403
        if request.user.is_authenticated and not self.has_permission():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def has_permission(self) -> bool:
        """Whether the user may open the page. Each view asks `access`."""
        raise NotImplementedError

    @cached_property
    def access(self) -> ModelAccess:
        return ModelPermissions(self.get_model(), self.queryset)

    def get_model(self) -> type[Model]:
        # the model of the rows first: its permissions guard them
        if self.queryset is not None:
            return self.queryset.model
        if self.model is not None:
            return self.model
        name = type(self).__name__
        raise ImproperlyConfigured(f"{name} is missing a model. Define {name}.model or {name}.queryset.")

    def get_queryset(self) -> QuerySet:
        return self.access.get_queryset(self.request)

    def get_data_attr(self, name: str) -> DataAttr:
        """Resolve a list column name: model field, model attribute."""
        return get_data_attr(self.get_model(), name)

    # Urls

    def reverse(self, name: str, *args: Any) -> str | None:
        """Reverse a sibling url in the current namespace, None if it is not mounted."""
        namespace = self.get_url_namespace()
        try:
            return reverse(f"{namespace}:{name}" if namespace else name, args=args)
        except NoReverseMatch:
            return None

    def get_url_namespace(self) -> str:
        if self.url_namespace is not None:
            return self.url_namespace
        return self.request.resolver_match.namespace if self.request.resolver_match else ""

    # Values

    def to_text(self, value: Any) -> str:
        return cells.to_text(value, self.empty_value_display)

    def get_cell(self, obj: Model, attr: DataAttr, value: Any) -> Cell:
        """Choose the frontend cell of a list column: a built-in cell for the type of the value."""
        return cells.to_cell(value, self.empty_value_display)

    def handle_no_permission(self) -> HttpResponse:
        """Send an anonymous Inertia request (table data) to the login page as a full page load."""
        response = super().handle_no_permission()
        if "X-Inertia" in self.request.headers and isinstance(response, HttpResponseRedirect):
            # Inertia would show the login page, a non-Inertia response, in a modal
            return location(response.url)
        return response

    def render(self, props: CamelCaseJSON) -> CrudlinkResponse:
        # top level fields are separate Inertia props, so partial reloads (`only`) work.
        # The `crudlink` prop comes from `CrudlinkMiddleware`, shared with every page.
        return CrudlinkResponse(self.request, self.component, props.to_json())
