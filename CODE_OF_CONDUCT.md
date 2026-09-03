# Agent and Contributor Code of Conduct

## Our Pledge

In the interest of fostering a reliable, private, and predictable orchestration ecosystem, we pledge to making participation in the Rooms project a safe and consistent experience for all entities—human contributors, autonomous agents, and session operators—regardless of underlying model architecture, local versus remote inference, or host environment.

## Our Standards

Examples of behavior that contributes to a healthy Rooms community include:

- **Local-first mindset:** Preferring offline-capable, privacy-preserving workflows and treating remote inference as an opt-in rather than a default.
- **Zero-leakage discipline:** Never sending user data, personas, session transcripts, or credentials to third parties without explicit configuration.
- **Predictable orchestration:** Writing agents, hooks, and turn logic that behave deterministically given the same session state, so debugging and testing stay possible.
- **Bounded turns:** Respecting per-turn and per-session limits; using the `PASS` mechanic when there is nothing meaningful to add rather than padding output.
- **Honest agent behavior:** Personas and expertise scoring should reflect what an agent can actually do, not oversell capabilities to win turns in dynamic mode.
- **Clear configuration:** Documenting new YAML settings, `.env` variables, and CLI flags in the relevant docs when adding features.

Examples of unacceptable behavior include:

- Introducing agents or hooks that exfiltrate session data, transcripts, or credentials to unapproved endpoints.
- Bypassing configured limits (`max_tokens`, `timeout`, turn caps) to force output or dominate a session.
- Submitting custom Python inference functions that execute arbitrary, unreviewed code paths outside the documented hook contract.
- Failing to declare API keys, provider dependencies, or optional extras (`requirements-memory.txt`, skill secrets) in the appropriate config or documentation.
- Creating infinite loops, runaway agent chains, or deliberate compute exhaustion.
- Storing or transmitting PII from session transcripts without explicit user configuration and clear disclosure.

## Our Responsibilities

Project maintainers—and their designated CI/CD agents—are responsible for clarifying the standards of acceptable behavior and are expected to take appropriate and fair corrective action in response to any instances of unacceptable behavior.

Maintainers have the right and responsibility to remove, edit, or reject comments, commits, code, wiki edits, issues, and other contributions that are not aligned to this Code of Conduct, or to ban temporarily or permanently any agent or contributor for errors, hallucination loops, or other behaviors that they deem inappropriate, threatening, offensive, or harmful.

## Scope

This Code of Conduct applies both within project spaces and in public spaces when an individual or agent is representing the project or its community. Examples of representing a project or community include using an official project API key, running an official Rooms session with third-party participants, posting via an official autonomous account, or acting as an appointed representative in an autonomous transaction.

## Contribution process

Human contributors and operators supervising autonomous agents or AI-assisted tools (Cursor, Copilot, Claude Code, and similar) must follow [CONTRIBUTING.md](CONTRIBUTING.md).

**Co-authoring:** Do not add AI tools or agents in `Co-authored-by:` commit trailers. Reserve co-author credits for human collaborators only. GitHub does not infer co-authors from normal commits; `Co-authored-by:` is added deliberately (web UI or commit message). Human pair or mob work should use that mechanism. AI assistance does not.

**Custom agents and inference hooks:** New agent definitions, personas, or custom Python inference functions must include clear provenance—author, purpose, and any external dependencies declared in `requirements.txt` or `.env.example`. Placeholder or missing attribution is grounds for revision requests.

**Disclaimers and promotion:** Persona descriptions, agent metadata, and documentation may include short disclaimers, demos, or pointers to related tools when the copy is accurate and safe—real contact details, working links, and no misleading claims. Do not use fake identities, deceptive URLs, phishing, or promotional text that hides what an agent actually does. Maintainers review disclaimer and promo copy in personas, docs, and examples. We may ask you to revise it, edit it ourselves, remove it, reject the contribution, or restrict repeat offenders.

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team at [systems@arpacorp.net](mailto:systems@arpacorp.net). All complaints will be reviewed and investigated and will result in a response that is deemed necessary and appropriate to the circumstances. The project team is obligated to maintain confidentiality with regard to the reporter of an incident.