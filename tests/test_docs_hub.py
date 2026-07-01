"""Smoke tests for documentation hub structure and internal links."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS = REPO_ROOT / "docs"

MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _collect_markdown_files() -> list[Path]:
    files = [REPO_ROOT / "README.md", REPO_ROOT / "CONTRIBUTING.md"]
    files.extend(sorted(DOCS.glob("*.md")))
    return files


def _resolve_link(source: Path, target: str) -> Path:
    raw = target.split("#", 1)[0].strip()
    if not raw or raw.startswith("http"):
        return Path()  # skip external / anchors-only
    if raw.startswith("/"):
        return REPO_ROOT / raw.lstrip("/")
    return (source.parent / raw).resolve()


@pytest.mark.parametrize("path", _collect_markdown_files(), ids=lambda p: p.name)
def test_doc_hub_files_exist(path: Path) -> None:
    assert path.is_file(), f"Expected doc file missing: {path}"


def test_docs_readme_lists_core_guides() -> None:
    hub = (DOCS / "README.md").read_text(encoding="utf-8")
    for name in (
        "introduction.md",
        "SETTINGS.md",
        "ARCHITECTURE.md",
        "EXAMPLES.md",
        "SKILLWARE.md",
        "TESTING.md",
    ):
        assert name in hub, f"docs/README.md should link to {name}"


@pytest.mark.parametrize("path", _collect_markdown_files(), ids=lambda p: p.name)
def test_internal_markdown_links_resolve(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    broken: list[str] = []
    for match in MARKDOWN_LINK.finditer(text):
        target = match.group(1)
        resolved = _resolve_link(path, target)
        if not str(resolved):
            continue
        if not resolved.exists():
            broken.append(f"{target} -> {resolved}")
    assert not broken, f"Broken links in {path}:\n" + "\n".join(broken)
