<div align="center">
  <img src="assets/roomslogo.png" alt="Rooms Logo" width="400px" />

  A secure, local-first multi-agent orchestration framework.
</div>

<br/>

<div align="center">
  <img src="https://img.shields.io/badge/License-MIT-e8c4c0?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Python-3.13+-bbd4e8?style=flat-square" alt="Python Version">
  <img src="https://img.shields.io/badge/Status-Experimental-c4d8c0?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/Powered_by-ARPA_HLS-cfc8dc?style=flat-square" alt="ARPA HLS">
</div>

<br/>

## Overview

**Rooms** is a robust, highly-configurable framework designed for testing, simulating, and orchestrating multiple AI agents in structured conversation spaces. Built with a local-first philosophy, it leverages `LiteLLM` to securely route requests to local models (like Ollama) or commercial APIs without data leakage.

> [!TIP]
> **Extensibility**: Rooms natively supports dropping in your own custom Python inference functions. You aren't limited to standard LLM endpoints.

## Key Features

- **Local Priority Integration**: Zero-leakage API routing via `litellm`. Seamlessly integrates with local offline instances.
- **Dynamic Turn Orchestration**: Agents interact via `round_robin`, `argumentative`, or `dynamic` relevance-based conversational flows.
- **Expertise-Weighted Selection**: In `dynamic` mode, agents are scored against the live topic context — the most relevant expert speaks next.
- **User-Directed Addressing**: Type `@AgentName` in any input to force a specific agent to respond next, bypassing automatic scoring.
- **PASS Mechanic**: Agents may respond with `PASS` if they have nothing meaningful to add, silently skipping their turn and keeping the flow clean.
- **Deep Personas**: Configure intricate agent backgrounds and behavioral instructions dynamically per session.
- **Custom Architectures**: Bypass standard LLMs entirely and plug in custom Python functions for specific agent inference.
- **Human-In-The-Loop**: Inject user instructions at defined intervals — or instantly when an agent directly addresses the user by name.
- **User Profile & Identity**: Name and background provided at session start; agents treat the user as an equal room participant.
- **Global Orchestrator**: A designated room moderator that fires every N turns to summarize or redirect agents, with no runaway loop risk.
- **Timestamped Session Memory**: All turns, messages, and system events are tagged with precise timestamps for full auditability.
- **Optional Skillware Integration**: Assign skills per agent, execute tools lazily, and keep user-facing replies natural.

## Framework Capabilities

The framework allows extreme granularity in handling session configurations:

| Capability | Scope | Notes |
| :--- | :--- | :--- |
| **Generative Control** | **Per-Agent** | Set `temperature`, `max_tokens`, `timeout`, and system prompts individually. |
| **Logic Hooks** | **Runtime** | Dynamically load native `.py` files to act as agents. |
| **Data Preservation** | **Ephemeral** | RAM-only by default. Prompted to export as Markdown or CSV on exit. |
| **Session Memory** | **Full History** | Timestamped history shared across all participants throughout the session. |
| **User Identity** | **Per-Session** | User name and background injected into room intro for agent awareness. |
| **Expert Routing** | **Dynamic** | Agents scored by expertise against live context — best fit speaks next. |
| **Forced Addressing** | **On-Demand** | `@AgentName` in any message forces that agent's next response. |

## Documentation Library

**[Documentation hub](docs/README.md)** — start here for the full index (introduction, settings, architecture, examples, skills, testing).

| Guide | Description |
|-------|-------------|
| [Introduction](docs/introduction.md) | What Rooms is and a five-minute quick start |
| [Settings & preflight](docs/SETTINGS.md) | YAML keys, `.env`, search paths, Ollama preflight |
| [Architecture & LiteLLM](docs/ARCHITECTURE.md) | Session memory, orchestration, transcripts, custom models |
| [Examples & best practices](docs/EXAMPLES.md) | Parameter cheat sheet, personas, scenarios, edge cases |
| [Skillware integration](docs/SKILLWARE.md) | Skills CLI, wizard assignment, runtime behavior |
| [Testing](docs/TESTING.md) | Pytest, mocking, CI smoke tests |
| [Contributing](CONTRIBUTING.md) | Contribution types, fork workflow, local checks, and PR process |
| [Code of Conduct](CODE_OF_CONDUCT.md) | Community standards for human and agent contributors |
| [Security Policy](SECURITY.md) | How to report vulnerabilities |
| [Changelog](CHANGELOG.md) | Notable updates |

## Project Structure

```bash
Rooms/
├── rooms/                      # Core package
│   ├── agent.py                # Agent inference (LiteLLM / custom functions)
│   ├── config.py               # Pydantic session & agent models
│   ├── env.py                  # Optional .env bootstrap
│   ├── ollama_preflight.py     # Local Ollama connectivity check
│   ├── session.py              # Turn orchestration & memory
│   ├── settings.py             # YAML settings loader
│   ├── skills_cli.py           # Rooms-native Skillware CLI helpers
│   ├── skills_runtime.py       # Lazy skill load & tool execution
│   └── storage.py              # Transcript export (Markdown / CSV)
├── docs/                       # Documentation hub (see docs/README.md)
├── tests/                      # Pytest suite
├── cli.py                      # Interactive wizard entry point
├── rooms.settings.example.yaml # Settings template (commit this)
├── requirements.txt            # Core dependencies (includes skillware)
└── requirements-memory.txt     # Optional vector memory dependencies
```

`rooms.settings.yaml` is gitignored — create it locally with `python cli.py config init` or by copying the example file.

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/arpahls/Rooms.git
cd Rooms

# Setup Environment
python -m venv venv
venv\Scripts\activate  # Windows: venv\Scripts\activate | Unix: source venv/bin/activate

# Install Core Dependencies
pip install -r requirements.txt
```
#### Optional: Long-Term Memory & RAG Support
If you plan to use vector memory features, install the heavier machine learning dependencies separately:
```bash
pip install -r requirements-memory.txt
```

### 2. Configure defaults (optional)

You do **not** need a settings file to run the CLI — built-in defaults apply. For the full YAML key reference, search paths, and Ollama preflight, see **[docs/SETTINGS.md](docs/SETTINGS.md)**.

To customize per machine, create a local file (gitignored):

| File | In git? | Purpose |
|------|---------|---------|
| `rooms.settings.example.yaml` | Yes (template) | Committed reference; copy or use `config init` |
| `rooms.settings.yaml` | No (gitignored) | Your local overrides (model tag, user name, personas) |
| `.env` | No (gitignored) | API keys and skill secrets (see [SETTINGS.md](docs/SETTINGS.md)) |

```bash
python cli.py config init    # copies example → rooms.settings.yaml in cwd
# Or manually: copy rooms.settings.example.yaml to rooms.settings.yaml
# Edit rooms.settings.yaml — e.g. defaults.litellm_model from `ollama list`
python cli.py config reset   # remove user file; revert to shipped defaults
python cli.py --config path/to/settings.yaml
```

**API keys and skill secrets**

LiteLLM and Skillware read credentials from the **process environment** (not from YAML). Rooms loads `.env` automatically at startup (shell/CI env vars take precedence). See [docs/SETTINGS.md](docs/SETTINGS.md) for details and skill variables such as `ETHERSCAN_API_KEY`.

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux
# edit .env with your provider and skill keys
```

### 3. Usage

**Start the Interactive Wizard**
```bash
python cli.py
```
The wizard will step you through:
- Setting your user profile (name and background)
- Defining the session topic and turn limits
- Inviting default or custom agents with individual temperatures and system prompts
- Optionally assigning Skillware skills (and per-skill overrides) to custom agents
- Optionally assigning a Global Orchestrator

During a session, type `@AgentName` in any user input to force a specific agent to respond next.

For skills-specific commands and usage, see `docs/SKILLWARE.md`.

**Run Tests**
```bash
# Always run via pytest with PYTHONPATH set:
$env:PYTHONPATH="."; python -m pytest tests/ -v
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<br>
<div align="center">
  <img src="https://raw.githubusercontent.com/arpahls/cfd/main/assets/arpalogo26.png" width="50" alt="ARPA Logo">
  <br>
  <sub>Developed and Maintained by <b>ARPA HELLENIC LOGICAL SYSTEMS</b></sub>
  <br>
  <sub>Support: systems@arpacorp.net</sub>
</div>
