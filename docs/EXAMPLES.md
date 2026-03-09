# Use Cases & Examples: Who, How, and What For?

The Multi-Agent Rooms framework is designed to be highly versatile, scaling from personal ideation sessions to enterprise-grade compliance testing. 

Here is a breakdown of how different individuals and organizations can leverage the framework.

## 1. Risk Mitigation & Compliance Stress-Testing
**Who**: Corporate lawyers, auditors, risk officers, and cybersecurity analysts.
**What For**: Aggressively stress-testing upcoming policies, legal contracts, or security architectures against edge cases before they are deployed to production.
**How**:
1. **Setup**: Create an `argumentative` room.
2. **Participants**:
   - `Agent 1 (The Defender)`: *"You are the Chief Information Security Officer. You designed this new zero-trust architecture. You must defend its merits and explain how it prevents unauthorized access."*
   - `Agent 2 (The Attacker)`: *"You are an elite, hostile Red Team auditor who specializes in social engineering, supply chain attacks, and exploiting misconfigurations. Your sole job is to destroy the CISO's architecture conceptually. Do not hold back."*
3. **Flow**: Set human-in-the-loop to 0 and let them clash for 10 turns.
4. **Value**: The raw output generates a comprehensive list of vulnerabilities and legal liabilities a single human reviewer might overlook.

## 2. Automated Incident Report Generation
**Who**: DevOps teams, Site Reliability Engineers (SRE), and IT Managers.
**What For**: Rapidly digesting a massive server outage log or post-mortem and generating a clear, executive-friendly Incident Report summarizing root causes and action items.
**How**:
1. **Setup**: Create a `round_robin` room with highly specialized technical and managerial personas.
2. **Participants**:
   - `Agent 1 (The SRE)`: *"You are a senior SRE. You have the memory of the recent database cascade failure. Analyze the raw logs I provide and state only the technical root cause."*
   - `Agent 2 (The PM)`: *"You are the Product Manager. Take the SRE's technical babble and translate it into a polite, clear paragraph suitable for our public status page."*
   - `Agent 3 (The VP)`: *"You are the VP of Engineering. Read both the technical cause and the public statement, then generate 3 harsh, actionable engineering tasks to ensure this never happens again."*
3. **Value**: Turns chaotic logs into structured, multi-audience documentation instantly.

## 3. Think Tanks & Strategic Planning
**Who**: Think tanks, CEOs, strategists, and urban planners.
**What For**: Exploring the long-term geopolitical or economic ramifications of a new policy or technology (e.g., universal basic income, quantum computing, or a new tax law).
**How**:
1. **Setup**: Invite default personas like `Nyx (The Visionary)` alongside custom agents representing different demographics.
2. **Participants**:
   - `Agent 1 (The Economist)`: *"You are a macro-economist focused on inflation and job displacement. Analyze the prompt strictly through the lens of supply and demand."*
   - `Agent 2 (The Sociologist)`: *"You are a sociologist focused on wealth inequality and community cohesion. Argue how this policy affects the working class."*
   - `Orchestrator`: *"You are the room moderator. Every 4 turns, summarize the economic and sociological impacts discussed so far, and demand the agents propose a combined compromise."*
3. **Value**: Synthesizes a massive diversity of thought into actionable strategic intelligence.

## 4. Software Engineering & Architecture
**Who**: Software architects and backend developers.
**What For**: Architecture reviews and pair-programming debates on complex systemic issues.
**How**:
1. **Setup**: Create a `dynamic` room where the agents talk organically.
2. **Participants**: Use `Viktor (The Coder)` and a custom junior developer persona.
3. **Prompt**: "We are migrating from monolith to microservices. Debate the merits of gRPC vs REST."
4. **Value**: Uncovers performance bottlenecks and implementation hurdles during the planning phase.

---

## Crafting Deep Personas (Prompting Guide)

The secret to maximizing the Rooms framework is giving agents **rich, detailed backgrounds and memories**. A generic prompt ("You are a helpful assistant") yields generic results. A deep persona yields specialized insights.

### Good vs. Great Prompts

**Generic (Avoid):**
> *"You are a marketing expert. Help us plan a campaign."*

**Deep Persona (Recommended):**
> *"You are Isabella, a cutthroat CMO with 20 years of experience in luxury retail. You survived the 2008 financial crash by pivoting your entire brand to digital marketing overnight. You are cynical, hate influencer marketing, and believe data is the only truth. Your memory of the '08 crash makes you extremely risk-averse regarding ad spend. Analyze this new product launch strategy from that perspective."*

### Key Elements of a Deep Persona:
1. **Name and Title**: Gives the model a distinct grounding (e.g., "Dr. Aris, Lead Bioethicist").
2. **Past Trauma or Defining Memory**: Forces the agent to have a specific bias or lens (e.g., "You lost your last job because of an unpatched server...").
3. **Communication Style**: Dictates how they talk (e.g., "You speak in short, blunt sentences and use heavy nautical metaphors").
4. **Specific Directives**: Explicit interaction instructions (e.g., "Never agree fully with the other agents; always find one flaw").
