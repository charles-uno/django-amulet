from django.urls import path

from . import views

urlpatterns = [
    path("html/e2e", views.htmx_e2e),
    path("html/opener", views.htmx_opener),
    path("html/play", views.htmx_play_it_out),
]
