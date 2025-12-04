## Contributing Guide (EN)

- Read this in Korean: [CONTRIBUTING.md](CONTRIBUTING.md)

Thank you for your interest in contributing to Act Operator! We welcome all forms of contribution — bug reports, documentation improvements, tests, feature proposals/implementations, and developer experience enhancements. Small, clear changes with kind explanations and sufficient tests make for great collaboration.

## Types of Contributions
- **Bug Reports**: Use the issue templates and include reproduction steps, environment, expected vs actual behavior.
- **Documentation Improvements**: Update Claude Skills/README/guides/examples; fix typos and clarify phrasing.
- **Tests**: Add unit/integration tests for new or changed functionality.
- **Feature Proposals/Implementations**: Split into small, reviewable PRs with clear goals.
- **Developer Experience/Performance**: Improve linting/build/run flows or runtime efficiency when appropriate.

## Quick Start

### Requirements
- **Python 3.12+**
- **Windows, macOS, Linux** supported
- **uv** (recommended): manage dependencies, execution, and builds.

Installation guide: [uv Installation](https://docs.astral.sh/uv/getting-started/installation/)

```bash
# Install uv
pip install uv
```

### Clone the repository and set up development
```bash
# Clone repository
git clone https://github.com/Proact0/Act-Operator.git
cd act-operator

# Install runtime + dev dependencies
uv sync --dev

# Add the package as editable (optional but handy for local development)
uv add --editable .
```

### Run tests and CLI locally
```bash
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

```bash
# Lint checks
uv run ruff check .

# Optional: apply formatting
uv run ruff format .
```

Note: the `act_operator/scaffold` path is excluded from linting.

### Tests (pytest)
Tests live under `tests/` as unit/integration tests. Add appropriate tests for new or modified behavior.

```bash
uv run pytest -q
```

## Docs/Examples Updates
- If a change affects users, update `README.md` or related guides accordingly.
- Check whether scaffold templates (`act_operator/act_operator/scaffold/`) need updates in `README.md` or `TEMPLATE_README.md`.

## Contributing to Claude Agent Skills

The Act Operator scaffold includes Skills that help Claude Agent support Cast development. This section guides you on how to improve existing Skills or add new ones.

### Skill Structure

Each Skill follows this directory structure:

```
.claude/skills/<skill-name>/
├── SKILL.md          # Skill main document (required)
├── references/       # Reference documents (optional)
│   └── *.md
├── scripts/          # Utility scripts (optional)
│   └── *.py
└── assets/           # Example files (optional)
    └── *.txt, *.py, etc.
```

### Improving Existing Skills

**SKILL.md Writing Guide:**
- **Required Frontmatter**: Include `name` and `description` in YAML frontmatter
  ```yaml
  ---
  name: skill-name
  description: Clear and concise description - include when to use this skill
  ---
  ```
- **Clear Usage Scenarios**: Specify usage scenarios with "Use this skill when:" section
- **Structured Content**: Choose appropriate structure from Workflow/Task/Reference patterns
- **Practical Examples**: Include code samples, checklists, step-by-step guides
- **Reference Links**: Mention related `references/`, `scripts/`, `assets/` files

**references/ Documents:**
- API references, best practices, pattern guides, etc.
- Write in Markdown format
- Link appropriately from the Skill's main document

**scripts/ Utilities:**
- Validation, automation, helper scripts, etc.
- Python scripts recommended
- Should be executable independently or usable within Skill context

**assets/ Examples:**
- Templates, configuration files, example code, etc.
- Real, usable examples referenced in Skill documentation

### Adding a New Skill

1. **Create Skill Directory**
   ```bash
   mkdir -p act_operator/act_operator/scaffold/{{ cookiecutter.act_slug }}/.claude/skills/<skill-name>/{references,scripts,assets}
   ```

2. **Write SKILL.md**
   - Reference existing Skills (`cast-development`, `act-setup`, etc.) for structure
   - Include clear name and description in frontmatter
   - Include usage scenarios, workflows, examples

3. **Add Required Resources**
   - `references/`: Related documents
   - `scripts/`: Utility scripts
   - `assets/`: Example files

4. **Test and Validate**
   - Verify the Skill works correctly in actual Claude Agent
   - Validate that examples in documentation are accurate

### Skill Contribution Checklist

- [ ] SKILL.md includes frontmatter (`name`, `description`)
- [ ] "Use this skill when:" section clearly describes usage scenarios
- [ ] Structured content (Workflow/Task/Reference, etc.)
- [ ] Practical examples and code samples included
- [ ] Links to related references/scripts/assets files
- [ ] Consistent style with existing Skills
- [ ] Verify all links and references in documentation are accurate

### Existing Skills List

Currently included Skills:
- **cast-development**: Cast module development (nodes, state, graph implementation)
- **act-setup**: Act project setup and uv workspace management
- **graph-composition**: Graph composition and edge connections
- **modules-integration**: Module integration (agents, tools, prompts, etc.)
- **node-implementation**: Node implementation patterns and best practices
- **state-management**: State management and schema definition
- **testing-debugging**: Test writing and debugging

Please update this list when adding new Skills.

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
- Module entry: `uv run -m act_operator` when needed.

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