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
- **Dynamic Turn Orchestration**: Agents can interact via `round_robin`, `argumentative` debates, or `dynamic` relevance-based conversational flows.
- **Deep Personas**: Configure intricate agent backgrounds, expertise, and behavioral instructions dynamically per session.
- **Custom Architectures**: Bypass standard LLMs entirely and specify custom Python functions (`model_type = custom_function`) for specific agent inference.
- **Human-In-The-Loop**: Inject user instructions and steer the conversation dynamically based on specific interval thresholds.
- **Global Orchestrator**: Deploy a designated room moderator to summarize progress or steer off-topic agents iteratively.

## Framework Capabilities

The framework allows extreme granularity in handling session configurations:

| Capability | Scope | Notes |
| :--- | :--- | :--- |
| **Generative Control** | **Per-Agent** | Set `temperature`, `max_tokens`, and system prompts individually. |
| **Logic Hooks** | **Runtime** | Dynamically load native `.py` files to act as agents. |
| **Data Preservation** | **Ephemeral** | By default, RAM-only. Prompts for safe markdown export upon conclusion. |

## Documentation Library

For deeper insights into how to leverage and modify the framework, please refer to our dedicated documentation guides:

- [Architecture & LiteLLM Guide](docs/ARCHITECTURE.md) - Understand our zero-leakage local API translation mapping.
- [Use Cases & Personas (Examples)](docs/EXAMPLES.md) - Learn how to build deep, trauma-informed personas for Risk Mitigation, SRE Incident Reports, and Think Tanks.
- [Testing Strategy](docs/TESTING.md) - How to use `unittest.mock` to write deterministic validation tests for AI workflows.

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
Follow the robust wizard prompts to define the room's overarching goal, add custom or default participants, assign an orchestrator, and set conversational rules.

**Run Tests**
```bash
pytest tests/
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
