# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

> **Note:** This project is currently in a pre-release stage. Official versioned release entries will begin tracking here soon.

## [Unreleased]

### Added

- Settings YAML support with personas and builtin defaults (#26, #28).
- `.env` bootstrap precedence and settings integration (#62).
- Rooms-native Skillware CLI wrapper and wizard skill assignment (#61).
- Session Skill UX for skills list, inspect, and suggest (#60).
- Ollama preflight checks with `--skip-preflight` flag (#36, #43).
- Test coverage for settings, CLI smoke tests, session logic, and Skillware UX.
- Documentation hub at `docs/README.md` with introduction, settings reference, and cross-links to all guides.
- `docs/introduction.md` — short onboarding and quick start.
- `docs/SETTINGS.md` — consolidated YAML key reference, `.env` guidance, and Ollama preflight documentation.
- Created initial CHANGELOG.md structure following the Keep a Changelog standard.
- **Docs:** `CODE_OF_CONDUCT.md` and `SECURITY.md` for community and vulnerability-reporting guidelines; linked from `CONTRIBUTING.md` (#50).

### Changed

- Slimmed project dependencies (#35).
- README documentation section now points to the docs hub; project structure tree updated to match the current package layout.
