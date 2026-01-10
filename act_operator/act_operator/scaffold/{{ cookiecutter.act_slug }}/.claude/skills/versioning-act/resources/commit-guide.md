# Commit Message Guide

Standardized commit message format for {{ cookiecutter.act_name }} Act project.

**All commit messages MUST be written in {{ cookiecutter.language }}.**

## Format

```
<type><breaking change(!)?>(scope?): <subject>

<body>
```

---

## Header (Required)

### Structure
```
<type>(!)?(<scope>)?: <subject>
```

- **type**: Required. See type table below.
- **!**: Optional. Indicates breaking change.
- **scope**: Optional. Component/area affected.
- **subject**: Required. Short description (imperative mood).

### Types

| Type | When to Use |
|------|-------------|
| `cast` | New cast (graph) feature or functionality |
| `fix` | Bug fix |
| `docs` | Documentation changes only |
| `style` | Formatting, whitespace (no code logic change) |
| `refactor` | Code restructuring without behavior change |
| `perf` | Performance improvement |
| `test` | Adding or updating tests |
| `build` | Build system or dependencies |
| `ci` | CI configuration changes |
| `chore` | Maintenance, tooling |
| `revert` | Revert previous commit |
| `remove` | Remove feature or file |
| `rename` | Rename files or directories |
| `release` | Release version preparation |
| `comment` | Code comments only |
| `HOTFIX` | Urgent production fix |

### Subject Guidelines

- Use imperative mood ("add" not "added", "fix" not "fixed")
- No period at end
- Max 50 characters recommended
- Capitalize first letter

---

## Body (Optional, Required for Breaking Changes)

### When to Include

- **Required**: Breaking changes (`!` in header)
- **Recommended**: Complex changes needing explanation
- **Optional**: Simple, self-explanatory changes

### Format

```
<blank line>
<body content>
```

### Guidelines

- Explain **motivation** for the change
- Contrast with previous behavior
- Use bullet points (`-`) for multiple items
- Use present tense ("change" not "changed")
- Wrap at 72 characters

---

## Breaking Changes

When introducing breaking changes:

1. Add `!` after type/scope in header
2. **MUST** include body explaining the change

```
cast!(processor): change state schema structure

- InputState now requires 'config' field
- OutputState 'result' field renamed to 'output'
- Existing graphs must update state definitions
```

---

## Examples

### Simple Commit
```
cast(analyzer): add sentiment analysis node
```

### With Scope
```
fix(retriever): handle empty query gracefully
```

### With Body
```
refactor(state): simplify state schema

- Remove redundant fields from OverallState
- Consolidate input validation into InputState
- Improves type safety and reduces boilerplate
```

### Breaking Change
```
cast!(api): migrate to v2 endpoint structure

- All API endpoints now prefixed with /v2/
- Response format changed to include metadata wrapper
- Clients must update endpoint URLs and response parsing
```

### Hotfix
```
HOTFIX(auth): fix token expiration check

Token was comparing timestamps incorrectly causing premature expiration.
```

---

## Workflow

```bash
# 1. Check changes
git status
git diff

# 2. Stage files
git add <files>
# or
git add .

# 3. Commit with message
git commit -m "<type>(<scope>): <subject>"

# 4. For multi-line (with body)
git commit
# Opens editor for full message

# 5. Push
git push origin <branch>
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Past tense ("added feature") | Use imperative ("add feature") |
| Type not in allowed list | Check pr_lint.yml types |
| Missing body for `!` | Always explain breaking changes |
| Subject too long | Keep under 50 chars |
| Wrong language | Use {{ cookiecutter.language }} |
