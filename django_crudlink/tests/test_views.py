import json
from typing import Any
from unittest import mock

from django.contrib.auth.models import Group, User
from django.http import HttpResponse
from django.test import TestCase, override_settings
from django.utils import translation
from django.utils.translation import gettext_lazy

INERTIA = {"HTTP_X_INERTIA": "true"}


def page(response: HttpResponse) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(response.content)
    return data


@override_settings(ROOT_URLCONF="django_crudlink.tests.urls", LOGIN_URL="/login/", LANGUAGE_CODE="en")
class ViewsTest(TestCase):
    def setUp(self) -> None:
        self.admin = User.objects.create_superuser("admin", "admin@example.com", "x")
        self.group = Group.objects.create(name="staff")
        self.bob = User.objects.create_user("bob", first_name="Bob", last_name="Zed")
        self.bob.groups.add(self.group)
        self.client.force_login(self.admin)

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
