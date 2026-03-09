# Testing Strategy

The Multi-Agent Rooms framework places paramount importance on reliability and predictable logic flow, particularly concerning the orchestration of multiple AI agents and the preservation of human-in-the-loop interventions.

## Our Testing Approach

We utilize `pytest` as our core testing framework, coupled with the native `unittest.mock` library. 

**Why Mocking?**
Testing live AI agents is inherently non-deterministic, slow, and expensive (if using commercial APIs). To verify the *logic* of the room (e.g. "Does the orchestrator speak exactly every 3 turns?", "Does the session pause for human input after N turns?"), we **Mock** the `Agent.generate_response` method. This guarantees the tests run in milliseconds and tests our framework logic exactly, without relying on external network conditions or local GPU availability.

## Running Tests

To run the entire test suite, ensure your virtual environment is active and execute:
```bash
python -m pytest tests/
```

## How to Write Custom Tests

If you are developing new session logic (for example, a new `SessionType`), you should create a new test inside `tests/test_session.py`.

### Step 1: Define a Mock Configuration
Use the `Config` Pydantic models to define exactly the scenario you want to test.
```python
from rooms.config import SessionConfig, AgentConfig, SessionType

config = SessionConfig(
    topic="Test Topic",
    agents=[
        AgentConfig(name="Agent1", system_prompt="Sys"),
        AgentConfig(name="Agent2", system_prompt="Sys")
    ],
    session_type=SessionType.ROUND_ROBIN,
    max_turns=3
)
```

### Step 2: Instantiate Agents and Mock Inference
Create the agents and replace the expensive LLM call with a guaranteed string return.
```python
from rooms.agent import Agent
from unittest.mock import MagicMock

agent1 = Agent(config.agents[0])
agent2 = Agent(config.agents[1])

# This prevents real API calls during the test
agent1.generate_response = MagicMock(return_value="Agent 1 simulated response")
agent2.generate_response = MagicMock(return_value="Agent 2 simulated response")
```

### Step 3: Instantiate Session and Assert
Create the session and manually trigger `generate_next_turn()`. Use standard `assert` statements to verify the output matches your expected framework behavior.
```python
from rooms.session import Session

session = Session(config, [agent1, agent2])

turn1 = session.generate_next_turn()
assert turn1["role"] == "Agent1"
assert turn1["content"] == "Agent 1 simulated response"

turn2 = session.generate_next_turn()
assert turn2["role"] == "Agent2"
```
