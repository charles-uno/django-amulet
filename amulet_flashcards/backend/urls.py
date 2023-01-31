from django.urls import path

from . import views

urlpatterns = [
    path("e2e", views.e2e),
    path("opener", views.opener),
    path("play", views.play_it_out),
]
