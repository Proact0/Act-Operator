# Architecture Decisions

This document records the key architectural and design decisions made for the `architecting-act` skill.

## Decision 1: Interactive Questioning Approach

**Decision:** Ask ONE question at a time, wait for response before proceeding.

**Justification:**
- Users need time to think about complex architectural decisions
- Prevents overwhelming users with multiple questions
- Allows for course correction mid-design
- Better requirement gathering through focused questions

**Alternatives Considered:**
- All-at-once questionnaire: Rejected - too overwhelming for architecture design
- Freeform input: Rejected - leads to incomplete specifications

**Trade-offs:**
- (+) Higher quality requirements gathering
- (+) Better user experience
- (-) Longer interaction time
- (-) More back-and-forth

---

## Decision 2: No Code Generation

**Decision:** This skill focuses ONLY on architecture design, not implementation.

**Justification:**
- Separation of concerns: design vs implementation
- Architecture documents should be technology-agnostic where possible
- Allows other skills (developing-cast, engineering-act) to handle implementation
- Prevents premature implementation decisions

**Alternatives Considered:**
- Include basic code scaffolding: Rejected - blurs skill boundaries
- Generate TypedDict/Pydantic models: Rejected - implementation detail

**Trade-offs:**
- (+) Clean separation of concerns
- (+) Architecture remains flexible
- (-) Requires handoff to other skills
- (-) No immediate runnable output

---

## Decision 3: Distributed CLAUDE.md Structure

**Decision:** Use separate CLAUDE.md files: root (Act-level) + per-cast (Cast-level).

**Justification:**
- Act-level provides project overview
- Cast-level provides detailed specifications
- Enables independent cast development
- Better version control (smaller, focused changes)
- Easier navigation for large projects

**Alternatives Considered:**
- Single monolithic CLAUDE.md: Rejected - becomes unwieldy for multi-cast projects
- Per-node documentation: Rejected - too granular, hard to maintain

**Trade-offs:**
- (+) Scalable for large projects
- (+) Clear ownership per cast
- (-) Cross-reference management needed
- (-) Requires validation script for consistency

---

## Decision 4: Agentic-First Assessment

**Decision:** Always check for AI agent needs BEFORE defaulting to basic patterns.

**Justification:**
- Many modern workflows benefit from agentic capabilities
- Easy to overlook agent needs with basic pattern focus
- Explicit assessment ensures conscious decision
- Prevents retrofitting agent capabilities later

**Alternatives Considered:**
- Basic patterns first, add agentic later: Rejected - leads to architectural rework
- No agentic support: Rejected - misses major use case

**Trade-offs:**
- (+) Comprehensive pattern coverage
- (+) Prevents rework
- (-) More complex decision tree
- (-) Learning curve for agentic patterns

---

## Decision 5: Pattern-First Design

**Decision:** Select pattern BEFORE designing state schema and nodes.

**Justification:**
- Pattern determines structural requirements
- State schema varies by pattern (cyclic needs iteration tracking, etc.)
- Node responsibilities depend on pattern flow
- Prevents pattern-schema mismatch

**Alternatives Considered:**
- State-first design: Rejected - leads to pattern constraints
- Parallel design: Rejected - creates inconsistencies

**Trade-offs:**
- (+) Coherent architecture
- (+) Pattern-appropriate state
- (-) Requires pattern knowledge upfront
- (-) May need iteration if pattern changes

---

## Decision 6: Mermaid for Diagrams

**Decision:** Use Mermaid syntax for all architecture diagrams.

**Justification:**
- Text-based, version-controllable
- Renders in GitHub, VS Code, many tools
- Simple syntax for flowcharts
- No external tools required

**Alternatives Considered:**
- ASCII art: Rejected - limited expressiveness
- External diagram tools: Rejected - adds dependencies
- No diagrams: Rejected - critical for understanding

**Trade-offs:**
- (+) Version-controlled diagrams
- (+) Portable across platforms
- (-) Limited layout control
- (-) Complex diagrams can be verbose

---

## Decision 7: Three Operational Modes

**Decision:** Support three distinct modes: Initial Design, Add Cast, Extract Sub-Cast.

**Justification:**
- Covers all common architectural workflows
- Each mode has focused, optimized questions
- Clear entry points for different user needs
- Mode detection guides appropriate workflow

**Alternatives Considered:**
- Single generic mode: Rejected - too many conditional branches
- More granular modes: Rejected - unnecessary complexity

**Trade-offs:**
- (+) Focused workflows per scenario
- (+) Optimized question sets
- (-) Mode detection logic needed
- (-) Some overlap between modes

---

## Decision 8: Validation Script

**Decision:** Include automated validation script for architecture consistency.

**Justification:**
- Ensures completeness of specifications
- Catches common errors (missing sections, broken links)
- Enables CI integration
- Provides confidence before implementation

**Alternatives Considered:**
- Manual checklist only: Rejected - error-prone
- No validation: Rejected - leads to incomplete specs

**Trade-offs:**
- (+) Automated quality assurance
- (+) Consistent specifications
- (-) Script maintenance overhead
- (-) May need updates for new patterns

---

## Decision 9: 3-Layer Activation System

**Decision:** Use keywords + patterns + description for skill activation.

**Justification:**
- 95%+ activation reliability target
- Keywords for exact phrase matching
- Patterns for flexible variations
- Description as NLU fallback

**Alternatives Considered:**
- Description only: Rejected - ~70% reliability
- Keywords only: Rejected - too rigid

**Trade-offs:**
- (+) High activation reliability
- (+) Handles query variations
- (-) More configuration to maintain
- (-) Requires tuning

---

## Decision 10: Template-Based Output

**Decision:** Use Markdown templates for CLAUDE.md generation.

**Justification:**
- Consistent output format
- Easy to update templates
- Clear structure for users
- Reduces generation errors

**Alternatives Considered:**
- Free-form generation: Rejected - inconsistent results
- JSON/YAML output: Rejected - less readable

**Trade-offs:**
- (+) Consistent documentation
- (+) Easy maintenance
- (-) Template rigidity
- (-) May not fit all edge cases

---

## Future Considerations

1. **Integration with developing-cast**: Seamless handoff from architecture to implementation
2. **Complexity metrics**: Quantitative analysis for sub-cast extraction decisions
3. **Pattern recommendations**: ML-based pattern suggestions from requirements
4. **Visual comparison**: Side-by-side architecture comparisons
