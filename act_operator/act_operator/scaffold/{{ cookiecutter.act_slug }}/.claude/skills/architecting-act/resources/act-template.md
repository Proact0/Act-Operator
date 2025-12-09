# Act-Level CLAUDE.md Template

Template for creating the root CLAUDE.md with Act overview and Casts summary.

## Full Template Structure

```markdown
# {{ cookiecutter.act_name }}

## Act Overview
**Purpose:** {One sentence describing what this project does}
**Domain:** {e.g., Customer Support, Data Processing, Business Automation}

## Casts
| Cast Name | Purpose | Location |
|-----------|---------|----------|
| {{ cookiecutter.cast_name }} | {Brief purpose} | [casts/{{ cookiecutter.cast_slug }}/CLAUDE.md](casts/{{ cookiecutter.cast_slug }}/CLAUDE.md) |

## Next Steps

### Initial Setup
1. Review this architecture
2. Create cast package: `uv run act cast -c "{{ cookiecutter.cast_name }}"`
3. Implement cast following [casts/{{ cookiecutter.cast_slug }}/CLAUDE.md](casts/{{ cookiecutter.cast_slug }}/CLAUDE.md)

### Development Workflow
1. **Design**: Use `architecting-act` skill - Create/update architecture
2. **Scaffold**: Use `engineering-act` skill - Create cast package and manage dependencies
3. **Implement**: Use `developing-cast` skill - Implement nodes, state, and graph
4. **Test**: Use `testing-cast` skill - Write and run tests
```

## Usage Notes

### Location
- **File path**: `PROJECT_ROOT/CLAUDE.md`
- **Contains**: Act-level information and Casts summary only
- **Does NOT contain**: Detailed Cast specifications (those go in `casts/{cast_slug}/CLAUDE.md`)

### When to Update

- **Initial Design (Mode 1)**: Create this file
- **Add Cast (Mode 2)**: Add row to Casts table
- **Extract Sub-Cast (Mode 3)**: Add row to Casts table for sub-cast
- **Update Act Purpose**: Modify Act Overview section

### Casts Table Format

Each row should have:
- **Cast Name**: Display name (PascalCase)
- **Purpose**: One sentence describing what this cast does
- **Location**: Link to cast's CLAUDE.md file in `casts/` directory

### Next Steps Section

Keep this section updated with:
- Current implementation status
- Next cast to implement
- Outstanding architecture decisions
- Dependencies between casts

## Checklist

- [ ] Act Overview is clear and concise (1-2 sentences)
- [ ] Domain is specified
- [ ] All Casts are listed in Casts table
- [ ] Each Cast has a working link to its CLAUDE.md
- [ ] Next Steps are actionable
