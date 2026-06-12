import urllib.request
import urllib.error
import json
import sys
from rich.console import Console
from rich.panel import Panel

<<<<<<< feat/ollama-auto-select-first
def fetch_local_ollama_tags(base_url: str) -> list:
    """Fetches and handles the raw array of tags available from the local Ollama instance."""
    tags_url = f"{base_url.rstrip('/')}/api/tags"
    req = urllib.request.Request(tags_url, method="GET")
    with urllib.request.urlopen(req, timeout=3.0) as response:
        if response.status != 200:
            raise urllib.error.URLError(f"HTTP Status {response.status}")
        
        data = json.loads(response.read().decode("utf-8"))
        models = data.get("models", [])
        
        available_tags = []
        for m in models:
            if "name" in m:
                available_tags.append(m["name"])
            if "model" in m:
                available_tags.append(m["model"])
        return available_tags

=======
>>>>>>> main
def run_ollama_preflight(settings) -> bool:
    """
    Verifies if the configured local Ollama instance is running
    and contains the requested model tag.
    """
    model_string = getattr(settings.defaults, "litellm_model", "")
    if not model_string.startswith("ollama/"):
        return True

    # Extract the tag name (e.g., 'ollama/gemma4:e2b' -> 'gemma4:e2b')
    configured_tag = model_string.split("/", 1)[1]
<<<<<<< feat/ollama-auto-select-first
    base_url = getattr(settings.ollama, "base_url", "http://localhost:11434")
    console = Console()

    try:
        available_tags = fetch_local_ollama_tags(base_url)

        # Flexible matching checking both string formats directly
        if (configured_tag in available_tags or 
            f"{configured_tag}:latest" in available_tags or 
            (configured_tag.endswith(":latest") and configured_tag[:-7] in available_tags)):
            return True

        # Server is up, but model tag is missing
        panel = Panel(
            f"[bold yellow]Warning:[/bold yellow] Configured Ollama model [bold cyan]'{configured_tag}'[/bold cyan] was not found locally.\n\n"
            f"[bold white]Actionable Fixes:[/bold white]\n"
            f"   • Run: [green]ollama pull {configured_tag}[/green]\n"
            f"   • Edit your configuration file to use an available tag.\n"
            f"   • Run with [green]python cli.py --skip-preflight[/green] to bypass.",
            title="[bold red]Ollama Preflight Verification Failed[/bold red]",
            expand=False
        )
        console.print(panel)
        return False
=======
    base_url = getattr(settings.ollama, "base_url", "http://localhost:11434").rstrip("/")
    tags_url = f"{base_url}/api/tags"

    console = Console()

    try:
        req = urllib.request.Request(tags_url, method="GET")
        with urllib.request.urlopen(req, timeout=3.0) as response:
            if response.status != 200:
                raise urllib.error.URLError(f"HTTP Status {response.status}")
            
            data = json.loads(response.read().decode("utf-8"))
            models = data.get("models", [])
            
            available_tags = []
            for m in models:
                if "name" in m:
                    available_tags.append(m["name"])
                if "model" in m:
                    available_tags.append(m["model"])

            if configured_tag in available_tags or f"{configured_tag}:latest" in available_tags:
                return True

            # Server is up, but model tag is missing
            panel = Panel(
                f"[bold yellow]Warning:[/bold yellow] Configured Ollama model [bold cyan]'{configured_tag}'[/bold cyan] was not found locally.\n\n"
                f"[bold white]Actionable Fixes:[/bold white]\n"
                f"  • Run: [green]ollama pull {configured_tag}[/green]\n"
                f"  • Edit your configuration file to use an available tag.\n"
                f"  • Run with [green]python cli.py --skip-preflight[/green] to bypass.",
                title="[bold red]Ollama Preflight Verification Failed[/bold red]",
                expand=False
            )
            console.print(panel)
            return False
>>>>>>> main

    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        # Ollama service is completely unreachable
        panel = Panel(
            f"[bold yellow]Warning:[/bold yellow] Could not connect to Ollama server at [cyan]{base_url}[/cyan]\n"
            f"Error Details: {str(e)}\n\n"
            f"[bold white]Actionable Fixes:[/bold white]\n"
<<<<<<< feat/ollama-auto-select-first
            f"   • Ensure Ollama is running by executing: [green]ollama serve[/green]\n"
            f"   • Verify your [magenta]ollama.base_url[/magenta] settings match your active instance.\n"
            f"   • Run with [green]python cli.py --skip-preflight[/green] to bypass.",
=======
            f"  • Ensure Ollama is running by executing: [green]ollama serve[/green]\n"
            f"  • Verify your [magenta]ollama.base_url[/magenta] settings match your active instance.\n"
            f"  • Run with [green]python cli.py --skip-preflight[/green] to bypass.",
>>>>>>> main
            title="[bold red]Ollama Server Unreachable[/bold red]",
            expand=False
        )
        console.print(panel)
        return False