---
name: architecting-act
description: Use when user requests graph/cast architecture design, before any implementation - enforces requirements gathering, SOLID node design, and creates formal design document (claude.md) preventing premature implementation
---

# Architecting Act

## Overview

**Design before code.** Gather requirements through strategic questions, design minimal SOLID nodes, document decisions in `claude.md` before implementation.

**Anti-pattern:** Jumping to code under time pressure with assumed requirements and bloated nodes.

## When to Use

Use when user says:
- "I need a graph/cast for..."
- "Help me design architecture for..."
- "What nodes do I need for..."

**NOT for:** Implementation tasks (use `developing-cast`), basic setup (use `engineering-act`)

## Core Workflow

### 1. Requirements Phase (ALWAYS FIRST)

**STOP: Never skip to design under time pressure. 2-3 critical questions save days of rework.**

Ask in stages:

**Stage 1 - Input/Output**
```
What inputs should this graph receive and what outputs should it produce?
(Defines InputState and OutputState schemas)
```

**Stage 2 - Latency Requirements**
```
What's your latency requirement?
A. Low (< 10 sec)
B. Medium (< 60 sec)
C. High (> 60 sec)
D. Custom: ___

(Affects node granularity, parallelism, streaming)
```

**Stage 3 - Context Questions** (Pick 2-3 most relevant)
- Platform/technology constraints?
- Integration points (existing systems, APIs, databases)?
- Human-in-the-loop requirements?
- Key challenges or goals?
- Expected volume/scale?
- Error handling needs?

**Stage 4 - Validate Assumptions**

Before designing, confirm:
- Automation level (fully automated vs human review)
- Team/category structure (if routing involved)
- Persistence needs (session-only vs long-term memory)

**Minimum viable questions:** Always ask Stage 1 + Stage 2 + at least 2 from Stage 3 + Stage 4 validation. Don't design with less.

### Handling User Pushback

If user says "Just design something" or "I don't have time for questions":

**Response script:**
```
I understand the urgency. However, designing without these answers will likely cost more time:

- Wrong assumptions = days of rework
- Missing integrations = rebuild entire graph
- Wrong latency design = performance issues in production

These 4-5 questions take 3 minutes but could save us 2-3 days of rework.
Which would you prefer?
```

**If user still refuses:** Document assumptions explicitly in claude.md and get their sign-off before implementation.

### Partial Information Handling

If user only answers some questions:
1. Design with available information
2. Mark gaps in claude.md with **[ASSUMPTION]** tags
3. Proceed ONLY if assumptions are non-critical
4. Flag critical unknowns as blockers requiring answers

### 2. Architecture Phase

**Node Design Principle: Minimum functional units following SOLID**

Each node should have ONE responsibility:
- ❌ `MultiSourceSearch` (searches 3 sources) → ❌ Violates SRP
- ✅ `AcademicSearch`, `WebSearch`, `InternalSearch` → ✅ Single responsibility each

**Benefits of granular nodes:**
- Independent testing and monitoring
- Easy to add/remove/swap implementations
- Clear error isolation
- Better observability

**Design checklist:**
- [ ] Each node has single, clear responsibility
- [ ] State schema defined (InputState, OutputState, internal State)
- [ ] Edge logic identified (conditional routing if needed)
- [ ] Subgraph necessity determined
- [ ] Error handling nodes included

### 3. Documentation Phase (MANDATORY)

**Create `claude.md` in project root with formalized architecture**

Run generation script:
```bash
python .claude/skills/architecting-act/scripts/generate-claude-md.py
```

Template sections:
- **Overview**: One paragraph describing graph purpose
- **Requirements**: Key inputs/outputs/constraints from Stage 1-4
- **State Schema**: InputState, OutputState, internal State fields
- **Nodes**: Each node with single responsibility description
- **Edges**: Flow including conditional logic
- **Design Decisions**: Why key choices were made

**This artifact is required before moving to implementation.**

### Architecture vs Implementation Boundary

**Architecture (this skill):**
- State schema design (field names, types, purpose)
- Node responsibilities (what each node does)
- Edge logic (flow and routing rules)
- Design decisions (why choices were made)

**Implementation (developing-cast skill):**
- Actual node code (execute methods)
- LangChain/LangGraph API calls
- Tool implementations
- Error handling code
- Tests

**Grey area - Acceptable in architecture:**
- Pseudocode showing node logic flow
- State update examples (`return {"field": value}`)
- High-level tool mentions ("uses @tool decorator")

**Not acceptable - Belongs in implementation:**
- Complete working code
- Import statements
- Actual LangChain classes instantiation
- Test code

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "User is in a hurry, skip questions" | 2-3 questions take 2 min, wrong design wastes days |
| "I can assume basic requirements" | Assumptions lead to rework, always validate |
| "Fewer nodes = simpler" | Wrong. Clear single-purpose nodes = simpler maintenance |
| "Combine related operations (3 searches in 1 node)" | Violates SRP, harder to test/monitor/scale independently |
| "Design doc is overhead" | Doc takes 5 min, prevents implementation drift and miscommunication |
| "I'll document after implementation" | Never happens, tribal knowledge lost |
| "User said 'just design something'" | Use pushback script, don't enable bad decisions |
| "I'll just show quick pseudocode" | Still implementation, belongs in developing-cast |
| "This is just architecture draft" | Draft without requirements = wrong foundation |
| "Stage 3 says 2-3 questions, I'll skip others" | Minimum viable = Stage 1+2+2 from Stage 3+Stage 4 |

## Red Flags - STOP and Ask Questions

- Jumping to code/implementation
- "Let me quickly design this..."
- Making assumptions about teams/categories/integrations
- Creating `MultiX` nodes (MultiSourceSearch, MultiProcessing, etc.)
- Combining analysis + synthesis in one node
- No design document created
- "The requirements are obvious"

**All of these mean: Stop, gather requirements, apply SOLID, document.**

## Act Project Specifics

**Tools location:** ONLY in `modules/tools/`, never in agents or other modules

**Memory patterns:** Location depends on use case:
- Session state: Graph state schema
- Agent scratchpad: `modules/agents/`
- Cross-session: Long-term memory integration

**Subgraphs:** New cast required via `uv run act cast -c [name]`

**Node base class:** Extend `casts/base_node.py`

## Quick Reference

| Task | Action |
|------|--------|
| Start architecture | Ask Stage 1-4 questions |
| Design nodes | One responsibility each, SOLID principles |
| Routing logic | Implement in `modules/conditions.py` |
| Document design | Run `generate-claude-md.py` script |
| Ready to implement | Hand off to `developing-cast` skill |

## Workflow Example

```
User: "I need a graph for processing customer support tickets."

You:
1. What inputs/outputs? → ticket details in, response + team out
2. Latency needs? → Medium (< 60 sec)
3. Human review before sending? → Yes, draft only
4. What teams exist? → Technical, Billing, Sales

Design:
- AnalyzeTicket (categorize)
- RouteTechnical/Billing/Sales (separate nodes, SRP)
- DraftResponse (generate draft)
- FormatForReview (prepare for human)

Document: Generate claude.md with this architecture

✓ Ready for implementation with developing-cast
```

## Real-World Impact

Following this workflow:
- Eliminates rework from wrong assumptions (saves days)
- Creates maintainable graphs (single-purpose nodes)
- Provides documentation for team collaboration
- Enables confident implementation (design validates requirements)

**Time investment:** 10-15 minutes architecture → Saves hours/days implementation + maintenance
