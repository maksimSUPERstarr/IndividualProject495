"""Сквозные проверки меню с настоящим временным JSON-хранилищем."""

from assignments import get_manager_load
from main import main
from storage import load_data, save_data


def enter(monkeypatch, answers):
    values = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt: next(values))


def test_all_read_menu_commands_keep_file_unchanged(
    app_data, tmp_path, monkeypatch, capsys
):
    path = tmp_path / "state.json"
    save_data(app_data, path)
    before = path.read_bytes()
    enter(monkeypatch, [
        "1", "2", "3", "8", "ПОРТАЛ", "9", "АННА", "10", "1", "11", "0",
    ])
    assert main(["--data", str(path)]) == 0
    output = capsys.readouterr().out
    assert "#1 Портал" in output
    assert "загрузка 2/3" in output
    assert "дата 2026-09-01; действует" in output
    assert path.read_bytes() == before


def test_write_commands_persist_and_survive_restart(
    app_data, tmp_path, monkeypatch
):
    path = tmp_path / "state.json"
    save_data(app_data, path)
    enter(monkeypatch, [
        "4", "Новый отчёт", "Аналитика",
        "5", "Елена", "Аналитика", "1", "да",
        "6", "5", "5", "да", "7", "3", "да", "0",
    ])
    assert main(["--data", str(path)]) == 0
    data = load_data(path)
    assert data["projects"][-1]["name"] == "Новый отчёт"
    assert data["assignments"][-1]["is_cancelled"] is True
    assert get_manager_load(data["assignments"], 5) == 0
    enter(monkeypatch, ["6", "5", "5", "да", "0"])
    assert main(["--data", str(path)]) == 0
    data = load_data(path)
    assert data["assignments"][-1]["id"] == 4
    assert get_manager_load(data["assignments"], 5) == 1


def test_bad_numbers_unknown_ids_and_unknown_menu_do_not_crash(
    app_data, tmp_path, monkeypatch, capsys
):
    path = tmp_path / "state.json"
    save_data(app_data, path)
    before = path.read_bytes()
    enter(monkeypatch, [
        "буква", "-1", "99", "6", "не число", "999", "1", "7", "999", "0",
    ])
    assert main(["--data", str(path)]) == 0
    output = capsys.readouterr().out
    assert "Введите целое число" in output
    assert "Такого пункта нет" in output
    assert "Проект с указанным ID не найден" in output
    assert "Назначение с указанным ID не найдено" in output
    assert path.read_bytes() == before


def test_empty_fields_invalid_limit_and_confirmation_are_retried(
    tmp_path, monkeypatch, capsys
):
    path = tmp_path / "state.json"
    enter(monkeypatch, [
        "4", "", "Проект", "Веб",
        "5", "Анна", "Веб", "0", "два", "2", "может быть", "да", "0",
    ])
    assert main(["--data", str(path)]) == 0
    data = load_data(path)
    assert len(data["projects"]) == len(data["managers"]) == 1
    assert data["managers"][0]["project_limit"] == 2
    assert "Введите «да» или «нет»" in capsys.readouterr().out


def test_declined_assignment_and_cancellation_keep_data(
    app_data, tmp_path, monkeypatch
):
    path = tmp_path / "state.json"
    save_data(app_data, path)
    before = path.read_bytes()
    enter(monkeypatch, ["6", "1", "1", "нет", "7", "1", "нет", "0"])
    assert main(["--data", str(path)]) == 0
    assert path.read_bytes() == before


def test_corrupt_file_causes_friendly_startup_error(tmp_path, capsys):
    path = tmp_path / "state.json"
    path.write_text("broken", encoding="utf-8")
    assert main(["--data", str(path)]) == 1
    assert "Исходный файл не изменён" in capsys.readouterr().out
    assert path.read_text(encoding="utf-8") == "broken"


def test_write_failure_is_reported_and_menu_remains_usable(
    app_data, tmp_path, monkeypatch, capsys
):
    path = tmp_path / "state.json"
    save_data(app_data, path)
    before = path.read_bytes()

    def deny_save(*args, **kwargs):
        raise PermissionError("Нет доступа")

    monkeypatch.setattr("main.save_data", deny_save)
    enter(monkeypatch, ["4", "Несохранённый проект", "Веб", "1", "0"])
    assert main(["--data", str(path)]) == 0
    output = capsys.readouterr().out
    assert "Не удалось сохранить данные" in output
    assert "Несохранённый проект" not in output
    assert path.read_bytes() == before


def test_eof_during_confirmation_does_not_save_partial_operation(
    app_data, tmp_path, monkeypatch
):
    path = tmp_path / "state.json"
    save_data(app_data, path)
    before = path.read_bytes()
    values = iter(["6", "1", "1"])

    def read(prompt):
        try:
            return next(values)
        except StopIteration as error:
            raise EOFError from error

    monkeypatch.setattr("builtins.input", read)
    assert main(["--data", str(path)]) == 0
    assert path.read_bytes() == before
