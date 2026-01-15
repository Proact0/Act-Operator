---
name: architecting-act
description: Use when starting new Act project (CLAUDE.md doesn't exist), adding cast to existing Act (CLAUDE.md exists), or facing complex cast needing sub-cast extraction (>10 nodes) - guides through interactive questioning (one question at a time) from requirements to validated architecture with mermaid diagrams, emphasizing design before implementation, no code generation
version: 1.0.0
context: fork
activation:
  keywords:
    - design new act
    - create act architecture
    - add cast to act
    - extract sub-cast
    - cast too complex
    - architecture diagram
    - state schema design
    - node specification
    - mermaid diagram for cast
    - langgraph architecture
    - design cast workflow
    - act project structure
    - CLAUDE.md not exist
    - planning cast design
  patterns:
    - (?i)(design|create|plan)\s+(new\s+)?act\s+(architecture|project)
    - (?i)(add|create|design)\s+(new\s+)?cast\s+(to|for)
    - (?i)(extract|split|decompose)\s+sub-?cast
    - (?i)cast\s+(is\s+)?(too\s+)?(complex|large|>?10\s*nodes)
    - (?i)(architecture|design)\s+(diagram|specification)
    - (?i)(state|node)\s+schema\s+(design|definition)
    - (?i)CLAUDE\.md\s+(doesn'?t|does\s+not)\s+exist
---

# Architecting {{ cookiecutter.act_name }} Act

Design and manage Act (project) and Cast (graph) architectures through interactive questioning. Outputs `CLAUDE.md` at project root containing Act overview and all Cast specifications.

## When to Use

- Planning initial Act architecture (after `act new`)
- Adding new Cast to existing Act
- Analyzing Cast complexity for Sub-Cast extraction
- Unclear about architecture design

## When NOT to Use

- Implementing code → use `developing-cast`
- Creating cast files → use `engineering-act`
- Writing tests → use `testing-cast`

---

## Core Principles

**INTERACTIVE**: Ask ONE question at a time. Wait for response before proceeding.

**NO CODE**: Describe structures only. No TypedDict, functions, or implementation code.

**DIAGRAMS SHOW EDGES**: Mermaid diagram contains all nodes and edges. No separate tables.

---

## Mode Detection

**First, determine which mode:**

- **CLAUDE.md doesn't exist?** → **Mode 1: Initial Design**
- **CLAUDE.md exists + adding cast?** → **Mode 2: Add Cast**
- **CLAUDE.md exists + cast complex?** → **Mode 3: Extract Sub-Cast**

---

## Mode 1: Initial Design

**When:** First time designing (no CLAUDE.md)

**Steps:**
1. **{{ cookiecutter.act_name }} Act Questions** → [modes/initial-design-questions.md](resources/modes/initial-design-questions.md)
   - Act Purpose, Cast Identification, Cast Goal, Input/Output, Constraints
2. **{{ cookiecutter.cast_name }} Cast Design** → Follow "Cast Design Workflow" below
3. **Generate CLAUDE.md files** → See "Generating CLAUDE.md Files" section below
   - Create `/CLAUDE.md` (Act info + Casts table)
   - Create `/casts/{{ cookiecutter.cast_slug }}/CLAUDE.md` (Cast details)
   - Note: Initial cast directory already exists from `act new` command
4. **Validate** → Run validation script

---

## Mode 2: Add Cast

**When:** CLAUDE.md exists, adding new cast

**Steps:**
1. **Read CLAUDE.md** → Understand existing {{ cookiecutter.act_name }} Act and Casts
   - Read `/CLAUDE.md` for Act overview and existing casts
   - Read existing `/casts/*/CLAUDE.md` files as needed for context
2. **Questions** → [modes/add-cast-questions.md](resources/modes/add-cast-questions.md)
   - New Cast Purpose, Goal, Relationship, Input/Output, Constraints
3. **Cast Design** → Follow "Cast Design Workflow" below
4. **Create Cast Package** (if not exists) → Run command
   - Run: `uv run act cast -c "{New Cast Name}"`
   - This creates `/casts/{new_cast_slug}/` directory structure
5. **Update CLAUDE.md files** → See "Generating CLAUDE.md Files" section below
   - Update `/CLAUDE.md` Casts table (add new row)
   - Create `/casts/{new_cast_slug}/CLAUDE.md` (new Cast details)
6. **Validate** → Run validation script

---

## Mode 3: Extract Sub-Cast

**When:** Cast has >10 nodes or complexity mentioned

**Steps:**
1. **Analyze** → Use [cast-analysis-guide.md](resources/cast-analysis-guide.md)
   - Read `/casts/{parent_cast}/CLAUDE.md` to analyze complexity
2. **Questions** → [modes/extract-subcast-questions.md](resources/modes/extract-subcast-questions.md)
   - Complexity Check, Extraction Proposal, Sub-Cast Purpose, Input/Output
3. **Sub-Cast Design** → Follow "Cast Design Workflow" below
4. **Create Sub-Cast Package** → Run command
   - Run: `uv run act cast -c "{Sub-Cast Name}"`
   - This creates `/casts/{subcast_slug}/` directory structure
5. **Update CLAUDE.md files** → See "Generating CLAUDE.md Files" section below
   - Update `/CLAUDE.md` Casts table (add sub-cast row)
   - Create `/casts/{subcast_slug}/CLAUDE.md` (sub-cast details)
   - Update `/casts/{parent_cast}/CLAUDE.md` (reference sub-cast)
6. **Validate** → Run validation script

---

## Cast Design Workflow

**Use for all modes when designing a cast:**

### 1. Pattern Selection

#### 1a. Determine if AI Agent is Needed

**First, assess if the workflow requires AI agent capabilities:**

| Indicator | → Consider Agentic Pattern |
|-----------|---------------------------|
| Autonomous decision-making | Yes |
| Tool/API access required | Yes |
| Iterative reasoning needed | Yes |
| Self-correction capability | Yes |
| Human oversight checkpoints | Yes |
| Multiple specialized AI roles | Yes |

**If ANY indicator applies** → Use [agentic-design-patterns.md](resources/agentic-design-patterns.md) to select Agentic Pattern.

**If ALL are NO** (simple data transformation, deterministic rules) → Proceed to Step 1b.

Ask: "Does your workflow need AI agent capabilities?" Wait for confirmation.

#### 1b. Basic Pattern Selection (for non-agentic workflows)

**YOU suggest pattern** using [pattern-decision-matrix.md](resources/pattern-decision-matrix.md):

| Requirements | Pattern |
|-------------|---------|
| Linear transformation | Sequential |
| Multiple handlers | Branching |
| Refinement loop | Cyclic |

Ask: "Does this pattern fit?" Wait for confirmation.

### 2. State Schema

**YOU design schema** using [state-schema.md](resources/design/state-schema.md).

Present as **TABLES ONLY** (InputState, OutputState, OverallState).

Ask: "Any fields to modify?" Wait for response.

### 3. Node Specification

**Ask pattern-specific question** using [node-specification.md](resources/design/node-specification.md):

**YOU design nodes** (single responsibility, CamelCase naming).

### 4. Architecture Diagram

**YOU create Mermaid diagram** using [edge-routing.md](resources/design/edge-routing.md).

Ensure: All nodes connected, all paths reach END, conditionals labeled.

### 5. Technology Stack

> `langgraph`, `langchain` included. Identify **additional** dependencies only.

**Based on Architecture Diagram, ask ONLY if relevant:**
- If diagram shows LLM nodes → "Which LLM provider?" → Wait
- If diagram shows retrieval/search → "Vector store or search tool needed?" → Wait
- If diagram shows document processing → "Document types to handle?" → Wait

**Skip questions** for dependencies not implied by the architecture.

**YOU determine** packages + environment variables.

### 6. Validate

```bash
python .claude/skills/architecting-act/scripts/validate_architecture.py
```

The validation script checks ALL requirements automatically:
- Root CLAUDE.md exists with Act Overview, Purpose, Domain, Casts table
- All casts in table have corresponding CLAUDE.md files
- Each Cast CLAUDE.md has all required sections
- Mermaid diagrams have START/END nodes, no orphan nodes
- Node specifications match diagram nodes
- State schemas are complete (OverallState includes Input/Output fields)
- Cross-references between files work
- No placeholder text

Fix any errors shown in output, then proceed.

---

## Generating CLAUDE.md Files

Generate files using the EXACT template structure. Follow these steps precisely:

1. **Copy template skeleton** - Use template files as the base structure
2. **Use exact marker format** - See Marker Syntax section below
3. **Replace placeholders** - Substitute `{{PLACEHOLDER}}` with actual content
4. **Include all required sections** - Even if content is minimal
5. **Add MANUAL section** at the end for user notes

### Marker Syntax

**CRITICAL**: Use the EXACT marker format below. Do NOT use variations.

```markdown
<!-- AUTO-MANAGED: section-name -->
## Section Heading

Content goes here

<!-- END AUTO-MANAGED -->
```

For user-editable content:

```markdown
<!-- MANUAL -->
## Notes

Add project-specific notes here. This section is never auto-modified.

<!-- END MANUAL -->
```

**Common mistakes to avoid**:
- `<!-- BEGIN AUTO-MANAGED: name -->` - WRONG (no BEGIN prefix)
- `<!-- END AUTO-MANAGED: name -->` - WRONG (no name in closing tag)
- `<!-- AUTO-MANAGED section-name -->` - WRONG (missing colon)

### Section Definitions

#### Act-Level CLAUDE.md Sections

Generate these sections in order:

| Section Name | Heading | Required | Placeholder | Content |
|--------------|---------|----------|-------------|---------|
| `act-overview` | ## Act Overview | Yes | `{{PURPOSE}}`, `{{DOMAIN}}` | Purpose and domain |
| `casts-table` | ## Casts | Yes | `{{CASTS_TABLE}}` | Table of all casts with links |
| `project-structure` | ## Project Structure | Yes | `{{ACT_SLUG}}` | Directory tree |

#### Cast-Level CLAUDE.md Sections

Generate these sections in order:

| Section Name | Heading | Required | Placeholder | Content |
|--------------|---------|----------|-------------|---------|
| `cast-overview` | ## Overview | Yes | `{{PURPOSE}}`, `{{PATTERN}}`, `{{LATENCY}}` | Purpose, pattern, latency |
| `architecture-diagram` | ## Architecture Diagram | Yes | `{{MERMAID_DIAGRAM}}` | Mermaid graph definition |
| `state-schema` | ## State Schema | Yes | `{{*_STATE_FIELDS}}` | InputState, OutputState, OverallState tables |
| `node-specifications` | ## Node Specifications | Yes | `{{NODE_SPECIFICATIONS}}` | Node details with Responsibility, Reads, Writes |
| `technology-stack` | ## Technology Stack | Yes | `{{DEPENDENCIES}}`, `{{ENV_VARIABLES}}` | Dependencies and env vars |
| `cast-structure` | ## Cast Structure | No | `{{CAST_SLUG}}` | Directory tree |

### Templates

Reference the template files for exact structure:

#### Act Template
@templates/CLAUDE.act.md.template

#### Cast Template
@templates/CLAUDE.cast.md.template

---

## Design Resources

Reference guides for detailed design information:

| Resource | Purpose |
|----------|---------|
| [agentic-design-patterns.md](resources/agentic-design-patterns.md) | AI agent pattern selection |
| [pattern-decision-matrix.md](resources/pattern-decision-matrix.md) | Basic pattern selection |
| [cast-analysis-guide.md](resources/cast-analysis-guide.md) | Complexity analysis |
| [design/state-schema.md](resources/design/state-schema.md) | State schema design |
| [design/node-specification.md](resources/design/node-specification.md) | Node specification |
| [design/edge-routing.md](resources/design/edge-routing.md) | Mermaid diagram creation |

---

## Output

After generating files, verify:
- Files created/modified at correct locations
- All AUTO-MANAGED sections populated
- Validation script passes

**Next:** `engineering-act` (scaffold casts) → `developing-cast` (implement) → `testing-cast` (test)
