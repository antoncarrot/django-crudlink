from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, PermissionDenied, ValidationError
from django.db.models import Model, QuerySet
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
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

    Before the handler runs, `dispatch()` sets `object` (the detail page, see
    `get_page_object()`) and checks `has_permission()`. A page object that isn't
    found is a 404 only for users who pass the check without it, else a 403.
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
    # set by dispatch()
    object: Model | None = None

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        # anonymous users get the login redirect of LoginRequiredMixin, not a 404 or 403
        if request.user.is_authenticated:
            try:
                self.object = self.get_page_object()
            except Http404:
                # checked without the object: a 404 for a missing object and a 403 for an existing one
                # would tell a user without permission which objects exist
                if not self.has_permission():
                    raise PermissionDenied from None
                raise
            if not self.has_permission():
                raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_page_object(self) -> Model | None:
        """Return the object the page is about, None for pages about no single object, like the list."""
        return None

    def has_permission(self) -> bool:
        """Whether the user may open the page. Each view asks `access`.

        `self.object` is set, None when the page object wasn't found: then the check decides between 403 and 404.
        """
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

    def get_object(self) -> Model:
        """Object by the `pk` url kwarg, from `get_queryset()`. A missing or malformed pk is a 404."""
        if "pk" not in self.kwargs:
            raise ImproperlyConfigured(f"{type(self).__name__} needs a `pk` url kwarg, e.g. path('<pk>/', ...).")
        queryset = self.get_queryset()
        try:
            pk = queryset.model._meta.pk.to_python(self.kwargs["pk"])
            return queryset.get(pk=pk)
        except (ValidationError, ValueError, queryset.model.DoesNotExist):
            raise Http404 from None

    def get_data_attr(self, name: str) -> DataAttr:
        """Resolve a list column or detail field name: model field, `@column` method of the view, model attribute."""
        return get_data_attr(self.get_model(), name, [self])

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
        """Choose the frontend cell of a list column or detail field: its `component`, else a built-in one by type.

        An empty value is `empty_value_display` in a text cell, whatever the component.
        """
        if attr.component and not cells.is_empty(value):
            return Cell(attr.component, {"value": cells.to_cell_value(value)})
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
