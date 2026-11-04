"""Inference backends for agents.

An AgentBrain is the unit that turns a conversation history into the next
agent response. Concrete brains live next to this module; the abstract base
class here is the contract the rest of the framework will depend on.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypedDict

__all__ = ["AgentBrain", "BrainResult"]


class BrainResult(TypedDict):
    """The structured result every AgentBrain returns from ``generate``.

    Matches the shape ``Agent.generate_response_with_events`` already returns
    today, so callers can swap implementations without touching parsing code.
    """

    content: str
    skill_events: List[Dict[str, Any]]


class AgentBrain(ABC):
    """Abstract base class for agent inference backends.

    Concrete implementations are expected to take an ``AgentConfig`` (and,
    optionally, a ``SkillRuntime``) in their constructor:

        def __init__(
            self,
            config: AgentConfig,
            skill_runtime: Optional[SkillRuntime] = None,
        ) -> None: ...

    This is the uniform initialization contract the Step 2–4 brains
    (``LiteLLMBrain``, ``CustomFunctionBrain``) and any external plugins
    should follow.
    """

    @abstractmethod
    def generate(
        self,
        context_messages: List[Dict[str, str]],
        override_params: Optional[Dict[str, Any]] = None,
    ) -> BrainResult:
        """Generate a response from the given context.

        Args:
            context_messages: The conversation history, already including the
                system message as the first element.
            override_params: Optional runtime parameters (e.g. temperature)
                that override the brain's configured defaults.

        Returns:
            A ``BrainResult`` with ``content`` (a string, possibly empty) and
            ``skill_events`` (a list, possibly empty).
        """
        raise NotImplementedError