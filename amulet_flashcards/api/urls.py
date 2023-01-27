from django.urls import path

from . import views

urlpatterns = [
    path("json/e2e", views.json_e2e),
    path("html/e2e", views.html_e2e),
    path("html/opener", views.html_opener),
]
