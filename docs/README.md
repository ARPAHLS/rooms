# Rooms Documentation

Welcome to the Rooms documentation hub. Start here to find the right guide by audience and task.

## Start here

| If you want to… | Read |
|-----------------|------|
| Understand what Rooms is and run your first session | [Introduction](introduction.md) |
| Configure models, YAML, `.env`, and Ollama preflight | [Settings & preflight](SETTINGS.md) |
| See scenario walkthroughs and parameter tips | [Examples & best practices](EXAMPLES.md) |

## Deep dives

| Topic | Guide |
|-------|--------|
| LiteLLM routing, session memory, orchestration, transcripts | [Architecture](ARCHITECTURE.md) |
| Skillware skills CLI, wizard assignment, runtime behavior | [Skillware integration](SKILLWARE.md) |
| Pytest strategy, mocking, CI smoke tests | [Testing](TESTING.md) |

## Project meta

| Topic | Location |
|-------|----------|
| Contributing, design philosophy, PR workflow | [CONTRIBUTING.md](../CONTRIBUTING.md) |
| Notable changes | [CHANGELOG.md](../CHANGELOG.md) |
| Roadmap and open work | [GitHub Issues](https://github.com/arpahls/Rooms/issues) |

## Related issues

- **Settings key semantics and override rules** are documented in [Global defaults vs per-agent overrides](SETTINGS.md#global-defaults-vs-per-agent-overrides); use `rooms.settings.example.yaml` as the complete template.
- **This hub** focuses on navigation and discoverability so architecture, examples, and configuration are easy to find in one place.

## Install paths

| Method | Status | Command |
|--------|--------|---------|
| Clone from GitHub | **Supported** | `git clone https://github.com/arpahls/Rooms.git` |
| Editable local install | **Supported** | `pip install -r requirements.txt` in a venv after clone |
| PyPI package | **Planned** | Not published yet — install from source for now |
