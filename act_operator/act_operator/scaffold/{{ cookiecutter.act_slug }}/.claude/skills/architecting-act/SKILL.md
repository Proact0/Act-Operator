---
name: architecting-act
description: Designs Act and Cast architectures through dynamic questioning, outputting validated CLAUDE.md with mermaid diagrams. Covers resilience patterns (Saga/compensation, long-running threads with DeltaChannel, graceful drain checkpoints, node timeout boundaries) from langgraph v1.2+. Use when starting new Act project, adding cast, planning architecture, extracting sub-cast (10+ nodes), redesigning existing cast, or ask "design architecture", "plan cast", "redesign cast", "create CLAUDE.md".
version: "2026.05.26"
author: Proact0
allowed-tools:
  - Bash(uv run act cast *)
  - Bash(python *)
  - Read
  - Write
  - Edit
  - AskUserQuestion
---

# Architecting {{ cookiecutter.act_name }} Act

Design and manage Act (project) and Cast (graph) architectures through dynamic, context-aware questioning. Outputs `CLAUDE.md` at project root containing Act overview and all Cast specifications.

## When to Use

- Planning initial Act architecture (after `act new`)
- Adding new Cast to existing Act
- Analyzing Cast complexity for Sub-Cast extraction
- Redesigning existing Cast architecture (already implemented code exists)
- Unclear about architecture design

## When NOT to Use

- Implementing LangGraph cast code → use `developing-cast`
- Implementing DeepAgent agent code → use `developing-deepagent`
- Scaffolding cast directories → run `uv run act cast -c "<Cast Name>"` directly
- Writing tests → use `testing-cast`

---

## Core Principles

**DYNAMIC QUESTIONING**:
- First analyze context (user request, CLAUDE.md, existing files)
- Use AskUserQuestion tool for structured option selection
- Skip questions when answer is inferable from context
- Group related questions when appropriate (up to 4 at once)

**NO CODE**: Describe structures only. No TypedDict, functions, or implementation code.

**DIAGRAMS SHOW EDGES**: Mermaid diagram contains all nodes and edges. No separate tables.

---

## Mode Detection

**First, determine which mode:**

- **CLAUDE.md doesn't exist?** → **Mode 1: Initial Design**
- **CLAUDE.md exists + adding cast?** → **Mode 2: Add Cast**
- **CLAUDE.md exists + cast complex?** → **Mode 3: Extract Sub-Cast**
- **Implementation code exists + redesign requested?** → **Mode 4: Redesign Cast**

---

## Mode 1: Initial Design

**When:** First time designing (no CLAUDE.md)

**Steps:**
1. **{{ cookiecutter.act_name }} Act Questions** → [modes/initial-design-questions.md](./resources/modes/initial-design-questions.md)
   - Analyze context first, then ask only necessary questions using AskUserQuestion
   - Questions: Act Purpose, Cast Goal, Input/Output, Constraints (skip if inferable)
2. **{{ cookiecutter.cast_name }} Cast Design** → Follow "Cast Design Workflow" below
3. **Generate CLAUDE.md files** → See "Generating CLAUDE.md" section below
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
2. **Questions** → [modes/add-cast-questions.md](./resources/modes/add-cast-questions.md)
   - Analyze context first, then ask only necessary questions using AskUserQuestion
   - Questions: New Cast Purpose, Goal, Relationship, Input/Output, Constraints (skip if inferable)
3. **Cast Design** → Follow "Cast Design Workflow" below
4. **Create Cast Package** (if not exists) → Run command
   - Run: `uv run act cast -c "{New Cast Name}"`
   - This creates `/casts/{new_cast_slug}/` directory structure
5. **Update CLAUDE.md files** → See "Generating CLAUDE.md" section below
   - Update `/CLAUDE.md` Casts table (add new row)
   - Create `/casts/{new_cast_slug}/CLAUDE.md` (new Cast details)
6. **Validate** → Run validation script

---

## Mode 3: Extract Sub-Cast

**When:** Cast has >10 nodes or complexity mentioned

**Steps:**
1. **Analyze** → Use [cast-analysis-guide.md](./resources/cast-analysis-guide.md)
   - Read `/casts/{parent_cast}/CLAUDE.md` to analyze complexity
2. **Questions** → [modes/extract-subcast-questions.md](./resources/modes/extract-subcast-questions.md)
   - Present analysis first, then use AskUserQuestion for confirmations
   - Questions: Proceed Confirmation, Node Selection (multiSelect), Sub-Cast Purpose, I/O Verification
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

## Mode 4: Redesign Cast

**When:** Cast already has implementation code, user wants to redesign or update architecture

**Steps:**
1. **Analyze existing implementation** → Read cast source files
   - Read `/casts/{cast_slug}/graph.py` → Current graph structure, nodes, edges
   - Read `/casts/{cast_slug}/modules/*.py` → State, nodes, agents, tools, conditions
   - Read `/casts/{cast_slug}/CLAUDE.md` if exists → Current architecture spec
2. **Summarize current architecture** → Present findings to user
   - List discovered nodes (custom / ToolNode / `create_agent` subgraph / `create_deep_agent`)
   - List discovered edges and conditional routing
   - Identify pattern (Sequential, Branching, Cyclic, Coordinator, etc.)
   - Note any discrepancies between CLAUDE.md (if exists) and actual code
3. **Questions** → [modes/redesign-cast-questions.md](./resources/modes/redesign-cast-questions.md)
   - Present current architecture summary first
   - Ask what needs to change using AskUserQuestion
4. **Redesign** → Follow "Cast Design Workflow" below
   - Use current implementation as baseline, apply requested changes
5. **Update CLAUDE.md files** → See "Generating CLAUDE.md" section below
   - Update `/casts/{cast_slug}/CLAUDE.md` (redesigned architecture)
   - Update `/CLAUDE.md` Casts table if cast purpose/pattern changed
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

**If ANY indicator applies** → Use [agentic-design-patterns.md](./resources/agentic-design-patterns.md) to select Agentic Pattern.

**If ALL are NO** (simple data transformation, deterministic rules) → Proceed to Step 1b.

**AskUserQuestion Format**:
```json
{
  "question": "Does this workflow require AI agent capabilities?",
  "header": "Agent Need",
  "options": [
    {"label": "Yes - Tool/API Access", "description": "External API calls, database queries, etc."},
    {"label": "Yes - Autonomous Decision", "description": "Dynamic routing, self-correction"},
    {"label": "Yes - Human Review Needed", "description": "High-stakes decisions, approval process"},
    {"label": "No", "description": "Simple data transformation, fixed rule-based"}
  ],
  "multiSelect": true
}
```

#### 1b. Basic Pattern Selection (for non-agentic workflows)

**YOU suggest pattern** using [pattern-decision-matrix.md](./resources/pattern-decision-matrix.md):

| Requirements | Pattern |
|-------------|---------|
| Linear transformation | Sequential |
| Multiple handlers | Branching |
| Refinement loop | Cyclic |

**AskUserQuestion Format**:
```json
{
  "question": "Which workflow pattern is appropriate?",
  "header": "Pattern",
  "options": [
    {"label": "Sequential (Recommended)", "description": "Linear transformation, fixed steps"},
    {"label": "Branching", "description": "Branch processing by input type"},
    {"label": "Cyclic", "description": "Iterative refinement until quality threshold"}
  ],
  "multiSelect": false
}
```

### 2. Node Composition Strategy

**For each node, determine its type from the 5 node types.**

Refer to [agentic-design-patterns.md](./resources/agentic-design-patterns.md) § "Node Type Decision" and [node-specification.md](./resources/design/node-specification.md) § "Node Types".

**AskUserQuestion Format** (for nodes where the type is ambiguous):
```json
{
  "question": "How should this node be composed?",
  "header": "Node Composition: {NodeName}",
  "options": [
    {"label": "Custom Node (BaseNode)", "description": "Single deterministic function, no tools/reasoning needed"},
    {"label": "ToolNode", "description": "Stateless tool execution — parses AIMessage.tool_calls, no reasoning loop"},
    {"label": "create_agent Subgraph", "description": "Tool-calling agent with autonomous ReAct reasoning loop"},
    {"label": "create_deep_agent", "description": "Complex agent with subagent delegation, sandbox, long-term memory"}
  ],
  "multiSelect": false
}
```

**Skip this question** when the composition is obvious (e.g., simple data transform → custom node, model tool calls without reasoning → ToolNode, tool-heavy autonomous task → create_agent subgraph).

**Note:** START/END are always present — they are structural constants, not design choices.

### 3. Node Specification

**Ask pattern-specific question** using [node-specification.md](./resources/design/node-specification.md):

**YOU design nodes** (single responsibility, CamelCase naming). Use the appropriate output format per node type (custom / ToolNode / agent subgraph / deep agent).

### 4. Architecture Diagram

**YOU create Mermaid diagram** using [edge-routing.md](./resources/design/edge-routing.md).

Ensure: All nodes connected, all paths reach END, conditionals labeled. Use subgraph syntax for agent nodes (see edge-routing § "Agent Subgraph as Node").

### 5. Validate

```bash
python ./scripts/validate_architecture.py
```

Fix issues if found, then present summary.

{% raw %}---

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
| `development-commands` | ## Development Commands | Yes | — | Dev server, sync, create cast, add dependency |

#### Cast-Level CLAUDE.md Sections

Generate these sections in order:

| Section Name | Heading | Required | Placeholder | Content |
|--------------|---------|----------|-------------|---------|
| `cast-overview` | ## Overview | Yes | `{{PURPOSE}}`, `{{PATTERN}}`, `{{LATENCY}}` | Purpose, pattern, latency |
| `architecture-diagram` | ## Architecture Diagram | Yes | `{{MERMAID_DIAGRAM}}` | Mermaid graph definition |
| `node-specifications` | ## Node Specifications | Yes | `{{NODE_SPECIFICATIONS}}` | Node details with responsibility and type |
| `cast-structure` | ## Cast Structure | No | `{{CAST_SLUG}}` | Directory tree |
| `development-commands` | ## Development Commands | Yes | `{{CAST_SLUG}}` | Cast-specific dependency commands |{% endraw %}