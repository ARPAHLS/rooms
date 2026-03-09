# Contributing to Rooms

Thank you for your interest in contributing to **Rooms**! We welcome contributions from the community to help make this framework even better for local-first multi-agent orchestration.

---

## 🚀 How to Contribute

### 1. Reporting Bugs
- Use the **Bug Report** template to describe the issue.
- Provide clear steps to reproduce the bug.
- Include information about your environment (OS, Python version, Local LLM provider).

### 2. Suggesting Enhancements
- Use the **Feature Request** template.
- Explain the motivation behind the suggestion and how it benefits the framework.

### 3. Pull Requests (PRs)
- **Fork the Repository**: Create your own branch from `main`.
- **Implement Changes**: Follow the project's coding style and naming conventions.
- **Run Tests**: Ensure all existing tests pass by running:
  ```bash
  $env:PYTHONPATH="."; python -m pytest tests/ -v
  ```
- **Add Tests**: If you are adding new logic, please include corresponding tests in `tests/test_session.py`.
- **Submit PR**: Provide a clear description of what the PR changes and why.

---

## 🎨 Design Philosophy
- **Local-First**: Always favor solutions that respect user privacy and offline execution.
- **Aesthetic Excellence**: All CLI and documentation updates should prioritize a premium, modern feel.
- **Zero-Leakage**: Be cautious with third-party integrations that might leak data.

## 🛠 Project Roadmap
Check our [GitHub Issues](https://github.com/arpahls/Rooms/issues) to see what we are currently working on.

---

<div align="center">
  <img src="https://raw.githubusercontent.com/arpahls/cfd/main/assets/arpalogo26.png" width="40" alt="ARPA Logo">
  <br>
  <sub>Developed and Maintained by <b>ARPA HELLENIC LOGICAL SYSTEMS</b></sub>
</div>
