import os
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm

# Main imports from your local package structure
from rooms.settings import RoomsSettings, PresetSettings
from rooms.config import SessionType, ModelType, AgentConfig, SessionConfig
from rooms.agent import Agent
from rooms.session import Session

console = Console()

def _set_session_env_key(env_key: str, tracked_env_keys: List[str]) -> None:
    """Helper to track and prompt for environment variables if not set."""
    if env_key and env_key not in os.environ:
        val = Prompt.ask(f"Enter value for [yellow]{env_key}[/yellow]")
        os.environ[env_key] = val
        tracked_env_keys.append(env_key)

def create_custom_agent_wizard(settings: RoomsSettings, tracked_env_keys: List[str]) -> AgentConfig:
    """Wizard interface to provision a new agent configuration block."""
    console.print("\n[bold cyan]--- Custom Agent Wizard ---[/bold cyan]")
    name = Prompt.ask("Agent Name")
    system_prompt = Prompt.ask("System Prompt")
    expertise_raw = Prompt.ask("Expertise (comma separated)")
    expertise = [e.strip() for e in expertise_raw.split(",") if e.strip()]
    
    model = ""
    use_preset = False
    
    if settings.presets:
        use_preset = Confirm.ask("Use a pre-configured model preset?")
        
    if use_preset and settings.presets:
        preset_options = list(settings.presets.keys())
        console.print(f"Available presets: [green]{', '.join(preset_options)}[/green]")
        preset_choice = Prompt.ask("Select a preset", choices=preset_options)
        preset: PresetSettings = settings.presets[preset_choice]
        
        model = preset.litellm_model
        if preset.api_key_env:
            _set_session_env_key(preset.api_key_env, tracked_env_keys)
    else:
        model_type_input = Prompt.ask("Model type", choices=["litellm", "ollama", "custom"])
        if model_type_input == "litellm":
            model = Prompt.ask("Enter LiteLLM model string (e.g. gpt-4o)")
            env_key = Prompt.ask("API Key Env Var (Optional, press Enter to skip)")
            if env_key:
                _set_session_env_key(env_key, tracked_env_keys)
        elif model_type_input == "ollama":
            model = Prompt.ask("Enter Ollama model name", default=settings.defaults.litellm_model)
        else:
            model = Prompt.ask("Enter custom model identification string")

    color = Prompt.ask("Display color", default="blue")
    temperature_str = Prompt.ask("Temperature (0.0 - 1.0)", default=str(settings.defaults.temperature))
    try:
        temperature = float(temperature_str)
    except ValueError:
        temperature = settings.defaults.temperature

    return AgentConfig(
        name=name,
        system_prompt=system_prompt,
        expertise=expertise,
        model_type=ModelType.LITELLM,
        model=model,
        temperature=temperature,
        color=color,
        custom_instructions=None
    )

def main_menu(settings: RoomsSettings) -> None:
    """Primary interactive CLI selection layout loop."""
    console.print("[bold magenta]Welcome to Rooms CLI[/bold magenta]")
    
    user_name = Prompt.ask("Your Profile Name", default=settings.user.name)
    user_bg = Prompt.ask("Your Profile Background", default=settings.user.background)
    
    topic = Prompt.ask("Chat Room Conversation Topic")
    max_turns = int(Prompt.ask("Max Simulation Turns", default="20"))
    
    session_choice = Prompt.ask("Session Type", choices=["dynamic", "round_robin", "argumentative"], default="dynamic")
    session_type_map = {
        "dynamic": SessionType.DYNAMIC,
        "round_robin": SessionType.ROUND_ROBIN,
        "argumentative": SessionType.ARGUMENTATIVE
    }
    session_type = session_type_map.get(session_choice, SessionType.DYNAMIC)
    
    hitl_turns = int(Prompt.ask("Human-In-The-Loop Intervention Turns", default="5"))
    
    agent_configs: List[AgentConfig] = []
    
    if settings.use_shipped_personas:
        for p_name in ["Elena (The Lawyer)", "Viktor (The Dev)", "Nyx (The Critic)"]:
            if Confirm.ask(f"Include default persona {p_name}?"):
                agent_configs.append(AgentConfig(
                    name=p_name,
                    system_prompt=f"You are {p_name}",
                    expertise=[],
                    model_type=ModelType.LITELLM,
                    model=settings.defaults.litellm_model,
                    temperature=settings.defaults.temperature,
                    color="white",
                    custom_instructions=None
                ))
                
    tracked_env_keys: List[str] = []
    
    while Confirm.ask("Add a custom agent to the room?"):
        agent_cfg = create_custom_agent_wizard(settings, tracked_env_keys)
        agent_configs.append(agent_cfg)
        
    orchestrator_cfg = None
    if Confirm.ask("Configure custom global room orchestrator?"):
        orch_prompt = Prompt.ask("Orchestrator System Prompt", default="Manage the room flow efficiently.")
        
        orch_model = settings.defaults.orchestrator_model
        if settings.presets and Confirm.ask("Use a preset for the orchestrator model?"):
            preset_options = list(settings.presets.keys())
            preset_choice = Prompt.ask("Select orchestrator preset", choices=preset_options)
            orch_model = settings.presets[preset_choice].litellm_model
            
            api_key_env = settings.presets[preset_choice].api_key_env
            if api_key_env:
                _set_session_env_key(api_key_env, tracked_env_keys)
                
        orchestrator_cfg = AgentConfig(
            name="Orchestrator",
            system_prompt=orch_prompt,
            expertise=["orchestration"],
            model_type=ModelType.LITELLM,
            model=orch_model,
            temperature=settings.defaults.temperature,
            color="gold",
            custom_instructions=None
        )
        
    config = SessionConfig(
        topic=topic,
        agents=agent_configs,
        orchestrator=orchestrator_cfg,
        session_type=session_type,
        max_turns=max_turns,
        human_in_the_loop_turns=hitl_turns
    )
    
    console.print("\n[bold green]Launching simulation room session...[/bold green]")
    
    # Instantiate Agent runtime objects from their configuration schemas
    agents = [Agent(cfg) for cfg in config.agents]
    user_profile = {"name": user_name, "background": user_bg}
    
    # Build and initialize runtime session instance directly
    session = Session(config=config, agents=agents, user_profile=user_profile)
    
    # Run loop execution driving agent turns sequentially
    while session.turn_count < config.max_turns:
        if session.needs_human_input():
            human_msg = Prompt.ask(f"[bold cyan]{user_name}[/bold cyan]")
            if human_msg.strip().lower() in ("exit", "quit"):
                break
            session.add_user_message(user_name, human_msg)
            
        turn_data = session.generate_next_turn()
        if turn_data is None:
            break
            
        # Display response outputs conditionally based on text flags
        content = turn_data.get("content", "")
        role = turn_data.get("role", "Agent")
        color = turn_data.get("color", "white")
        
        if not turn_data.get("skipped") and content != "PASS":
            console.print(f"[{color}][bold]{role}:[/bold] {content}[/{color}]")