# Security Policy

## Supported Versions

Rooms is currently in pre-release development and has not been published to PyPI. Security fixes are applied to the `main` branch only.

| Version | Supported |
| :--- | :--- |
| `main` (latest) | Yes |
| Pre-release commits | Best effort |

A supported-version table with tagged releases will be added when Rooms publishes its first PyPI version.

## Reporting a Vulnerability

If you discover a security vulnerability in Rooms, please report it privately rather than opening a public GitHub issue.

**Report to:** [systems@arpacorp.net](mailto:systems@arpacorp.net)

Include as much of the following as possible:

- A description of the vulnerability and its potential impact
- Steps to reproduce, or a proof-of-concept
- Affected files, functions, or configuration paths
- Suggested mitigation, if you have one

We will acknowledge receipt within a reasonable timeframe and work with you on disclosure. Please give us time to investigate and prepare a fix before any public discussion.

## Scope

Security-relevant areas of Rooms include, but are not limited to:

- **Agent inference paths:** LiteLLM routing, custom Python inference hooks, and any code that receives model output.
- **Session data:** In-memory turn history, personas, user profile fields, and exported transcripts (Markdown, CSV).
- **Credentials handling:** `.env` loading, API key exposure through logs or transcripts, and interaction with local model endpoints (Ollama, custom servers).
- **Skillware integration:** Tool execution boundaries, skill secrets in `.env`, and any behavior that could leak session data through skill calls.
- **CLI and settings:** `rooms.settings.yaml`, environment variable precedence, and any input surface that could allow path traversal, arbitrary code execution, or unintended file writes.

## Out of Scope

The following are generally not treated as vulnerabilities:

- Issues that require an attacker to already have local machine access with your credentials.
- Behavior arising from user-provided custom Python inference functions—these are the operator's responsibility to review.
- Third-party model provider issues (e.g., an issue in an underlying LLM API); please report those upstream.
- Denial of service caused by intentionally misconfigured turn limits, token limits, or expensive personas.

## Pre-Release Disclaimer

Rooms is under active development. APIs, session formats, and configuration schemas may change without notice until the first stable release. Do not rely on Rooms for production security guarantees at this stage.