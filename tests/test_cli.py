import os
from argparse import Namespace
from unittest.mock import patch

import cli
from rooms.config import AgentConfig


def test_set_session_env_key_tracks_new_keys():
    tracked = []
    key = "ROOMS_TEST_WIZARD_KEY"
    os.environ.pop(key, None)

    cli._set_session_env_key(tracked, key, "secret-value")

    assert tracked == [key]
    assert os.environ[key] == "secret-value"

    cli._cleanup_session_env(tracked)
    assert key not in os.environ


def test_set_session_env_key_skips_existing_keys():
    tracked = []
    key = "ROOMS_TEST_EXISTING_KEY"
    os.environ[key] = "pre-existing"

    cli._set_session_env_key(tracked, key, "new-value")

    assert tracked == []
    assert os.environ[key] == "pre-existing"

    os.environ.pop(key, None)


def test_cleanup_session_env_removes_only_tracked_keys():
    wizard_key = "ROOMS_TEST_CLEANUP_WIZARD"
    existing_key = "ROOMS_TEST_CLEANUP_EXISTING"
    os.environ.pop(wizard_key, None)
    os.environ[existing_key] = "keep-me"

    tracked = []
    cli._set_session_env_key(tracked, wizard_key, "wizard-secret")
    cli._cleanup_session_env(tracked)

    assert wizard_key not in os.environ
    assert os.environ[existing_key] == "keep-me"

    os.environ.pop(existing_key, None)


def test_cmd_skills_list_success():
    fake = [{"id": "finance/wallet_screening", "description": "Screen wallets"}]
    with patch.object(cli, "list_skills", return_value=(fake, None)):
        rc = cli.cmd_skills_list(Namespace())
    assert rc == 0


def test_cmd_skills_list_handles_missing_skillware():
    with patch.object(cli, "list_skills", return_value=([], "Skillware is not installed")):
        rc = cli.cmd_skills_list(Namespace())
    assert rc == 0


def test_cmd_skills_inspect_success():
    payload = {
        "id": "finance/wallet_screening",
        "version": "1.0.0",
        "description": "Screen wallet risk",
        "inputs": {"wallet": "string"},
        "instructions": "Use carefully.",
    }
    with patch.object(cli, "inspect_skill", return_value=(payload, None)):
        rc = cli.cmd_skills_inspect(Namespace(skill_id="finance/wallet_screening"))
    assert rc == 0


def test_cmd_skills_suggest_requires_expertise():
    rc = cli.cmd_skills_suggest(Namespace(expertise=""))
    assert rc == 1


def test_cmd_skills_suggest_success():
    available = [
        {"id": "finance/wallet_screening", "title": "Wallet Screening", "description": "risk sanctions checks"},
        {"id": "legal/contract_parser", "title": "Contract Parser", "description": "contracts"},
    ]
    with patch.object(cli, "list_skills", return_value=(available, None)):
        rc = cli.cmd_skills_suggest(Namespace(expertise="finance,risk"))
    assert rc == 0


def test_assign_skills_in_wizard_manual_ids():
    cfg = AgentConfig(name="A", system_prompt="S")
    prompts = iter(["finance/wallet_screening", "mode=strict"])

    def _ask(_text, default="", **_kwargs):
        return next(prompts)

    with patch.object(cli, "list_skills", return_value=([], "Skillware missing")), \
         patch.object(cli.Confirm, "ask", side_effect=[True, True, True]), \
         patch.object(cli.Prompt, "ask", side_effect=_ask):
        cli._assign_skills_in_wizard(cfg)

    assert cfg.skills == ["finance/wallet_screening"]
    assert cfg.skill_settings["finance/wallet_screening"]["mode"] == "strict"
