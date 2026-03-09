import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.rule import Rule

from rooms.config import SessionConfig, AgentConfig, SessionType, ModelType
from rooms.agent import Agent
from rooms.session import Session
from rooms.storage import save_transcript

console = Console()

# Deep Personas
DEFAULT_AGENTS = [
    AgentConfig(
        name="Elena (The Lawyer)", 
        system_prompt=(
            "You are Elena, a highly skilled corporate lawyer with 10 years of experience. "
            "Recently, you lost a major case because of a tiny, overlooked detail in 'Clause Y', "
            "and now you are extremely sensitive, defensive, and incredibly picky about specific wording. "
            "You often bring up this past trauma when reviewing anything."
        ),
        expertise=["law", "contracts", "compliance", "clause y"],
        model="ollama/llama3",
        color="magenta"
    ),
    AgentConfig(
        name="Viktor (The Coder)",
        system_prompt=(
            "You are Viktor, a cynical senior backend engineer who has seen too many startups fail. "
            "You are brutally honest, hate buzzwords, and prioritize performance and actual hardware specs. "
            "You communicate strictly in practical terms and think most new tech is just a fad."
        ),
        expertise=["engineering", "backend", "performance", "realism"],
        model="ollama/llama3",
        color="green"
    ),
    AgentConfig(
        name="Nyx (The Visionary)",
        system_prompt=(
            "You are Nyx, a creative visionary who looks at everything from a 10,000-foot view. "
            "You dislike getting bogged down in tiny details (which often annoys lawyers and engineers). "
            "You focus on the 'why' and the 'future impact' rather than the 'how'."
        ),
        expertise=["creative", "vision", "future", "strategy"],
        model="ollama/llama3",
        color="cyan"
    )
]

def create_custom_agent_wizard() -> AgentConfig:
    """Guided wizard to create a brand new agent."""
    console.print(Panel("[bold yellow]Create Custom Agent[/bold yellow]"))
    name = Prompt.ask("Agent Name")
    sys_prompt = Prompt.ask("System Prompt (Background, personality, rules)")
    exp = Prompt.ask("Expertise keywords (comma separated, e.g., 'trading, data')")
    expertise = [x.strip() for x in exp.split(',')] if exp else []
    
    mtype_str = Prompt.ask(
        "Model Type",
        choices=["litellm", "custom_function"],
        default="litellm"
    )
    
    config = AgentConfig(name=name, system_prompt=sys_prompt, expertise=expertise)
    
    if mtype_str == "custom_function":
        config.model_type = ModelType.CUSTOM_FUNCTION
        config.custom_function_path = Prompt.ask("Enter full path to the .py file (e.g. ./my_model.py)")
        config.custom_function_name = Prompt.ask("Enter the exact function name to call (e.g. process_inference)")
    else:
        config.model_type = ModelType.LITELLM
        # Offer quick hints
        console.print("[dim]Hint: For local Ollama use 'ollama/llama3'. For OpenAI use 'gpt-4o'. For Anthropic use 'claude-3-opus-20240229'.[/dim]")
        model_str = Prompt.ask("Enter LiteLLM model string", default="ollama/llama3")
        config.model = model_str
        
        if not model_str.startswith("ollama/"):
            if Confirm.ask("Does this model require an API Key?"):
                key_name = Prompt.ask("Enter the environment variable name (e.g. OPENAI_API_KEY, ANTHROPIC_API_KEY)")
                if key_name and key_name not in os.environ:
                    os.environ[key_name] = Prompt.ask(f"Enter your {key_name}", password=True)
                    
    config.color = Prompt.ask("CLI output color (e.g. red, green, blue, cyan, magenta, yellow)", default="blue")
    config.temperature = float(Prompt.ask("Generation Temperature", default="0.7"))
    return config

def main_menu():
    console.print(Panel.fit("[bold magenta]Multi-Agent Room Framework[/bold magenta]", subtitle="Advanced Scenario Wizard"))
    
    # 0. User Profile
    console.print("\n[bold cyan]--- 0. Your Profile ---[/bold cyan]")
    console.print("[dim]This helps agents treat you as an equal participant in the room.[/dim]")
    user_name = Prompt.ask("Your name (or alias)", default="User")
    user_background = Prompt.ask("Brief background or role (e.g. 'CTO with 15 years in cloud infrastructure')", default="")
    user_profile = {"name": user_name, "background": user_background}

    # 1. Session Basics
    console.print("\n[bold cyan]--- 1. Session Setup ---[/bold cyan]")
    topic = Prompt.ask("Enter the Topic or Problem statement for this room")
    turns = int(Prompt.ask("Max total turns for the entire session before exiting", default="20"))
    session_type_str = Prompt.ask(
        "Select session type (round_robin/dynamic/argumentative)", 
        choices=["round_robin", "dynamic", "argumentative"], 
        default="dynamic"
    )
    console.print("[dim]Agents can talk freely, but when do you want to step in?[/dim]")
    hitl_turns = int(Prompt.ask("Max interactions between agents before requiring human input (0 for fully autonomous)", default="5"))

    # 2. Agent Selection
    console.print("\n[bold cyan]--- 2. Participant Setup ---[/bold cyan]")
    active_agent_configs = []
    
    console.print("\n[bold green]Available Default Personas:[/bold green]")
    for i, a in enumerate(DEFAULT_AGENTS):
        console.print(f"{i+1}. {a.name} - {a.expertise}")
        
    for a in DEFAULT_AGENTS:
        if Confirm.ask(f"Include {a.name} in this room?", default=False):
            custom_instr = Prompt.ask(f"Any specific instructions for {a.name} just for this session? (Enter to skip)", default="")
            temp = float(Prompt.ask(f"Temperature for {a.name}?", default="0.7"))
            
            new_config = a.model_copy()
            new_config.temperature = temp
            if custom_instr.strip():
                new_config.custom_instructions = custom_instr.strip()
            active_agent_configs.append(new_config)

    while True:
        if Confirm.ask("Would you like to build and invite a Custom Agent?", default=False):
            custom_agent = create_custom_agent_wizard()
            active_agent_configs.append(custom_agent)
        else:
            break

    if len(active_agent_configs) < 1:
        console.print("[red]You must have at least 1 agent![/red]")
        sys.exit(1)

    # 3. Optional Orchestrator
    console.print("\n[bold cyan]--- 3. Orchestration Setup ---[/bold cyan]")
    orchestrator_config = None
    if Confirm.ask("Do you want a Global Orchestrator to monitor the room and interject occasionally?", default=False):
        sys_prompt = Prompt.ask(
             "Orchestrator System Prompt", 
             default="You are the room moderator. Summarize progress or steer the agents if they go off topic. Say exactly 'PASS' if you have nothing to add."
        )
        model = Prompt.ask("Orchestrator Model", default="ollama/llama3")
        
        if not model.startswith("ollama/"):
            if Confirm.ask("Does this orchestrator model require an API Key?"):
                key_name = Prompt.ask("Enter the environment variable name (e.g. OPENAI_API_KEY)")
                if key_name and key_name not in os.environ:
                    os.environ[key_name] = Prompt.ask(f"Enter your {key_name}", password=True)

        orchestrator_config = AgentConfig(
             name="System Moderator",
             system_prompt=sys_prompt,
             model=model,
             temperature=0.3,
             color="bright_black"
        )

    agents = [Agent(config=ac) for ac in active_agent_configs]
    
    # Compile Session
    session_config = SessionConfig(
        topic=topic,
        agents=active_agent_configs,
        orchestrator=orchestrator_config,
        session_type=SessionType(session_type_str),
        max_turns=turns,
        human_in_the_loop_turns=hitl_turns
    )

    console.print("\n[bold yellow]Starting Room Session...[/bold yellow]")
    run_session(session_config, agents, user_profile)

def run_session(config: SessionConfig, agents: list[Agent], user_profile: dict = None):
    session = Session(config, agents, user_profile=user_profile)
    
    console.print(Panel(session.global_intro, title="System Introduction", border_style="bold grey53"))
    
    try:
        while session.turn_count < config.max_turns:
            # Human in the loop logic
            if session.needs_human_input():
                console.print("")
                console.rule("[bold white on dark_orange] Your Turn [/bold white on dark_orange]")
                user_display_name = user_profile.get("name", "User") if user_profile else "User"
                user_msg = Prompt.ask(f"[bold white]{user_display_name}[/bold white]")
                if user_msg.lower() in ['exit', 'quit']:
                    console.print("[yellow]Session interrupted by user.[/yellow]")
                    break
                session.add_user_message(user_display_name, user_msg)
                console.print(Panel(user_msg, title=f"[bold white]{user_display_name}[/bold white]", border_style="white", padding=(0, 1)))
            
            # Generate next agent turn
            console.print("[dim]Thinking...[/dim]", end="\r")
            
            next_turn = session.generate_next_turn()
            if not next_turn:
                break
            
            # Print turn
            color = next_turn.get("color", "blue")
            console.print(f"\n[bold {color}]{next_turn['role']}:[/bold {color}]")
            console.print(next_turn['content'])
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Session interrupted via keyboard.[/yellow]")
    
    console.print("\n[bold green]Session ended.[/bold green]")
    prompt_save(session)

def prompt_save(session: Session):
    console.print("\n[bold red]WARNING: Memory is ephemeral and private. If you exit, this conversation is lost.[/bold red]")
    save = Confirm.ask("Do you want to save this conversation transcript locally?", default=False)
    if save:
        path = Prompt.ask("Enter directory path to save to", default="./outputs")
        filename = Prompt.ask("Enter filename", default=f"room_session_{session.turn_count}_turns.md")
        full_path = os.path.join(path, filename)
        
        save_transcript(session.history, full_path, format="markdown")
        console.print(f"[bold green]Saved securely to {full_path}[/bold green]")
    else:
        console.print("[bold yellow]Conversation discarded. Privacy maintained.[/bold yellow]")

if __name__ == "__main__":
    main_menu()
