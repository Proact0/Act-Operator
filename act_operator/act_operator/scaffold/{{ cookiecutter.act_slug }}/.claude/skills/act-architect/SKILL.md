---
name: act-architect
description: Use when starting new Act project (CLAUDE.md doesn't exist), adding cast to existing Act (CLAUDE.md exists), or facing complex cast needing sub-cast extraction (>10 nodes) - guides through interactive questioning (one question at a time) from requirements to validated architecture with mermaid diagrams, emphasizing design before implementation, no code generation
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

Design and manage Act (project) and Cast (graph) architectures through **interactive questioning**. Outputs `CLAUDE.md` at project root containing Act overview and all Cast specifications.

---

## 🎮 Interactive Conversation Protocol

**CRITICAL: This skill operates as an interactive wizard. Follow these rules:**

### Fundamental Principles

1. **One Question at a Time** - Never ask multiple questions in a single message
2. **Wait for Response** - Always pause after asking, do not proceed until user responds
3. **Show Progress** - Display visual progress indicators at each phase
4. **Summarize Before Proceeding** - Confirm understanding before moving to next phase
5. **Provide Clear Options** - Use labeled choices (A, B, C, D) with descriptions
6. **Minimize Questions** - Infer/decide whenever possible, only ask if critical

### Progress Indicator Format

Use this format to show progress:

```
╭─────────────────────────────────────────────╮
│  🏗️ Act Architect - Mode 1: Initial Design  │
├─────────────────────────────────────────────┤
│  Phase: [1/5] Act Overview                  │
│  Progress: ████░░░░░░░░░░░░░░░░ 20%         │
╰─────────────────────────────────────────────╯
```

### Question Format

Always format questions like this:

```
📋 **Question 1 of 5: Act Purpose**

What does this project do? (one sentence describing the overall goal)

💡 **Examples:**
- "Customer support automation system"
- "Document processing pipeline"
- "Multi-agent research assistant"

Your answer: _
```

### Multiple Choice Format

For choices, use this format:

```
📋 **Question 5 of 5: Constraints**

Any constraints?

   A) ⚡ Low latency (<10s)
   B) 🕐 Normal (<60s)
   C) 🐢 Long-running (>60s)
   D) 📝 Other (please specify)

Select [A/B/C/D]: _
```

### Confirmation Format

Before proceeding to next phase, always confirm:

```
╭─────────────────────────────────────────────╮
│  ✅ Phase 1 Complete - Please Confirm       │
╰─────────────────────────────────────────────╯

**Act: {{ cookiecutter.act_name }}**
- **Purpose:** [captured purpose]

**Cast: {{ cookiecutter.cast_snake }}**
- **Goal:** [cast goal]
- **Input:** [input]
- **Output:** [output]
- **Constraints:** [constraints]

Is this correct? [Y/n] or specify what to change: _
```

---

## Mode Detection

**First, determine which mode:**

- **CLAUDE.md doesn't exist?** → **Mode 1: Initial Design**
- **CLAUDE.md exists + adding cast?** → **Mode 2: Add Cast**
- **CLAUDE.md exists + cast complex?** → **Mode 3: Extract Sub-Cast**

**Show mode detection:**

```
🔍 Detecting mode...
   ✓ Checking for /CLAUDE.md... [exists/not found]
   ✓ Checking user intent... [new cast/extract/initial]

→ Mode Selected: [Mode X: Name]
```

---

## Mode 1: Initial Design

**When:** First time designing (no CLAUDE.md)

**Interactive Flow:**

```
Phase 1: Act Overview Questions    → [5 questions, sequential]
Phase 2: Pattern Selection         → [YOU suggest, user confirms]
Phase 3: State Schema Design       → [YOU design, user reviews]
Phase 4: Node Specification        → [Interactive refinement]
Phase 5: Architecture Diagram      → [Preview + confirmation]
Phase 6: Technology Stack          → [Only ask if relevant]
Phase 7: Generate & Validate       → [Auto-generate + validate]
```

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

**Interactive Flow:**

```
Phase 1: Context Analysis          → [Read existing, summarize]
Phase 2: New Cast Questions        → [5 questions, sequential]
Phase 3: Pattern Selection         → [YOU suggest, user confirms]
Phase 4: State Schema Design       → [YOU design, user reviews]
Phase 5: Node Specification        → [Interactive refinement]
Phase 6: Architecture Diagram      → [Preview + confirmation]
Phase 7: Create & Update           → [Auto-create + validate]
```

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

**Interactive Flow:**

```
Phase 1: Complexity Analysis       → [Analyze, present findings]
Phase 2: Extraction Proposal       → [YOU propose, user decides]
Phase 3: Sub-Cast Questions        → [If user agrees, ask details]
Phase 4: Sub-Cast Design           → [Follow Cast Design Workflow]
Phase 5: Create & Update           → [Auto-create + validate]
```

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

**Use for all modes when designing a cast.**

**This is an interactive workflow - follow the conversation protocol above.**

### Interactive Design Flow

```
╭─────────────────────────────────────────────╮
│  🎨 Cast Design Workflow                    │
├─────────────────────────────────────────────┤
│  Step 1: Pattern Selection      ░░░░░░░░░░  │
│  Step 2: State Schema           ░░░░░░░░░░  │
│  Step 3: Node Specification     ░░░░░░░░░░  │
│  Step 4: Architecture Diagram   ░░░░░░░░░░  │
│  Step 5: Technology Stack       ░░░░░░░░░░  │
│  Step 6: Validation             ░░░░░░░░░░  │
╰─────────────────────────────────────────────╯
```

### 1. Pattern Selection

#### 1a. Determine if AI Agent is Needed

**First, assess if the workflow requires AI agent capabilities:**

```
📋 **Agentic Capabilities Assessment**

I'll analyze if your workflow needs AI agent capabilities:

| Indicator                       | Your Workflow |
|---------------------------------|---------------|
| Autonomous decision-making      | [Yes/No]      |
| Tool/API access required        | [Yes/No]      |
| Iterative reasoning needed      | [Yes/No]      |
| Self-correction capability      | [Yes/No]      |
| Human oversight checkpoints     | [Yes/No]      |
| Multiple specialized AI roles   | [Yes/No]      |
```

**If ANY indicator applies** → Use [agentic-design-patterns.md](resources/agentic-design-patterns.md) to select Agentic Pattern.

**If ALL are NO** (simple data transformation, deterministic rules) → Proceed to Step 1b.

**Interactive Question:**

```
📋 **Pattern Selection - Agentic Check**

Based on your requirements, I've assessed the following:
[Show assessment table above]

Does your workflow need AI agent capabilities?

   A) ✅ Yes - needs autonomous decisions, tools, or iterative reasoning
   B) ❌ No - simple data transformation or deterministic rules
   C) 🤔 Not sure - help me decide

Select [A/B/C]: _
```

**Wait for response before proceeding.**

#### 1b. Basic Pattern Selection (for non-agentic workflows)

**YOU suggest pattern** using [pattern-decision-matrix.md](resources/pattern-decision-matrix.md):

```
📋 **Pattern Recommendation**

Based on your requirements, I recommend:

┌─────────────────────────────────────────────┐
│  🎯 Recommended: [Pattern Name]             │
├─────────────────────────────────────────────┤
│  Why: [Brief justification]                 │
│                                             │
│  Pattern fits because:                      │
│  • [Reason 1]                               │
│  • [Reason 2]                               │
│                                             │
│  Alternatives considered:                   │
│  • [Other Pattern] - [Why not]              │
└─────────────────────────────────────────────┘

Does this pattern fit your needs? [Y/n]: _
```

**Wait for confirmation.**

### 2. State Schema

**YOU design schema** using [state-schema.md](resources/design/state-schema.md).

Present as **TABLES ONLY** (InputState, OutputState, OverallState).

```
╭─────────────────────────────────────────────╮
│  📊 State Schema Design                     │
╰─────────────────────────────────────────────╯

Based on your inputs, I've designed the following schema:

**InputState:**
| Field | Type | Description |
|-------|------|-------------|
| ... | ... | ... |

**OutputState:**
| Field | Type | Description |
|-------|------|-------------|
| ... | ... | ... |

**OverallState:**
| Field | Type | Reducer | Description |
|-------|------|---------|-------------|
| ... | ... | ... | ... |

Any fields to add, modify, or remove? [Y/n or specify changes]: _
```

**Wait for response.**

### 3. Node Specification

**YOU design nodes** (single responsibility, CamelCase naming).

```
╭─────────────────────────────────────────────╮
│  🔧 Node Specification                      │
╰─────────────────────────────────────────────╯

Based on your pattern and state, I've designed these nodes:

┌──────────────────┬────────────────────────────┐
│ Node Name        │ Responsibility             │
├──────────────────┼────────────────────────────┤
│ [NodeA]          │ [What it does]             │
│ [NodeB]          │ [What it does]             │
│ [NodeC]          │ [What it does]             │
└──────────────────┴────────────────────────────┘

**Detailed Specifications:**

**[NodeA]**
- Reads: [fields from state]
- Writes: [fields to state]
- Logic: [brief description]

[Repeat for each node...]

Any nodes to add, modify, or remove? [Y/n or specify changes]: _
```

**Wait for response.**

### 4. Architecture Diagram

**YOU create Mermaid diagram** using [edge-routing.md](resources/design/edge-routing.md).

```
╭─────────────────────────────────────────────╮
│  📐 Architecture Diagram Preview            │
╰─────────────────────────────────────────────╯

Here's the Mermaid diagram for your cast:

\`\`\`mermaid
graph TD
    START([START]) --> NodeA[Node A]
    NodeA --> NodeB[Node B]
    ...
    NodeN --> END([END])
\`\`\`

**Verification Checklist:**
✅ All nodes connected
✅ All paths reach END
✅ Conditionals labeled
✅ No orphan nodes

Does this architecture look correct? [Y/n or specify changes]: _
```

Ensure: All nodes connected, all paths reach END, conditionals labeled.

**Wait for confirmation.**

### 5. Technology Stack

> `langgraph`, `langchain` included. Identify **additional** dependencies only.

**Based on Architecture Diagram, ask ONLY if relevant:**

```
╭─────────────────────────────────────────────╮
│  🛠️ Technology Stack                        │
╰─────────────────────────────────────────────╯

Base packages included:
• langgraph
• langchain

[Only show if LLM nodes detected:]
📋 Your diagram includes LLM-powered nodes.

Which LLM provider would you like to use?

   A) 🟢 OpenAI (GPT-4, GPT-3.5)
   B) 🔵 Anthropic (Claude)
   C) 🟡 Google (Gemini)
   D) 📝 Other (specify)

Select [A/B/C/D]: _
```

**Skip questions** for dependencies not implied by the architecture.

**YOU determine** packages + environment variables based on responses.

### 6. Validate

```
╭─────────────────────────────────────────────╮
│  ✅ Final Validation                        │
╰─────────────────────────────────────────────╯

Running validation script...
```

```bash
python .claude/skills/act-architect/scripts/validate_architecture.py
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

```
Validation Results:
✅ Root CLAUDE.md exists
✅ All casts have CLAUDE.md files
✅ Mermaid diagrams valid
✅ Node specifications complete
✅ State schemas complete

All checks passed! Ready to proceed.
```

Fix any errors shown in output, then proceed.

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

#### Cast-Level CLAUDE.md Sections

Generate these sections in order:

| Section Name | Heading | Required | Placeholder | Content |
|--------------|---------|----------|-------------|---------|
| `cast-overview` | ## Overview | Yes | `{{PURPOSE}}`, `{{PATTERN}}`, `{{LATENCY}}` | Purpose, pattern, latency |
| `architecture-diagram` | ## Architecture Diagram | Yes | `{{MERMAID_DIAGRAM}}` | Mermaid graph definition |
| `state-schema` | ## State Schema | Yes | `{{STATE_FIELDS}}` | InputState, OutputState, OverallState tables |
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

## Output

After generating files, verify:
- Files created/modified at correct locations
- All AUTO-MANAGED sections populated
- Validation script passes{% endraw %}