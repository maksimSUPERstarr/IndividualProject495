"""Корневые маршруты и общий обработчик неизвестных адресов."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("projects/", include("project_pages.urls")),
    path("managers/", include("manager_pages.urls")),
    path("assignments/", include("assignment_pages.urls")),
]

handler404 = "homepage.views.page_not_found"
