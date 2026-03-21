import re
from datetime import datetime
from typing import List, Dict, Any, Optional

from .config import SessionConfig, SessionType
from .agent import Agent

def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _score_agent_expertise(agent: Agent, context_text: str) -> int:
    """Score an agent's expertise keywords against the context text.
    Returns the number of matching keywords found."""
    if not agent.config.expertise:
        return 0
    context_lower = context_text.lower()
    score = 0
    for kw in agent.config.expertise:
        if re.search(rf"\b{re.escape(kw)}\b", context_lower, re.IGNORECASE):
            score += 1
    return score

def _find_forced_agent(message: str, agents: List[Agent]) -> Optional[Agent]:
    """Detect if user explicitly addresses an agent by name via @Name or 'I want to hear X'.
    Returns the matching Agent or None."""
    message_lower = message.lower()

    # Check for @AgentName shorthand
    at_mentions = re.findall(r"@(\w[\w\s]*)", message, re.IGNORECASE)
    for mention in at_mentions:
        for agent in agents:
            # Match on first name or full name (case-insensitive)
            first_name = agent.name.split("(")[0].strip().lower()
            if mention.strip().lower() in (agent.name.lower(), first_name):
                return agent

    # Check for "I want to hear [Name]" or "What does [Name] think" patterns
    for agent in agents:
        first_name = agent.name.split("(")[0].strip()
        if re.search(rf"\b{re.escape(first_name.lower())}\b", message_lower):
            return agent

    return None

def _user_is_addressed(message: str, user_profile: Optional[Dict[str, str]]) -> bool:
    """Detect if the agent's response is directly addressing the user by name."""
    if not user_profile or not user_profile.get("name"):
        return False
    user_name = user_profile["name"].lower()
    return bool(re.search(rf"\b{re.escape(user_name)}\b", message.lower()))


class Session:
    def __init__(self, config: SessionConfig, agents: List[Agent], user_profile: Optional[Dict[str, str]] = None):
        self.config = config
        self.agents = agents
        self.user_profile = user_profile  # {"name": "...", "background": "..."}
        self.history: List[Dict[str, str]] = []
        self.turn_count = 0
        self._last_orchestrator_turn = -1
        self._forced_next_agent: Optional[Agent] = None  # Locked next agent from @mention or user direction
        self._hitl_triggered = False  # Track if early HITL was already triggered for current turn

        # Build global introduction including user if provided
        agent_names = ', '.join([a.name for a in self.agents])
        user_intro = ""
        if self.user_profile:
            user_intro = f"\nUser Participant: {self.user_profile['name']} - {self.user_profile.get('background', '')}"

        self.global_intro = (
            f"The room is active. Topic: {self.config.topic}\n"
            f"Participating Agents: {agent_names}{user_intro}\n"
            f"Note: Agents may respond with 'PASS' if they have nothing meaningful to add."
        )
        self.history.append({"role": "system", "content": self.global_intro, "timestamp": _now()})
        self._agent_index = 0

    def add_user_message(self, username: str, message: str):
        """Inject a human message into the session history, and detect @mention agent forcing."""
        self.history.append({"role": username, "content": message, "timestamp": _now()})

        # Check if the user addressed a specific agent
        forced = _find_forced_agent(message, self.agents)
        if forced:
            self._forced_next_agent = forced
        
        # Reset HITL trigger on user input
        self._hitl_triggered = False

    def get_agent_context(self, current_agent: Agent) -> List[Dict[str, str]]:
        """Format history into an LLM context including system prompt."""
        context = []
        for msg in self.history:
            role = "user"
            if msg["role"] == current_agent.name:
                role = "assistant"
            elif msg["role"] == "system":
                role = "system"

            content = msg["content"]
            if msg["role"] not in (current_agent.name, "system"):
                content = f"[{msg['role']} said]: {content}"

            context.append({"role": role, "content": content})
        return context

    def generate_next_turn(self) -> Optional[Dict[str, str]]:
        """Determine next agent, get response, and log it."""
        if self.turn_count >= self.config.max_turns:
            return None

        # Optional Orchestrator Intervention (every 3 turns, once per interval)
        if (
            self.config.orchestrator
            and self.turn_count > 0
            and self.turn_count % 3 == 0
            and self._last_orchestrator_turn != self.turn_count
        ):
            self._last_orchestrator_turn = self.turn_count
            orch_agent = Agent(self.config.orchestrator)
            context = self.get_agent_context(orch_agent)
            msg = orch_agent.generate_response(context)
            self.turn_count += 1
            if "PASS" not in msg:
                turn_data = {
                    "role": f"Orchestrator ({orch_agent.name})",
                    "content": msg,
                    "color": orch_agent.config.color,
                    "timestamp": _now()
                }
                self.history.append(turn_data)
                return turn_data
            # Orchestrator passed — fall through to normal turn

        # Resolve agent: forced @mention > smart selection
        if self._forced_next_agent:
            agent = self._forced_next_agent
            self._forced_next_agent = None
        else:
            agent = self._select_next_agent()

        context = self.get_agent_context(agent)
        response_text = agent.generate_response(context)

        # Handle PASS: agent has nothing to add — silently skip turn
        if response_text.strip().upper() == "PASS":
            self.turn_count += 1
            return {"role": agent.name, "content": "PASS", "color": agent.config.color, "timestamp": _now(), "skipped": True}

        turn_data = {
            "role": agent.name,
            "content": response_text,
            "color": agent.config.color,
            "timestamp": _now()
        }
        self.history.append(turn_data)
        self.turn_count += 1
        return turn_data

    def _select_next_agent(self) -> Agent:
        """Select who talks next based on SessionType and expertise scoring."""
        if self.config.session_type == SessionType.ROUND_ROBIN:
            agent = self.agents[self._agent_index]
            self._agent_index = (self._agent_index + 1) % len(self.agents)
            return agent

        elif self.config.session_type == SessionType.ARGUMENTATIVE:
            if len(self.agents) >= 2:
                return self.agents[self.turn_count % 2]
            return self.agents[0]

        elif self.config.session_type == SessionType.DYNAMIC:
            # Build context text from recent history for scoring
            recent = " ".join(m["content"] for m in self.history[-5:])

            # 1. Check for @mention or name reference in last user/agent message
            if self.history:
                last_content = self.history[-1].get("content", "")
                forced = _find_forced_agent(last_content, self.agents)
                if forced:
                    return forced

            # 2. Score all agents by expertise relevance to recent context
            scored = [(agent, _score_agent_expertise(agent, recent)) for agent in self.agents]
            scored.sort(key=lambda x: x[1], reverse=True)

            # If top scorer has meaningful score AND is NOT the agent that just spoke, pick them
            if scored and scored[0][1] > 0:
                last_speaker = self.history[-1].get("role", "") if self.history else ""
                for candidate, score in scored:
                    if candidate.name != last_speaker:
                        return candidate

            # 3. Fallback to round-robin
            agent = self.agents[self._agent_index]
            self._agent_index = (self._agent_index + 1) % len(self.agents)
            return agent

        return self.agents[0]

    def needs_human_input(self) -> bool:
        """Check if it's time for human input, including early trigger if user is directly addressed."""
        if self.config.human_in_the_loop_turns <= 0:
            return False

        # Early HITL: if the last agent's message addressed the user by name
        if not self._hitl_triggered and len(self.history) > 1:
            last = self.history[-1]
            if last.get("role") not in ("system",) and _user_is_addressed(last.get("content", ""), self.user_profile):
                self._hitl_triggered = True
                return True

        return self.turn_count > 0 and self.turn_count % self.config.human_in_the_loop_turns == 0
