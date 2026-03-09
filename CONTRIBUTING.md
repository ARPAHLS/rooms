<div align="center">
  <img src="assets/roomslogo.png" alt="Rooms Logo" width="200px" />

  # Contributing to Rooms
</div>

<br/>

Thank you for your interest in contributing to Rooms. We welcome contributions from the community to help make this framework even better for local-first multi-agent orchestration.

---

## How to Contribute

### Reporting Bugs
Use the Bug Report template to describe the issue. Provide clear steps to reproduce the bug and include information about your environment (OS, Python version, Local LLM provider).

### Suggesting Enhancements
Use the Feature Request template. Explain the motivation behind the suggestion and how it benefits the framework.

### Pull Requests
1. **Fork the Repository**: Create your own branch from `main`.
2. **Implement Changes**: Follow the project's coding style and naming conventions.
3. **Run Tests**: Ensure all existing tests pass by running:
   ```bash
   $env:PYTHONPATH="."; python -m pytest tests/ -v
   ```
4. **Add Tests**: If you are adding new logic, please include corresponding tests in `tests/test_session.py`.
5. **Submit PR**: Provide a clear description of what the PR changes and why.

---

## Design Philosophy

**Local-First**
Always favor solutions that respect user privacy and offline execution.

**Aesthetic Excellence**
All CLI and documentation updates should prioritize a premium, modern feel.

**Zero-Leakage**
Be cautious with third-party integrations that might leak data.

## Automated Checks
Every push and Pull Request is automatically verified by our GitHub Actions CI/CD pipeline, which runs:
- **Style Checks**: Code formatting and linting via `flake8`.
- **Logic Verification**: Full suite of `pytest` unit tests for turn orchestration, expertise scoring, and session memory.

Ensure your changes pass locally before submitting to maintain the build status.

## Project Roadmap
Check our [GitHub Issues](https://github.com/arpahls/Rooms/issues) to see what we are currently working on.

---

<div align="center">
  <img src="https://raw.githubusercontent.com/arpahls/cfd/main/assets/arpalogo26.png" width="40" alt="ARPA Logo">
  <br>
  <sub>Developed and Maintained by <b>ARPA HELLENIC LOGICAL SYSTEMS</b></sub>
</div>
