"""CLI + settings smoke tests (no Ollama / no interactive wizard)."""

from unittest.mock import patch

import pytest
import yaml

import cli
from rooms.settings import (
    SettingsError,
    USER_SETTINGS_FILENAME,
    load_settings,
    get_default_personas,
)


def test_cli_config_init_creates_settings_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert cli.main(["config", "init"]) == 0
    dest = tmp_path / USER_SETTINGS_FILENAME
    assert dest.is_file()
    data = yaml.safe_load(dest.read_text(encoding="utf-8"))
    assert data["defaults"]["litellm_model"] == "ollama/gemma4:e2b"


def test_cli_config_init_refuses_overwrite(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert cli.main(["config", "init"]) == 0
    assert cli.main(["config", "init"]) == 1


def test_cli_config_reset_removes_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cli.main(["config", "init"])
    dest = tmp_path / USER_SETTINGS_FILENAME
    assert dest.is_file()
    assert cli.main(["config", "reset", "-y"]) == 0
    assert not dest.is_file()


def test_cli_config_reset_with_explicit_path(tmp_path):
    dest = tmp_path / USER_SETTINGS_FILENAME
    dest.write_text("defaults:\n  litellm_model: ollama/x\n", encoding="utf-8")
    assert cli.main(["config", "reset", "-y", "--path", str(dest)]) == 0
    assert not dest.is_file()


def test_cli_main_loads_explicit_config_without_wizard(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg = tmp_path / "my.settings.yaml"
    cfg.write_text(
        yaml.dump({
            "defaults": {"litellm_model": "ollama/smoke:1b", "timeout": 99},
            "user": {"name": "SmokeUser", "background": "Tester"},
        }),
        encoding="utf-8",
    )

    with patch.object(cli, "main_menu") as mock_menu:
        rc = cli.main(["--config", str(cfg)])

    assert rc == 0
    mock_menu.assert_called_once()
    settings = mock_menu.call_args[0][0]
    assert settings.defaults.litellm_model == "ollama/smoke:1b"
    assert settings.defaults.timeout == 99
    assert settings.user.name == "SmokeUser"


def test_cli_main_missing_required_config_exits_nonzero(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    missing = tmp_path / "missing.yaml"
    rc = cli.main(["--config", str(missing)])
    assert rc == 1


def test_init_settings_produces_loadable_personas(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cli.main(["config", "init"])
    settings = load_settings()
    personas = get_default_personas(settings)
    assert len(personas) == 3
    assert all(p.model == "ollama/gemma4:e2b" for p in personas)


def test_settings_error_from_init_guard(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cli.main(["config", "init"])
    with pytest.raises(SettingsError):
        from rooms.settings import init_settings_file
        init_settings_file()
