"""Правила назначения, сохранённые из первой практической работы."""


def specializations_match(
    project_specialization: str, manager_specialization: str
) -> bool:
    """Сравнить непустые специализации без регистра и пробелов по краям."""
    project_specialization = project_specialization.strip().casefold()
    manager_specialization = manager_specialization.strip().casefold()
    return bool(project_specialization) and (
        project_specialization == manager_specialization
    )


def has_free_capacity(current_load: int, project_limit: int) -> bool:
    """Проверить, что можно добавить ещё один проект к текущей загрузке."""
    return 0 <= current_load < project_limit


def get_assignment_rejection_reason(
    project_specialization: str,
    manager_specialization: str,
    current_load: int,
    project_limit: int,
    manager_is_active: bool,
    assigned_manager: str,
) -> str:
    """Вернуть причину отказа или пустую строку при допустимом назначении."""
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
