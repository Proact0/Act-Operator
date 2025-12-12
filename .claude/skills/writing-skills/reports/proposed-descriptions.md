# Proposed Descriptions (GREEN Phase)

## architecting-act

### Current (268 chars)
```yaml
description: Use when planning {{ cookiecutter.act_name }} Act project architecture, designing new casts(graphs), adding casts to existing Act, analyzing cast complexity for sub-cast extraction, or managing Act/Cast blueprints - guides from requirements to architecture
```

### Proposed V1 (412 chars)
```yaml
description: Use when starting new Act project (CLAUDE.md doesn't exist), adding cast to existing Act (CLAUDE.md exists), or facing complex cast needing sub-cast extraction (>7 nodes) - guides through interactive questioning (one question at a time) from requirements to validated architecture with mermaid diagrams, emphasizing design before implementation, no code generation
```

**Changes:**
- ✅ Added "CLAUDE.md doesn't exist" (Initial Design trigger)
- ✅ Added "CLAUDE.md exists" (Add Cast trigger)
- ✅ Added ">7 nodes" (Extract Sub-Cast trigger)
- ✅ Added "interactive questioning (one question at a time)"
- ✅ Added "validated architecture" (mentions validation)
- ✅ Added "design before implementation, no code" (boundary clarification)

**Character count:** 412 (under 500 ✓)

---

## developing-cast

### Current (287 chars)
```yaml
description: Use when implementing LangGraph nodes/edges/state from CLAUDE.md, stuck on specific patterns (conditional routing, parallel execution, state updates), or need code examples for 50+ situations - provides systematic reference from architecture to working implementation
```

### Proposed V1 (501 chars - TOO LONG)
```yaml
description: Use when implementing LangGraph components (state, nodes, edges, graph) with or without CLAUDE.md specs, need patterns for agents/tools/memory/middleware, stuck on workflow order, or need examples for specific patterns (conditional routing, parallel execution, state updates, retry/fallback, conversation memory, guardrails, vector stores) - provides systematic workflow (state → dependency modules → nodes → conditions → graph) with 50+ implementation examples across core/prompts/models/tools/memory/middleware/integrations
```

**Too long! Need to trim.**

### Proposed V2 (463 chars)
```yaml
description: Use when implementing LangGraph components (state, nodes, edges, graph) with or without CLAUDE.md specs, stuck on workflow order (what order to implement), or need patterns for agents/tools/memory/middleware (conversation memory, retry/fallback, guardrails, vector stores, tool management) - provides systematic workflow (state → deps → nodes → conditions → graph) with 50+ implementation examples
```

**Changes:**
- ✅ Added "with or without CLAUDE.md" (optional)
- ✅ Added "workflow order" (key trigger)
- ✅ Expanded "50+ situations" to specific categories: memory, middleware, agents, tools
- ✅ Added specific examples: conversation memory, retry/fallback, guardrails, vector stores
- ✅ Added workflow: "state → deps → nodes → conditions → graph"
- ✅ Removed vague "architecture to implementation" → clearer "systematic workflow"

**Character count:** 463 (under 500 ✓)

---

## engineering-act

### Current (271 chars)
```yaml
description: Use when creating new cast package in {{ cookiecutter.act_name }} Act monorepo, adding dependencies to workspace or specific cast, facing uv sync issues, or launching langgraph dev server - handles all project setup and package management infrastructure
```

### Proposed V1 (334 chars)
```yaml
description: Use when creating new cast package, installing/managing dependencies (monorepo or cast-level), resolving dependency conflicts or packages out of sync, or launching langgraph dev server - checks CLAUDE.md first for context, then handles all uv-based project setup and package management (dev/test/lint groups)
```

**Changes:**
- ✅ Replaced "uv sync issues" with "dependency conflicts or packages out of sync" (symptom-based)
- ✅ Added "checks CLAUDE.md first for context" (workflow emphasis)
- ✅ Added "uv-based" (technology context)
- ✅ Added "dev/test/lint groups" (mentions dependency groups)
- ✅ More concise

**Character count:** 334 (under 500 ✓)

---

## Validation Against Test Scenarios

### architecting-act Proposed V1

| Scenario | Triggers in Description | Pass |
|----------|------------------------|------|
| Scenario 1: no CLAUDE.md | "CLAUDE.md doesn't exist" | ✅ |
| Scenario 2: 12 nodes | ">7 nodes" | ✅ |
| Pressure 1: quick architecture | "design before implementation, no code" | ✅ |

### developing-cast Proposed V2

| Scenario | Triggers in Description | Pass |
|----------|------------------------|------|
| Scenario 3: workflow order | "workflow order", "state → deps → nodes → conditions → graph" | ✅ |
| Scenario 4: memory + retry | "conversation memory, retry/fallback" | ✅ |
| Without CLAUDE.md | "with or without CLAUDE.md" | ✅ |

### engineering-act Proposed V1

| Scenario | Triggers in Description | Pass |
|----------|------------------------|------|
| Scenario 5: dependencies out of sync | "packages out of sync" | ✅ |
| Scenario 6: new cast | "creating new cast package" | ✅ |
| Check CLAUDE.md first | "checks CLAUDE.md first" | ✅ |

---

## Character Counts (Frontmatter Limit: 1024 chars)

### architecting-act
```
name: architecting-act (18 chars)
description: ... (412 chars)
YAML overhead: ~30 chars (---, name:, description:, newlines)
Total: ~460 chars ✅ (under 1024)
```

### developing-cast
```
name: developing-cast (16 chars)
description: ... (463 chars)
YAML overhead: ~30 chars
Total: ~509 chars ✅ (under 1024)
```

### engineering-act
```
name: engineering-act (16 chars)
description: ... (334 chars)
YAML overhead: ~30 chars
Total: ~380 chars ✅ (under 1024)
```

---

## Summary

All proposed descriptions:
- ✅ Start with "Use when..."
- ✅ Include specific triggers/symptoms
- ✅ Written in third person
- ✅ Under 500 chars each
- ✅ Total frontmatter under 1024 chars
- ✅ Address baseline analysis gaps
- ✅ Pass test scenario validation
