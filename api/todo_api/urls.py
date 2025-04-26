import os

from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.urls import include, path
from rest_framework import status


def health_check(request: HttpRequest) -> HttpResponse:
    return HttpResponse(status=status.HTTP_200_OK)


urlpatterns = [
    path("health/", health_check),
    path("admin/", admin.site.urls),
    path("tasks/", include("tasks.urls")),
]

# Conditionally include URLs for the 'atomicserver' app, typically only for CI/testing.
# These URLs provide endpoints to control atomic transactions for E2E tests.
# IMPORTANT: Do not include these URLs in production!
if os.environ.get("CI") == "true":
    urlpatterns.append(path("atomic/", include("atomicserver.urls")))
