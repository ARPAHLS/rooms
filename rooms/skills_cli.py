"""Rooms-native Skillware CLI helpers."""

from __future__ import annotations

import importlib
from typing import Any, Dict, List, Optional, Tuple


def load_skill_loader() -> Tuple[Optional[Any], Optional[str]]:
    """Return SkillLoader class or a user-facing error message."""
    try:
        loader_mod = importlib.import_module("skillware.core.loader")
        loader = getattr(loader_mod, "SkillLoader", None)
        if loader is None:
            return None, "Skillware was found but SkillLoader is unavailable."
        return loader, None
    except Exception:
        return None, "Skillware is not installed. Install with: pip install skillware"


def _normalize_skill_record(raw: Any) -> Dict[str, str]:
    if isinstance(raw, str):
        return {"id": raw, "title": raw, "description": ""}
    if not isinstance(raw, dict):
        text = str(raw)
        return {"id": text, "title": text, "description": ""}

    skill_id = (
        raw.get("id")
        or raw.get("name")
        or raw.get("skill_id")
        or raw.get("slug")
        or raw.get("manifest", {}).get("name")
        or "unknown"
    )
    title = raw.get("title") or raw.get("display_name") or skill_id
    description = raw.get("description") or raw.get("summary") or ""
    return {"id": str(skill_id), "title": str(title), "description": str(description)}


def list_skills(limit: int = 200) -> Tuple[List[Dict[str, str]], Optional[str]]:
    """List available skills from Skillware discovery APIs."""
    loader, err = load_skill_loader()
    if err:
        return [], err

    candidates = (
        "list_skills",
        "discover_skills",
        "discover",
        "list_available_skills",
    )
    for meth in candidates:
        fn = getattr(loader, meth, None)
        if not callable(fn):
            continue
        try:
            result = fn()
            if isinstance(result, dict):
                items = list(result.values())
            else:
                items = list(result or [])
            normalized = [_normalize_skill_record(item) for item in items][:limit]
            normalized.sort(key=lambda x: x["id"])
            return normalized, None
        except Exception as exc:  # noqa: BLE001
            return [], f"Skill discovery failed via Skillware: {exc}"

    return [], "Skillware is installed but no supported discovery API was found."


def inspect_skill(skill_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Load one skill and return normalized inspect payload."""
    loader, err = load_skill_loader()
    if err:
        return None, err

    try:
        bundle = loader.load_skill(skill_id)
    except Exception as exc:  # noqa: BLE001
        return None, f"Could not load '{skill_id}': {exc}"

    manifest = bundle.get("manifest", {}) if isinstance(bundle, dict) else {}
    info = {
        "id": manifest.get("name", skill_id),
        "version": manifest.get("version", ""),
        "description": manifest.get("description", ""),
        "inputs": manifest.get("inputs", {}),
        "instructions": (bundle.get("instructions", "") if isinstance(bundle, dict) else ""),
    }
    return info, None


def suggest_skills(skills: List[Dict[str, str]], expertise: List[str]) -> List[Dict[str, str]]:
    """Suggest skills by lightweight keyword matching."""
    keywords = [k.strip().lower() for k in expertise if k and k.strip()]
    if not keywords:
        return []

    scored: List[Tuple[int, Dict[str, str]]] = []
    for skill in skills:
        haystack = f"{skill.get('id', '')} {skill.get('title', '')} {skill.get('description', '')}".lower()
        score = sum(1 for kw in keywords if kw in haystack)
        if score > 0:
            scored.append((score, skill))

    scored.sort(key=lambda item: (-item[0], item[1].get("id", "")))
    return [item[1] for item in scored]
