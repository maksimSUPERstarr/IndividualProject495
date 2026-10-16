"""Общие операции с коллекциями и безопасный консольный ввод."""

from data_types import Record, Records


def next_id(records: Records) -> int:
    """Получить свободный ID, не переиспользуя ID существующих записей."""
    return max((item["id"] for item in records), default=0) + 1


def find_by_id(records: Records, record_id: int) -> Record | None:
    """Найти запись генератором; вернуть None, если ID не существует."""
    return next((item for item in records if item["id"] == record_id), None)


def require_text(value: str, label: str) -> str:
    """Проверить и нормализовать обязательное текстовое поле."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Поле «{label}» не должно быть пустым.")
    return value.strip()


def input_text(prompt: str) -> str:
    """Запрашивать непустую строку до получения корректного значения."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Значение не должно быть пустым. Повторите ввод.")


def input_int(prompt: str, minimum: int = 1) -> int:
    """Безопасно прочитать целое число не меньше указанной границы."""
    while True:
        try:
            value = int(input(prompt))
            if value < minimum:
                raise ValueError
            return value
        except ValueError:
            print(f"Введите целое число не меньше {minimum}.")


def input_yes_no(prompt: str) -> bool:
    """Прочитать подтверждение, повторяя запрос при неизвестном ответе."""
    while True:
        answer = input(prompt).strip().casefold()
        if answer in ("да", "нет"):
            return answer == "да"
        print("Введите «да» или «нет».")
