# Changelog

All notable changes to the `architecting-act` skill will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2025-01-15

### Added

**Core Functionality:**
- Three operational modes: Initial Design, Add Cast, Extract Sub-Cast
- Interactive questioning workflow (one question at a time)
- Architecture diagram generation with Mermaid syntax
- State schema design (InputState, OutputState, OverallState)
- Node specification templates

**Pattern Support:**
- Sequential, Branching, Cyclic patterns for non-agentic workflows
- Comprehensive agentic design patterns:
  - Single-Agent System
  - Multi-Agent Systems (Sequential, Parallel, Loop, Review & Critique, Iterative Refinement, Coordinator, Hierarchical, Swarm)
  - ReAct (Reason and Act) Pattern
  - Human-in-the-Loop Pattern
  - Custom Logic Pattern

**Templates (in `templates/` directory):**
- `CLAUDE.act.md.template`: Root CLAUDE.md template with AUTO-MANAGED markers
- `CLAUDE.cast.md.template`: Cast-level CLAUDE.md template with AUTO-MANAGED markers

**Resources (in `resources/` directory):**
- `agentic-design-patterns.md`: Comprehensive agentic pattern guide
- `pattern-decision-matrix.md`: Pattern selection guide
- `cast-analysis-guide.md`: Complexity analysis guide
- Mode-specific question guides:
  - `initial-design-questions.md`
  - `add-cast-questions.md`
  - `extract-subcast-questions.md`
- Design guides:
  - `state-schema.md`
  - `node-specification.md`
  - `edge-routing.md`

**Scripts:**
- `validate_architecture.py`: Distributed architecture validation tool (730+ lines)
  - Validates root CLAUDE.md (Act-level)
  - Validates cast CLAUDE.md files
  - Cross-reference validation between Act and Casts
  - Mermaid diagram validation (START/END nodes, orphan detection)
  - State schema completeness validation
  - Placeholder detection
  - Fix hints for all errors
  - JSON output option for CI integration
  - All checks from former `validation-checklist.md` integrated

**3-Layer Activation System:**
- 14 keyword phrases for exact matching
- 7 regex patterns for flexible matching
- Enhanced description for NLU fallback

### Architecture Decisions

- **Interactive Design Philosophy**: One question at a time to ensure focused requirements gathering
- **No Code Generation**: Skill focuses on architecture design only; implementation delegated to other skills
- **Distributed CLAUDE.md**: Act-level root file + Cast-level files for maintainability
- **Pattern-First Approach**: Pattern selection before state/node design
- **Agentic-First Assessment**: Always check for AI agent needs before defaulting to basic patterns

### Known Limitations

- Does not generate implementation code (by design)
- Requires manual execution of `act cast` command for new cast directories
- Validation script requires Python 3.10+

### Planned for v2.0

- Auto-detection of existing casts from file system
- Integration with developing-cast skill for seamless handoff
- Enhanced sub-cast extraction analysis with complexity metrics
- Template-based quick start for common patterns

## [Unreleased]

### Changed

- Migrated templates from `resources/` to `templates/` directory with AUTO-MANAGED markers
- Integrated all validation checks from `validation-checklist.md` into `validate_architecture.py`
- Enhanced validation script with fix hints, placeholder detection, and JSON output
- Removed redundant resource files (content merged into templates/scripts)

### Planned

- Add support for more complex hybrid patterns
- Add visual architecture comparison tool
