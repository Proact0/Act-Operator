---
name: architecting-act
description: Use when starting new Act project (CLAUDE.md doesn't exist), adding cast to existing Act (CLAUDE.md exists), or facing complex cast needing sub-cast extraction (>10 nodes) - guides through interactive questioning (one question at a time) from requirements to validated architecture with mermaid diagrams, emphasizing design before implementation, no code generation
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
3. **Generate CLAUDE.md files** → Use [act-template.md](resources/act-template.md) and [cast-template.md](resources/cast-template.md)
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
5. **Update CLAUDE.md files** → Use [act-template.md](resources/act-template.md) and [cast-template.md](resources/cast-template.md)
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
5. **Update CLAUDE.md files** → Use [act-template.md](resources/act-template.md) and [cast-template.md](resources/cast-template.md)
   - Update `/CLAUDE.md` Casts table (add sub-cast row)
   - Create `/casts/{subcast_slug}/CLAUDE.md` (sub-cast details)
   - Update `/casts/{parent_cast}/CLAUDE.md` (reference sub-cast)
6. **Validate** → Run validation script

---

## Cast Design Workflow

**Use for all modes when designing a cast:**

### 1. Pattern Selection

**YOU suggest pattern** using [pattern-decision-matrix.md](resources/pattern-decision-matrix.md):

| Requirements | Pattern |
|-------------|---------|
| Linear transformation | Sequential |
| Multiple handlers | Branching |
| Refinement loop | Cyclic |
| Specialized roles | Multi-agent |

Ask: "Does this pattern fit?" Wait for confirmation.

### 2. State Schema

**YOU design schema** using [state-schema.md](resources/design/state-schema.md).

Present as **TABLES ONLY** (InputState, OutputState, OverallState).

Ask: "Any fields to modify?" Wait for response.

### 3. Node Specification

**Ask pattern-specific question** using [node-specification.md](resources/design/node-specification.md):
- Sequential/Branching: "Main processing steps?" (3-7 nodes)
- Cyclic: "What gets refined? Exit condition?"
- Multi-agent: "What specialized roles?"

**YOU design nodes** (single responsibility, CamelCase naming).

### 4. Architecture Diagram

**YOU create Mermaid diagram** using [edge-routing.md](resources/design/edge-routing.md).

Ensure: All nodes connected, all paths reach END, conditionals labeled.

### 5. Technology Stack

> `langgraph`, `langchain` included. Identify **additional** dependencies only.

**Ask ONE at a time:**
1. LLM provider? → Wait
2. Vector store? → Wait
3. Search tool? → Wait
4. Document types? → Wait

**YOU determine** packages + environment variables.

### 6. Validate

```bash
python .claude/skills/architecting-act/scripts/validate_architecture.py
```

See [validation-checklist.md](resources/validation-checklist.md).

Fix issues if found, then present summary.
