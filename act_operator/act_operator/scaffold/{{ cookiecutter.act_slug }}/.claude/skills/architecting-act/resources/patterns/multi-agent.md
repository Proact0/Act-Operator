# Multi-Agent Pattern

Specialized agents with distinct roles and handoffs.

## Structure

```
START → Supervisor → {
    "research" → Researcher → Supervisor
    "write" → Writer → Supervisor
    "review" → Reviewer → Supervisor
    "done" → END
}
```

## When to Use

- Complex tasks requiring expertise
- Distinct specialized roles
- Collaborative problem-solving

## Design Checklist

- [ ] Each agent has clear specialty
- [ ] Handoff criteria defined
- [ ] Shared state identified
- [ ] Termination condition exists

## Coordination Patterns

**Supervisor (recommended):** Central coordinator routes to specialists.

**Peer-to-peer:** Agents communicate directly (for debates, negotiations).

**Hierarchical:** Nested supervisors for large-scale systems.

## Subgraph Decision

**Use subgraphs when:**
- Agent needs private message history
- Agent logic is complex (>5 nodes)
- Agent will be reused elsewhere

**Keep in main graph when:**
- Agents are simple (1-3 nodes)
- All state is shared

## Common Mistakes

**Too many agents:** Start with 2-3, add more only if needed.

**Unclear handoffs:** Define exactly when control transfers.

**Supervisor doing work:** Supervisor should ONLY route.

**Missing termination:** Must have clear "done" condition.

## Example: Research & Write

```
START → Supervisor → {
    phase == "research" → Researcher → Supervisor
    phase == "write" → Writer → Supervisor
    phase == "review" → Reviewer → Supervisor
    phase == "done" → END
}
```
