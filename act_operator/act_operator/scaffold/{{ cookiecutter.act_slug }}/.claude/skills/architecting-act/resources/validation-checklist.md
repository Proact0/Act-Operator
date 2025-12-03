# Validation Checklist

Step 8: Review & Validate generated CLAUDE.md.

## Automated Validation

**Run validation script:**
```bash
python .claude/skills/architecting-act/scripts/validate_architecture.py CLAUDE.md
```

**Script checks:**
- All required sections present
- Mermaid diagram has START/END nodes
- Node specifications defined
- No placeholder text ([brackets])

---

## Manual Review Checklist

| Check | Issue Found? | Go Back To |
|-------|--------------|------------|
| Overview complete? | Missing goal/pattern | Step 1-2 |
| State schema complete? | Missing fields | Step 3 |
| All nodes defined? | Missing nodes | Step 4 |
| All edges connected? | Orphan nodes, missing END | Step 5 |
| Dependencies listed? | Missing packages | Step 6 |
| No placeholders? | Incomplete content | Relevant step |

---

## Common Issues

### Missing END Node
**Problem:** Graph has no termination path

**Fix:** Return to Step 5, ensure all paths reach END

---

### Orphan Nodes
**Problem:** Node not connected to graph

**Fix:** Return to Step 5, add edges connecting node

---

### Incomplete State Schema
**Problem:** Missing fields needed by nodes

**Fix:** Return to Step 3, add missing fields to OverallState

---

### Placeholder Text
**Problem:** `[TODO]`, `[FILL THIS IN]`, `[...]` in document

**Fix:** Return to relevant step, complete section properly

---

## Success Criteria

**Validation passes when:**
- ✅ Script reports no errors
- ✅ All sections complete
- ✅ All nodes connected START → ... → END
- ✅ State schema matches node requirements
- ✅ Dependencies identified
- ✅ No placeholder text

---

## Hand-off Checklist

After validation passes:

- [ ] CLAUDE.md generated at project root
- [ ] Validation script passed
- [ ] No issues requiring step revisit
- [ ] Pattern clearly identified
- [ ] All components specified
- [ ] Dependencies identified
- [ ] Environment variables documented

**Ready for next skill:** `engineering-act` (setup) → `developing-cast` (implementation) → `testing-cast` (tests)
