from django.urls import path

from . import views

urlpatterns = [
    path("json", views.json, name="json"),
    path("html", views.html, name="html"),
]
