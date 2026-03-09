<div align="center">

<br>

**A Secure, Local-First Multi-Agent Orchestration Framework**

[![License](https://img.shields.io/badge/License-MIT-D6BCFA?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.13%2B-90CDF4?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Experimental-4FD1C5?style=flat-square)](#)
[![ARPA](https://img.shields.io/badge/Powered_by-ARPA_HLS-756f6a?style=flat-square)](https://arpacorp.net)

<br>

</div>

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

## Framework Capabilities

The framework allows extreme granularity in handling session configurations:

| Capability | Scope | Notes |
| :--- | :--- | :--- |
| **Generative Control** | **Per-Agent** | Set `temperature`, `max_tokens`, and system prompts individually. |
| **Logic Hooks** | **Runtime** | Dynamically load native `.py` files to act as agents. |
| **Data Preservation** | **Ephemeral** | RAM-only by default. Prompted to export as Markdown or CSV on exit. |
| **Session Memory** | **Full History** | Timestamped history shared across all participants throughout the session. |
| **User Identity** | **Per-Session** | User name and background injected into room intro for agent awareness. |
| **Expert Routing** | **Dynamic** | Agents scored by expertise against live context — best fit speaks next. |
| **Forced Addressing** | **On-Demand** | `@AgentName` in any message forces that agent's next response. |

## Documentation Library

For deeper insights into how to leverage and modify the framework, please refer to our dedicated documentation guides:

- [Architecture & LiteLLM Guide](docs/ARCHITECTURE.md) - Understand how local API routing, session memory, and agent selection work.
- [Use Cases, Examples & Best Practices](docs/EXAMPLES.md) - Parameter cheat sheet, deep persona guide, scenario walkthroughs, and an edge case reference table.
- [Testing Strategy](docs/TESTING.md) - How to write and run deterministic tests for multi-agent logic.

## Project Structure

```bash
Rooms/
├── rooms/              # Core Package
│   ├── __init__.py
│   ├── config.py       # Pydantic Configuration Models
│   ├── agent.py        # Agent & LiteLLM/Custom Logic
│   ├── session.py      # Turn Orchestration & Memory
│   └── storage.py      # Secure Log Serialization
├── tests/              # Unit Tests
│   └── test_session.py # Logic Verification
├── outputs/            # Session Transcripts
├── cli.py              # Interactive Wizard Entry Point
└── requirements.txt    # Project Dependencies
```

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/arpahls/Rooms.git
cd Rooms

# Setup Environment
python -m venv venv
venv\Scripts\activate  # Windows: venv\Scripts\activate | Unix: source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt
```

### 2. Usage

**Start the Interactive Wizard**
```bash
python cli.py
```
The wizard will step you through:
- Setting your user profile (name and background)
- Defining the session topic and turn limits
- Inviting default or custom agents with individual temperatures and system prompts
- Optionally assigning a Global Orchestrator

During a session, type `@AgentName` in any user input to force a specific agent to respond next.

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
