"""Загрузка и безопасное сохранение коллекций в одном JSON-файле."""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile

from data_types import AppData
from validation import validate_data

DEFAULT_DATA_PATH = Path(__file__).resolve().parent / "data" / "app_data.json"


def empty_data() -> AppData:
    """Создать независимые пустые коллекции нового хранилища."""
    return {"projects": [], "managers": [], "assignments": []}


def load_data(file_path: Path = DEFAULT_DATA_PATH) -> AppData:
    """Загрузить и проверить JSON; отсутствие файла означает новую базу."""
    try:
        with Path(file_path).open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return empty_data()
    validate_data(data)
    return data


def save_data(data: AppData, file_path: Path = DEFAULT_DATA_PATH) -> None:
    """Атомарно заменить JSON только после полной записи временного файла."""
    validate_data(data)
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with NamedTemporaryFile(
            "w", encoding="utf-8", dir=file_path.parent,
            prefix=f".{file_path.name}.", suffix=".tmp", delete=False,
        ) as file:
            temporary_path = Path(file.name)
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")
        temporary_path.replace(file_path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
