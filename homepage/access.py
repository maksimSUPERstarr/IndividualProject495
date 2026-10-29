"""Загрузка снимка данных один раз на запрос и безопасный режим чтения."""

import logging
from functools import wraps

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_safe

from storage import load_catalog
from .presentation import heading, link, page

logger = logging.getLogger(__name__)


def missing(title: str, route: str, label: str) -> HttpResponse:
    """Вернуть предметную страницу ошибки с HTTP-статусом 404."""
    content = '<p class="error-number">404</p>'
    content += heading(title, "Проверьте адрес или вернитесь к списку.")
    content += link(route, label, css="action")
    return HttpResponse(page(title, content), status=404)


def catalog_view(view):
    """Передать объектный снимок в view; не записывать данные из HTTP."""
    @wraps(view)
    def wrapped(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            catalog = load_catalog(settings.DATA_FILE)
        except (OSError, ValueError):
            logger.exception("Не удалось прочитать хранилище проекта")
            content = heading(
                "Данные временно недоступны",
                "Не удалось прочитать хранилище. Обратитесь к координатору.",
            )
            return HttpResponse(page("Данные недоступны", content), status=503)
        return view(request, catalog, *args, **kwargs)

    return require_safe(wrapped)
