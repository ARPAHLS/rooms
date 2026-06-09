"""Load user settings from YAML with shipped fallbacks (#26, #27)."""

from __future__ import annotations

import os
import shutil
import json

from pathlib import Path
from typing import Dict, List, Optional
from urllib.request import urlopen
from urllib.error import URLError

import yaml
from pydantic import BaseModel, Field, ValidationError

from .config import AgentConfig

# Shipped persona definitions (single source for reset / use_shipped_personas)
SHIPPED_PERSONAS: List[dict] = [
    {
        "name": "Elena (The Lawyer)",
        "system_prompt": (
            "You are Elena, a highly skilled corporate lawyer with 10 years of experience. "
            "Recently, you lost a major case because of a tiny, overlooked detail in 'Clause Y', "
            "and now you are extremely sensitive, defensive, and incredibly picky about specific wording. "
            "You often bring up this past trauma when reviewing anything."
        ),
        "expertise": ["law", "contracts", "compliance", "clause y"],
        "color": "magenta",
    },
    {
        "name": "Viktor (The Coder)",
        "system_prompt": (
            "You are Viktor, a cynical senior backend engineer who has seen too many startups fail. "
            "You are brutally honest, hate buzzwords, and prioritize performance and actual hardware specs. "
            "You communicate strictly in practical terms and think most new tech is just a fad."
        ),
        "expertise": ["engineering", "backend", "performance", "realism"],
        "color": "green",
    },
    {
        "name": "Nyx (The Visionary)",
        "system_prompt": (
            "You are Nyx, a creative visionary who looks at everything from a 10,000-foot view. "
            "You dislike getting bogged down in tiny details (which often annoys lawyers and engineers). "
            "You focus on the 'why' and the 'future impact' rather than the 'how'."
        ),
        "expertise": ["creative", "vision", "future", "strategy"],
        "color": "cyan",
    },
]

BUILTIN_DEFAULT_MODEL = "ollama/gemma4:e2b"
EXAMPLE_SETTINGS_FILENAME = "rooms.settings.example.yaml"
USER_SETTINGS_FILENAME = "rooms.settings.yaml"


class DefaultsSettings(BaseModel):
    litellm_model: str = BUILTIN_DEFAULT_MODEL
    orchestrator_model: Optional[str] = None
    temperature: float = 0.7
    timeout: int = 30

    @property
    def resolved_orchestrator_model(self) -> str:
        return self.orchestrator_model or self.litellm_model


class PresetSettings(BaseModel):
    litellm_model: str
    api_key_env: Optional[str] = None


class OllamaSettings(BaseModel):
    auto_select_first: bool = False
    base_url: str = "http://localhost:11434"


class UserSettings(BaseModel):
    name: str = "User"
    background: str = ""


class PersonaSettings(BaseModel):
    name: str
    system_prompt: str
    expertise: List[str] = Field(default_factory=list)
    model: Optional[str] = None
    temperature: Optional[float] = None
    color: str = "blue"


class RoomsSettings(BaseModel):
    defaults: DefaultsSettings = Field(default_factory=DefaultsSettings)
    presets: Dict[str, PresetSettings] = Field(default_factory=dict)
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    user: UserSettings = Field(default_factory=UserSettings)
    use_shipped_personas: bool = True
    personas: List[PersonaSettings] = Field(default_factory=list)


class SettingsError(Exception):
    """Raised when settings YAML is missing, invalid, or cannot be written."""


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def example_settings_path() -> Path:
    return repo_root() / EXAMPLE_SETTINGS_FILENAME


def settings_search_paths(explicit_path: Optional[str] = None) -> List[Path]:
    """Precedence: explicit --config, cwd, user config dir."""
    paths: List[Path] = []
    if explicit_path:
        paths.append(Path(explicit_path).expanduser())
    paths.append(Path.cwd() / USER_SETTINGS_FILENAME)
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            paths.append(Path(appdata) / "rooms" / "settings.yaml")
    else:
        paths.append(Path.home() / ".config" / "rooms" / "settings.yaml")
    return paths


def find_settings_file(explicit_path: Optional[str] = None) -> Optional[Path]:
    for path in settings_search_paths(explicit_path):
        if path.is_file():
            return path
    return None


def _apply_ollama_env(settings: RoomsSettings) -> None:
    if settings.ollama.base_url:
        os.environ.setdefault("OLLAMA_API_BASE", settings.ollama.base_url)

def resolve_ollama_model(settings: RoomsSettings) -> str:
    model = settings.defaults.litellm_model

    if not settings.ollama.auto_select_first:
        return model

    if model != "ollama/auto":
        return model

    try:
        url = f"{settings.ollama.base_url}/api/tags"

        with urlopen(url, timeout=3) as response:
            data = json.loads(response.read().decode("utf-8"))

        models = data.get("models", [])

        if models:
            return f"ollama/{models[0]['name']}"

    except (URLError, KeyError, IndexError, json.JSONDecodeError):
        pass

    return model

def load_settings(explicit_path: Optional[str] = None, *, required: bool = False) -> RoomsSettings:
    """Load settings from the first matching file, or return built-in defaults."""
    path = find_settings_file(explicit_path)
    if path is None:
        if required and explicit_path:
            raise SettingsError(
                f"Settings file not found: {explicit_path}\n"
                f"Copy {EXAMPLE_SETTINGS_FILENAME} to {USER_SETTINGS_FILENAME} or run: python cli.py config init"
            )
        settings = RoomsSettings()
        _apply_ollama_env(settings)
        return settings

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        settings = RoomsSettings.model_validate(raw)
    except (yaml.YAMLError, ValidationError) as e:
        raise SettingsError(
            f"Invalid settings in {path}: {e}\n"
            f"See {EXAMPLE_SETTINGS_FILENAME} for the expected format."
        ) from e

    _apply_ollama_env(settings)
    return settings


def persona_settings_to_agent_config(persona: PersonaSettings, defaults: DefaultsSettings) -> AgentConfig:
    return AgentConfig(
        name=persona.name,
        system_prompt=persona.system_prompt,
        expertise=persona.expertise,
        model=persona.model or defaults.litellm_model,
        temperature=persona.temperature if persona.temperature is not None else defaults.temperature,
        timeout=defaults.timeout,
        color=persona.color,
    )


def _shipped_persona_dicts_to_configs(defaults: DefaultsSettings) -> List[AgentConfig]:
    configs: List[AgentConfig] = []
    for data in SHIPPED_PERSONAS:
        configs.append(
            AgentConfig(
                name=data["name"],
                system_prompt=data["system_prompt"],
                expertise=data["expertise"],
                model=defaults.litellm_model,
                temperature=defaults.temperature,
                timeout=defaults.timeout,
                color=data["color"],
            )
        )
    return configs


def get_default_personas(settings: RoomsSettings) -> List[AgentConfig]:
    """Resolve persona list: custom YAML personas or shipped defaults."""
    if settings.personas:
        return [persona_settings_to_agent_config(p, settings.defaults) for p in settings.personas]
    if settings.use_shipped_personas:
        return _shipped_persona_dicts_to_configs(settings.defaults)
    return _shipped_persona_dicts_to_configs(settings.defaults)


def resolve_preset_model(settings: RoomsSettings, preset_name: str) -> str:
    preset = settings.presets.get(preset_name)
    if not preset:
        raise SettingsError(f"Unknown preset '{preset_name}'. Available: {', '.join(settings.presets) or '(none)'}")
    return preset.litellm_model


def user_settings_path_preferred() -> Path:
    """Where config init writes the user file (cwd first)."""
    return Path.cwd() / USER_SETTINGS_FILENAME


def init_settings_file(target: Optional[Path] = None, *, force: bool = False) -> Path:
    src = example_settings_path()
    if not src.is_file():
        raise SettingsError(f"Example settings missing: {src}")
    dest = target or user_settings_path_preferred()
    if dest.exists() and not force:
        raise SettingsError(f"Settings file already exists: {dest}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, dest)
    return dest


def reset_settings_file(target: Optional[Path] = None) -> bool:
    """Remove user settings file if present. Returns True if a file was removed."""
    removed = False
    if target:
        paths = [Path(target).expanduser()]
    else:
        paths = [Path.cwd() / USER_SETTINGS_FILENAME]
        appdata = os.environ.get("APPDATA")
        if appdata:
            paths.append(Path(appdata) / "rooms" / "settings.yaml")
        paths.append(Path.home() / ".config" / "rooms" / "settings.yaml")

    for path in paths:
        if path.is_file():
            path.unlink()
            removed = True
    return removed
