# Cyclic Pattern

Loops that iterate until exit condition is met.

## Structure

```
START → Generate → Evaluate → {
    "pass" → END
    "fail" → Refine → Evaluate (loop)
}
```

## When to Use

- Iterative refinement needed
- Quality gates with retry
- Self-correcting workflows
- Agent conversation loops

## Design Checklist

- [ ] Exit condition clearly defined
- [ ] Maximum iterations set (3-10 recommended)
- [ ] Progress tracked per iteration
- [ ] Fallback if max iterations reached

## Loop Types

**Refinement:** Generate → Review → Improve → Review... (exit: quality threshold)

**Retry:** Try → Check → {success: END, fail: Try} (exit: success or max attempts)

**Conversation:** Agent → User → Agent... (exit: goal achieved)

## Common Mistakes

**No iteration limit:** ALWAYS set max iterations to prevent infinite loops.

**No progress tracking:** Must detect if stuck (no improvement).

**Weak exit conditions:** Use numeric thresholds when possible.

## Example: Content Refinement

```
START → GenerateDraft → EvaluateQuality → {
    score >= 0.8 → END
    score < 0.8 AND iteration < 5 → RefineDraft → EvaluateQuality
    iteration >= 5 → END (best attempt)
}
```
