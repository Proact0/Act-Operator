---
name: versioning-act
description: Use when committing changes (commit message formatting), managing branches (create/merge/delete following git flow), or performing git operations (push, pull, rebase, stash) - provides Act-specific conventions for version control with semantic commit messages and branch naming
---

# Versioning {{ cookiecutter.act_name }} Act

Manage version control for {{ cookiecutter.act_name }} Act project using Git Flow strategy adapted for Act conventions.

## When to Use

- Committing code changes with proper message format
- Creating/managing branches following Act conventions
- Merging branches (cast → dev, dev → release, etc.)
- General git operations (push, pull, rebase, stash)

## When NOT to Use

- Architecture design → `architecting-act`
- Implementation → `developing-cast`
- Testing → `testing-cast`
- Project setup → `engineering-act`

---

## Operation Detection

**First, determine which operation:**

- **Need to commit?** → **Commit Workflow**
- **Need to create/manage branch?** → **Branch Workflow**
- **Other git operation?** → **Git Commands Reference**

---

## Commit Workflow

**When:** Committing changes to repository

**Format:**
```
<type><breaking change(!)?>(scope?): <subject>

<body>
```

**Commit messages MUST be written in {{ cookiecutter.language }}.**

**Steps:**
1. **Review Changes** → `git status`, `git diff`
2. **Stage Changes** → `git add <files>` or `git add .`
3. **Write Message** → Follow [commit-guide.md](resources/commit-guide.md)
4. **Commit** → `git commit -m "<message>"`
5. **Push** → `git push origin <branch>`

### Commit Types (from pr_lint.yml)

| Type | Description |
|------|-------------|
| `cast` | New cast (graph) feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no code change |
| `refactor` | Code restructuring |
| `perf` | Performance improvement |
| `test` | Adding/updating tests |
| `build` | Build system changes |
| `ci` | CI configuration |
| `chore` | Maintenance tasks |
| `revert` | Revert previous commit |
| `remove` | Remove feature/file |
| `rename` | Rename files/directories |
| `release` | Release preparation |
| `comment` | Code comments only |
| `HOTFIX` | Urgent production fix |

---

## Branch Workflow

**When:** Creating or managing branches

{{ cookiecutter.act_name }} Act follows **Git Flow** strategy with Act-specific branch naming.

**Steps:**
1. **Identify Purpose** → What type of work?
2. **Follow Convention** → See [branch-strategy.md](resources/branch-strategy.md)
3. **Create Branch** → `git checkout -b <branch-name>`
4. **Work & Commit** → Follow Commit Workflow
5. **Merge** → Follow merge rules per branch type

### Branch Types

| Branch | Purpose | Naming |
|--------|---------|--------|
| `main` | Production-ready code | `main` |
| `dev` | Development integration | `dev` |
| `release/*` | Release preparation | `release/{version}` |
| `cast/*` | New cast development | `cast/{cast-name}` |
| `HOTFIX/*` | Urgent production fix | `HOTFIX/{issue}` |

### Merge Rules

```
cast/{name} → dev (only)
dev → release/{version} → main, dev
HOTFIX/{issue} → main, dev
```

---

## Operations

| Task | Resource |
|------|----------|
| Write commit message | `resources/commit-guide.md` |
| Manage branches | `resources/branch-strategy.md` |
| Git commands reference | `resources/git-commands.md` |

---

## Quick Reference

```bash
# Commit
git add .
git commit -m "cast(graph-name): add new processing node"
git push origin cast/my-feature

# Branch
git checkout -b cast/new-feature    # Create cast branch
git checkout dev                     # Switch to dev
git merge cast/new-feature          # Merge cast into dev
git branch -d cast/new-feature      # Delete local branch

# Common
git status                          # Check status
git log --oneline -10               # Recent commits
git pull origin dev                 # Update from remote
git stash                           # Stash changes
git stash pop                       # Restore stashed changes
```

---

## Verification Checklist

- [ ] Commit type matches pr_lint.yml types
- [ ] Commit message written in {{ cookiecutter.language }}
- [ ] Breaking changes marked with `!` and explained in body
- [ ] Branch follows naming convention
- [ ] Merge follows allowed direction rules
