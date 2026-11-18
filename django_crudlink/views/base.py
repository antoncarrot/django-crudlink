import functools
from collections.abc import Mapping, Sequence
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, PermissionDenied, ValidationError
from django.db.models import Model, QuerySet
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import NoReverseMatch, URLPattern, path, reverse
from django.utils.functional import cached_property
from inertia import InertiaResponse, location

from ..access import ModelAccess, ModelPermissions
from ..helpers import cells
from ..helpers.columns import DataAttr, get_data_attr
from ..json import CrudlinkJSONEncoder
from ..shared import CamelCaseJSON, Cell, CellComponent, PageComponent

# a `@column` with one of these components links its related objects, like a `related_links` entry
LINK_COMPONENTS = (CellComponent.LINK, CellComponent.LINKS)


class CrudlinkResponse(InertiaResponse):
    json_encoder = CrudlinkJSONEncoder


class CrudViewMixin(LoginRequiredMixin):
    """Common part of crudlink views.

    Rows and permissions come from `access`: Django model permissions of `get_model()`,
    the rows of `queryset`, else all rows of the model.

    Before the handler runs, `dispatch()` sets `object` (the detail page, see
    `get_page_object()`) and checks `has_permission()`. A page object that isn't
    found is a 404 only for users who pass the check without it, else a 403.

    Pages find each other by url name, as in django-material: `<app_label>:<model_name>_<view_type>`,
    e.g. `auth:user_detail`. `as_path()` gives a route that name, `url_names` points to pages named otherwise.
    """

    # declared without a value, so not class attributes: View.setup() sets them on the instance
    request: HttpRequest
    kwargs: dict[str, Any]
    view_type: str = ""  # the page in url names: "list", "detail"
    # options, overridden in subclasses or by as_view()
    component: PageComponent | str = ""
    model: type[Model] | None = None
    queryset: QuerySet | None = None
    # view type -> url name of the model's pages mounted under other names, e.g. {"detail": "teams:team"}
    url_names: Mapping[str, str] | None = None
    # columns or fields whose related objects link to their detail page, see get_cell();
    # a mapping gives the url name of each, e.g. {"groups": "teams:team"}
    related_links: Sequence[str] | Mapping[str, str] = ()
    empty_value_display: str = "—"
    # set by dispatch()
    object: Model | None = None

    @classmethod
    def as_path(cls, route: str, **initkwargs: Any) -> URLPattern:
        """Return a `path()` of the view named `<model_name>_<view_type>`, e.g. `user_detail`.

        The model comes from the class or `initkwargs`, like for `as_view()`. Mount the pages of an app
        in one `include()` with the app label as the namespace, so they find each other::

            path("", include(([UserListView.as_path("users/"), UserDetailView.as_path("users/<pk>/")], "auth")))
        """
        if not cls.view_type:
            raise ImproperlyConfigured(f"{cls.__name__} has no view_type to name its url.")
        view = cls.as_view(**initkwargs)
        model = cls(**initkwargs).get_model()
        return path(route, view, name=f"{model._meta.model_name}_{cls.view_type}")

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

    def get_url_name(self, view_type: str) -> str:
        """Url name of a page of the model: from `url_names`, else `<app_label>:<model_name>_<view_type>`."""
        if self.url_names and view_type in self.url_names:
            return self.url_names[view_type]
        opts = self.get_model()._meta
        return f"{opts.app_label}:{opts.model_name}_{view_type}"

    def reverse(self, view_type: str, *args: Any) -> str | None:
        """Url of a page of the model ("list", "detail", ...), None if it is not mounted."""
        try:
            return reverse(self.get_url_name(view_type), args=args, current_app=self.get_current_app())
        except NoReverseMatch:
            return None

    def get_current_app(self) -> str | None:
        """Instance namespace of the request, so pages mounted more than once link within their own copy.

        Like Django's `{% url %}` tag: `reverse()` prefers it among the instances of an app namespace.
        """
        match = self.request.resolver_match
        return match.namespace if match else None

    def get_related_links(self) -> dict[str, str | None]:
        """`related_links` as column name -> url name, None for the detail page of the related object's model."""
        if isinstance(self.related_links, Mapping):
            return dict(self.related_links)
        return dict.fromkeys(self.related_links)

    def get_related_url(self, obj: Model, url_name: str | None = None) -> str | None:
        """Url of a related object: `url_name`, else the `<app_label>:<model_name>_detail` page of its model.

        None when that page isn't mounted or the user has neither view nor change permission on the model.
        Model permissions only, no object ones: Django loads them once per request, so many related
        objects cost no queries. Override to link somewhere else; keep the signature, `get_cell()`
        passes the `related_links` url name as `url_name`.
        """
        if not ModelPermissions(type(obj)).has_view_permission(self.request):
            return None
        opts = obj._meta
        try:
            url_name = url_name or f"{opts.app_label}:{opts.model_name}_detail"
            return reverse(url_name, args=[obj.pk], current_app=self.get_current_app())
        except NoReverseMatch:
            return None

    # Values

    def to_text(self, value: Any) -> str:
        return cells.to_text(value, self.empty_value_display)

    def get_cell(self, obj: Model, attr: DataAttr, value: Any) -> Cell:
        """Choose the frontend cell of a list column or detail field.

        - `related_links` columns and `@column(component=CellComponent.LINK)` (or `LINKS`) ones link
          their related objects to `get_related_url()`. Without a url they are text or tags.
        - Other columns with a `component` get the value in that custom cell.
        - The rest get a built-in cell by the value's type.

        An empty value is `empty_value_display` in a text cell, whatever the component.
        """
        links = self.get_related_links()
        if attr.name in links or attr.component in LINK_COMPONENTS:
            related_url = functools.partial(self.get_related_url, url_name=links.get(attr.name))
            return cells.to_cell(value, self.empty_value_display, related_url)
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
