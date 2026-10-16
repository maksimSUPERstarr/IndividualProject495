"""Тема 495: консольный сервис назначения руководителей проекта (ПР2)."""

import argparse
from collections.abc import Callable
from copy import deepcopy
from pathlib import Path

from assignments import (
    cancel_assignment, check_assignment, create_assignment,
    find_suitable_managers, get_active_assignment, get_manager_load,
    sort_managers_by_load,
)
from data_types import AppData, Records
from managers import add_manager, find_manager_by_id, find_managers
from projects import add_project, find_projects
from storage import DEFAULT_DATA_PATH, load_data, save_data
from utils import input_int, input_text, input_yes_no

MENU = """
=== Назначение руководителей проекта — ПР2 ===
1. Показать проекты
2. Показать руководителей и загрузку
3. Показать историю назначений
4. Добавить проект
5. Добавить руководителя
6. Назначить руководителя
7. Отменить назначение
8. Найти проекты по названию
9. Найти руководителей по имени
10. Подобрать руководителей для проекта
11. Отсортировать руководителей по загрузке
0. Выход
"""


def show_projects(data: AppData, items: Records | None = None) -> None:
    """Показать проекты и их действующих руководителей."""
    items = data["projects"] if items is None else items
    if not items:
        print("Проекты не найдены.")
    for project in items:
        assignment = get_active_assignment(data["assignments"], project["id"])
        manager = (
            find_manager_by_id(data["managers"], assignment["manager_id"])
            if assignment else None
        )
        name = manager["name"] if manager else "не назначен"
        print(f"#{project['id']} {project['name']}")
        print(f"  {project['specialization']}; руководитель: {name}")


def show_managers(data: AppData, items: Records | None = None) -> None:
    """Показать руководителей с загрузкой, вычисленной по назначениям."""
    items = data["managers"] if items is None else items
    if not items:
        print("Руководители не найдены.")
    for manager in items:
        load = get_manager_load(data["assignments"], manager["id"])
        state = "доступен" if manager["is_active"] else "недоступен"
        print(f"#{manager['id']} {manager['name']}")
        print(
            f"  {manager['specialization']}; {state}; "
            f"загрузка {load}/{manager['project_limit']}"
        )


def show_assignments(data: AppData) -> None:
    """Показать действующие и отменённые назначения со связанными именами."""
    if not data["assignments"]:
        print("Назначений пока нет.")
    projects = {item["id"]: item["name"] for item in data["projects"]}
    managers = {item["id"]: item["name"] for item in data["managers"]}
    for item in data["assignments"]:
        state = "отменено" if item["is_cancelled"] else "действует"
        print(
            f"#{item['id']} {projects[item['project_id']]} → "
            f"{managers[item['manager_id']]}"
        )
        print(f"  дата {item['assigned_on']}; {state}")


def add_project_flow(data: AppData) -> str:
    """Прочитать поля и добавить новый проект."""
    project = add_project(
        data["projects"], input_text("Название: "), input_text("Направление: ")
    )
    return f"Проект #{project['id']} добавлен."


def add_manager_flow(data: AppData) -> str:
    """Прочитать поля и добавить руководителя."""
    manager = add_manager(
        data["managers"], input_text("Имя: "),
        input_text("Специализация: "), input_int("Лимит проектов: "),
        input_yes_no("Доступен для назначений (да/нет): "),
    )
    return f"Руководитель #{manager['id']} добавлен."


def assign_flow(data: AppData) -> str | None:
    """Проверить выбранные ID и запросить подтверждение координатора."""
    project_id = input_int("ID проекта: ")
    manager_id = input_int("ID руководителя: ")
    reason = check_assignment(
        data["projects"], data["managers"], data["assignments"],
        project_id, manager_id,
    )
    if reason:
        raise ValueError(reason)
    if not input_yes_no("Подтвердить назначение (да/нет): "):
        print("Назначение отменено координатором. Данные не изменены.")
        return None
    item = create_assignment(
        data["projects"], data["managers"], data["assignments"],
        project_id, manager_id,
    )
    return f"Назначение #{item['id']} создано."


def cancel_flow(data: AppData) -> str | None:
    """Запросить ID и подтверждение отмены назначения."""
    assignment_id = input_int("ID назначения: ")
    candidate = deepcopy(data["assignments"])
    cancel_assignment(candidate, assignment_id)
    if not input_yes_no("Подтвердить отмену (да/нет): "):
        print("Отмена не подтверждена. Данные не изменены.")
        return None
    cancel_assignment(data["assignments"], assignment_id)
    return f"Назначение #{assignment_id} отменено. Место освобождено."


def apply_change(
    data: AppData,
    file_path: Path,
    operation: Callable[[AppData], str | None],
) -> AppData:
    """Принять изменения в памяти только после успешной записи на диск."""
    candidate = deepcopy(data)
    message = operation(candidate)
    if message is None:
        return data
    save_data(candidate, file_path)
    print(message)
    print("Данные сохранены.")
    return candidate


def run_menu(data: AppData, file_path: Path) -> None:
    """Обрабатывать пункты меню, перехватывая ошибки ввода и файлов."""
    changes = {
        4: add_project_flow, 5: add_manager_flow,
        6: assign_flow, 7: cancel_flow,
    }
    while True:
        print(MENU)
        command = input_int("Выберите действие: ", minimum=0)
        try:
            if command == 0:
                print("Работа завершена. Успешные изменения уже сохранены.")
                return
            if command in changes:
                data = apply_change(data, file_path, changes[command])
            elif command == 1:
                show_projects(data)
            elif command == 2:
                show_managers(data)
            elif command == 3:
                show_assignments(data)
            elif command == 8:
                show_projects(data, find_projects(
                    data["projects"], input_text("Часть названия: ")
                ))
            elif command == 9:
                show_managers(data, find_managers(
                    data["managers"], input_text("Часть имени: ")
                ))
            elif command == 10:
                show_managers(data, find_suitable_managers(
                    data["projects"], data["managers"], data["assignments"],
                    input_int("ID проекта: "),
                ))
            elif command == 11:
                show_managers(data, sort_managers_by_load(
                    data["managers"], data["assignments"]
                ))
            else:
                print("Такого пункта нет. Выберите число из меню.")
        except ValueError as error:
            print(f"Операция не выполнена: {error}")
        except OSError as error:
            print(f"Не удалось сохранить данные: {error}")
            print("Изменения не приняты. Исправьте ошибку и повторите.")


def main(argv: list[str] | None = None) -> int:
    """Разобрать аргументы, загрузить данные и запустить консольное меню."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data", type=Path, default=DEFAULT_DATA_PATH,
        help="путь к JSON; по умолчанию data/app_data.json рядом с программой",
    )
    file_path = parser.parse_args(argv).data
    try:
        data = load_data(file_path)
    except (ValueError, OSError) as error:
        print(f"Не удалось загрузить данные: {error}")
        print("Исходный файл не изменён. Исправьте его или выберите --data.")
        return 1
    try:
        run_menu(data, file_path)
    except (EOFError, KeyboardInterrupt):
        print("\nРабота завершена. Незавершённая операция не сохранена.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
