import pytest
from unittest.mock import MagicMock
from rooms.config import SessionConfig, AgentConfig, SessionType
from rooms.agent import Agent
from rooms.session import Session

def test_round_robin_session():
    # Setup
    config = SessionConfig(
        topic="Test Topic",
        agents=[
            AgentConfig(name="AgentA", system_prompt="SysA", color="red"),
            AgentConfig(name="AgentB", system_prompt="SysB", color="blue")
        ],
        session_type=SessionType.ROUND_ROBIN,
        max_turns=2,
        human_in_the_loop_turns=0
    )
    
    agent_a = Agent(config.agents[0])
    agent_b = Agent(config.agents[1])
    
    # Mock LLM calls
    agent_a.generate_response = MagicMock(return_value="A response")
    agent_b.generate_response = MagicMock(return_value="B response")
    
    session = Session(config, [agent_a, agent_b])
    
    # Turn 1
    t1 = session.generate_next_turn()
    assert t1["role"] == "AgentA"
    assert "A response" in t1["content"]
    
    # Turn 2
    t2 = session.generate_next_turn()
    assert t2["role"] == "AgentB"
    assert "B response" in t2["content"]
    
    # Check max turns
    t3 = session.generate_next_turn()
    assert t3 is None

def test_human_in_the_loop():
    config = SessionConfig(
        topic="Test Topic",
        agents=[AgentConfig(name="AgentA", system_prompt="SysA")],
        session_type=SessionType.ROUND_ROBIN,
        max_turns=5,
        human_in_the_loop_turns=2
    )
    agent_a = Agent(config.agents[0])
    agent_a.generate_response = MagicMock(return_value="Response")
    session = Session(config, [agent_a])
    
    session.generate_next_turn() # turn 1 (doesn't trigger hitl)
    assert not session.needs_human_input()
    
    session.generate_next_turn() # turn 2 (triggers hitl because it's multiple of 2)
    assert session.needs_human_input()

def test_orchestrator():
    config = SessionConfig(
        topic="Test Topic",
        agents=[AgentConfig(name="AgentA", system_prompt="SysA")],
        orchestrator=AgentConfig(name="Orch", system_prompt="SysO", color="black"),
        session_type=SessionType.ROUND_ROBIN,
        max_turns=5,
        human_in_the_loop_turns=0
    )
    
    agent_a = Agent(config.agents[0])
    agent_a.generate_response = MagicMock(return_value="A response")
    
    # We need to mock the Orch agent generation inside the session
    session = Session(config, [agent_a])
    
    # Turn 1
    t1 = session.generate_next_turn()
    assert t1["role"] == "AgentA"
    
    # Turn 2
    t2 = session.generate_next_turn()
    assert t2["role"] == "AgentA"
    
    # Turn 3 (Turn count is 2 (0-indexed 1st, 2nd, 3rd) -> triggers when turn_count % 3 == 0 but after the turn logic. Wait, the logic is modulo on `self.turn_count`, which is incremented after generation. 
    # Let's see: start at 0. generate()-> turn_count=1. turn_count%3 == 1 (no orch)
    # turn 2 -> turn_count=2. turn_count%3 == 2 (no orch)
    # before turn 3 -> turn_count=2. turn_count>0 and turn_count%3==0 is False.
    # Ah! The % 3 == 0 will trigger when turn_count == 3 (before the 4th turn!). Let's verify that.
    t3 = session.generate_next_turn()
    assert t3["role"] == "AgentA"
    
    # Turn 4 (Before this turn, turn_count = 3. 3 % 3 == 0 -> Orchestrator triggers!)
    # Mock Litellm or Agent initialization inside generate_next_turn
    import rooms.session
    original_agent = rooms.session.Agent
    try:
        mock_orch = MagicMock()
        mock_orch.name = "Orch"
        mock_orch.generate_response.return_value = "Orch response"
        rooms.session.Agent = MagicMock(return_value=mock_orch)
        
        t4 = session.generate_next_turn()
        assert "Orchestrator" in t4["role"]
        assert t4["content"] == "Orch response"
    finally:
        rooms.session.Agent = original_agent

def test_custom_function_execution():
    from rooms.config import ModelType
    
    # We create a dummy test module for the custom function
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("def my_func(messages):\n    return 'Hello from custom script!'\n")
        temp_path = f.name
        
    try:
        config = SessionConfig(
            topic="Custom Execution",
            agents=[
                AgentConfig(
                    name="Custom Agent",
                    system_prompt="sys",
                    model_type=ModelType.CUSTOM_FUNCTION,
                    custom_function_path=temp_path,
                    custom_function_name="my_func"
                )
            ],
            session_type=SessionType.ROUND_ROBIN,
            max_turns=1,
            human_in_the_loop_turns=0
        )
        
        agent_custom = Agent(config.agents[0])
        session = Session(config, [agent_custom])
        
        # We don't mock generate_response here, we want it to actually run `_execute_custom_function`
        turn1 = session.generate_next_turn()
        assert turn1["role"] == "Custom Agent"
        assert turn1["content"] == "Hello from custom script!"
        
    finally:
        os.remove(temp_path)
