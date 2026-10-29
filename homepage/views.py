"""Обзор сервиса и обработчик неизвестных адресов."""

from django.http import HttpRequest, HttpResponse
from django.urls import reverse

from models import Catalog
from .access import catalog_view
from .presentation import (
    assignment_table, badge, capacity, heading, link, manager_status, page,
    table,
)


@catalog_view
def index(request: HttpRequest, catalog: Catalog) -> HttpResponse:
    """Показать сводку, свободные проекты и доступную нагрузку команды."""
    unassigned = [p for p in catalog.projects
                  if catalog.active_assignment(p.id) is None]
    active = [a for a in catalog.assignments if not a.is_cancelled]
    free_slots = sum(max(0, m.project_limit - catalog.manager_load(m.id))
                     for m in catalog.managers if m.is_active)
    content = heading(
        "Проекты и руководители",
        "Контролируйте назначения и находите руководителей с подходящей "
        "специализацией и свободной загрузкой.",
        "Обзор сервиса",
    )
    content += '<div class="stats">'
    for label, value, note, route, attention in [
        ("Всего проектов", len(catalog.projects), "В рабочем каталоге",
         "projects:list", False),
        ("Без руководителя", len(unassigned), "Ожидают назначения",
         "projects:list", True),
        ("Действующих назначений", len(active), "В истории сервиса",
         "assignments:list", False),
        ("Свободных мест", free_slots, "У доступных руководителей",
         "managers:list", False),
    ]:
        css = "stat stat-attention" if attention else "stat"
        query = ""
        if attention:
            query = "?status=unassigned"
        elif route == "assignments:list":
            query = "?status=active"
        elif route == "managers:list":
            query = "?status=available"
        content += (
            f'<a class="{css}" href="{reverse(route)}{query}">'
            f'<span class="stat-label">{label}</span><strong>{value}</strong>'
            f'<span class="stat-note">{note}</span></a>'
        )
    content += '</div><div class="section-title"><h2>'
    content += "Требуют назначения</h2>"
    content += link("projects:list", "Все проекты →") + '</div>'
    rows = [[
        link("projects:detail", p.name, p.id),
        badge(p.specialization),
        str(len(catalog.suitable_managers(p.id))),
        link("projects:detail", "Посмотреть кандидатов →", p.id),
    ] for p in unassigned]
    content += table(["Проект", "Направление", "Кандидатов", "Подбор"],
                     rows, "Все проекты уже имеют руководителей")
    content += '<div class="section-title"><h2>Нагрузка команды</h2>'
    content += link("managers:list", "Все руководители →") + '</div>'
    rows = [[
        link("managers:detail", manager.name, manager.id),
        badge(manager.specialization), capacity(catalog, manager),
        manager_status(catalog, manager),
    ] for manager in catalog.managers]
    content += table(
        ["Руководитель", "Специализация", "Загрузка", "Доступность"],
        rows, "Руководителей пока нет",
    )
    content += '<div class="section-title"><h2>Последние назначения</h2>'
    content += link("assignments:list", "Вся история →") + '</div>'
    content += assignment_table(sorted(
        catalog.assignments, key=lambda item: item.id, reverse=True
    )[:5])
    return HttpResponse(page("Обзор", content, "homepage"))


def page_not_found(request: HttpRequest, exception) -> HttpResponse:
    """Показать общую 404 при DEBUG=False без внутренних сведений Django."""
    content = '<p class="error-number">404</p>'
    content += heading("Страница не найдена", "Такого адреса в сервисе нет.")
    content += link("homepage:index", "Вернуться к обзору", css="action")
    return HttpResponse(page("Страница не найдена", content), status=404)
