"""Lazy Skillware runtime integration for Rooms agents."""

from __future__ import annotations

import concurrent.futures
import importlib
import inspect
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .config import AgentConfig

logger = logging.getLogger(__name__)


@dataclass
class SkillEntry:
    skill_id: str
    tool_name: str
    instructions: str
    instance: Any
    tool_def: Dict[str, Any]


class SkillRuntime:
    """Loads and executes skills assigned to one agent lazily."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self._loaded = False
        self._load_error: Optional[str] = None
        self._entries: List[SkillEntry] = []
        self._by_tool_name: Dict[str, SkillEntry] = {}
        self._calls_made = 0

    @property
    def has_skills(self) -> bool:
        return bool(self.config.skills)

    @property
    def load_error(self) -> Optional[str]:
        return self._load_error

    @property
    def calls_made(self) -> int:
        return self._calls_made

    def get_tools(self) -> List[Dict[str, Any]]:
        if not self.has_skills:
            return []
        self._ensure_loaded()
        return [entry.tool_def for entry in self._entries]

    def get_combined_instructions(self) -> str:
        if not self.has_skills:
            return ""
        self._ensure_loaded()
        blocks = [entry.instructions.strip() for entry in self._entries if entry.instructions.strip()]
        if not blocks:
            return ""
        return "\n\n".join(blocks)

    def execute_tool(self, tool_name: str, args: Dict[str, Any], timeout_s: int) -> Dict[str, Any]:
        self._ensure_loaded()
        if self._load_error:
            return {"ok": False, "error": self._load_error, "tool_name": tool_name}

        if self.config.max_skill_calls_per_session >= 0 and self._calls_made >= self.config.max_skill_calls_per_session:
            return {
                "ok": False,
                "error": f"Max skill calls per session reached ({self.config.max_skill_calls_per_session})",
                "tool_name": tool_name,
            }

        entry = self._by_tool_name.get(tool_name)
        if not entry:
            return {"ok": False, "error": f"Unknown tool call '{tool_name}' for agent", "tool_name": tool_name}

        effective_timeout = self.config.skill_timeout or timeout_s
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(entry.instance.execute, args)
            try:
                result = future.result(timeout=effective_timeout)
                self._calls_made += 1
                return {"ok": True, "tool_name": tool_name, "skill_id": entry.skill_id, "result": result}
            except concurrent.futures.TimeoutError:
                return {
                    "ok": False,
                    "tool_name": tool_name,
                    "skill_id": entry.skill_id,
                    "error": f"Skill execution timed out after {effective_timeout}s",
                }
            except Exception as exc:  # noqa: BLE001
                logger.error("Skill execute failed for %s: %s", entry.skill_id, exc)
                return {"ok": False, "tool_name": tool_name, "skill_id": entry.skill_id, "error": str(exc)}

    def _ensure_loaded(self) -> None:
        if self._loaded or not self.has_skills:
            return
        self._loaded = True
        try:
            loader_mod = importlib.import_module("skillware.core.loader")
            skill_loader = getattr(loader_mod, "SkillLoader")
        except Exception as exc:  # noqa: BLE001
            self._load_error = (
                "Skillware is not installed or could not be imported. "
                "Install with: pip install skillware"
            )
            logger.warning("Skillware import failed: %s", exc)
            return

        for skill_id in self.config.skills:
            try:
                bundle = skill_loader.load_skill(skill_id)
                tool_def = skill_loader.to_openai_tool(bundle)
                tool_name = tool_def.get("function", {}).get("name", "")
                skill_class = self._pick_skill_class(bundle.get("module"))
                if skill_class is None:
                    raise ValueError(f"No executable skill class found for '{skill_id}'")
                overrides = self.config.skill_settings.get(skill_id, {})
                instance = skill_class(config=overrides)
                entry = SkillEntry(
                    skill_id=skill_id,
                    tool_name=tool_name,
                    instructions=bundle.get("instructions", ""),
                    instance=instance,
                    tool_def=tool_def,
                )
                self._entries.append(entry)
                self._by_tool_name[tool_name] = entry
            except Exception as exc:  # noqa: BLE001
                self._load_error = f"Failed loading skill '{skill_id}': {exc}"
                logger.error("Skill load failed for %s: %s", skill_id, exc)
                return

    @staticmethod
    def _pick_skill_class(module: Any) -> Optional[type]:
        if module is None:
            return None
        candidates: List[type] = []
        for _, value in inspect.getmembers(module, inspect.isclass):
            if value.__module__ != module.__name__:
                continue
            if value.__name__.startswith("_"):
                continue
            if hasattr(value, "execute") and callable(getattr(value, "execute")):
                candidates.append(value)
        if not candidates:
            return None
        named = [c for c in candidates if c.__name__.endswith("Skill")]
        return named[0] if named else candidates[0]


def build_tool_messages(tool_calls: List[Dict[str, Any]], tool_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build OpenAI-compatible tool messages for second-pass synthesis."""
    messages: List[Dict[str, Any]] = []
    if tool_calls:
        messages.append({"role": "assistant", "content": "", "tool_calls": tool_calls})
    for result in tool_results:
        messages.append(
            {
                "role": "tool",
                "tool_call_id": result["tool_call_id"],
                "name": result["tool_name"],
                "content": json.dumps(result["payload"], ensure_ascii=True),
            }
        )
    return messages
