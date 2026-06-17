import types

from rooms.skills_cli import _normalize_skill_record, inspect_skill, list_skills, suggest_skills


def test_normalize_skill_record_string():
    out = _normalize_skill_record("finance/wallet_screening")
    assert out["id"] == "finance/wallet_screening"
    assert out["title"] == "finance/wallet_screening"


def test_list_skills_via_loader_api(monkeypatch):
    class FakeLoader:
        @staticmethod
        def list_skills():
            return [
                {"id": "finance/wallet_screening", "description": "Wallet checks"},
                {"id": "legal/contract_parser", "description": "Parse contracts"},
            ]

    monkeypatch.setattr(
        "rooms.skills_cli.importlib.import_module",
        lambda _name: types.SimpleNamespace(SkillLoader=FakeLoader),
    )
    skills, err = list_skills()
    assert err is None
    assert len(skills) == 2
    assert skills[0]["id"] == "finance/wallet_screening"


def test_inspect_skill_returns_manifest(monkeypatch):
    class FakeLoader:
        @staticmethod
        def load_skill(_skill_id):
            return {
                "manifest": {
                    "name": "finance/wallet_screening",
                    "version": "1.2.3",
                    "description": "Screen wallet risk",
                    "inputs": {"wallet": "string"},
                },
                "instructions": "Use tool for wallet checks.",
            }

    monkeypatch.setattr(
        "rooms.skills_cli.importlib.import_module",
        lambda _name: types.SimpleNamespace(SkillLoader=FakeLoader),
    )
    payload, err = inspect_skill("finance/wallet_screening")
    assert err is None
    assert payload["id"] == "finance/wallet_screening"
    assert payload["version"] == "1.2.3"


def test_suggest_skills_keyword_match():
    skills = [
        {"id": "finance/wallet_screening", "title": "Wallet Screening", "description": "Risk and sanctions"},
        {"id": "ops/log_parser", "title": "Log Parser", "description": "infra diagnostics"},
    ]
    suggested = suggest_skills(skills, ["finance", "risk"])
    assert len(suggested) == 1
    assert suggested[0]["id"] == "finance/wallet_screening"
