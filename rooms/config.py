import enum
from typing import List, Optional
from pydantic import BaseModel, Field

class SessionType(str, enum.Enum):
    ROUND_ROBIN = "round_robin"
    DYNAMIC = "dynamic"
    ARGUMENTATIVE = "argumentative"

class ModelType(str, enum.Enum):
    LITELLM = "litellm"
    CUSTOM_FUNCTION = "custom_function"

class AgentConfig(BaseModel):
    name: str = Field(..., description="Name of the agent")
    system_prompt: str = Field(..., description="System prompt defining the role")
    expertise: List[str] = Field(default_factory=list, description="Keywords defining expertise areas")
    model_type: ModelType = Field(default=ModelType.LITELLM, description="Whether to use LiteLLM routing or a custom python script")
    model: str = Field(default="ollama/llama3", description="LiteLLM compatible model name or placeholder for custom")
    temperature: float = Field(default=0.7, description="Generation temperature")
    max_tokens: Optional[int] = Field(default=None, description="Max generated tokens")
    timeout: int = Field(default=30, description="Timeout in seconds for model generation")
    color: str = Field(default="blue", description="CLI output color for this agent")
    custom_function_path: Optional[str] = Field(default=None, description="Path to .py file if model_type is custom_function")
    custom_function_name: Optional[str] = Field(default=None, description="Name of the python function to call")
    custom_instructions: Optional[str] = Field(None, description="Per session custom instructions from the user")

class SessionConfig(BaseModel):
    topic: str = Field(..., description="The main topic or problem for this session")
    agents: List[AgentConfig] = Field(..., description="Agents participating in the room")
    orchestrator: Optional[AgentConfig] = Field(default=None, description="An overarching agent to guide or summarize the conversation periodically")
    session_type: SessionType = Field(default=SessionType.DYNAMIC, description="Type of turn logic to employ")
    max_turns: int = Field(default=20, description="Maximum number of agent turns before ending or pausing")
    human_in_the_loop_turns: int = Field(default=0, description="Prompt user for input every N turns. 0 to disable.")

