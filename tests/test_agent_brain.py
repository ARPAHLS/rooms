"""Tests for the AgentBrain abstract base class."""

import pytest

from rooms.brains import AgentBrain


def test_agent_brain_cannot_be_instantiated():
    """The ABC has abstract methods and cannot be constructed directly."""
    with pytest.raises(TypeError):
        AgentBrain()  # type: ignore[abstract]


def test_subclass_must_implement_generate():
    """A subclass that does not implement generate() stays abstract."""

    class Incomplete(AgentBrain):
        pass

    with pytest.raises(TypeError):
        Incomplete()  # type: ignore[abstract]


def test_minimal_subclass_works():
    """A subclass that implements generate() can be instantiated and called."""

    class Echo(AgentBrain):
        def generate(self, context_messages, override_params=None):
            last = context_messages[-1]["content"] if context_messages else ""
            return {"content": last, "skill_events": []}

    brain = Echo()
    result = brain.generate([{"role": "user", "content": "hello"}])
    assert result == {"content": "hello", "skill_events": []}


def test_generate_result_shape():
    """The result matches the shape Agent.generate_response_with_events returns."""

    class Stub(AgentBrain):
        def generate(self, context_messages, override_params=None):
            return {"content": "ok", "skill_events": [{"event_type": "skill_execution"}]}

    result = Stub().generate([])
    assert set(result.keys()) == {"content", "skill_events"}
    assert isinstance(result["content"], str)
    assert isinstance(result["skill_events"], list)


def test_override_params_passed_through():
    """Brains receive override_params from the caller."""

    class Spy(AgentBrain):
        def generate(self, context_messages, override_params=None):
            self.last_override = override_params
            return {"content": "", "skill_events": []}

    brain = Spy()
    brain.generate([], override_params={"temperature": 0.1})
    assert brain.last_override == {"temperature": 0.1}
