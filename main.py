"""Тема 495: начальный сценарий назначения руководителя проекта (ПР1)."""

from datetime import date


def specializations_match(project_specialization, manager_specialization):
    """Проверить совпадение непустых специализаций без учёта регистра."""
    project_specialization = project_specialization.strip().casefold()
    manager_specialization = manager_specialization.strip().casefold()
    return bool(project_specialization) and (
        project_specialization == manager_specialization
    )


def has_free_capacity(current_load, project_limit):
    """Проверить, что руководителю можно добавить ещё один проект."""
    return 0 <= current_load < project_limit


def get_assignment_rejection_reason(
    project_specialization,
    manager_specialization,
    current_load,
    project_limit,
    manager_is_active,
    assigned_manager,
):
    """Вернуть причину отказа или пустую строку, если назначение допустимо."""
    if assigned_manager.strip():
        return "У проекта уже есть руководитель."
    if not manager_is_active:
        return "Руководитель недоступен для новых назначений."
    if current_load < 0 or project_limit <= 0:
        return "Некорректные данные о загрузке или лимите проектов."
    if not specializations_match(
        project_specialization, manager_specialization
    ):
        return "Специализация руководителя не соответствует проекту."
    if not has_free_capacity(current_load, project_limit):
        return "Достигнут лимит проектов руководителя."
    return ""


def main():
    """Проверить кандидата и выполнить назначение по решению координатора."""
    # Учебные данные: на ПР2 они будут заменены коллекциями и JSON-файлами.
    project_name = "Корпоративный портал задач"
    project_specialization = "Веб-разработка"
    manager_name = "Анна Смирнова"
    manager_specialization = "Веб-разработка"
    current_load = 2
    project_limit = 3
    manager_is_active = True
    assigned_manager = ""

    print("Сервис назначения руководителей проекта — тема 495")
    print(f"Проект: {project_name}")
    print(f"Направление проекта: {project_specialization}")
    print(f"Кандидат: {manager_name}")
    print(f"Специализация: {manager_specialization}")
    print(f"Текущая загрузка: {current_load} из {project_limit} проектов")

    rejection_reason = get_assignment_rejection_reason(
        project_specialization,
        manager_specialization,
        current_load,
        project_limit,
        manager_is_active,
        assigned_manager,
    )
    if rejection_reason:
        print(f"Назначение невозможно: {rejection_reason}")
        return

    print("Проверка пройдена: руководителя можно назначить.")
    confirmation = input("Координатор, подтвердите назначение (да/нет): ")
    if confirmation.strip().casefold() != "да":
        print("Назначение отменено. Загрузка руководителя не изменилась.")
        return

    assigned_manager = manager_name
    current_load += 1
    assignment_date = date.today()

    print("Назначение выполнено.")
    print(f"Проект: {project_name}")
    print(f"Назначенный руководитель: {assigned_manager}")
    print(f"Дата назначения: {assignment_date:%d.%m.%Y}")
    print(f"Новая загрузка: {current_load} из {project_limit} проектов")
    print("В ПР1 результат хранится в памяти до завершения программы.")


if __name__ == "__main__":
    main()
