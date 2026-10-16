"""Проверки JSON, связей, повреждений и отказов при записи."""

from copy import deepcopy
from pathlib import Path

import pytest

from assignments import get_manager_load
from main import apply_change
from projects import add_project
from storage import empty_data, load_data, save_data
from validation import validate_data


def test_json_roundtrip_preserves_unicode_and_relationships(
    app_data, tmp_path
):
    path = tmp_path / "new-folder" / "state.json"
    save_data(app_data, path)
    loaded = load_data(path)
    assert loaded == app_data
    assert "Анна" in path.read_text(encoding="utf-8")
    assert get_manager_load(loaded["assignments"], 1) == 2


def test_missing_file_returns_independent_empty_collections(tmp_path):
    path = tmp_path / "missing.json"
    first = load_data(path)
    first["projects"].append({"id": 1})
    assert load_data(path) == empty_data()
    assert not path.exists()


def test_invalid_json_is_not_overwritten(tmp_path):
    path = tmp_path / "broken.json"
    original = '{"projects": ['
    path.write_text(original, encoding="utf-8")
    with pytest.raises(ValueError):
        load_data(path)
    assert path.read_text(encoding="utf-8") == original


@pytest.mark.parametrize(
    "collection,index,field,value",
    [("projects", 1, "id", 1),
     ("projects", 0, "id", True),
     ("managers", 0, "project_limit", 1),
     ("managers", 0, "is_active", "true"),
     ("assignments", 0, "project_id", 999),
     ("assignments", 0, "manager_id", 999),
     ("assignments", 0, "assigned_on", "не дата"),
     ("assignments", 0, "is_cancelled", 0),
     ("assignments", 0, "cancelled_on", "2026-10-16")],
)
def test_invalid_data_is_rejected_before_write(
    app_data, tmp_path, collection, index, field, value
):
    path = tmp_path / "state.json"
    save_data(app_data, path)
    original = path.read_bytes()
    app_data[collection][index][field] = value
    with pytest.raises(ValueError):
        save_data(app_data, path)
    assert path.read_bytes() == original


def test_duplicate_active_project_is_rejected(app_data):
    duplicate = deepcopy(app_data["assignments"][0])
    duplicate["id"] = 3
    app_data["assignments"].append(duplicate)
    with pytest.raises(ValueError, match="два действующих"):
        validate_data(app_data)


def test_failed_replace_preserves_disk_and_memory(
    app_data, tmp_path, monkeypatch
):
    path = tmp_path / "state.json"
    save_data(app_data, path)
    original_bytes = path.read_bytes()
    original_data = deepcopy(app_data)

    def deny_replace(*args, **kwargs):
        raise PermissionError("Файл недоступен для записи")

    def change(candidate):
        add_project(candidate["projects"], "Новый проект", "Веб")
        return "Проект добавлен"

    monkeypatch.setattr(Path, "replace", deny_replace)
    with pytest.raises(PermissionError):
        apply_change(app_data, path, change)
    assert path.read_bytes() == original_bytes
    assert app_data == original_data
    assert list(tmp_path.glob("*.tmp")) == []
