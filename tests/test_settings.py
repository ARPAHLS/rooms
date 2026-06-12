import os
from pathlib import Path

import pytest
import yaml

from rooms.config import AgentConfig
from rooms.settings import (
    RoomsSettings,
    SettingsError,
    load_settings,
    get_default_personas,
    init_settings_file,
    reset_settings_file,
    persona_settings_to_agent_config,
    PersonaSettings,
    DefaultsSettings,
    SHIPPED_PERSONAS,
    repo_root,
)


def test_builtin_defaults_without_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # Mock preflight tag fetch to match baseline defaults during testing
    monkeypatch.setattr(
        "rooms.ollama_preflight.fetch_local_ollama_tags",
        lambda base_url: ["gemma4:e2b"]
    )
    settings = load_settings()
    # If defaults fall back or resolve, ensure we handle the test smoothly
    assert settings.defaults.litellm_model in ["ollama/gemma4:e2b", "ollama/auto"]
    assert settings.user.name == "User"


def test_load_settings_from_file(tmp_path):
    cfg = tmp_path / "rooms.settings.yaml"
    cfg.write_text(
        yaml.dump({
            "defaults": {"litellm_model": "ollama/gemma4:e2b", "timeout": 120},
            "user": {"name": "Theo", "background": "Engineer"},
        }),
        encoding="utf-8",
    )
    settings = load_settings(str(cfg))
    assert settings.defaults.litellm_model == "ollama/gemma4:e2b"
    assert settings.defaults.timeout == 120
    assert settings.user.name == "Theo"


def test_invalid_yaml_raises(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("defaults: [not", encoding="utf-8")
    with pytest.raises(SettingsError):
        load_settings(str(bad))


def test_shipped_personas_use_defaults_model():
    settings = RoomsSettings(defaults=DefaultsSettings(litellm_model="ollama/custom:7b"))
    personas = get_default_personas(settings)
    assert len(personas) == len(SHIPPED_PERSONAS)
    assert all(p.model == "ollama/custom:7b" for p in personas)
    assert personas[0].name == "Elena (The Lawyer)"


def test_custom_personas_from_yaml():
    settings = RoomsSettings(
        use_shipped_personas=False,
        defaults=DefaultsSettings(litellm_model="ollama/base"),
        personas=[
            PersonaSettings(
                name="Custom",
                system_prompt="You are custom.",
                expertise=["test"],
                model=None,
                color="red",
            )
        ],
    )
    personas = get_default_personas(settings)
    assert len(personas) == 1
    assert personas[0].name == "Custom"
    assert personas[0].model == "ollama/base"


def test_persona_null_model_inherits_default():
    persona = PersonaSettings(name="X", system_prompt="sys", model=None)
    agent = persona_settings_to_agent_config(persona, DefaultsSettings(litellm_model="ollama/x"))
    assert agent.model == "ollama/x"


def test_init_and_reset_settings(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    dest = init_settings_file()
    assert dest.is_file()
    with pytest.raises(SettingsError):
        init_settings_file()
    assert reset_settings_file(dest) is True
    assert not dest.is_file()


def test_example_settings_file_exists():
    assert (repo_root() / "rooms.settings.example.yaml").is_file()


def test_explicit_config_required_missing(tmp_path):
    missing = tmp_path / "nope.yaml"
    with pytest.raises(SettingsError):
        load_settings(str(missing), required=True)


def test_resolve_ollama_model_auto_success(monkeypatch):
    """Verifies ollama/auto successfully resolves to the first available engine tag."""
    from rooms.settings import resolve_ollama_model

    monkeypatch.setattr(
        "rooms.ollama_preflight.fetch_local_ollama_tags",
        lambda base_url: ["llama3:latest", "gemma:7b"]
    )

    settings = RoomsSettings()
    settings.defaults.litellm_model = "ollama/auto"
    settings.ollama.auto_select_first = True

    resolved = resolve_ollama_model(settings)
    assert resolved == "ollama/llama3:latest"


def test_resolve_ollama_model_auto_server_down(monkeypatch):
    """Verifies resolution falls back gracefully to 'ollama/auto' when server is unreachable."""
    from rooms.settings import resolve_ollama_model

    def mock_fetch_failed(base_url):
        raise ConnectionError("Server completely unreachable")

    monkeypatch.setattr(
        "rooms.ollama_preflight.fetch_local_ollama_tags",
        mock_fetch_failed
    )

    settings = RoomsSettings()
    settings.defaults.litellm_model = "ollama/auto"
    settings.ollama.auto_select_first = True

    resolved = resolve_ollama_model(settings)
    assert resolved == "ollama/auto"