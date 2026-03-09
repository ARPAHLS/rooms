# Use Cases, Examples & Best Practices

The Multi-Agent Rooms framework is extremely versatile. This guide covers practical use cases, how to configure agents for best results, scenario tips, and common edge cases to be aware of.

---

## Quick Reference: Parameter Cheat Sheet

| Parameter | What it controls | Tips |
|---|---|---|
| `temperature` | Creativity vs. determinism | `0.3–0.5` for lawyers/analysts; `0.8–1.0` for visionaries/writers |
| `max_turns` | Total session length | 10–15 for focused debates; 20–30 for think tanks |
| `human_in_the_loop_turns` | How often you steer | 0 for fully autonomous; 3–5 for guided; 1 for full collab |
| `session_type` | Agent interaction style | See the table below |
| `expertise` | Keywords for smart routing | Be specific — improves `dynamic` mode selection accuracy |
| `system_prompt` | Agent identity and role | The more vivid and specific, the more coherent the agent |

**Session Type Guide:**

| Type | Best For |
|---|---|
| `round_robin` | Equal screen time, structured meetings, moderated panels |
| `argumentative` | Red Teaming, devil's advocate debates, stress-testing ideas |
| `dynamic` | Organic, expertise-driven discussions, think tanks |

---

## 1. Risk Mitigation & Compliance Stress-Testing

**Who**: Corporate lawyers, auditors, risk officers, cybersecurity analysts.

**Goal**: Stress-test a new policy, contract, or architecture against edge cases before deployment.

**Setup Example:**
```
Session Type: argumentative
Max Turns: 12
Human Interval: 4
```

**Agents:**

- **Agent 1 — The Defender**
  ```
  You are the Chief Security Officer. You designed our new zero-trust architecture and you believe it is airtight. 
  You have 20 years of experience in enterprise security. Defend your architecture confidently but respond 
  to specific technical concerns with evidence. You may cite EU NIS2 or ISO 27001 references.
  Temperature: 0.5
  Expertise: security, compliance, zero-trust, architecture, audit
  ```

- **Agent 2 — The Red Team Auditor**
  ```
  You are a hostile Red Team auditor specialising in social engineering, supply-chain attacks, and 
  misconfigurations. Your only job is to break the CISO's security architecture. Find every gap. 
  Be aggressive. Use real-world attack vector terminology. Never accept the first answer.
  Temperature: 0.7
  Expertise: attack, exploit, vulnerability, social engineering, supply chain
  ```

> **Tip:** Keep `temperature` lower for the Defender (more consistent reasoning) and slightly higher for the Attacker (more creative attack paths). Use `argumentative` mode so they alternate directly.

> **Edge Case:** If both agents reach agreement too quickly, inject `@Red Team Auditor` in your input followed by *"Find one more critical flaw before we proceed"* to break the consensus.

---

## 2. Incident Report Generation (SRE / DevOps)

**Who**: Site Reliability Engineers, IT Managers, Product Managers.

**Goal**: Transform raw incident logs into structured multi-audience documentation instantly.

**Setup Example:**
```
Session Type: round_robin
Max Turns: 6
Human Interval: 0 (fully autonomous)
```

**Agents:**

- **Agent 1 — The SRE**
  ```
  You are a senior Site Reliability Engineer. The user will paste raw logs or describe an outage. 
  Your job is to provide a precise, jargon-heavy technical root cause analysis limited to 3 sentences.
  Do not provide solutions — only root cause.
  Temperature: 0.3
  Expertise: infrastructure, logs, database, latency, failure, root cause
  ```

- **Agent 2 — The PM Translator**
  ```
  You are a Product Manager. Take the SRE's technical root cause and rewrite it in one paragraph 
  suitable for a public status page. It must be calm, clear, and non-technical. Never use acronyms without 
  explaining them first.
  Temperature: 0.4
  Expertise: communication, customer, status page, messaging
  ```

- **Agent 3 — The Engineering VP**
  ```
  You have read both the root cause and the public statement. List exactly 3 engineering action items 
  to prevent recurrence. Be blunt and specific. Assign a priority level (P0/P1/P2) to each item.
  Temperature: 0.4
  Expertise: action items, engineering, prevention, remediation, process
  ```

> **Tip:** Paste the raw log dump as your first user message to seed the conversation. Then set `human_in_the_loop_turns=0` and let all three agents complete their turns.

> **Save Format:** Use **CSV** to produce a structured incident template. Open in Excel to generate a team report with minimal formatting work.

---

## 3. Think Tanks & Policy Simulation

**Who**: Economists, think tanks, strategists, urban planners.

**Goal**: Explore the long-term impacts of a new policy across multiple stakeholder lenses simultaneously.

**Setup Example:**
```
Session Type: dynamic
Max Turns: 20
Human Interval: 5
Orchestrator: Yes
```

**Orchestrator Prompt:**
```
You are the moderator of a multidisciplinary policy summit. Every time you speak, do two things: 
(1) Summarize the strongest arguments made so far in one paragraph. 
(2) Identify the SINGLE most unresolved tension and direct the next agent to address it specifically. 
Say exactly 'PASS' if the discussion is sufficiently progressing on its own.
```

> **Tip:** With `dynamic` mode and strong `expertise` keywords, agents self-organise around the most pressing aspects. The Orchestrator prevents the debate from looping or going off-topic.

> **Edge Case: Too much repetition?** Reduce `max_turns` or lower temperature on all agents. Repetition usually means agents lack specific enough instructions. Add *"Do not repeat anything already stated by another participant"* to each system prompt.

---

## 4. Creative Worldbuilding & Dialogue Generation

**Who**: Novelists, screenwriters, game designers.

**Goal**: Generate raw, organic character dialogue and uncover new narrative angles.

**Setup Example:**
```
Session Type: argumentative
Max Turns: 15
Human Interval: 3
Temperature: 0.85–0.95 for both agents
```

> **Tip:** For creative work, `temperature` is your most powerful lever. Push it to `0.9` for surprising, unpredictable answers. Set `0.6` for a more coherent but less wild voice.

> **Tip:** Inject yourself every 3 turns to redirect the scene: *"The tension peaks — @CharacterName, deliver the ultimatum."*

---

## 5. Software Architecture Reviews

**Who**: CTOs, architects, backend engineers.

**Setup Example:**
```
Session Type: dynamic
Max Turns: 10
Human Interval: 2
```

**Agents:**
- **The Pragmatist**: Focused on cost and simplicity. *"Resist over-engineering. Always propose the simplest solution that works at our scale."*
- **The Purist**: Focused on correctness and future-proofing. *"Propose the architecturally correct solution regardless of short-term cost."*

> **Tip:** You want these agents to disagree. Use `argumentative` if you need strict alternation, or `dynamic` if you want them to self-select based on what the last message raised.

> **Edge Case:** If they converge immediately, add *"You must find at least one unresolved tradeoff before the session ends"* to both system prompts.

---

## Crafting Deep Personas — Prompting Guide

The quality of your agents is entirely determined by the quality of their system prompts. Here are the key ingredients:

### The 5 Elements of a Great Agent Persona

| Element | Example |
|---|---|
| **Name & Title** | *"You are Dr. Mara, Chief Bioethicist at a European hospital consortium"* |
| **Defining Trauma or Bias** | *"You lost funding for a clinical trial due to regulatory delays — you distrust bureaucracy"* |
| **Communication Style** | *"You speak in short declarative sentences. You never hedge. You cite specific regulation articles."* |
| **Hard Constraint** | *"You must always find at least one ethical concern even in seemingly harmless proposals."* |
| **Relationship to Others** | *"You respect factual arguments but actively challenge emotional appeals."* |

### Good vs. Great Prompts

**Generic (avoid):**
> *"You are a helpful marketing expert. Help us plan a campaign."*

**Deep Persona (recommended):**
> *"You are Isabella, a CMO who survived the 2008 financial crash by pivoting your entire brand to digital overnight. You are cynical about influencer marketing and believe that measurable ROI is the only truth. You've been burned before by vague creative briefs. Your memory of '08 makes you extremely risk-averse. You speak in bullet points and always end your turn by asking for a specific metric."*

---

## Common Edge Cases & How to Handle Them

| Situation | What Happens | Solution |
|---|---|---|
| Agents agree too quickly | `dynamic` mode routes to same agent repeatedly | Lower temperature; add *"always find a counterargument"* to prompts |
| Orchestrator starts looping | Already fixed — `_last_orchestrator_turn` prevents re-triggering | No action needed |
| You want one specific agent | Model keeps picking the wrong one | Type `@AgentName` in your input |
| Agent produces rambling output | No output length constraint | Add `max_tokens: 300` to the agent config |
| Session feels too fast | HITL interval too long | Lower `human_in_the_loop_turns` to 1 or 2 |
| You want fully autonomous output | No human needed | Set `human_in_the_loop_turns: 0` |
| Agent addresses you directly | Session auto-triggers HITL early | This is by design — respond or type `continue` |
| Agent has nothing to add | Returns `PASS` | Turn is silently skipped; visible in logs only |
| Topic is very broad | Agents go off-scope | Add Orchestrator with *"steer back to [topic] if agents drift"* |
