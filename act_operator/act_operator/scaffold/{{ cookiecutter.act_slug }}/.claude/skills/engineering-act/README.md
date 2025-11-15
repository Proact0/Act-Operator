# Engineering Act Skill

**Version:** 1.0.0
**Purpose:** Automates Act project setup, dependency management, and cast scaffolding through scripts and clear command guidance

## Overview

This skill provides **maximum automation** for repetitive project operations. Scripts do the work, SKILL.md is a command index.

**Core Principle:** If Claude has to type it more than once, there's a script for it.

## File Structure

```
engineering-act/
├── SKILL.md                    # Command cheat sheet (~1.5k tokens)
├── README.md                   # This file
├── resources/                  # Quick references (< 2k tokens each)
│   ├── uv-commands.md          # Essential uv command reference
│   ├── cast-structure.md       # Cast directory layout guide
│   └── troubleshooting.md      # Common issues and fixes
└── scripts/                    # Automation scripts (save 100+ tokens each)
    ├── create_cast.py          # Create cast with full boilerplate (~300 tokens saved)
    ├── project_info.py         # Display project status (~150 tokens saved)
    ├── validate_project.py     # Check structure and config (~200 tokens saved)
    ├── batch_dependencies.py   # Batch add/remove packages (~100 tokens saved)
    └── sync_check.py           # Sync with change tracking (~100 tokens saved)
```

## Design Philosophy

### Automation First
- Every repetitive operation has a script
- Scripts handle edge cases and errors
- Scripts provide helpful output and guidance
- Minimum 100-token savings per script

### Token Efficiency
- SKILL.md is scannable reference, not tutorial
- Resources are quick-lookup, not manuals
- Scripts do the heavy lifting
- Total skill: < 10k tokens (highly optimized)

### Developer Productivity
- Remove friction from common tasks
- Provide instant feedback
- Guide next steps
- Enable flow state

## Scripts Overview

### create_cast.py (~300 tokens saved)
**Problem:** Manual cast creation is tedious and error-prone
**Solution:** Create cast with full boilerplate structure

**Usage:**
```bash
uv run python .claude/skills/engineering-act/scripts/create_cast.py "My Graph"
uv run python .claude/skills/engineering-act/scripts/create_cast.py "Simple Cast" --minimal
```

**Creates:**
- Cast directory structure
- graph.py with BaseGraph template
- modules/state.py with proper schema
- modules/models.py with LLM configs
- modules/agents.py, tools.py, prompts.py, utils.py, middlewares.py

**Token Savings:** ~300 tokens vs manual file creation and typing

---

### project_info.py (~150 tokens saved)
**Problem:** Need to run multiple commands to see project status
**Solution:** Single command shows everything

**Usage:**
```bash
uv run python .claude/skills/engineering-act/scripts/project_info.py
uv run python .claude/skills/engineering-act/scripts/project_info.py --packages
```

**Shows:**
- Project name and Python version
- Installed package count
- List of casts
- Dependency groups
- Environment status

**Token Savings:** ~150 tokens vs multiple commands

---

### validate_project.py (~200 tokens saved)
**Problem:** Structural issues cause runtime errors
**Solution:** Comprehensive validation before development

**Usage:**
```bash
uv run python .claude/skills/engineering-act/scripts/validate_project.py
uv run python .claude/skills/engineering-act/scripts/validate_project.py --fix
```

**Checks:**
- Required files and directories
- pyproject.toml structure
- Cast structures
- Workspace configuration
- Environment setup

**Token Savings:** ~200 tokens vs manual verification

---

### batch_dependencies.py (~100 tokens saved)
**Problem:** Adding multiple packages requires multiple commands
**Solution:** Batch operations

**Usage:**
```bash
uv run python .claude/skills/engineering-act/scripts/batch_dependencies.py add langchain-openai langchain-anthropic
uv run python .claude/skills/engineering-act/scripts/batch_dependencies.py add --dev pytest-asyncio pytest-mock
uv run python .claude/skills/engineering-act/scripts/batch_dependencies.py remove old-package
```

**Token Savings:** ~100 tokens vs multiple `uv add` commands

---

### sync_check.py (~100 tokens saved)
**Problem:** Don't know what changed after sync
**Solution:** Show added/removed packages

**Usage:**
```bash
uv run python .claude/skills/engineering-act/scripts/sync_check.py
uv run python .claude/skills/engineering-act/scripts/sync_check.py --all-extras
```

**Shows:**
- Packages before/after sync
- Added packages
- Removed packages

**Token Savings:** ~100 tokens vs manual comparison

---

## Resources Overview

### uv-commands.md (~1k tokens)
Scannable reference of essential `uv` commands:
- Dependency management
- Environment synchronization
- Package information
- Python version management
- Tool execution
- Common workflows

**Format:** Command → Example → Explanation

---

### cast-structure.md (~1.5k tokens)
Cast directory layout and organization:
- Standard structure
- File purposes
- Import patterns
- Best practices
- Minimal vs full structure

**Format:** Structure diagram → File explanations → Examples

---

### troubleshooting.md (~2k tokens)
Common issues and fixes:
- Environment issues
- Dependency conflicts
- Cast problems
- LangGraph errors
- Python version issues
- Debugging workflow

**Format:** Symptom → Fix → Explanation

---

## Usage Patterns

### After architecting-act (CLAUDE.md created)
```bash
# Add dependencies
uv add langchain-experimental

# Create cast
uv run python .claude/skills/engineering-act/scripts/create_cast.py "MyGraph"

# Validate
uv run python .claude/skills/engineering-act/scripts/validate_project.py

# Proceed to developing-cast
/developing-cast
```

### Setting Up Development Environment
```bash
# Sync all dependencies
uv sync --all-extras

# Check status
uv run python .claude/skills/engineering-act/scripts/project_info.py

# Validate setup
uv run python .claude/skills/engineering-act/scripts/validate_project.py
```

### Adding Multiple Packages
```bash
# Instead of:
# uv add pkg1
# uv add pkg2
# uv add pkg3

# Do:
uv run python .claude/skills/engineering-act/scripts/batch_dependencies.py add pkg1 pkg2 pkg3
```

## Integration with Other Skills

**Position in Skillset:**
This is **skill 2 of 4** in the Act Operator skillset:
1. architecting-act - Designs graph architecture
2. **engineering-act** ← (THIS SKILL) - Manages project and environment
3. developing-cast - Implements graph components
4. testing-cast - Tests nodes and graphs

**Workflow:**
```
architecting-act → CLAUDE.md → engineering-act → Cast setup → developing-cast
```

**Inputs:**
- Project created by `act new`
- Architecture from architecting-act (CLAUDE.md)

**Outputs:**
- Synced environment
- Created casts with boilerplate
- Validated project structure
- Ready for developing-cast

## Token Budget Analysis

**Total Skill Size:** ~8.5k tokens (highly optimized)

- SKILL.md: ~1.5k tokens
- Resources: ~4.5k tokens
  - uv-commands.md: ~1k tokens
  - cast-structure.md: ~1.5k tokens
  - troubleshooting.md: ~2k tokens
- Scripts: Executable (loaded on demand, not in context)
- README: ~1.5k tokens

**Optimization Strategy:**
- Aggressively concise SKILL.md (just command index)
- Resources are scannable quick reference
- Scripts do all the work (not in context)
- Total context usage minimal

**Token Savings:**
- Per cast creation: ~300 tokens
- Per project status check: ~150 tokens
- Per validation: ~200 tokens
- Per batch operation: ~100 tokens

**ROI:** Skill pays for itself after ~6 operations

## Quality Criteria Met

✓ SKILL.md under 2k tokens (highly scannable)
✓ Each resource under 2k tokens
✓ Scripts save 100+ tokens each
✓ All commands tested and work
✓ Proper error handling
✓ Self-documenting (--help)
✓ Templates generate valid code
✓ Follows Act project conventions
✓ Maximum automation achieved

## Testing Validation

All scripts include:
- Argument parsing with --help
- Error handling with actionable messages
- Success/failure reporting
- Proper exit codes

Common edge cases handled:
- Missing files/directories
- Invalid configurations
- Network failures (for uv commands)
- Environment issues

## Development Notes

### Created
2025-11-15

### Research Sources
- uv official documentation (https://docs.astral.sh/uv/)
- Act project structure analysis
- LangGraph integration patterns
- Python project management best practices

### Design Decisions
1. **Scripts over docs** - Automation saves more tokens than documentation
2. **Minimal SKILL.md** - Command index, not tutorial
3. **Quick reference resources** - Scannable, not comprehensive
4. **Token efficiency priority** - Every word earns its place
5. **Developer productivity focus** - Remove all friction

## Future Enhancements

Potential improvements:
- CI/CD integration scripts
- Deployment automation
- Performance monitoring
- Dependency security scanning
- Auto-update notifications

## Contributing

This skill is part of the Act Operator project. Improvements welcome via:
- New automation scripts (if they save 100+ tokens)
- Enhanced validation rules
- Additional troubleshooting solutions
- Token optimization

---

**Remember:** This skill's value is in AUTOMATION, not documentation. If you're typing repetitive commands, there should be a script for it.
