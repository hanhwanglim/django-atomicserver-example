from django.urls import path

from atomicserver import views

urlpatterns = [
    path("begin/", views.begin, name="begin"),
    path("setup/", views.setup, name="setup"),
    path("rollback/", views.rollback, name="rollback"),
]
