# Pattern Decision Matrix

Guide for Step 1b: Basic Pattern Selection for non-agentic workflows.

> **Note:** If the workflow requires AI agent capabilities (tool access, autonomous decision-making, iterative reasoning, human oversight), use [agentic-design-patterns.md](agentic-design-patterns.md) instead.

## Decision Matrix

| If Requirements Suggest... | Recommend Pattern | Why |
|---------------------------|-------------------|-----|
| Linear transformation, no branching, fixed steps | **Sequential** | Simple, predictable flow |
| Multiple handlers based on input type/classification | **Branching** | Route to specialized processors |
| Refinement until quality threshold met | **Cyclic** | Iterate and improve |

## Detailed Pattern Characteristics

### Sequential
**Structure:** START → Step1 → Step2 → ... → END

```mermaid
graph LR
    START([START]) --> A[Step1]
    A --> B[Step2]
    B --> C[Step3]
    C --> D[Step4]
    D --> END([END])
```

**Use when:**
- Each step depends on previous output
- Order cannot change
- No decision points needed

**Example:** Document parsing → Cleaning → Entity extraction → Summary generation

**Design notes:**
- 3-7 nodes typical
- Each step has single responsibility
- Fail fast on bad input

---

### Branching
**Structure:** START → Router → [Handler1 | Handler2 | Handler3] → END

```mermaid
graph LR
    START([START]) --> A{Router}
    A -->|path_1| B[Handler1]
    A -->|path_2| C[Handler2]
    A -->|default| D[Handler3]
    B --> END([END])
    C --> END([END])
    D --> END([END])
```

**Use when:**
- Different input types need different processing
- Classification determines next step
- Multiple specialized paths exist

**Example:** Customer query → Classify → [Billing | Technical | Sales] → Response

**Design notes:**
- Always include default/fallback path
- Make conditions mutually exclusive
- <5 branches recommended

---

### Cyclic
**Structure:** START → Process → Evaluate → [Refine → Process | Complete → END]

```mermaid
graph LR
    START([START]) --> A[Process]
    A --> B[Evaluate]
    B -->|refine| C[Refine]
    C --> A
    B -->|complete| D[Complete]
    D --> END([END])
```

**Use when:**
- Output quality needs improvement
- Iterative refinement required
- Feedback loop necessary

**Example:** Generate draft → Review quality → [Refine draft | Finalize]

**Design notes:**
- Set max iterations (3-10)
- Track progress per iteration
- Use numeric thresholds for exit

---

## Hybrid Patterns

**Can combine patterns:**
- Branching + Sequential: Route, then process linearly
- Sequential + Branching: Linear flow with conditional exits

**Recommend starting simple** - add complexity only if needed.

---

## Presentation Template

After analyzing requirements, present recommendation:

```
"Based on your requirements, I recommend the **[Pattern]** pattern.

**Why:** [brief justification based on their requirements]

[Simple diagram showing the pattern]

Does this pattern fit your needs, or would you prefer a different approach?"
```

**Wait for confirmation before proceeding to Step 3.**
