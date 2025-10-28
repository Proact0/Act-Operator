## Contributing Guide

Thank you for your interest in contributing to Act Operator! We welcome all forms of contribution — bug reports, documentation improvements, tests, feature proposals/implementations, and developer experience enhancements. Small, clear changes with kind explanations and sufficient tests make for great collaboration.

## Types of Contributions
- **Bug Reports**: Use the issue templates and include reproduction steps, environment, expected vs actual behavior.
- **Documentation Improvements**: Update README/guides/examples; fix typos and clarify phrasing.
- **Tests**: Add unit/integration tests for new or changed functionality.
- **Feature Proposals/Implementations**: Split into small, reviewable PRs with clear goals.
- **Developer Experience/Performance**: Improve linting/build/run flows or runtime efficiency when appropriate.

## Quick Start

### Requirements
- **Python 3.12+**
- **Windows, macOS, Linux** supported
- **uv** (recommended): manage dependencies, execution, and builds.

Installation guide: [uv Installation](https://docs.astral.sh/uv/getting-started/installation/)

```powershell
# Install uv
pip install uv
```

### Clone the repository and set up development
```powershell
# Clone repository
git clone https://github.com/Proact0/Act-Operator.git
cd act-operator

# Install runtime + dev dependencies
uv sync --dev

# Add the package as editable (optional but handy for local development)
uv add --editable .
```

### Run tests and CLI locally
```powershell
# Run the full test suite
uv run pytest

# CLI example: create a new Act project
uv run act new --path ./my-act --act-name "My Act" --cast-name "Main Cast"

# CLI example: add a Cast to an existing project
uv run act cast --act-path ./my-act --cast-name "Support Cast"

# Build artifacts (pre-release check)
uv build
```

## Workflow & Principles
- **Small and clear**: keep changes focused and well-defined.
- **Issue first**: when possible, open an issue to capture background, problem, and goal.
- **Branch strategy**: use a dedicated branch per feature/fix.
  - Examples: `feat/add-cast-validation`, `fix/cli-prompt-edge-case`
- **Commit convention (Conventional Commits recommended)**
  - Format: `type(scope): subject`
  - Types: `feat`, `fix`, `docs`, `refactor`, `test`, `build`, `ci`, `chore`
  - Examples:
    ```text
    feat(cli): add --act-name default from custom path
    fix(scaffold): normalize cast directory to snake_case
    docs(readme): clarify Python version requirement to 3.12+
    ```

## Code Style & Quality
This project uses **ruff** and **pytest**.

### Lint (ruff)
Configuration in `pyproject.toml` checks general errors (E/F), imports (I), and Bugbear (B). Line length (E501) is ignored, but keep readability in mind.

```powershell
# Lint checks
uv run ruff check .

# Optional: apply formatting
uv run ruff format .
```

Note: the `act_operator/scaffold` path is excluded from linting.

### Tests (pytest)
Tests live under `tests/` as unit/integration tests. Add appropriate tests for new or modified behavior.

```powershell
uv run pytest -q
```

## Docs/Examples Updates
- If a change affects users, update `README.md` or related guides accordingly.
- Check whether scaffold templates (`act_operator/act_operator/scaffold/`) need updates in `README.md` or `TEMPLATE_README.md`.

## Issue Templates
- Use templates under `.github/ISSUE_TEMPLATE`.
  - **Backlog / Feature Request**: propose new features, define tasks/steps.
  - **Bug Report**: programmer-origin bugs (e.g., null pointer, bounds errors, resource leaks).

## PR Checklist
- Description: clearly state problem/motivation/solution/alternatives/risks.
- Tests: add new tests or ensure existing tests pass.
- Quality: `uv run ruff check .`, `uv run pytest` must both pass.
- Docs: update documentation if user-facing behavior changes.
- Scope: keep PRs small and easy to review.

## CLI Development Tips
- Entry point: `[project.scripts]` in `pyproject.toml`
  - `act` → `act_operator.cli:main`
- Local run: `uv run act ...`
- Module entry: `uv run python -m act_operator` when needed.

## Versioning & Release Policy
- Version is managed via `hatch` and defined in `act_operator/__init__.py`.
- **Contributors do not bump versions directly.** Maintainers handle version increments and publishing (`uv build`).

## Security Vulnerability Reporting
- Prefer private channels (e.g., GitHub Security Advisories) over public issues.
- Include reproducibility, impact scope, and any mitigations/workarounds if available.

## License
- Project is licensed under **Apache-2.0**. Contributions are provided under the same license.

## Community & Questions
- For questions, please use our Discord: https://discord.gg/4GTNbEy5EB
- We welcome constructive feedback and collaboration.


