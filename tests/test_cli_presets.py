import os
from unittest.mock import MagicMock, patch, PropertyMock
import pytest

from cli import create_custom_agent_wizard, main_menu
from rooms.settings import RoomsSettings, DefaultsSettings, PresetSettings


@pytest.fixture
def mock_settings():
    return RoomsSettings(
        defaults=DefaultsSettings(
            litellm_model="ollama/gemma4:e2b",
            orchestrator_model="ollama/gemma4:e2b",
            temperature=0.7,
            timeout=30
        ),
        presets={
            "local-ollama": PresetSettings(litellm_model="ollama/gemma4:e2b"),
            "openai": PresetSettings(litellm_model="gpt-4o", api_key_env="OPENAI_API_KEY")
        }
    )


def test_create_custom_agent_wizard_with_preset(mock_settings):
    tracked_keys = []
    
    with patch("cli.Prompt.ask") as mock_ask, \
         patch("cli.Confirm.ask") as mock_confirm, \
         patch("cli._set_session_env_key"):
         
        # Interactive Wizard Sequence:
        # 1. Name, 2. System Prompt, 3. Expertise, 4. Preset Choice Selection, 5. Display Color, 6. Temperature
        mock_ask.side_effect = ["TestAgent", "You are a tester", "testing", "openai", "blue", "0.7"]
        mock_confirm.side_effect = [True]

        config = create_custom_agent_wizard(mock_settings, tracked_env_keys=tracked_keys)
        
        assert config.name == "TestAgent"
        assert config.model == "gpt-4o"
        assert config.system_prompt == "You are a tester"


def test_main_menu_orchestrator_with_preset(mock_settings):
    with patch("cli.Prompt.ask") as mock_ask, \
         patch("cli.Confirm.ask") as mock_confirm, \
         patch("cli.Session") as mock_session_class:
         
        # Setup the mock instance behavior for the session object loop
        mock_session_instance = MagicMock()
        mock_session_instance.turn_count = 0
        
        # side_effect controls how many times the loop evaluates session.turn_count < config.max_turns
        type(mock_session_instance).turn_count = PropertyMock(side_effect=[0, 25])
        mock_session_instance.needs_human_input.return_value = False
        mock_session_instance.generate_next_turn.return_value = {"role": "Orchestrator", "content": "Hello", "color": "gold"}
        mock_session_class.return_value = mock_session_instance

        # CLI Layout Prompts Sequence:
        # User Name, User Background, Chat Topic, Max Turns, Session Type Selection, HITL Turns, Orchestrator Prompt, Preset Name Selection
        mock_ask.side_effect = ["User", "Tester", "Test Topic", "20", "dynamic", "5", "System Moderator Prompt", "local-ollama"]
        
        # Confirm Loop Prompts Sequence:
        # 3x False (Skip default agents)
        # 1x False (Skip custom agent wizard loop)
        # 1x True  (Configure Orchestrator)
        # 1x True  (Use preset for orchestrator)
        mock_confirm.side_effect = [False, False, False, False, True, True]

        main_menu(mock_settings)
        
        assert mock_session_class.called
        passed_config = mock_session_class.call_args[1]["config"]
        assert passed_config.orchestrator is not None
        assert passed_config.orchestrator.model == "ollama/gemma4:e2b"