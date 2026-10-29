"""Страницы руководителей, текущей загрузки и истории назначений."""

from django.http import HttpRequest, HttpResponse
from django.utils.html import escape

from homepage.access import catalog_view, missing
from homepage.presentation import (
    assignment_table, badge, capacity, heading, link, manager_status, page,
    table,
)
from models import Catalog


@catalog_view
def manager_list(request: HttpRequest, catalog: Catalog) -> HttpResponse:
    """Найти руководителей и показать загрузку в порядке возрастания."""
    query = request.GET.get("q", "").strip()
    only_available = request.GET.get("status") == "available"
    managers = sorted([
        m for m in catalog.managers if query.casefold() in m.name.casefold()
        and (not only_available or (m.is_active and
             catalog.manager_load(m.id) < m.project_limit))
    ], key=lambda m: (catalog.manager_load(m.id), m.name.casefold(), m.id))
    content = heading("Руководители", "Специализация, доступность и текущая "
                      "загрузка каждого руководителя.")
    checked = " selected" if only_available else ""
    content += f'''
    <form class="filters" method="get">
        <label for="manager-search">Имя руководителя
            <input id="manager-search" type="search" name="q"
                value="{escape(query)}" placeholder="Найти руководителя">
        </label>
        <label for="manager-status">Доступность
            <select id="manager-status" name="status">
                <option value="">Все руководители</option>
                <option value="available"{checked}>
                    Со свободными местами
                </option>
            </select>
        </label>
        <button class="action" type="submit">Показать</button>
        {link('managers:list', 'Сбросить', css='back-link')}
    </form>'''
    content += f'<p class="eyebrow">Найдено руководителей: {len(managers)}</p>'
    rows = [[
        link("managers:detail", m.name, m.id)
        + f'<span class="secondary">Руководитель № {m.id}</span>',
        badge(m.specialization), capacity(catalog, m),
        manager_status(catalog, m),
    ] for m in managers]
    content += table(
        ["Руководитель", "Специализация", "Загрузка", "Доступность"],
        rows, "Руководители не найдены",
    )
    return HttpResponse(page("Руководители", content, "managers"))


@catalog_view
def manager_detail(request: HttpRequest, catalog: Catalog,
                   manager_id: int) -> HttpResponse:
    """Показать руководителя и проекты, на которые его можно назначить."""
    manager = catalog.find_manager(manager_id)
    if manager is None:
        return missing("Руководитель не найден", "managers:list",
                       "К списку руководителей")
    content = link("managers:list", "← Все руководители", css="back-link")
    content += heading(manager.name, manager.specialization,
                       f"Руководитель № {manager.id}")
    content += '<div class="panel"><div class="detail-grid"><dl>'
    content += '<dt>Специализация</dt>'
    content += f'<dd>{escape(manager.specialization)}</dd>'
    content += '<dt>Доступность для новых назначений</dt><dd>'
    content += manager_status(catalog, manager) + '</dd></dl><dl>'
    content += '<dt>Текущая загрузка</dt><dd>'
    content += capacity(catalog, manager) + '</dd><dt>Личный лимит</dt>'
    content += f'<dd>{manager.project_limit} проектов</dd></dl></div></div>'
    content += '<div class="section-title"><h2>Можно назначить на проекты'
    content += '</h2></div>'
    projects = [p for p in catalog.projects
                if not catalog.rejection_reason(p.id, manager.id)]
    content += table(["Проект", "Направление"], [[
        link("projects:detail", p.name, p.id), badge(p.specialization),
    ] for p in projects], "Нет подходящих проектов для нового назначения")
    content += '<div class="section-title"><h2>История назначений</h2></div>'
    content += assignment_table(sorted(
        [a for a in catalog.assignments if a.manager.id == manager.id],
        key=lambda item: item.id, reverse=True,
    ))
    return HttpResponse(page(manager.name, content, "managers"))
