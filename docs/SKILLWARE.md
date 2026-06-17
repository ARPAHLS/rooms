# Skillware Integration

Rooms supports optional Skillware-based tool use for agents.

## Design Principles

- Skills are assigned per agent, not globally.
- Skillware is loaded lazily only when an agent has configured skills.
- Agent replies remain human-readable even when tools are used.
- Skill execution metadata is logged as structured session events.

## Install (Optional)

```bash
pip install skillware
```

Rooms works normally without Skillware. Skill commands and wizard steps fail gracefully with guidance.

## Skills CLI Commands

```bash
python cli.py skills list
python cli.py skills inspect finance/wallet_screening
python cli.py skills suggest --expertise finance,risk,compliance
```

## Wizard Assignment Flow

When creating a custom agent, you can optionally:

- assign one or more skill IDs
- add per-skill override settings (`key=value` pairs)
- skip skills entirely

Assigned skills are stored in agent config:

- `skills`
- `skill_settings`

## Runtime Behavior

- Tools are exposed to the model only for agents with configured skills.
- Skill calls are guarded by per-turn and per-session limits.
- Tool results are passed back to the model for second-pass synthesis.
- Final user-visible output remains a normal agent message, not raw JSON.

## Session Logging and Transcripts

Skill calls are recorded as structured `role: skill` events in session history.

Saved transcripts include those events with:

- agent name
- tool name
- arguments
- status
- result payload
