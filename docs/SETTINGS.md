# Settings & preflight

Rooms separates **configuration** (YAML), **credentials** (environment / `.env`), and **runtime checks** (Ollama preflight). This page is the single reference for all three.

For deep architecture context (memory, orchestration, LiteLLM), see [ARCHITECTURE.md](ARCHITECTURE.md). For scenario tuning, see [EXAMPLES.md](EXAMPLES.md).

---

## Configuration files

| File | In git? | Purpose |
|------|---------|---------|
| `rooms.settings.example.yaml` | Yes | Committed template — documents every supported key |
| `rooms.settings.yaml` | No (gitignored) | Your local overrides (model, personas, user profile) |
| `.env` | No (gitignored) | API keys and skill-related secrets (never put keys in YAML) |
| `.env.example` | Yes | Template for optional provider keys |

**Rule:** `rooms.settings.yaml` holds non-secrets only. LiteLLM provider keys and skill `env_vars` (e.g. `ETHERSCAN_API_KEY`) belong in the process environment or `.env`.

---

## Settings search order

The CLI loads the **first file that exists**:

1. `--config path/to/settings.yaml` (explicit)
2. `./rooms.settings.yaml` (current working directory)
3. User config directory:
   - Windows: `%APPDATA%\rooms\settings.yaml`
   - macOS / Linux: `~/.config/rooms/settings.yaml`

If none exist, **built-in defaults** apply (same shape as `rooms.settings.example.yaml`).

### CLI helpers

```bash
python cli.py config init    # copy example → ./rooms.settings.yaml
python cli.py config reset   # remove local settings file(s)
python cli.py --config path/to/settings.yaml
```

---

## YAML key reference

Top-level keys in `rooms.settings.yaml`:

### `defaults`

Global fallbacks for personas and orchestrator unless overridden per persona.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `litellm_model` | string | `ollama/gemma4:e2b` | LiteLLM model string (`ollama/tag`, `openai/gpt-4o`, etc.) |
| `orchestrator_model` | string | *(same as `litellm_model`)* | Model for the global orchestrator when enabled |
| `temperature` | float | `0.7` | Default sampling temperature |
| `timeout` | int | `30` | Inference timeout in seconds |

### `presets`

Named model shortcuts (optional). Used when selecting a preset in tooling; keys are arbitrary names.

| Key | Type | Description |
|-----|------|-------------|
| `litellm_model` | string | Model string for this preset |
| `api_key_env` | string | Env var name hint for cloud providers (documentation only) |

### `ollama`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `base_url` | string | `http://localhost:11434` | Ollama API base; sets `OLLAMA_API_BASE` when loaded |
| `auto_select_first` | bool | `false` | Reserved for future auto-model selection |

### `user`

Wizard defaults for the human participant.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `name` | string | `User` | Display name in the room |
| `background` | string | `""` | Role / bio shown to agents |

### `use_shipped_personas`

| Value | Behavior |
|-------|----------|
| `true` (default) | Use built-in Elena, Viktor, Nyx personas |
| `false` | Use custom `personas` list below (or fall back to shipped if list empty) |

### `personas` (optional list)

Override or replace shipped personas entirely when `use_shipped_personas: false`.

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `name` | string | yes | Agent display name |
| `system_prompt` | string | yes | Persona instructions |
| `expertise` | list[string] | no | Keywords for `dynamic` mode routing |
| `model` | string | no | Per-agent model; falls back to `defaults.litellm_model` |
| `temperature` | float | no | Falls back to `defaults.temperature` |
| `color` | string | no | Rich terminal color (e.g. `yellow`, `magenta`) |
| `skills` | list[string] | no | Skillware skill IDs (e.g. `finance/wallet_screening`) |
| `skill_settings` | object | no | Per-skill override map (`skill_id` → `{key: value}`) |

**Override rule:** Persona-level `model` / `temperature` / `timeout` win over `defaults` for that agent only. Session wizard choices can still override per run.

---

## Environment variables (`.env`)

Rooms separates credentials from YAML. LiteLLM and Skillware read keys from the **process environment**.

Rooms bootstraps `.env` automatically at CLI startup and when settings load (`rooms/env.py`):

1. Existing shell/CI environment variables (highest priority)
2. `.env` in the current working directory
3. `.env` in the repository root

For local development, copy `.env.example` to `.env` and set provider keys (`OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, …) and any skill `env_vars` (e.g. `ETHERSCAN_API_KEY`).

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux
```

Never commit `.env`. Skill-specific requirements are listed in each skill manifest (`python cli.py skills inspect <skill_id>`).

---

## Ollama preflight

Before the wizard starts, Rooms checks whether:

1. Ollama is reachable at `ollama.base_url`, and
2. The configured `defaults.litellm_model` tag exists locally (when model starts with `ollama/`).

If the check fails, the CLI prints actionable fixes (`ollama serve`, `ollama pull <tag>`, edit settings).

### Skip preflight

For CI, automation, or when you know Ollama is not needed:

```bash
python cli.py --skip-preflight
```

Preflight is implemented in `rooms/ollama_preflight.py` and only applies to `ollama/` models.

---

## Local Ollama tips

```bash
ollama list          # installed models
ollama ps            # models loaded in memory right now
ollama pull <tag>    # download a model
```

Set `defaults.litellm_model` to `ollama/<tag>` matching `ollama list` (e.g. `ollama/qwen3.5:4b`).

---

## See also

- [Introduction](introduction.md) — first run
- [Examples](EXAMPLES.md) — parameter cheat sheet and scenarios
- [Architecture](ARCHITECTURE.md) — session memory and orchestration
- [Documentation index](README.md)
