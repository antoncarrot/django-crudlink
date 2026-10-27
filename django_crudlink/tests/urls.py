from django.contrib.auth.models import Group, User
from django.http import HttpRequest, HttpResponse
from django.urls import include, path
from django.utils.translation import gettext_lazy
from inertia import render

from django_crudlink import column
from django_crudlink.views import ListMode, ListModelView


class UserColumns:
    """Computed columns of the user views. The viewset issue moves them to UserViewSet."""

    @column(label="Full name", order_field="last_name")
    def full_name(self, user: User) -> str:
        return user.get_full_name()


class UserListView(UserColumns, ListModelView):
    model = User
    list_display = ("username", "email", "full_name", "is_staff", "groups")


class GroupListView(ListModelView):
    model = Group
    list_display = ("name", "size")  # a computed column with a custom cell

    # lazy label, msgid from django.contrib.auth catalog, translated per request
    @column(label=gettext_lazy("users"), component="badge")
    def size(self, group: Group) -> int:
        return len(group.user_set.all())


def host_page(request: HttpRequest) -> HttpResponse:
    """Render a page of the host project, not a crudlink view."""
    return render(request, "HostPage")


# The routes a viewset of each model will mount, in its namespace (the model name): "user:list", ...
user_urls = [
    path("", UserListView.as_view(), name="list"),
]
group_urls = [
    path("", GroupListView.as_view(), name="list"),
]
# The server list modes; the viewset issue swaps in ServerUserViewSet and UncountedUserViewSet
server_user_urls = [
    path(
        "",
        UserListView.as_view(list_display=("username", "email", "full_name", "groups"), list_mode=ListMode.SERVER),
        name="list",
    ),
]
uncounted_user_urls = [
    path(
        "",
        ListModelView.as_view(
            model=User, list_display=("username", "email", "groups"), list_mode=ListMode.SERVER_UNCOUNTED
        ),
        name="list",
    ),
]

app_name = "test"

urlpatterns = [
    path("users/", include((user_urls, "user"))),
    path("groups/", include((group_urls, "group"))),
    path("server-users/", include((server_user_urls, "server-users"))),
    path("uncounted-users/", include((uncounted_user_urls, "uncounted-users"))),
    path("host/", host_page, name="host"),
]
