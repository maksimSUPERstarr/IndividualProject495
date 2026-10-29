"""Общие элементы HTML; входные данные всегда экранируются."""

from django.urls import reverse
from django.utils.html import escape

from models import Assignment, Catalog, Manager
from .styles import CSS


def link(route: str, label: str, *args, css: str = "") -> str:
    """Сформировать ссылку по имени маршрута."""
    url = reverse(route, args=args)
    return f'<a class="{escape(css)}" href="{url}">{escape(label)}</a>'


def badge(label: str, tone: str = "blue") -> str:
    """Показать статус текстом и цветом."""
    return (f'<span class="badge pill pill-{escape(tone)}">'
            f'{escape(label)}</span>')


def page(title: str, content: str, section: str = "") -> str:
    """Собрать общий HTML-каркас по схеме методички ПР5."""
    navigation = []
    for name, label in [
        ("homepage", "Обзор"), ("projects", "Проекты"),
        ("managers", "Руководители"), ("assignments", "Назначения"),
    ]:
        current = ' aria-current="page"' if name == section else ""
        url = reverse(f"{name}:index" if name == "homepage" else
                      f"{name}:list")
        navigation.append(f'<a href="{url}"{current}>{label}</a>')
    bootstrap = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8"
        "/dist/css/bootstrap.min.css"
    )
    return f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(title)} · Руководители проектов</title>
    <link rel="stylesheet" href="{bootstrap}">
    <style>{CSS}</style>
</head>
<body>
    <header class="site-header">
        <div class="shell header-inner">
            <a class="brand" href="{reverse('homepage:index')}">
                <span class="brand-mark" aria-hidden="true">Р</span>
                <span>Руководители проектов<small>СЕРВИС КООРДИНАТОРА</small>
                </span>
            </a>
            <nav class="nav site-nav" aria-label="Основная навигация">
                {''.join(navigation)}
            </nav>
        </div>
    </header>
    <main class="container shell">{content}</main>
    <footer class="site-footer">
        <div class="shell footer-inner">
            <span>Назначение руководителей проекта</span>
            <span>Специализация · Загрузка · История назначений</span>
        </div>
    </footer>
</body>
</html>'''


def heading(title: str, description: str,
            eyebrow: str = "Рабочее пространство") -> str:
    """Сформировать заголовок страницы без общего каркаса."""
    return (
        f'<p class="eyebrow">{escape(eyebrow)}</p>'
        f'<h1>{escape(title)}</h1><p class="subtitle">'
        f'{escape(description)}</p>'
    )


def empty(title: str, description: str = "") -> str:
    """Сообщить об отсутствии записей или результатов фильтра."""
    return (f'<div class="empty-state"><strong>{escape(title)}</strong>'
            f'{escape(description)}</div>')


def table(headers: list[str], rows: list[list[str]], message: str) -> str:
    """Объединить доверенную разметку ячеек в адаптивную таблицу."""
    if not rows:
        return f'<div class="panel">{empty(message)}</div>'
    head = ''.join(f'<th scope="col">{escape(h)}</th>' for h in headers)
    body = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in row) + '</tr>'
                   for row in rows)
    return (f'<div class="panel panel-flush"><div class="table-wrap">'
            f'<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody>'
            '</table></div></div>')


def manager_status(catalog: Catalog, manager: Manager) -> str:
    """Различить отключённого руководителя и исчерпанный лимит."""
    if not manager.is_active:
        return badge("Недоступен", "gray")
    if catalog.manager_load(manager.id) >= manager.project_limit:
        return badge("Лимит достигнут", "amber")
    return badge("Есть свободные места", "green")


def capacity(catalog: Catalog, manager: Manager) -> str:
    """Показать число назначений и полосу нагрузки с текстовым эквивалентом."""
    load = catalog.manager_load(manager.id)
    percent = min(100, round(load / manager.project_limit * 100))
    return (
        '<div class="capacity"><div class="capacity-label">'
        f'<span>{load} из {manager.project_limit} проектов</span>'
        f'<span>{percent}%</span></div><div class="capacity-bar" '
        f'aria-hidden="true"><span style="width:{percent}%"></span>'
        '</div></div>'
    )


def assignment_table(items: list[Assignment]) -> str:
    """Показать назначения со ссылками на связанные объекты."""
    rows = []
    for item in items:
        rows.append([
            link("assignments:detail", f"№ {item.id}", item.id),
            link("projects:detail", item.project.name, item.project.id),
            link("managers:detail", item.manager.name, item.manager.id),
            escape(item.assigned_on.strftime("%d.%m.%Y")),
            badge(item.status, "gray" if item.is_cancelled else "green"),
        ])
    return table(["Назначение", "Проект", "Руководитель", "Дата", "Статус"],
                 rows, "Назначений пока нет")
