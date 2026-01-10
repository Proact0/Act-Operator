# Branch Strategy

{{ cookiecutter.act_name }} Act follows **Git Flow** adapted for Act project conventions.

---

## Branch Overview

```
main ─────────────────────────────────────────────────
  │                              ↑            ↑
  │                           merge        merge
  │                              │            │
  └─→ dev ──────────────────────────────────────────
        │         ↑        ↑              ↑
        │      merge    merge          merge
        │         │        │              │
        ├─→ cast/feature-a ─┘              │
        │                                  │
        └─→ release/0.1.0 ─────────────────┘

main ←── HOTFIX/critical-bug ──→ dev
```

---

## Branch Types

### main

**Production-ready code. Always deployable.**

| Attribute | Value |
|-----------|-------|
| Naming | `main` |
| Source | `release/*` or `HOTFIX/*` |
| Merges to | None (except initial `dev` creation) |
| Protection | Required reviews, no direct commits |

**Rules:**
- Never commit directly
- Only receives merges from `release/*` or `HOTFIX/*`
- Always in deployable state

---

### dev (develop)

**Integration branch for completed features.**

| Attribute | Value |
|-----------|-------|
| Naming | `dev` |
| Source | `main` (initial) |
| Merges to | `release/*`, `cast/*` |
| Receives from | `cast/*`, `release/*` (bugfix), `HOTFIX/*` |

**Rules:**
- Integration point for all cast branches
- Bug fixes go back to the originating cast branch, not here
- Base for release branches

```bash
# Create dev from main (initial setup only)
git checkout main
git checkout -b dev
git push -u origin dev
```

---

### cast/* (feature)

**New cast (graph) development.**

| Attribute | Value |
|-----------|-------|
| Naming | `cast/{cast-name}` |
| Source | `dev` |
| Merges to | `dev` only |
| Receives from | `dev` (rebase/merge for updates) |

**Rules:**
- One branch per cast being developed
- Name matches cast slug (e.g., `cast/sentiment-analyzer`)
- Only merges back to `dev`
- Delete after merge

```bash
# Create cast branch
git checkout dev
git pull origin dev
git checkout -b cast/my-new-cast
git push -u origin cast/my-new-cast

# Work and commit...

# Merge back to dev
git checkout dev
git pull origin dev
git merge cast/my-new-cast
git push origin dev

# Cleanup
git branch -d cast/my-new-cast
git push origin --delete cast/my-new-cast
```

---

### release/*

**Release preparation and QA.**

| Attribute | Value |
|-----------|-------|
| Naming | `release/{version}` (e.g., `release/0.1.0`) |
| Source | `dev` |
| Merges to | `main` and `dev` |
| Receives from | Bug fixes only |

**Rules:**
- Only bug fixes allowed, no new features
- QA and final testing happens here
- Version bumps and changelog updates
- Merges to both `main` AND `dev` when complete

```bash
# Create release branch
git checkout dev
git pull origin dev
git checkout -b release/0.1.0
git push -u origin release/0.1.0

# Bug fixes during release...

# Complete release
git checkout main
git merge release/0.1.0
git tag -a v0.1.0 -m "Release 0.1.0"
git push origin main --tags

git checkout dev
git merge release/0.1.0
git push origin dev

# Cleanup
git branch -d release/0.1.0
git push origin --delete release/0.1.0
```

---

### HOTFIX/*

**Urgent production fixes.**

| Attribute | Value |
|-----------|-------|
| Naming | `HOTFIX/{issue-description}` |
| Source | `main` |
| Merges to | `main` AND `dev` |
| Purpose | Critical bug in production |

**Rules:**
- Branch from `main` only
- Fix must be minimal and focused
- Merges to BOTH `main` and `dev`
- Uppercase `HOTFIX` prefix

```bash
# Create hotfix branch
git checkout main
git pull origin main
git checkout -b HOTFIX/fix-auth-crash
git push -u origin HOTFIX/fix-auth-crash

# Fix and commit...

# Complete hotfix
git checkout main
git merge HOTFIX/fix-auth-crash
git tag -a v0.1.1 -m "Hotfix: fix auth crash"
git push origin main --tags

git checkout dev
git merge HOTFIX/fix-auth-crash
git push origin dev

# Cleanup
git branch -d HOTFIX/fix-auth-crash
git push origin --delete HOTFIX/fix-auth-crash
```

---

## Merge Rules Summary

| From | To | Allowed |
|------|----|---------|
| `cast/*` | `dev` | Yes |
| `cast/*` | `main` | No |
| `cast/*` | `release/*` | No |
| `dev` | `release/*` | Yes (create) |
| `dev` | `main` | No |
| `release/*` | `main` | Yes |
| `release/*` | `dev` | Yes (bug fixes) |
| `HOTFIX/*` | `main` | Yes |
| `HOTFIX/*` | `dev` | Yes |
| `main` | `dev` | Initial only |
| `main` | `HOTFIX/*` | Yes (create) |

---

## Naming Examples

```bash
# Cast branches
cast/sentiment-analyzer
cast/document-processor
cast/chat-agent

# Release branches
release/0.1.0
release/1.0.0
release/2.3.1

# Hotfix branches
HOTFIX/fix-memory-leak
HOTFIX/correct-api-endpoint
HOTFIX/patch-security-vuln
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Merge cast directly to main | Always go through dev first |
| Create feature on release branch | Create cast branch from dev |
| Hotfix from dev | Hotfix must branch from main |
| Forget to merge hotfix to dev | Always merge to both main and dev |
| Leave branches after merge | Delete merged branches |
