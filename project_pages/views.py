"""Список и карточка проектов; подбор использует общие бизнес-правила."""

from django.http import HttpRequest, HttpResponse
from django.utils.html import escape

from homepage.access import catalog_view, missing
from homepage.presentation import (
    assignment_table, badge, capacity, empty, heading, link, page, table,
)
from models import Catalog


@catalog_view
def project_list(request: HttpRequest, catalog: Catalog) -> HttpResponse:
    """Показать проекты с поиском по названию и фильтром назначения."""
    query = request.GET.get("q", "").strip()
    only_free = request.GET.get("status") == "unassigned"
    projects = [p for p in catalog.projects
                if query.casefold() in p.name.casefold()
                and (not only_free or catalog.active_assignment(p.id) is None)]
    content = heading(
        "Проекты", "Каталог проектов, их направления и назначения."
    )
    checked = " selected" if only_free else ""
    content += f'''
    <form class="filters" method="get">
        <label for="project-search">Название проекта
            <input id="project-search" type="search" name="q"
                value="{escape(query)}" placeholder="Найти проект">
        </label>
        <label for="project-status">Назначение
            <select id="project-status" name="status">
                <option value="">Все проекты</option>
                <option value="unassigned"{checked}>Без руководителя</option>
            </select>
        </label>
        <button class="action" type="submit">Показать</button>
        {link('projects:list', 'Сбросить', css='back-link')}
    </form>'''
    content += f'<p class="eyebrow">Найдено проектов: {len(projects)}</p>'
    rows = []
    for project in projects:
        active = catalog.active_assignment(project.id)
        manager = (link("managers:detail", active.manager.name,
                        active.manager.id) if active else "Не назначен")
        rows.append([
            link("projects:detail", project.name, project.id)
            + f'<span class="secondary">Проект № {project.id}</span>',
            badge(project.specialization), manager,
            badge("Руководитель назначен", "green") if active else
            badge("Ожидает назначения", "amber"),
        ])
    content += table(["Проект", "Направление", "Руководитель", "Статус"],
                     rows, "Проекты не найдены")
    return HttpResponse(page("Проекты", content, "projects"))


@catalog_view
def project_detail(request: HttpRequest, catalog: Catalog,
                   project_id: int) -> HttpResponse:
    """Показать проект, его назначения и подходящих руководителей."""
    project = catalog.find_project(project_id)
    if project is None:
        return missing(
            "Проект не найден", "projects:list", "К списку проектов"
        )
    active = catalog.active_assignment(project.id)
    content = link("projects:list", "← Все проекты", css="back-link")
    content += heading(project.name, project.specialization,
                       f"Проект № {project.id}")
    content += '<div class="panel"><div class="detail-grid"><dl>'
    content += '<dt>Направление проекта</dt>'
    content += f'<dd>{escape(project.specialization)}</dd><dt>Статус</dt><dd>'
    content += (badge("Руководитель назначен", "green") if active else
                badge("Ожидает назначения", "amber"))
    content += '</dd></dl><dl><dt>Текущий руководитель</dt><dd>'
    content += (link("managers:detail", active.manager.name, active.manager.id)
                if active else "Пока не назначен")
    content += '</dd><dt>Дата назначения</dt><dd>'
    content += active.assigned_on.strftime("%d.%m.%Y") if active else "—"
    content += '</dd></dl></div></div>'
    content += '<div class="section-title"><h2>Подходящие руководители'
    content += '</h2></div>'
    if active:
        content += '<div class="panel">' + empty(
            "У проекта уже есть руководитель",
            "Повторное назначение возможно после отмены текущего.",
        ) + '</div>'
    else:
        rows = [[
            link("managers:detail", m.name, m.id), badge(m.specialization),
            capacity(catalog, m),
            str(m.project_limit - catalog.manager_load(m.id)),
        ] for m in catalog.suitable_managers(project.id)]
        content += table(["Руководитель", "Специализация", "Загрузка",
                          "Свободных мест"], rows,
                         "Нет доступных кандидатов с нужной специализацией")
        content += '<p class="subtitle">Кандидаты отсортированы по загрузке. '
        content += 'Учитываются специализация, доступность и личный лимит.</p>'
    content += '<div class="section-title"><h2>История проекта</h2></div>'
    content += assignment_table(sorted(
        [a for a in catalog.assignments if a.project.id == project.id],
        key=lambda item: item.id, reverse=True,
    ))
    content += '<p class="info-note">Создание и отмена назначений доступны '
    content += 'в консольной версии сервиса.</p>'
    return HttpResponse(page(project.name, content, "projects"))
