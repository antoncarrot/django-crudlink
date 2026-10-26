from django.http import HttpRequest, HttpResponse
from django.urls import path
from inertia import render


def host_page(request: HttpRequest) -> HttpResponse:
    """Render a page of the host project, not a crudlink view."""
    return render(request, "HostPage")


app_name = "test"

urlpatterns = [
    path("host/", host_page, name="host"),
]
