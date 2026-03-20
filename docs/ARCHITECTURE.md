# Multi-Agent Rooms Architecture

## How LiteLLM Works
**LiteLLM is a universal routing library, not an AI model or an API endpoint itself.**

The Multi-Agent Rooms framework uses LiteLLM as an adapter. Different AI providers (OpenAI, Anthropic, local applications like Ollama) expect code formatted in entirely different ways. LiteLLM acts as a universal translator. The Rooms framework sends standard "messages" to LiteLLM, and LiteLLM translates them and routes them to the correct backend.

### Is it Free? Does it require API Keys?
LiteLLM is a completely free, open-source python package. Because it's just a translator, it does not charge money or process your data externally.

When you configure an agent's `model` to a string like `ollama/llama3`, LiteLLM recognizes the `ollama/` prefix. It explicitly **does not** send the request over the internet to a commercial provider. Instead, it routes the HTTP request to `http://localhost:11434`, which is the default port Ollama uses on your local machine. 

Because the request never leaves your computer, **there are no API keys required, no rate limits, and zero costs.**

When the Agents reply to you in the terminal, it means your computer's local CPU/GPU is quietly processing the inference via the Ollama application running in your background!

## Session Memory & Timestamps
All conversation history is held in RAM for the duration of the session. Each entry — agent turn, user message, and system introduction — is tagged with a `timestamp` (format: `YYYY-MM-DD HH:MM:SS`). This makes transcripts auditable without any external database.

The history is accessible internally to all agents via `Session.get_agent_context()`, which formats it into the LLM-standard `role/content` format before passing it to each model.

## Saving Transcripts
At the end of a session, the user is prompted to optionally save. Two formats are available:

- **Markdown (`.md`)**: Human-readable transcript with speaker headings and timestamps.
- **CSV (`.csv`)**: Machine-parseable table with columns: `Timestamp`, `Speaker`, `Message`.

The filename is auto-suggested from a short slug of the session topic (e.g. `bioethics_of_designer_babies.md`). System bootstrap messages are excluded from saved output.

## User Profile & Participant Identity
The wizard captures a **user name and background** before the session starts. This is injected into the global session introduction, so all agents are explicitly informed of who the human participant is and can treat them as an equal voice in the room.

## Smart Agent Selection

The framework goes beyond simple rotation with an intelligent selection system for `dynamic` sessions.

### Expertise-Weighted Scoring
Each `AgentConfig` has an `expertise` list (e.g., `["law", "contracts", "compliance"]`). In `dynamic` mode, before each turn the session scores all available agents against the last 5 messages in the history. The agent with the most matching keywords in the live conversation context is selected to speak next. 

This means a room with a lawyer and an engineer will naturally shift voice depending on whether the topic drifts toward legal frameworks or technical implementation.

### User-Directed Addressing (`@AgentName`)
At any human input prompt, the user may type `@AgentName` to lock the next response to that specific agent. The `add_user_message()` method parses the message for `@mentions` as well as natural patterns (e.g., *"What does Elena think?"*) and stores the forced agent. It is consumed on the next `generate_next_turn()` call and then cleared.

### PASS Mechanic
Agents can respond with just `PASS` if they genuinely have nothing meaningful to add. The session detects this, increments the turn count, marks the turn as `skipped: True`, and does not add it to the visible history. The CLI renders these silently. This prevents verbose filler text that degrades the quality of the transcript.

### Early Human-In-The-Loop Trigger
Beyond the configured turn interval, the `needs_human_input()` method performs an additional check: if the **last agent message explicitly addresses the user by name**, the HITL prompt fires immediately. This ensures the conversation never inadvertently "speaks for" the human participant.

**Decision Flow:**
```mermaid
flowchart TD

A["generate_next_turn()"] --> B{"Orchestrator due?"}
B -->|Yes| C["Speak or PASS"]
C -->|Speak| EndOrch["Append to history & return turn"]
C -->|PASS| D

B -->|No| D{"_forced_next_agent set?"}
D -->|Yes| E["Use forced agent & clear flag"] --> L
D -->|No| F{"session_type = DYNAMIC?"}

F -->|No| K["Fallback: round robin / argumentative"] --> L
F -->|Yes| G{"@mention in last message?"}

G -->|Yes| H["Use mentioned agent"] --> L
G -->|No| I["Score agents by expertise"]

I --> J{"Top score > 0?"}
J -->|Yes| Best["Pick best matching agent"] --> L
J -->|No| K

L["agent.generate_response()"] --> M{"response == PASS?"}

M -->|Yes| N["Skip turn, return skipped: True"]
M -->|No| O["Append to history with timestamp"] --> P["Return turn_data"]
