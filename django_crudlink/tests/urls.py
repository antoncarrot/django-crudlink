from django.contrib.auth.models import Group, User
from django.http import HttpRequest, HttpResponse
from django.urls import include, path
from inertia import render

from django_crudlink.views import ListModelView


def host_page(request: HttpRequest) -> HttpResponse:
    """Render a page of the host project, not a crudlink view."""
    return render(request, "HostPage")


# The routes a viewset of each model will mount, in its namespace (the model name): "user:list", ...
user_urls = [
    path(
        "",
        ListModelView.as_view(model=User, list_display=("username", "email", "is_staff", "groups")),
        name="list",
    ),
]
group_urls = [
    path("", ListModelView.as_view(model=Group, list_display=("name",)), name="list"),
]

app_name = "test"

urlpatterns = [
    path("users/", include((user_urls, "user"))),
    path("groups/", include((group_urls, "group"))),
    path("host/", host_page, name="host"),
]
