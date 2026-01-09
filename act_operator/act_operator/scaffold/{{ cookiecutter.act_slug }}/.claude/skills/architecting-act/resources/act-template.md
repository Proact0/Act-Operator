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

## Project Structure

```
{{ cookiecutter.act_slug }}/
├── CLAUDE.md                    # Act-level architecture doc (THIS FILE)
├── pyproject.toml               # Project dependencies
├── langgraph.json               # LangGraph configuration
├── .env.example                 # Environment variables template
├── casts/                       # All Cast implementations
│   ├── __init__.py
│   ├── base_graph.py            # Base graph utilities
│   ├── base_node.py             # Base node utilities
│   └── {cast_slug}/             # Individual Cast package
│       ├── CLAUDE.md            # Cast-level architecture doc
│       ├── graph.py             # Graph definition
│       ├── pyproject.toml       # Cast-specific dependencies
│       └── modules/             # Implementation modules
└── tests/                       # Test suites
    ├── cast_tests/              # Integration tests
    └── node_tests/              # Unit tests
```

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

## Checklist

- [ ] Act Overview is clear and concise (1-2 sentences)
- [ ] Domain is specified
- [ ] All Casts are listed in Casts table
- [ ] Each Cast has a working link to its CLAUDE.md
