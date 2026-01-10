# Git Commands Reference

Quick reference for common Git operations in {{ cookiecutter.act_name }} Act project.

---

## Status & Information

```bash
# Check current status
git status

# View commit history
git log --oneline -10          # Last 10 commits, compact
git log --graph --oneline      # With branch graph
git log -p                     # With diffs

# View changes
git diff                       # Unstaged changes
git diff --staged              # Staged changes
git diff HEAD~1                # Compare with previous commit

# View branches
git branch                     # Local branches
git branch -r                  # Remote branches
git branch -a                  # All branches
```

---

## Staging & Committing

```bash
# Stage files
git add <file>                 # Specific file
git add .                      # All changes
git add -p                     # Interactive staging

# Unstage
git reset <file>               # Unstage file
git reset                      # Unstage all

# Commit
git commit -m "message"        # With message
git commit                     # Open editor
git commit --amend             # Amend last commit

# Undo commits
git reset --soft HEAD~1        # Undo commit, keep changes staged
git reset --mixed HEAD~1       # Undo commit, keep changes unstaged
git reset --hard HEAD~1        # Undo commit, discard changes
```

---

## Branching

```bash
# Create branch
git checkout -b <branch>       # Create and switch
git branch <branch>            # Create only

# Switch branch
git checkout <branch>          # Switch to branch
git switch <branch>            # Modern switch

# Delete branch
git branch -d <branch>         # Delete (safe)
git branch -D <branch>         # Force delete
git push origin --delete <branch>  # Delete remote

# Rename branch
git branch -m <old> <new>      # Rename local
```

---

## Merging & Rebasing

```bash
# Merge
git checkout dev
git merge cast/feature         # Merge feature into dev
git merge --no-ff <branch>     # Merge with commit

# Rebase
git checkout cast/feature
git rebase dev                 # Rebase onto dev
git rebase -i HEAD~3           # Interactive rebase

# Abort operations
git merge --abort              # Abort merge
git rebase --abort             # Abort rebase

# Resolve conflicts
# 1. Edit conflicted files
# 2. git add <resolved-files>
# 3. git merge --continue (or git rebase --continue)
```

---

## Remote Operations

```bash
# View remotes
git remote -v

# Fetch & Pull
git fetch origin               # Fetch all
git fetch origin <branch>      # Fetch specific
git pull origin <branch>       # Fetch + merge
git pull --rebase origin dev   # Fetch + rebase

# Push
git push origin <branch>       # Push branch
git push -u origin <branch>    # Push and set upstream
git push --force-with-lease    # Safe force push
git push origin --tags         # Push tags

# Track remote
git branch --set-upstream-to=origin/<branch> <local-branch>
```

---

## Stashing

```bash
# Stash changes
git stash                      # Stash working changes
git stash save "message"       # With description
git stash -u                   # Include untracked

# List stashes
git stash list

# Apply stash
git stash pop                  # Apply and remove
git stash apply                # Apply and keep
git stash apply stash@{2}      # Apply specific

# Remove stash
git stash drop                 # Drop latest
git stash drop stash@{2}       # Drop specific
git stash clear                # Clear all
```

---

## Tagging

```bash
# Create tags
git tag v0.1.0                 # Lightweight
git tag -a v0.1.0 -m "Release" # Annotated

# List tags
git tag
git tag -l "v1.*"              # Pattern match

# Push tags
git push origin v0.1.0         # Specific tag
git push origin --tags         # All tags

# Delete tags
git tag -d v0.1.0              # Local
git push origin --delete v0.1.0  # Remote
```

---

## Undoing & Recovery

```bash
# Discard working changes
git checkout -- <file>         # Specific file
git restore <file>             # Modern restore
git checkout .                 # All files

# Revert commit (creates new commit)
git revert <commit>
git revert HEAD                # Revert last commit

# Cherry-pick
git cherry-pick <commit>       # Apply specific commit

# Find lost commits
git reflog                     # View reference log
git checkout <commit>          # Recover commit
```

---

## Configuration

```bash
# User settings
git config --global user.name "Name"
git config --global user.email "email@example.com"

# View config
git config --list
git config user.name

# Aliases (examples)
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
```

---

## Useful Combinations

```bash
# Start new cast
git checkout dev && git pull origin dev
git checkout -b cast/new-feature
git push -u origin cast/new-feature

# Update cast with dev changes
git checkout cast/my-feature
git fetch origin dev
git rebase origin/dev
git push --force-with-lease origin cast/my-feature

# Complete cast merge
git checkout dev
git pull origin dev
git merge cast/my-feature
git push origin dev
git branch -d cast/my-feature
git push origin --delete cast/my-feature

# Quick commit and push
git add . && git commit -m "fix: resolve issue" && git push

# View what changed in a file
git log --oneline -p -- <file>
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Merge conflict | Edit files, `git add`, `git merge --continue` |
| Committed to wrong branch | `git reset HEAD~1`, switch, recommit |
| Need to undo push | `git revert` (don't force push shared branches) |
| Detached HEAD | `git checkout <branch>` to reattach |
| Forgot to add file to commit | `git add <file>`, `git commit --amend` |
| Stash conflicts | `git stash pop`, resolve, `git stash drop` |
