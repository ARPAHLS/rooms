import math
from typing import List, Dict, Any, Optional

from .config import SessionConfig, SessionType
from .agent import Agent

class Session:
    def __init__(self, config: SessionConfig, agents: List[Agent], user_profile: Optional[Dict[str, str]] = None):
        self.config = config
        self.agents = agents
        self.user_profile = user_profile  # {"name": "...", "background": "..."}
        self.history: List[Dict[str, str]] = []  # List of {"role": "username", "content": "msg"}
        self.turn_count = 0
        self._last_orchestrator_turn = -1  # Track last orch turn to prevent re-triggering
        
        # Build global introduction including user if provided
        agent_names = ', '.join([a.name for a in self.agents])
        user_intro = ""
        if self.user_profile:
            user_intro = f"\nUser Participant: {self.user_profile['name']} - {self.user_profile.get('background', '')}"
        self.global_intro = (
            f"The room is active. Topic: {self.config.topic}\n"
            f"Participating Agents: {agent_names}{user_intro}\n"
        )
        self.history.append({"role": "system", "content": self.global_intro})

        self._agent_index = 0

    def add_user_message(self, username: str, message: str):
        """Inject a human message into the session history."""
        self.history.append({"role": username, "content": message})

    def get_agent_context(self, current_agent: Agent) -> List[Dict[str, str]]:
        """Format history into an LLM context."""
        context = []
        for msg in self.history:
            role = "user"  # litellm expects user/assistant/system
            # If the specific agent spoke, it's 'assistant'
            if msg["role"] == current_agent.name:
                role = "assistant"
            elif msg["role"] == "system":
                role = "system"
            
            content = msg["content"]
            # If someone else spoke, attribute it in the content
            if msg["role"] not in (current_agent.name, "system"):
                content = f"[{msg['role']} said]: {content}"

            context.append({"role": role, "content": content})
        return context

    def generate_next_turn(self) -> Optional[Dict[str, str]]:
        """Determine next agent, get response, and log it."""
        if self.turn_count >= self.config.max_turns:
            return None
            
        # Optional Orchestrator Intervention (runs every 3 turns, but only ONCE per interval)
        if (
            self.config.orchestrator
            and self.turn_count > 0
            and self.turn_count % 3 == 0
            and self._last_orchestrator_turn != self.turn_count  # prevent re-triggering
        ):
            self._last_orchestrator_turn = self.turn_count
            orch_agent = Agent(self.config.orchestrator)
            context = self.get_agent_context(orch_agent)
            
            msg = orch_agent.generate_response(context)
            self.turn_count += 1  # Always increment, even for orchestrator turns
            if "PASS" not in msg:
                turn_data = {"role": f"Orchestrator ({orch_agent.name})", "content": msg, "color": orch_agent.config.color}
                self.history.append(turn_data)
                return turn_data
            # If PASS, fall through to normal agent turn below
            
        agent = self._select_next_agent()
        context = self.get_agent_context(agent)
        
        response_text = agent.generate_response(context)
        
        turn_data = {"role": agent.name, "content": response_text, "color": agent.config.color}
        self.history.append(turn_data)
        self.turn_count += 1
        return turn_data

    def _select_next_agent(self) -> Agent:
        """Select who talks next based on SessionType."""
        if self.config.session_type == SessionType.ROUND_ROBIN:
            agent = self.agents[self._agent_index]
            self._agent_index = (self._agent_index + 1) % len(self.agents)
            return agent
        
        elif self.config.session_type == SessionType.ARGUMENTATIVE:
            # Simple alternating between first two agents for arguments
            if len(self.agents) >= 2:
                agent = self.agents[self.turn_count % 2]
                return agent
            return self.agents[0]
            
        elif self.config.session_type == SessionType.DYNAMIC:
            # Placeholder for dynamic: if the last message mentions an agent by name, they go.
            # Else, round robin fallback.
            if len(self.history) > 1:
                last_msg = self.history[-1]["content"].lower()
                for i, agent in enumerate(self.agents):
                    if agent.name.lower() in last_msg:
                        self._agent_index = (i + 1) % len(self.agents)  # prime next
                        return agent
                        
            # fallback to round robin
            agent = self.agents[self._agent_index]
            self._agent_index = (self._agent_index + 1) % len(self.agents)
            return agent

        return self.agents[0]

    def needs_human_input(self) -> bool:
        """Check if it's time to prompt the human according to config."""
        if self.config.human_in_the_loop_turns <= 0:
            return False
        # If we hit the interval exactly
        return self.turn_count > 0 and self.turn_count % self.config.human_in_the_loop_turns == 0
