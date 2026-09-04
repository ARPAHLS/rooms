<div align="center">
  <img src="assets/roomslogo.png" alt="Rooms Logo" width="200px" />

  # Contributing to Rooms
</div>

Thank you for helping improve Rooms. This guide is the entry point for code, CLI, settings, documentation, and test contributions. Rooms is local-first: changes should preserve user privacy, predictable orchestration, and offline-friendly testing.

## Navigation

| Section | Purpose |
| :--- | :--- |
| [Ways to contribute](#ways-to-contribute) | Choose the right scope and verification path |
| [Getting started](#getting-started) | Fork, sync, branch, and install |
| [Universal expectations](#universal-expectations) | Follow project-wide contribution standards |
| [Pull request process](#pull-request-process) | Prepare a reviewable PR |
| [Related documents](#related-documents) | Find architecture, testing, and configuration references |

## Ways to contribute

Start from an approved or assigned issue when possible. For larger behavior or architecture changes, discuss the approach with maintainers before implementation.

Use the GitHub [Bug Report](https://github.com/ARPAHLS/rooms/issues/new?template=bug_report.yml) or [Feature Request](https://github.com/ARPAHLS/rooms/issues/new?template=feature_request.yml) template when opening new work.

| Type | Typical paths | Labels | Verify locally |
| :--- | :--- | :--- | :--- |
| Core framework | `rooms/agent.py`, `rooms/session.py`, `rooms/config.py` | `enhancement`, `session-logic` | Relevant unit tests plus the full suite |
| CLI wizard | `cli.py`, `rooms/skills_cli.py` | `cli` | `tests/test_cli.py`, CLI settings smoke tests |
| Settings | `rooms/settings.py`, `rooms.settings.example.yaml` | `enhancement`, `cli` | `tests/test_settings.py`, `tests/test_cli_settings_smoke.py` |
| Documentation | `README.md`, `docs/`, `CONTRIBUTING.md` | `documentation` | Run `pytest tests/test_docs_hub.py -q` |
| Tests | `tests/test_*.py` | `testing` | Run the changed test and the full suite |
| Bug fix | Paths identified by the issue | `bug` | Add a regression test that fails before the fix |
| Good first issue | Usually focused docs, tests, or small fixes | `good first issue` | Follow the verification path for the underlying type |

## Getting started

### 1. Fork and clone

Fork [ARPAHLS/rooms](https://github.com/ARPAHLS/rooms), then clone your fork and register the upstream repository:

```bash
git clone https://github.com/<your-username>/rooms.git
cd rooms
git remote add upstream https://github.com/ARPAHLS/rooms.git
```

### 2. Sync and branch

Create every branch from the latest upstream `main`:

```bash
git fetch upstream
git checkout main
git pull --ff-only upstream main
git checkout -b feat/issue-47-short-description
```

Use `<type>/issue-<number>-<short-description>`, with a focused prefix such as `feat`, `fix`, `docs`, or `test`. Do not work directly on `main`.

### 3. Install dependencies

Rooms targets Python 3.13. Create a virtual environment, then install runtime and contributor tools:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m pip install -r requirements.txt pytest flake8
```

## Universal expectations

### Scope and style

- Keep the diff limited to the issue's acceptance criteria; avoid unrelated refactors.
- Match existing Python, Markdown, Pydantic, and CLI patterns in nearby files.
- Add or update documentation when behavior, settings, or commands change.
- Keep inference tests deterministic. Mock LiteLLM, Ollama, filesystem, and Skillware boundaries rather than calling live services.
- Never commit API keys, `.env`, or `rooms.settings.yaml`. Credentials belong in the environment; see [Settings & preflight](docs/SETTINGS.md).

### Design principles

- **Local-first:** Prefer private, offline-capable workflows and local inference where practical.
- **Zero-leakage:** Do not send user data or credentials to third parties without explicit configuration.
- **Aesthetic CLI:** Keep terminal output clear, consistent, and polished when changing user-facing flows.

### Changelog policy

Update the `[Unreleased]` section of [CHANGELOG.md](CHANGELOG.md) when a PR changes user-visible behavior, configuration, CLI output, or documented workflows users rely on. Use the existing `Added`, `Changed`, or `Fixed` headings. Tests, internal refactors, and minor wording fixes usually do not need an entry. Do not create a release version heading unless a maintainer requests it.

### Tests and CI

Run the full suite and the CI-blocking Flake8 checks before opening a PR:

```bash
PYTHONPATH=. python -m pytest tests/test_docs_hub.py -q  # documentation link checks
PYTHONPATH=. python -m pytest tests/ -v
python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

See [Testing Strategy](docs/TESTING.md) for focused commands and mocking examples. GitHub Actions repeats lint and test checks on pull requests.

### Git authorship

Use an email verified on your GitHub account so commits are attributed correctly. Check before committing:

```bash
git config user.name
git config user.email
```

If needed, set a verified email with `git config user.email "you@example.com"`. GitHub's private `noreply` address is also acceptable when enabled in your [email settings](https://github.com/settings/emails).

## Pull request process

1. Link the assigned or approved issue using `Fixes #123` or `Refs #123`.
2. Implement only the requested scope and add tests for behavior changes.
3. Update `rooms.settings.example.yaml` when the supported settings schema changes.
4. Update `[Unreleased]` when required by the changelog policy above.
5. Run focused tests, the full test suite, and Flake8 locally.
6. Commit with a short imperative subject such as `fix: handle empty persona list` or `docs: clarify settings precedence`.
7. Push the branch to your fork and open a PR against `ARPAHLS/rooms` `main` using the [PR template](.github/PULL_REQUEST_TEMPLATE.md).
8. Ensure CI passes and address review feedback on the same branch.

PR descriptions should explain what changed, why it changed, and how it was verified. Include screenshots only when terminal output or another visible workflow changes.

## Related documents

| Document | Purpose |
| :--- | :--- |
| [Architecture](docs/ARCHITECTURE.md) | LiteLLM routing, sessions, orchestration, and storage |
| [Examples](docs/EXAMPLES.md) | Scenario and parameter guidance |
| [Settings & preflight](docs/SETTINGS.md) | YAML, environment variables, and Ollama checks |
| [Testing Strategy](docs/TESTING.md) | Pytest scope, commands, and mocking patterns |
| [Documentation hub](docs/README.md) | Index of all project guides |
| [Agent contribution workflow (planned)](https://github.com/ARPAHLS/rooms/issues/48) | Tracks the dedicated workflow guide for contributing agents |
| [Changelog](CHANGELOG.md) | Current `[Unreleased]` changes |
| [Pull request template](.github/PULL_REQUEST_TEMPLATE.md) | Required PR summary and checklist |
| [GitHub Issues](https://github.com/ARPAHLS/rooms/issues) | Open work and issue templates |
| [Code of Conduct](CODE_OF_CONDUCT.md) | Standards for human and agent contributors |
| [Security Policy](SECURITY.md) | How to report vulnerabilities |

---

<div align="center">
  <img src="https://raw.githubusercontent.com/arpahls/cfd/main/assets/arpalogo26.png" width="40" alt="ARPA Logo">
  <br>
  <sub>Developed and maintained by <b>ARPA HELLENIC LOGICAL SYSTEMS</b></sub>
</div>
