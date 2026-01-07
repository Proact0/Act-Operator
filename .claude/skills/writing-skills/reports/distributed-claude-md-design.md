# Distributed CLAUDE.md Design

## Current Structure

```
PROJECT_ROOT/
  CLAUDE.md                    # Single file with everything
    ├─ # Act Name
    ├─ ## Act Overview
    ├─ ## Casts (table)
    ├─ # Cast: CastName1 (full details)
    ├─ # Cast: CastName2 (full details)
    └─ ## Next Steps
```

---

## New Structure

```
PROJECT_ROOT/
  CLAUDE.md                    # Act-level information only
    ├─ # Act Name
    ├─ ## Act Overview
    ├─ ## Casts (summary table)
    └─ ## Next Steps

  casts/
    cast_name_1/
      CLAUDE.md                # Cast1 details
        ├─ # Cast: CastName1
        ├─ ## Overview
        ├─ ## Architecture Diagram
        ├─ ## State Schema
        ├─ ## Node Specifications
        └─ ## Technology Stack

    cast_name_2/
      CLAUDE.md                # Cast2 details
        └─ (same structure)
```

---

## Benefits

1. **Separation of Concerns**: Act-level vs Cast-level information
2. **Scalability**: Adding casts doesn't bloat root CLAUDE.md
3. **Team Collaboration**: Different people can work on different casts
4. **Clarity**: Cast implementers only need cast-specific CLAUDE.md
5. **Version Control**: Changes to one cast don't affect others

---

## File Changes Required

### 1. SKILL.md

**Mode 1: Initial Design**
```diff
- 3. Generate CLAUDE.md → Use output-template.md
+ 3. Generate CLAUDE.md → Use act-template.md (root) + cast-template.md (casts/{cast_name}/)
```

**Mode 2: Add Cast**
```diff
- 4. Update CLAUDE.md → Add to Casts table + new Cast section
+ 4. Update CLAUDE.md → Add to Casts table (root) + create casts/{cast_name}/CLAUDE.md
```

**Mode 3: Extract Sub-Cast**
```diff
- 4. Update CLAUDE.md → Add sub-cast + update parent cast
+ 4. Update CLAUDE.md → Add to Casts table (root) + create casts/{subcast_name}/CLAUDE.md + update parent cast CLAUDE.md
```

### 2. output-template.md

**Split into two files:**
- `act-template.md` - Act-level CLAUDE.md template
- `cast-template.md` - Cast-level CLAUDE.md template

### 3. validate_architecture.py

**Changes:**
- Check for root `/CLAUDE.md` (Act info)
- Find all `/casts/*/CLAUDE.md` files
- Validate each Cast CLAUDE.md independently
- Cross-reference: Casts table in root vs actual cast files

### 4. Mode Files (minimal changes)

- `modes/initial-design-questions.md` - Output mentions two CLAUDE.md files
- `modes/add-cast-questions.md` - Output location clarified
- `modes/extract-subcast-questions.md` - Output location clarified

---

## Template Structure Details

### Act Template (root /CLAUDE.md)

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
1. Design: Use `architecting-act` skill
2. Scaffold: Use `engineering-act` skill
3. Implement: Use `developing-cast` skill
4. Test: Use `testing-cast` skill
```

### Cast Template (casts/{cast_slug}/CLAUDE.md)

```markdown
# Cast: {{ cookiecutter.cast_name }}

> **Parent Act:** [{{ cookiecutter.act_name }}](../../CLAUDE.md)

## Overview
**Purpose:** {One sentence describing what this cast does}
**Pattern:** {Sequential | Branching | Cyclic | Multi-agent}
**Latency:** {Low | Medium | High}

## Architecture Diagram

\```mermaid
graph TD
    START((START)) --> Node1[NodeName]
    Node1 --> Node2[NodeName]
    Node2 --> END((END))
\```

## State Schema

### InputState
| Field | Type | Description |
|-------|------|-------------|
| field_name | type | description |

### OutputState
| Field | Type | Description |
|-------|------|-------------|
| field_name | type | description |

### OverallState
| Field | Type | Category | Description |
|-------|------|----------|-------------|
| field_name | type | Input | description |
| field_name | type | Output | description |
| field_name | type | Internal | description |

## Node Specifications

### NodeName
| Attribute | Value |
|-----------|-------|
| Responsibility | {Single sentence describing what this node does} |
| Reads | {state fields this node reads} |
| Writes | {state fields this node writes} |

## Technology Stack

> Note: `langgraph`, `langchain` are already in template. List only **additional** dependencies for this Cast.

### Additional Dependencies
| Package | Purpose |
|---------|---------|
| package-name | purpose |

### Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| VAR_NAME | Yes/No | description |
```

---

## Workflow Changes

### Mode 1: Initial Design (No CLAUDE.md exists)

**Old Flow:**
1. Ask Act questions
2. Ask Cast questions
3. Design Cast
4. Write single CLAUDE.md with Act + Cast info

**New Flow:**
1. Ask Act questions
2. Ask Cast questions
3. Design Cast
4. Write `/CLAUDE.md` (Act info + Casts table)
5. Write `/casts/{cast_slug}/CLAUDE.md` (Cast details)

### Mode 2: Add Cast (CLAUDE.md exists)

**Old Flow:**
1. Read CLAUDE.md (all info)
2. Ask new Cast questions
3. Design new Cast
4. Append Cast section to CLAUDE.md

**New Flow:**
1. Read `/CLAUDE.md` (Act info + existing Casts)
2. Ask new Cast questions
3. Design new Cast
4. Update `/CLAUDE.md` Casts table (add row)
5. Create `/casts/{new_cast_slug}/CLAUDE.md` (new Cast details)

### Mode 3: Extract Sub-Cast

**Old Flow:**
1. Read CLAUDE.md (all info)
2. Analyze complex cast section
3. Design sub-cast
4. Update parent cast section + add sub-cast section

**New Flow:**
1. Read `/CLAUDE.md` + `/casts/{parent_cast}/CLAUDE.md`
2. Analyze parent cast complexity
3. Design sub-cast
4. Update `/CLAUDE.md` Casts table (add sub-cast row)
5. Create `/casts/{subcast_slug}/CLAUDE.md` (sub-cast details)
6. Update `/casts/{parent_cast}/CLAUDE.md` (reference sub-cast)

---

## Validation Changes

### New Validation Logic

```python
def validate_distributed_architecture(project_root: Path) -> ValidationReport:
    """Validate distributed CLAUDE.md structure."""

    report = ValidationReport()

    # 1. Validate root CLAUDE.md exists
    root_claude = project_root / "CLAUDE.md"
    if not root_claude.exists():
        report.add(False, "Root CLAUDE.md not found")
        return report

    # 2. Parse root CLAUDE.md
    root_content = root_claude.read_text()
    validate_act_level(root_content, report)

    # 3. Extract casts from table
    casts = extract_casts_from_table(root_content)

    # 4. Validate each cast CLAUDE.md
    casts_dir = project_root / "casts"
    for cast_info in casts:
        cast_path = casts_dir / cast_info["slug"] / "CLAUDE.md"

        if not cast_path.exists():
            report.add(False, f"Cast CLAUDE.md not found: {cast_path}")
            continue

        cast_content = cast_path.read_text()
        validate_cast_level(cast_content, cast_info["name"], report)

    # 5. Cross-reference check
    validate_cast_references(root_content, casts_dir, report)

    return report
```

---

## Migration Path (for existing projects)

For projects with existing monolithic CLAUDE.md:

1. Read current CLAUDE.md
2. Extract Act-level sections (Overview, Casts table)
3. Write new root CLAUDE.md
4. For each Cast section:
   - Extract cast content
   - Create `/casts/{cast_slug}/` directory
   - Write `/casts/{cast_slug}/CLAUDE.md`
5. Validate new structure

---

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| Structure | Monolithic | Distributed |
| Act info | Mixed with casts | Separate file |
| Cast details | All in one file | One file per cast |
| Scalability | Decreases with casts | Constant |
| Discoverability | Scroll through one file | Navigate directory |
| Collaboration | Conflicts likely | Isolated changes |
| Validation | Single file | Multi-file |
