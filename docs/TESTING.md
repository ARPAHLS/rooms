# Testing Strategy

The Multi-Agent Rooms framework places paramount importance on reliability and predictable logic flow, particularly concerning the orchestration of multiple AI agents and the preservation of human-in-the-loop interventions.

## Our Testing Approach

We utilize `pytest` as our core testing framework, coupled with the native `unittest.mock` library.

**Why Mocking?**
Testing live AI agents is inherently non-deterministic, slow, and expensive. To verify the *logic* of the room (e.g. "Does the orchestrator speak exactly every 3 turns?", "Does @mention force the correct agent?"), we **mock** the `Agent.generate_response` method. This guarantees tests run in milliseconds and verifies framework logic exactly, without relying on local GPU availability or network conditions.

## Running Tests

Always run via `pytest` with `PYTHONPATH` set so the `rooms` package is importable:

```bash
# Windows (PowerShell)
$env:PYTHONPATH="."; python -m pytest tests/ -v

# Unix/Mac
PYTHONPATH=. python -m pytest tests/ -v
```

> **Note**: Running `python tests/test_session.py` directly will fail with a `ModuleNotFoundError`. Always use `pytest`.

## Current Test Coverage (10 tests)

| Test | What It Verifies |
|---|---|
| `test_round_robin_session` | Agents alternate correctly; turn returns `None` after `max_turns` |
| `test_human_in_the_loop` | `needs_human_input()` triggers at the correct interval |
| `test_orchestrator` | Orchestrator fires exactly once every 3 turns, never loops |
| `test_custom_function_execution` | Custom `.py` scripts act as agent brains correctly |
| `test_user_profile_in_session` | User name and background appear in the session intro |
| `test_add_user_message_timestamp` | User messages include a `timestamp` field |
| `test_pass_mechanic_skips_turn` | `PASS` responses are marked `skipped` and not added to history |
| `test_at_mention_forces_agent` | `@AgentName` in user input forces that agent to respond next |
| `test_expertise_scoring_dynamic` | Best-matching expertise agent is selected in `dynamic` mode |
| `test_early_hitl_when_user_addressed` | `needs_human_input()` triggers immediately when user is named |

## How to Write Custom Tests

### Step 1: Define a Mock Configuration

```python
from rooms.config import SessionConfig, AgentConfig, SessionType

config = SessionConfig(
    topic="Test Topic",
    agents=[
        AgentConfig(name="Agent1", system_prompt="Sys", expertise=["law"]),
        AgentConfig(name="Agent2", system_prompt="Sys", expertise=["engineering"]),
    ],
    session_type=SessionType.DYNAMIC,
    max_turns=3
)
```

### Step 2: Instantiate Agents and Mock Inference

```python
from rooms.agent import Agent
from unittest.mock import MagicMock

agent1 = Agent(config.agents[0])
agent1.generate_response = MagicMock(return_value="Legal perspective")
agent2 = Agent(config.agents[1])
agent2.generate_response = MagicMock(return_value="Technical perspective")
```

### Step 3: Instantiate Session and Assert

```python
from rooms.session import Session

session = Session(config, [agent1, agent2], user_profile={"name": "Theo", "background": "Researcher"})

# Test @mention forcing
session.add_user_message("Theo", "@Agent2 what is your take?")
t1 = session.generate_next_turn()
assert t1["role"] == "Agent2"

# Test PASS mechanic
agent2.generate_response = MagicMock(return_value="PASS")
t2 = session.generate_next_turn()
assert t2.get("skipped") is True

# Test timestamp presence
assert "timestamp" in t1
```
