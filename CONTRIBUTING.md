# Contributing Guide

- 한국어로 읽기: [CONTRIBUTING_KR.md](CONTRIBUTING_KR.md)

Thank you for your interest in contributing to the Act Operator open-source project! We welcome **all forms of contributions**—bug reports, documentation improvements, tests, feature proposals/implementations, and developer experience enhancements. Small, clear changes with friendly explanations and thorough testing make for great collaboration.

## Table of Contents

- [Quick Start](#quick-start)
- [Before Contributing](#before-contributing)
- [Contribution Scope](#contribution-scope)
- [Contribution Guidelines by Type](#contribution-guidelines-by-type)
  - [Bug Fixes](#bug-fixes)
  - [Feature Proposals and Implementation](#feature-proposals-and-implementation)
  - [Documentation Improvements](#documentation-improvements)
  - [Claude Agent Skill Contributions](#claude-agent-skill-contributions)
- [Code Quality Standards](#code-quality-standards)
- [Writing Tests](#writing-tests)
- [Using LLMs for Contributions](#using-llms-for-contributions)
- [Backward Compatibility Policy](#backward-compatibility-policy)
- [PRs and Code Review](#prs-and-code-review)
- [Versioning and Releases](#versioning-and-releases)
- [Community](#community)

---

## Quick Start

### Requirements

- **Python 3.11+**
- **uv**: Dependency management tool

Installation guide: [uv Installation](https://docs.astral.sh/uv/getting-started/installation/)

```bash
pip install uv
```

### Development Environment Setup

```bash
# Clone the repository
git clone https://github.com/Proact0/Act-Operator.git
cd Act-Operator/act_operator

# Install dependencies
uv sync

# Run CLI locally
uv run act new --path ./test-act --act-name "Test" --cast-name "Main"

# Run tests (when available)
uv run pytest
```

---

## Before Contributing

### 💬 Discussion First

**For major changes, always discuss before implementing:**

- **Discord**: https://discord.gg/4GTNbEy5EB
- **GitHub Issues**: [Create new issue](https://github.com/Proact0/act-operator/issues/new/choose)

**When discussion is required:**
- Adding new CLI commands
- Changing scaffold template structure
- Changes affecting backward compatibility
- Adding new dependencies
- Architecture changes

**Can proceed without discussion:**
- Bug fixes (restoring existing behavior)
- Documentation typos
- Adding tests
- Code formatting improvements

### 📋 Use Issue Templates

Before contributing, check for related issues or create a new one:

- **Bug Reports**: [Bug Report Template](https://github.com/Proact0/act-operator/issues/new?template=bug-report-kr.yml)
- **Feature Requests**: [Backlog Template](https://github.com/Proact0/act-operator/issues/new?template=backlog-kr.yml)

---

## Contribution Scope

The Act Operator project consists of several components.

### 1️⃣ Act Operator CLI (This Repository)

**Location**: `act_operator/`

**Includes**:
- CLI commands (`act new`, `act cast`)
- cookiecutter scaffold generation logic
- Build/deployment processes

### 2️⃣ Scaffold Templates

**Location**: `act_operator/scaffold/`

**Includes**:
- Project structure templates
- Base classes (`base_node.py`, `base_graph.py`)

### 3️⃣ Claude Agent Skills

**Location**: `act_operator/scaffold/{{ cookiecutter.act_slug }}/.claude/skills/`

**Includes**:
- `architecting-act`: Architecture design
- `developing-cast`: Implementation patterns
- `engineering-act`: Project management
- `testing-cast`: Testing strategies

### 4️⃣ Documentation (Separate Repository)

**Location**: [Proact0 Docs](https://github.com/Proact0/docs)

**Includes**:
- User guides
- Tutorials
- Pattern library
- Other useful tips

---

## Contribution Guidelines by Type

### Bug Fixes

**Workflow:**

1. Reproduce the bug and create a minimal reproduction case
2. Create an issue (reproduction steps, environment info, expected/actual behavior)
3. Create a branch: `git checkout -b fix/issue-123-descriptive-name`
4. Implement the fix (minimal changes, address root cause)
5. Test locally: `uv run ruff check .`, verify with reproduction case
6. Submit PR (include `Fixes #123`, describe changes and testing method)

### Feature Proposals and Implementation

**⚠️ Discussion required before implementation**

1. Propose in Discord or issue (problem, solution, alternatives, use cases)
2. Get maintainer approval and agree on implementation approach
3. Create branch: `git checkout -b feat/descriptive-feature-name`
4. Implement (type hints, docstrings, documentation updates)
5. Write tests (verify new functionality, edge cases)
6. Submit PR

### Documentation Improvements

**Documentation Types:**

| Type | Audience | Content | Location | Notes |
|------|----------|---------|----------|-------|
| 📘 User Guide | Act Operator users | Installation, usage, examples | `README.md`, `README_KR.md` | |
| 📙 Contributing Guide | Contributors | Dev environment, workflow | `CONTRIBUTING.md`, `CONTRIBUTING_KR.md` | Will migrate to Proact0 Docs |
| 📗 Skill Documentation | Claude Agent | Architecture, implementation guides | `.claude/skills/*/SKILL.md` | |
| 📕 Detailed Docs | Advanced usage, learners | Tutorials, patterns | [Proact0 Docs](https://docs.proact0.org/) | |

**Writing Guidelines:**
- ✅ Clear and concise
- ✅ Include executable examples
- ✅ Avoid duplication: write once, link elsewhere
- ✅ Accessibility: consider screen readers, provide alt text

### Claude Agent Skill Contributions

**Skill Structure:**

```
.claude/skills/<skill-name>/
├── SKILL.md              # Main documentation (required)
├── resources/            # Reference docs (optional)
│   └── *.md
└── scripts/              # Utility scripts (optional)
    └── *.py
```

**Contribution Types:**

1. **Improve Existing Skills**: Fix typos, clarify descriptions, add examples
2. **Write New Skills**: Design and implement completely new skills

**New Skill Requirements:**

- **Frontmatter (YAML)**:
  ```yaml
  ---
  name: skill-name-with-hyphens
  description: Use when [when to use] - [what it does]
  ---
  ```
- **Clear Usage Context**: "Use this skill when:" section
- **Structured Content**: Workflow/Task/Reference patterns
- **Practical Examples**: Code samples, checklists
- **Consistent Style**: Follow existing skills

**Recommended: TDD Approach**

Follow `.claude/skills/writing-skills` guide:
1. Write pressure scenarios
2. Run without skill (baseline)
3. Write skill
4. Re-run with skill
5. Find and fix vulnerabilities

**Skill Contribution Checklist:**
- [ ] Frontmatter (`name`, `description`) included
- [ ] "Use this skill when:" section clear
- [ ] Structured content
- [ ] Examples and code samples
- [ ] Consistent with existing skills
- [ ] (Recommended) Sub-agent testing completed

---

## Code Quality Standards

### Type Hints

**Required**: Complete type annotations for all functions.

```python
def build_name_variants(name: str) -> NameVariants:
    """Build name variants from display name.

    Args:
        name: Display name to convert.

    Returns:
        NameVariants object with snake_case and slug forms.
    """
    # implementation
```

### Docstrings

**Required**: [Google-style docstrings](https://google.github.io/styleguide/pyguide.html) for all public functions.
**Basic Principle**: Docstrings explain "what", [Docs](https://docs.proact0.org/) explain "how" and "why".

**Docstrings should include:**

1. One-line summary of class/function functionality
2. Link to Docs for tutorials, guides, and use cases (if applicable)
3. Parameter types and descriptions
4. Return value description
5. Possible exceptions
6. Minimal example showing basic usage

```python
def render_cookiecutter_template(
    template_path: Path,
    output_dir: Path,
    context: dict[str, str],
) -> Path:
    """Render a cookiecutter template to output directory.

    Args:
        template_path: Path to cookiecutter template directory.
        output_dir: Where to render the template.
        context: Template variables for cookiecutter.

    Returns:
        Path to the rendered project directory.

    Raises:
        CookiecutterError: If template rendering fails.
    """
    # implementation
```

### Code Style

Automation: Use [ruff](https://docs.astral.sh/ruff/) for automatic formatting and linting.

Standards:
- Descriptive variable names
- Break down complex functions (aim for under 20 lines)
- Follow existing patterns in the codebase

### Commit Conventions

**Conventional Commits recommended:**

```
type(scope): subject

feat(cli): add --output option to cast command
fix(scaffold): correct base_node import path
docs(readme): update installation instructions
refactor(utils): simplify name variant conversion
test(cli): add test for path resolution
ci(workflow): update ruff configuration
chore(deps): upgrade dependencies
```

**Allowed types**: `feat`, `fix`, `docs`, `refactor`, `test`, `build`, `ci`, `chore`

**Allowed scopes** (see [pr_lint.yml](.github/workflows/pr_lint.yml)):
- `cli`, `scaffold`, `utils`, `docs`, `tests`
- `workflow`, `cookiecutter`, `ci`, `deps`

---

## Writing Tests

### Unit Tests

**Location**: `tests/unit/`

**Target**: Individual functions/methods

**Requirements**:
- Test all code paths including exceptional cases
- Use mocks for external dependencies

### Integration Tests

Not all code changes require integration tests, but they may be requested separately during code review if needed.

**Location**: `tests/integration/`

**Target**: Complete workflows

**Requirements**:
- Skip gracefully when credentials unavailable

### Running pytest

```bash
# All tests
uv run pytest

# Specific file
uv run pytest tests/unit/test_cli.py

# Verbose output
uv run pytest -v

# Coverage (optional)
uv run pytest --cov=act_operator
```

---

## Using LLMs for Contributions

Proact0 embraces AI-native development. We welcome using LLM tools like Claude Code, Codex, Cursor, Windsurf, and GitHub Copilot as **collaboration partners**.

### ✅ Recommended Uses

- **Code Review**: Quality checks, refactoring suggestions
- **Documentation Drafts**: Structure and expression improvements (review before submission)
- **Test Generation**: Scenario ideas, edge case discovery
- **Debugging**: Error analysis, solution exploration

### ⚠️ Required Verification

**Don't submit LLM output directly.** Always verify:

1. **Contextual Relevance**
   - Does it fit Act Operator's structure and patterns?
   - Does it understand the project's design principles?

2. **Accuracy**
   - Is it technically correct?
   - Is it compatible with current dependencies?

3. **Quality**
   - Does it follow code style and conventions?
   - Can you fully understand and explain it?

### ❌ Avoid

- **Fully LLM-generated** code, documentation, and PR descriptions
- Submitting generated content without understanding it
- Applying generic patterns without project context

**Low-quality PRs/issues may be closed to protect maintainer resources.**

---

## Backward Compatibility Policy

### 🔴 Breaking Changes Prohibited

The following changes are **prohibited without maintainer approval**:

- **CLI API Changes**: Removing options, renaming options, changing behavior
- **Scaffold Structure Changes**: Directory structure, base class signatures, template file removal
- **Public API Changes**: Function signatures, return types

### 🟡 Changes Requiring Discussion

The following require **sufficient discussion**:

- Adding new dependencies
- Changing Python version requirements
- Adding/modifying scaffold template files

### 🟢 Safe Changes

The following can be freely changed:

- Bug fixes (restoring existing behavior)
- Documentation improvements
- Internal refactoring (maintaining public API)
- Adding new options (maintaining existing behavior)
- Adding tests

### Considerations for Changes

**When changing scaffold templates:**
- Will it affect existing users' projects?
- Is a migration guide needed?
- Is version-specific template management needed?

**When changing CLI:**
- Will it affect automation scripts?
- Is it used in CI/CD pipelines?

---

## PRs and Code Review

### PR Checklist

Before submitting a PR, verify:

**Required:**
- [ ] **Link issue**: Related issue link (Fixes #123)
- [ ] **Description**: Describe problem/motivation/solution/alternatives
- [ ] **Linting**: `uv run ruff check .` passes
- [ ] **Tests**: `uv run pytest` passes (if tests exist)
- [ ] **Documentation**: Updated if affecting users
- [ ] **Backward Compatibility**: No breaking changes
- [ ] **Commit Messages**: Conventional Commits format

**Code Quality:**
- [ ] Type hints added
- [ ] Docstrings written (public API)
- [ ] Small, clear changes

**Skill PRs:**
- [ ] Frontmatter included
- [ ] "Use this skill when:" section
- [ ] Structured content and examples

### Code Review Process

**Review Timeline:**
- **Initial Response**: Within 48 hours (business days)
- **Final Review**: Within 7 days (varies by complexity)
- **No Response**: Remind via Discord

**Reviewer Expectations:**
- Provide constructive feedback
- Review code quality, tests, documentation
- Check backward compatibility impact

**Contributor Expectations:**
- Respond promptly to feedback
- Address requested changes
- Keep CI/CD passing

---

## Versioning and Releases

### Version Management

- **Version Location**: `act_operator/__init__.py`
- **Management Tool**: hatch
- **Policy**: Contributors don't change versions directly. Maintainers manage at release time.

### Automatic Dependency Upgrades

- **Automation**: `uv lock --upgrade` runs weekly on Sundays at midnight ([uv_lock_upgrade.yml](.github/workflows/uv_lock_upgrade.yml))
- **PR Creation**: Automatically creates PRs when changes detected
- **Contributor Action**: Review and approve auto-generated dependency PRs

### Security Vulnerability Reports

**Reporting Method:**
- **Channel**: [GitHub Security Advisories](https://github.com/Proact0/Act-Operator/security/advisories)
- **Required Information**:
  - Reproduction steps (detailed step-by-step)
  - Impact scope (affected versions, features)
  - Workarounds (if available)

---

## Getting Help

Our goal is to create the most accessible developer environment possible. If you encounter difficulties during setup, reach out directly on [Discord](https://discord.gg/4GTNbEy5EB) or ask for help from community members.

> [!NOTE]
> You're now ready to contribute your excellent code to Proact0!

---

<div align="center">
  <p>We welcome constructive feedback and collaboration.</p>
  <p>Thank you! 🙏</p>
</div>
