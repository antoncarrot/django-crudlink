from django.contrib.auth.models import Group, User
from django.http import HttpRequest, HttpResponse
from django.urls import include, path
from django.utils.translation import gettext_lazy
from inertia import render

from django_crudlink import column
from django_crudlink.layout import Layout, Row
from django_crudlink.views import DetailModelView, ListMode, ListModelView


class UserColumns:
    """Computed columns of the user views. The viewset issue moves them to UserViewSet."""

    @column(label="Full name", order_field="last_name")
    def full_name(self, user: User) -> str:
        return user.get_full_name()


class UserListView(UserColumns, ListModelView):
    model = User
    list_display = ("username", "email", "full_name", "is_staff", "groups")
    related_links = ("groups",)


class UserDetailView(UserColumns, DetailModelView):
    model = User
    fields = ("username", "email", "is_staff", "groups", "full_name")
    related_links = ("groups",)


class GroupListView(ListModelView):
    model = Group
    list_display = ("name", "user", "size")  # a reverse M2M relation, a computed column with a custom cell
    related_links = ("user",)

    # lazy label, msgid from django.contrib.auth catalog, translated per request
    @column(label=gettext_lazy("users"), component="badge")
    def size(self, group: Group) -> int:
        return len(group.user_set.all())


def host_page(request: HttpRequest) -> HttpResponse:
    """Render a page of the host project, not a crudlink view."""
    return render(request, "HostPage")


# The pages of the auth app, in its namespace: "auth:user_list", "auth:user_detail", "auth:group_list", ...
auth_urls = [
    UserListView.as_path("users/"),
    UserDetailView.as_path("users/<pk>/"),
    GroupListView.as_path("groups/"),
    # the layout picks the fields; Permission has no detail page, so its links stay tags
    DetailModelView.as_path(
        "groups/<pk>/",
        model=Group,
        layout=Layout(Row("name", "user"), "permissions"),
        related_links=("user", "permissions"),
    ),
]

app_name = "test"

urlpatterns = [
    path("", include((auth_urls, "auth"))),
    # the same pages again, in the instance namespace "staff": they link within this copy
    path("staff/", include((auth_urls, "auth"), namespace="staff")),
    # more lists of users, under their own names: their rows link to the user detail page above.
    # The server list modes; the viewset issue swaps in ServerUserViewSet and UncountedUserViewSet
    path(
        "server-users/",
        UserListView.as_view(list_display=("username", "email", "full_name", "groups"), list_mode=ListMode.SERVER),
        name="server_users",
    ),
    path(
        "uncounted-users/",
        ListModelView.as_view(
            model=User, list_display=("username", "email", "groups"), list_mode=ListMode.SERVER_UNCOUNTED
        ),
        name="uncounted_users",
    ),
    # a group page under a name of its own, for `url_names` and `related_links` url names
    path("teams/<pk>/", DetailModelView.as_view(model=Group), name="team"),
    path("host/", host_page, name="host"),
]
