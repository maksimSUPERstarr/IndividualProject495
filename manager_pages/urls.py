"""Маршруты справочника руководителей."""

from django.urls import path

from . import views

app_name = "managers"
urlpatterns = [
    path("", views.manager_list, name="list"),
    path("<int:manager_id>/", views.manager_detail, name="detail"),
]
