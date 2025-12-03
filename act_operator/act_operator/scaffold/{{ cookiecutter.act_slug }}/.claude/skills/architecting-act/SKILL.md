---
name: architecting-act
description: Use when planning LangGraph cast, unclear about node/edge/state structure, starting new architecture, or need CLAUDE.md specification - guides interactive architecture design through 20-questions approach with automated validation
---

# Architecting Act

Design high-level LangGraph architectures through interactive questioning. Outputs `CLAUDE.md` at project root.

## When to Use

- Planning a new cast (graph)
- Unclear about node, edge, or state structure
- Need to create architecture specification
- Starting from scratch with no clear design

## When NOT to Use

- Implementing code → use `developing-cast`
- Project setup → use `engineering-act`
- Writing tests → use `testing-cast`

---

## Core Principle

**IMPORTANT**: This skill is interactive. Use a "20 questions" approach - ask ONE question at a time, narrowing focus based on responses. Never skip steps or make assumptions.

## Workflow

### Step 1: Requirements Gathering

**Ask sequentially** using [question-templates.md](resources/question-templates.md):
- Q1: Goal (one sentence)
- Q2: Input/Output
- Q3: Constraints

After Q3, summarize and confirm. **Wait for user confirmation.**

---

### Step 2: Pattern Selection

**YOU suggest a pattern** based on requirements. Use [pattern-decision-matrix.md](resources/pattern-decision-matrix.md):

| Requirements | Pattern |
|-------------|---------|
| Linear transformation | Sequential |
| Multiple handlers | Branching |
| Refinement loop | Cyclic |
| Specialized roles | Multi-agent |

Present recommendation with diagram. **Ask: "Does this pattern fit your needs?"**

Pattern details: [sequential](resources/patterns/sequential.md), [branching](resources/patterns/branching.md), [cyclic](resources/patterns/cyclic.md), [multi-agent](resources/patterns/multi-agent.md)

---

### Step 3: State Schema Design

**YOU design schema** using Step 1 requirements. See [state-schema.md](resources/design/state-schema.md).

Structure: InputState + OutputState + OverallState (combines both + internal fields)

Present schema. **Ask: "Any fields to add or modify?"**

---

### Step 4: Node Specification

**Ask pattern-specific question** (see [node-specification.md](resources/design/node-specification.md)):
- Sequential/Branching: "Main processing steps?" (3-7 steps)
- Cyclic: "What gets refined? What determines 'done'?"
- Multi-agent: "What specialized roles?" (e.g., Researcher, Writer)

**YOU design nodes** with single responsibilities. Present to user.

---

### Step 5: Edge Routing

**YOU design edges** matching pattern. See [edge-routing.md](resources/design/edge-routing.md).

**Critical:** Ensure all paths reach END. Present flow diagram.

---

### Step 6: Technology Stack

> `langgraph`, `langchain` already included. Only identify **additional** dependencies.

**Ask conditionally:**
- If LLM: "Which provider?" (OpenAI/Anthropic/Google)
- If vector store: "Which one?" (Chroma/Pinecone)
- If search: "Which tool?" (Tavily/SerpAPI)
- If docs: "What types?" (PDF/Word/etc.)

**YOU determine dependencies** based on architecture. List packages + environment variables.

---

### Step 7: Generate CLAUDE.md

Create CLAUDE.md at project root using [output-template.md](resources/output-template.md).

Include all gathered information from Steps 1-6.

---

### Step 8: Review & Validate

**Run validation:**
```bash
python .claude/skills/architecting-act/scripts/validate_architecture.py CLAUDE.md
```

See [validation-checklist.md](resources/validation-checklist.md) for manual review.

**If issues found:** Return to relevant step and fix.

**If passed:** Present summary and hand off to `engineering-act`.
