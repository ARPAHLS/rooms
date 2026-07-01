# Introduction to Rooms

**Rooms** is a local-first multi-agent orchestration framework. It runs structured conversations between AI personas (and you) in the terminal, with optional tool use via [Skillware](SKILLWARE.md).

## What Rooms does

- Routes inference through **LiteLLM** to local Ollama models or cloud APIs.
- Orchestrates turns via **round robin**, **argumentative**, or **dynamic** (expertise-weighted) modes.
- Keeps **timestamped session memory** in RAM and can export Markdown or CSV transcripts.
- Supports **Human-in-the-Loop** prompts, `@AgentName` addressing, and optional **Skillware** tools per agent.

Rooms does **not** replace Ollama or your LLM provider — it sits above them as the session layer. See [Architecture](ARCHITECTURE.md) for how routing and memory work.

## Five-minute quick start

```bash
git clone https://github.com/arpahls/Rooms.git
cd Rooms
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
python cli.py
```

No settings file is required — built-in defaults apply. To customize models and personas locally, see [Settings & preflight](SETTINGS.md).

## What to read next

| Goal | Guide |
|------|--------|
| Configure Ollama, YAML, API keys | [SETTINGS.md](SETTINGS.md) |
| Scenario ideas and tuning tips | [EXAMPLES.md](EXAMPLES.md) |
| Session flow, LiteLLM, orchestration | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Assign wallet screening and other skills | [SKILLWARE.md](SKILLWARE.md) |
| Run or extend tests | [TESTING.md](TESTING.md) |

Return to the [documentation index](README.md) anytime.
