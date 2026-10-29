"""Список назначений и карточка со связанными объектами."""

from django.http import HttpRequest, HttpResponse

from homepage.access import catalog_view, missing
from homepage.presentation import (
    assignment_table, badge, heading, link, page,
)
from models import Catalog


@catalog_view
def assignment_list(request: HttpRequest, catalog: Catalog) -> HttpResponse:
    """Показать историю, включая отменённые назначения."""
    status = request.GET.get("status", "")
    items = [a for a in catalog.assignments
             if (status != "active" or not a.is_cancelled)
             and (status != "cancelled" or a.is_cancelled)]
    content = heading("Назначения", "История назначения руководителей на "
                      "проекты. Отменённые записи сохраняются.")
    options = []
    for value, label in [("", "Все назначения"), ("active", "Действующие"),
                         ("cancelled", "Отменённые")]:
        checked = " selected" if value == status else ""
        options.append(f'<option value="{value}"{checked}>{label}</option>')
    content += '<form class="filters" method="get"><label '
    content += 'for="assignment-status">Статус назначения<select '
    content += 'id="assignment-status" name="status">'
    content += ''.join(options) + '</select></label><button class="action" '
    content += 'type="submit">Показать</button></form>'
    content += f'<p class="eyebrow">Найдено назначений: {len(items)}</p>'
    content += assignment_table(sorted(
        items, key=lambda a: a.id, reverse=True
    ))
    return HttpResponse(page("Назначения", content, "assignments"))


@catalog_view
def assignment_detail(request: HttpRequest, catalog: Catalog,
                      assignment_id: int) -> HttpResponse:
    """Показать данные назначения и ссылки на проект и руководителя."""
    item = catalog.find_assignment(assignment_id)
    if item is None:
        return missing("Назначение не найдено", "assignments:list",
                       "К списку назначений")
    content = link("assignments:list", "← Все назначения", css="back-link")
    content += heading(f"Назначение № {item.id}",
                       "Связь проекта и назначенного руководителя.",
                       "История сервиса")
    content += '<div class="panel"><div class="detail-grid"><dl>'
    content += '<dt>Проект</dt><dd>'
    content += link("projects:detail", item.project.name, item.project.id)
    content += '</dd><dt>Руководитель</dt><dd>'
    content += link("managers:detail", item.manager.name, item.manager.id)
    content += '</dd></dl><dl><dt>Дата назначения</dt><dd>'
    content += item.assigned_on.strftime("%d.%m.%Y")
    content += '</dd><dt>Статус</dt><dd>'
    content += badge(item.status, "gray" if item.is_cancelled else "green")
    content += '</dd><dt>Дата отмены</dt><dd>'
    content += (item.cancelled_on.strftime("%d.%m.%Y")
                if item.cancelled_on else "—")
    content += '</dd></dl></div></div>'
    content += '<p class="info-note">Отмена сохраняет запись в истории '
    content += 'и освобождает место в загрузке руководителя.</p>'
    title = f"Назначение № {item.id}"
    return HttpResponse(page(title, content, "assignments"))
