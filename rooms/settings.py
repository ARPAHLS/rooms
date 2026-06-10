from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class DefaultsSettings(BaseModel):
    litellm_model: str = "ollama/gemma4:e2b"
    orchestrator_model: str = "ollama/gemma4:e2b"
    temperature: float = 0.7
    timeout: int = 30

class PresetSettings(BaseModel):
    litellm_model: str
    api_key_env: Optional[str] = None

class OllamaSettings(BaseModel):
    auto_select_first: bool = False
    base_url: str = "http://localhost:11434"

class UserSettings(BaseModel):
    name: str = "User"
    background: str = ""

class RoomsSettings(BaseModel):
    defaults: DefaultsSettings = Field(default_factory=DefaultsSettings)
    presets: Dict[str, PresetSettings] = Field(default_factory=dict)
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    user: UserSettings = Field(default_factory=UserSettings)
    use_shipped_personas: bool = True
    personas: List[Any] = Field(default_factory=list)
    custom_instructions: Dict[str, Any] = Field(default_factory=dict)