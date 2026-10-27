import json
from typing import Any
from unittest import mock

from django.contrib.auth.models import Group, Permission, User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase, override_settings
from django.urls import resolve
from django.utils import translation
from django.utils.translation import gettext_lazy

from django_crudlink.shared import PageComponent
from django_crudlink.views import ListModelView

INERTIA = {"HTTP_X_INERTIA": "true"}
# the deferred `data` prop of a list page, as Inertia loads it right after the first render
DATA = {**INERTIA, "HTTP_X_INERTIA_PARTIAL_COMPONENT": PageComponent.LIST, "HTTP_X_INERTIA_PARTIAL_DATA": "data"}


def page(response: HttpResponse) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(response.content)
    return data


def table_data(response: HttpResponse) -> dict[str, Any]:
    """Return the `data` prop of a list page from a partial reload (`DATA` headers)."""
    data: dict[str, Any] = page(response)["props"]["data"]
    return data


def list_view(user: User, url: str = "/", **options: Any) -> ListModelView:
    """Return a `ListModelView` with `options`, set up for a GET of `url` by `user`, without the URLconf."""
    view = ListModelView(**options)
    request = RequestFactory().get(url)
    request.user = user
    view.setup(request)
    return view


@override_settings(ROOT_URLCONF="django_crudlink.tests.urls", LOGIN_URL="/login/", LANGUAGE_CODE="en")
class ViewsTest(TestCase):
    def setUp(self) -> None:
        self.admin = User.objects.create_superuser("admin", "admin@example.com", "x")
        self.group = Group.objects.create(name="staff")
        self.bob = User.objects.create_user("bob", first_name="Bob", last_name="Zed")
        self.bob.groups.add(self.group)
        self.client.force_login(self.admin)

    def test_login_required(self) -> None:
        self.client.logout()
        # login comes before the permission check: a redirect, not 403
        self.assertEqual(self.client.get("/users/").status_code, 302)
        # an expired session loads the login page as a full page, not inside an Inertia modal
        response = self.client.get("/users/?page=2", **DATA)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response["X-Inertia-Location"], "/login/?next=/users/%3Fpage%3D2")

    def test_list(self) -> None:
        # rows are deferred: the first render runs no row query (session + user only)
        with self.assertNumQueries(2):
            response = page(self.client.get("/users/?o=-username", **INERTIA))
        self.assertEqual(response["component"], "BaseListPage")
        self.assertEqual(response["deferredProps"], {"default": ["data"]})
        props = response["props"]
        self.assertNotIn("data", props)
        self.assertEqual(props["title"], "Users")
        self.assertEqual([c["name"] for c in props["columns"]], ["username", "email", "is_staff", "groups"])
        self.assertEqual(props["columns"][0]["label"], "Username")
        # the frontend sorts: every column is sortable, "groups" (M2M) too
        self.assertTrue(all(column["sortable"] for column in props["columns"]))
        data = table_data(self.client.get("/users/?o=-username", **DATA))
        self.assertEqual(data["ordering"], "-username")
        self.assertEqual([row["cells"]["username"]["props"]["text"] for row in data["rows"]], ["bob", "admin"])
        bob = data["rows"][0]["cells"]
        self.assertEqual(bob["username"], {"component": "text", "props": {"text": "bob"}})
        self.assertEqual(bob["email"], {"component": "text", "props": {"text": "—"}})
        self.assertEqual(bob["is_staff"], {"component": "bool", "props": {"value": False}})
        self.assertEqual(bob["groups"], {"component": "tags", "props": {"items": ["staff"]}})
        # plain values the frontend sorts by
        self.assertEqual(
            data["rows"][0]["values"], {"username": "bob", "email": "", "is_staff": False, "groups": "staff"}
        )

    def test_list_pagination(self) -> None:
        User.objects.bulk_create([User(username=f"user{i:02}") for i in range(30)])
        # frontend pages: all rows are sent, the requested page is only echoed (and clamped)
        data = table_data(self.client.get("/users/?page=2&o=username", **DATA))
        self.assertEqual(data["pagination"], {"page": 2, "pageSize": 25, "total": 32, "hasNext": False})
        self.assertEqual(len(data["rows"]), 32)
        self.assertEqual(table_data(self.client.get("/users/?page=9", **DATA))["pagination"]["page"], 2)
        self.assertEqual(table_data(self.client.get("/users/?page=x", **DATA))["pagination"]["page"], 1)
        # no paging, as in Django's ListView: all rows on one page
        for paginate_by in (None, 0):
            view = list_view(self.admin, "/?page=3", model=User, paginate_by=paginate_by)
            pagination = view.get_data(view.get_data_attrs()).pagination
            self.assertEqual((pagination.page, pagination.page_size, pagination.has_next), (1, 32, False))
        view = list_view(self.admin, model=Group, queryset=Group.objects.none(), paginate_by=None)
        self.assertEqual(view.get_data(view.get_data_attrs()).pagination.page, 1)

    def test_list_ordering(self) -> None:
        # the sort column is only sent back, the frontend sorts. The rows come in the same order
        # whatever it is, so equal values stay in the same order after a click and after a reload
        default = [row["pk"] for row in table_data(self.client.get("/users/", **DATA))["rows"]]
        for key in ("username", "-username", "-groups"):
            data = table_data(self.client.get(f"/users/?o={key}", **DATA))
            self.assertEqual(data["ordering"], key)
            self.assertEqual([row["pk"] for row in data["rows"]], default, key)
        # unknown columns and extra keys are ignored: one sort column only
        self.assertIsNone(table_data(self.client.get("/users/?o=bogus", **DATA))["ordering"])
        self.assertIsNone(table_data(self.client.get("/users/?o=username,email", **DATA))["ordering"])

    def test_default_ordering(self) -> None:
        view = ListModelView(model=Group)
        view.setup(RequestFactory().get("/"))
        # without `ordering`: the queryset's own order_by(), else the model's Meta.ordering; the pk keeps pages stable
        self.assertEqual(view.get_ordering({}, Group.objects.order_by("-name")), (None, ["-name", "pk"]))
        self.assertEqual(
            view.get_ordering({}, Permission.objects.all())[1],
            ["content_type__app_label", "content_type__model", "codename", "pk"],
        )
        self.assertEqual(view.get_ordering({}, Permission.objects.order_by())[1], ["-pk"])
        view.ordering = ("name",)
        self.assertEqual(view.get_ordering({}, Group.objects.order_by("-name"))[1], ["name", "pk"])

    def test_queryset(self) -> None:
        # only the rows of `queryset`, with the permissions of its model
        view = list_view(self.admin, queryset=User.objects.filter(is_staff=True), list_display=("username",))
        self.assertTrue(view.has_permission())
        self.assertEqual([row.pk for row in view.get_data(view.get_data_attrs()).rows], [str(self.admin.pk)])
        # with `model` set too, the permissions of the queryset's model guard its rows
        viewer = User.objects.create_user("viewer")
        viewer.user_permissions.add(Permission.objects.get(codename="view_group"))
        view = list_view(viewer, model=Group, queryset=User.objects.all())
        self.assertIs(view.get_model(), User)
        self.assertFalse(view.has_permission())

    def test_str_column(self) -> None:
        # the default column is the object's str(), labelled with the verbose name as written
        view = list_view(self.admin, model=Group)
        with mock.patch.object(Group._meta, "verbose_name", "API group"):
            columns = view.get_props().columns
        self.assertEqual([(column.name, column.label) for column in columns], [("__str__", "API group")])
        self.assertEqual(view.get_data(view.get_data_attrs()).rows[0].cells["__str__"].props, {"text": "staff"})

    def test_reverse(self) -> None:
        # sibling urls are reversed in the current namespace, or in `url_namespace`
        view = ListModelView(model=User)
        request = RequestFactory().get("/users/")
        request.resolver_match = resolve("/users/")
        view.setup(request)
        self.assertEqual(view.reverse("list"), "/users/")
        self.assertIsNone(view.reverse("detail", self.bob.pk))  # not mounted
        view.url_namespace = "group"
        self.assertEqual(view.reverse("list"), "/groups/")

    def test_permissions(self) -> None:
        user = User.objects.create_user("viewer")
        user.user_permissions.add(Permission.objects.get(codename="view_user"))
        self.client.force_login(user)
        self.assertEqual(self.client.get("/users/", **INERTIA).status_code, 200)
        self.assertEqual(self.client.get("/groups/").status_code, 403)
        # change permission grants view
        user.user_permissions.add(Permission.objects.get(codename="change_group"))
        self.assertEqual(self.client.get("/groups/").status_code, 200)

    def test_host_page_gets_shared_props(self) -> None:
        # CrudlinkMiddleware shares the `crudlink` prop with pages that aren't crudlink views
        props = page(self.client.get("/host/", **INERTIA))["props"]
        self.assertEqual(props["crudlink"], {"siteTitle": "Crudlink"})
        # the first load renders site.html, its <title> comes from {% crudlink_site_title %}
        self.assertContains(self.client.get("/host/"), "<title>Crudlink</title>")

    def test_site_title_from_catalog(self) -> None:
        # the msgid is a key: crudlink's en and ru catalogs have the title,
        # a language without a catalog (de) falls back to the LANGUAGE_CODE one
        for language in ("en", "ru", "de"):
            with translation.override(language):
                props = page(self.client.get("/host/", **INERTIA))["props"]
            self.assertEqual(props["crudlink"], {"siteTitle": "Crudlink"}, language)

    # en and ru titles are the same: a msgid from django.contrib.auth's catalog shows the language per request
    @mock.patch("django_crudlink.conf.SITE_TITLE", gettext_lazy("users"))
    def test_site_title_translated_per_request(self) -> None:
        for language, title in (("en", "users"), ("ru", "пользователи")):
            with translation.override(language):
                props = page(self.client.get("/host/", **INERTIA))["props"]
                self.assertContains(self.client.get("/host/"), f"<title>{title}</title>")
            self.assertEqual(props["crudlink"], {"siteTitle": title})
