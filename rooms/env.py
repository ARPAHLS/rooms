"""Process environment bootstrap for Rooms."""

from __future__ import annotations

from pathlib import Path
from typing import List

_BOOTSTRAPPED = False


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def dotenv_search_paths() -> List[Path]:
    """Return candidate .env paths, highest priority first."""
    seen: set[Path] = set()
    paths: List[Path] = []
    for root in (Path.cwd(), repo_root()):
        candidate = (root / ".env").resolve()
        if candidate not in seen:
            seen.add(candidate)
            paths.append(candidate)
    return paths


def bootstrap_environment(*, force: bool = False) -> List[Path]:
    """
    Load optional .env file into process environment.

    - Prefers `./.env` in the current working directory, then repository root.
    - Uses override=False so real shell/CI environment variables always win.
    - Safe to call multiple times.
    """
    global _BOOTSTRAPPED
    if _BOOTSTRAPPED and not force:
        return []

    try:
        from dotenv import load_dotenv
    except ImportError:
        _BOOTSTRAPPED = True
        return []

    loaded: List[Path] = []
    for env_path in dotenv_search_paths():
        if env_path.is_file():
            load_dotenv(env_path, override=False)
            loaded.append(env_path)
            break

    _BOOTSTRAPPED = True
    return loaded
