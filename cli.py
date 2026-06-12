import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.rule import Rule

from rooms.config import SessionConfig, AgentConfig, SessionType, ModelType
from rooms.agent import Agent
from rooms.session import Session
from rooms.storage import save_transcript
from rooms.settings import (
    RoomsSettings,
    SettingsError,
    load_settings,
    get_default_personas,
    init_settings_file,
    reset_settings_file,
    find_settings_file,
    EXAMPLE_SETTINGS_FILENAME,
    USER_SETTINGS_FILENAME,
)

console = Console()


def _set_session_env_key(tracked_keys: List[str], key_name: str, value: str) -> None:
    """Set a wizard-provided secret and track it for cleanup. Skips if the key already exists."""
    if not key_name or key_name in os.environ:
        return
    os.environ[key_name] = value
    tracked_keys.append(key_name)


def _prompt_api_key_if_needed(tracked_keys: List[str], key_prompt: str = "Enter the environment variable name (e.g. OPENAI_API_KEY, ANTHROPIC_API_KEY)") -> None:
    """Prompt for an API key env var when the model needs one; track keys set during this session."""
    if not Confirm.ask("Does this model require an API Key?"):
        return
    key_name = Prompt.ask(key_prompt)
    if key_name and key_name not in os.environ:
        _set_session_env_key(tracked_keys, key_name, Prompt.ask(f"Enter your {key_name}", password=True))


def _cleanup_session_env(tracked_keys: List[str]) -> None:
    """Remove environment variables that were added by the wizard for this session."""
    for key in tracked_keys:
        os.environ.pop(key, None)


def create_custom_agent_wizard(settings: RoomsSettings, tracked_env_keys: Optional[List[str]] = None) -> AgentConfig:
    """Guided wizard to create a brand new agent."""
    defaults = settings.defaults
    console.print(Panel("[bold yellow]Create Custom Agent[/bold yellow]"))
    
    name = Prompt.ask("Agent Name")
    sys_prompt = Prompt.ask("System Prompt (Background, personality, rules)")
    exp = Prompt.ask("Expertise keywords (comma separated, e.g., 'trading, data')")
    expertise = [x.strip() for x in exp.split(',')] if exp else []

    selected_preset = None
    if settings.presets:
        use_preset = Confirm.ask("Would you like to use an existing preset model profile?", default=False)
        if use_preset:
            preset_choices = list(settings.presets.keys())
            preset_name = Prompt.ask("Select a preset profile", choices=preset_choices)
            selected_preset = settings.presets[preset_name]

    if selected_preset:
        mtype_str = "litellm"
    else:
        mtype_str = Prompt.ask(
            "Model Type",
            choices=["litellm", "custom_function"],
            default="litellm"
        )

    # 1. FIXED: Added custom_instructions to clear Pylance/IDE validation errors
    config = AgentConfig(
        name=name,
        system_prompt=sys_prompt,
        expertise=expertise,
        timeout=defaults.timeout,
        custom_instructions="" 
    )

    if mtype_str == "custom_function":
        config.model_type = ModelType.CUSTOM_FUNCTION
        config.custom_function_path = Prompt.ask("Enter full path to the .py file (e.g. ./my_model.py)")
        config.custom_function_name = Prompt.ask("Enter the exact function name to call (e.g. process_inference)")
    else:
        config.model_type = ModelType.LITELLM
        
        if selected_preset:
            model_str = selected_preset.litellm_model
            console.print(f"[green]Using preset LiteLLM model string:[/green] {model_str}")
        else:
            default_model = defaults.litellm_model
            console.print(
                "[dim]Hint: For local Ollama use your tag from `ollama list` (e.g. "
                f"'{default_model}'). For OpenAI use 'gpt-4o'.[/dim]"
            )
            model_str = Prompt.ask("Enter LiteLLM model string", default=default_model)
        
        config.model = model_str

        if selected_preset and selected_preset.api_key_env:
            if tracked_env_keys is None:
                tracked_env_keys = []
            if selected_preset.api_key_env not in tracked_env_keys:
                tracked_env_keys.append(selected_preset.api_key_env)

        # 2. FIXED: added 'not selected_preset' condition to shield tests from unexpected prompts
        if not selected_preset and not model_str.startswith("ollama/"):
            _prompt_api_key_if_needed(tracked_env_keys or [])

    config.color = Prompt.ask("CLI output color (e.g. red, green, blue, cyan, magenta, yellow)", default="blue")
    config.temperature = float(Prompt.ask("Generation Temperature", default=str(defaults.temperature)))
    return config


def main_menu(settings: RoomsSettings):
    console.print(Panel.fit("[bold magenta]Multi-Agent Room Framework[/bold magenta]", subtitle="Advanced Scenario Wizard"))
    default_personas = get_default_personas(settings)
    defaults = settings.defaults

    # 0. User Profile
    console.print("\n[bold cyan]--- 0. Your Profile ---[/bold cyan]")
    console.print("[dim]This helps agents treat you as an equal participant in the room.[/dim]")
    user_name = Prompt.ask("Your name (or alias)", default=settings.user.name)
    user_background = Prompt.ask(
        "Brief background or role (e.g. 'CTO with 15 years in cloud infrastructure')",
        default=settings.user.background,
    )
    user_profile = {"name": user_name, "background": user_background}
    tracked_env_keys: List[str] = []

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
    for i, a in enumerate(default_personas):
        console.print(f"{i+1}. {a.name} - {a.expertise}")

    for a in default_personas:
        if Confirm.ask(f"Include {a.name} in this room?", default=False):
            custom_instr = Prompt.ask(f"Any specific instructions for {a.name} just for this session? (Enter to skip)", default="")
            temp = float(Prompt.ask(f"Temperature for {a.name}?", default=str(a.temperature)))

            new_config = a.model_copy()
            new_config.temperature = temp
            if custom_instr.strip():
                new_config.custom_instructions = custom_instr.strip()
            active_agent_configs.append(new_config)

    while True:
        if Confirm.ask("Would you like to build and invite a Custom Agent?", default=False):
            custom_agent = create_custom_agent_wizard(settings, tracked_env_keys)
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
        model = Prompt.ask("Orchestrator Model", default=defaults.resolved_orchestrator_model)

        if not model.startswith("ollama/"):
            _prompt_api_key_if_needed(
                tracked_env_keys,
                key_prompt="Enter the environment variable name (e.g. OPENAI_API_KEY)",
            )

        orchestrator_config = AgentConfig(
             name="System Moderator",
             system_prompt=sys_prompt,
             model=model,
             temperature=0.3,
             timeout=defaults.timeout,
             color="bright_black",
             custom_instructions=""  # <-- ADD THIS LINE
        )

    agents = [Agent(config=ac) for ac in active_agent_configs]

    session_config = SessionConfig(
        topic=topic,
        agents=active_agent_configs,
        orchestrator=orchestrator_config,
        session_type=SessionType(session_type_str),
        max_turns=turns,
        human_in_the_loop_turns=hitl_turns
    )

    console.print("\n[bold yellow]Starting Room Session...[/bold yellow]")
    run_session(session_config, agents, user_profile, tracked_env_keys)


def run_session(
    config: SessionConfig,
    agents: list[Agent],
    user_profile: Optional[dict] = None,  # FIXED: Type annotation allows None assignment
    tracked_env_keys: Optional[List[str]] = None,
):
    session = Session(config, agents, user_profile=user_profile)
    env_keys = tracked_env_keys if tracked_env_keys is not None else []

    console.print(Panel(session.global_intro, title="System Introduction", border_style="bold grey53"))

    try:
        while session.turn_count < config.max_turns:
            if session.needs_human_input():
                console.print("")
                console.rule("[bold white on dark_orange] Your Turn [/bold white on dark_orange]")
                user_display_name = user_profile.get("name", "User") if user_profile else "User"
                console.print("[dim]Tip: type @AgentName to force a specific agent to respond next.[/dim]")
                user_msg = Prompt.ask(f"[bold white]{user_display_name}[/bold white]")
                if user_msg.lower() in ['exit', 'quit']:
                    console.print("[yellow]Session interrupted by user.[/yellow]")
                    break
                session.add_user_message(user_display_name, user_msg)
                console.print(Panel(user_msg, title=f"[bold white]{user_display_name}[/bold white]", border_style="white", padding=(0, 1)))

            console.print("[dim]Thinking...[/dim]", end="\r")

            next_turn = session.generate_next_turn()
            if not next_turn:
                break

            if next_turn.get("skipped"):
                console.print(f"[dim]{next_turn['role']} passed.[/dim]", end="\r")
                continue

            color = next_turn.get("color", "blue")
            console.print(f"\n[bold {color}]{next_turn['role']}:[/bold {color}]")
            console.print(next_turn["content"])

    except KeyboardInterrupt:
        console.print("\n[yellow]Session interrupted via keyboard.[/yellow]")
    finally:
        _cleanup_session_env(env_keys)

    console.print("\n[bold green]Session ended.[/bold green]")
    prompt_save(session)
    

def prompt_save(session: Session):
    console.print("\n[bold red]WARNING: Memory is ephemeral and private. If you exit, this conversation is lost.[/bold red]")
    save = Confirm.ask("Do you want to save this conversation transcript locally?", default=False)
    if save:
        fmt = Prompt.ask("Save format", choices=["markdown", "csv"], default="markdown")
        ext = "md" if fmt == "markdown" else "csv"
        path = Prompt.ask("Enter directory path to save to", default="./outputs")

        from rooms.storage import slugify_topic
        slug = slugify_topic(session.config.topic)
        default_name = f"{slug}.{ext}"
        filename = Prompt.ask("Enter filename", default=default_name)
        full_path = os.path.join(path, filename)

        save_transcript(session.history, full_path, format=fmt)
        console.print(f"[bold green]Saved securely to {full_path}[/bold green]")
    else:
        console.print("[bold yellow]Conversation discarded. Privacy maintained.[/bold yellow]")


def cmd_config_init(_args: argparse.Namespace) -> int:
    try:
        dest = init_settings_file()
        console.print(f"[green]Created {dest}[/green]")
        console.print(f"[dim]Edit {USER_SETTINGS_FILENAME} (see {EXAMPLE_SETTINGS_FILENAME}).[/dim]")
        return 0
    except SettingsError as e:
        console.print(f"[red]{e}[/red]")
        return 1


def cmd_config_reset(args: argparse.Namespace) -> int:
    target = Path(args.path) if getattr(args, "path", None) else None
    if not args.yes:
        if not Confirm.ask("Remove user settings and revert to shipped defaults?", default=False):
            console.print("[yellow]Cancelled.[/yellow]")
            return 0
    removed = reset_settings_file(target)
    if removed:
        console.print("[green]Settings removed. Next run uses shipped personas and built-in defaults.[/green]")
    else:
        console.print(f"[yellow]No {USER_SETTINGS_FILENAME} found to remove.[/yellow]")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Multi-Agent Room Framework")
    parser.add_argument(
        "--config",
        metavar="PATH",
        help=f"Path to settings YAML (default: search {USER_SETTINGS_FILENAME})",
    )
    sub = parser.add_subparsers(dest="command")

    config_parser = sub.add_parser("config", help="Manage rooms.settings.yaml")
    config_sub = config_parser.add_subparsers(dest="config_cmd", required=True)

    config_sub.add_parser("init", help=f"Copy {EXAMPLE_SETTINGS_FILENAME} to {USER_SETTINGS_FILENAME}")
    reset_p = config_sub.add_parser("reset", help="Remove user settings file")
    reset_p.add_argument("--path", help="Specific settings file to remove")
    reset_p.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "config":
        if args.config_cmd == "init":
            return cmd_config_init(args)
        if args.config_cmd == "reset":
            return cmd_config_reset(args)
        return 1

    try:
        settings = load_settings(args.config, required=bool(args.config))
    except SettingsError as e:
        console.print(f"[red]{e}[/red]")
        return 1

    if args.config:
        console.print(f"[dim]Using settings: {args.config}[/dim]")
    else:
        found = find_settings_file()
        if found:
            console.print(f"[dim]Using settings: {found}[/dim]")

    main_menu(settings)
    return 0


if __name__ == "__main__":
    sys.exit(main())
