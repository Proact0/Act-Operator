# Validation Checklist

Review & Validate distributed CLAUDE.md structure (root + cast files).

## Automated Validation

**Run validation script:**
```bash
python .claude/skills/architecting-act/scripts/validate_architecture.py
```

**Script checks:**
- Root CLAUDE.md exists and has Act Overview, Casts table, Next Steps
- All casts in table have corresponding `/casts/{cast_slug}/CLAUDE.md` files
- Each Cast CLAUDE.md has all required sections
- Mermaid diagrams have START/END nodes
- Node specifications defined per Cast
- Cross-references between root and cast files are valid

---

## Manual Review Checklist

### Root CLAUDE.md (`/CLAUDE.md`)
| Check | Issue Found? | Fix |
|-------|--------------|-----|
| Act Overview complete? | Missing purpose/domain | Add Act context |
| Casts table lists all casts? | Missing entries | Update table |
| Cast table has Location links? | Missing links | Add links to cast CLAUDE.md |
| Next Steps present? | Missing | Add next steps |

### Per Cast (`/casts/{cast_slug}/CLAUDE.md`)
| Check | Issue Found? | Go Back To |
|-------|--------------|------------|
| Parent Act link present? | Missing link | Add link to root CLAUDE.md |
| Cast Overview complete? | Missing goal/pattern | Requirements |
| State schema complete? | Missing fields | State Schema step |
| All nodes defined? | Missing nodes | Node Specification step |
| Diagram shows all flows? | Orphan nodes, missing END | Diagram step |
| Dependencies listed? | Missing packages | Tech Stack step |
| No placeholders? | Incomplete content | Relevant step |

---

## Common Issues

### Missing END Node
**Problem:** Diagram has no termination path

**Fix:** Update diagram, ensure all paths reach END

---

### Orphan Nodes
**Problem:** Node not connected in diagram

**Fix:** Update diagram, connect node to flow

---

### Incomplete State Schema
**Problem:** Missing fields needed by nodes

**Fix:** Add missing fields to OverallState

---

### Placeholder Text
**Problem:** `[TODO]`, `{placeholder}` in document

**Fix:** Complete section with actual content

---

### Cast CLAUDE.md Not Created
**Problem:** Cast listed in root table but file doesn't exist

**Fix:** Create `/casts/{cast_slug}/CLAUDE.md` with cast specifications

---

### Broken Links
**Problem:** Root table links to wrong cast path

**Fix:** Update table link to match actual cast directory

---

## Success Criteria

**Validation passes when:**
- ✅ Script reports no errors
- ✅ Root `/CLAUDE.md` has Act Overview and Casts table
- ✅ All casts in table have corresponding `/casts/{cast_slug}/CLAUDE.md` files
- ✅ All Cast CLAUDE.md files have complete sections
- ✅ Diagrams show START → nodes → END
- ✅ State schemas match node requirements
- ✅ Dependencies identified per Cast
- ✅ Cross-references (Parent Act links, Cast table links) work

---

## File Structure

After successful validation, you should have:

```
PROJECT_ROOT/
  CLAUDE.md                           # Act-level info
  casts/
    cast_name_1/
      CLAUDE.md                       # Cast1 details
    cast_name_2/
      CLAUDE.md                       # Cast2 details
```

---

## Hand-off

After validation passes:

- [ ] Root `/CLAUDE.md` at project root
- [ ] All `/casts/*/CLAUDE.md` files created
- [ ] Validation script passed
- [ ] Cross-references work
- [ ] Ready for implementation

**Next:** `engineering-act` (scaffold casts) → `developing-cast` (implement) → `testing-cast` (test)
