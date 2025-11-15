---
name: developing-cast
description: Use when implementing LangGraph cast components (state, nodes, edges, tools, memory) after architecture design is complete - provides modular implementation guidance, code examples, decision frameworks, and Act project conventions for building production-ready casts
---

# Developing Cast

## Overview

Comprehensive implementation reference for LangGraph 1.0 cast components. Provides modular documentation, verified code examples, and decision frameworks for implementing state, nodes, edges, tools, memory, interrupts, streaming, subgraphs, and MCP adapters in Act Operator projects.

**When to use:** After architecting-act and engineering-act have created CLAUDE.md and scaffolded the cast structure. Use this skill during active implementation to find the right patterns and avoid common mistakes.

## Prerequisites

- CLAUDE.md exists (from architecting-act) with architecture spec
- Cast structure scaffolded (from engineering-act): `casts/[cast_name]/`
- Base classes available: `casts/base_node.py`, `casts/base_graph.py`
- Ready to implement the architecture

## Resource Navigation

### 🎯 Quick Start

**New to LangGraph?** Start here:
1. Read `resources/quick-reference.md` - one-page cheatsheet
2. Read `resources/from-architecture.md` - translate CLAUDE.md to code
3. Then navigate to specific topics below

**Have CLAUDE.md ready?** → `resources/from-architecture.md`

### 📦 Core Components (Frequently Accessed)

**All implementations start here:**

| Resource | When to Read | Token Count |
|----------|--------------|-------------|
| `01-core/state.md` | Defining state schemas, reducers, channels | < 2k |
| `01-core/nodes.md` | Creating node classes (BaseNode/AsyncBaseNode) | < 2k |
| `01-core/edges.md` | Adding routing logic (static/conditional/dynamic) | < 2k |
| `01-core/graph.md` | Building and compiling the graph | < 2k |

**Read in order** if new to LangGraph: state → nodes → edges → graph

### 🛠️ Tools (Common)

| Resource | When to Read | Token Count |
|----------|--------------|-------------|
| `02-tools/creating-tools.md` | Creating new tools for your cast | < 2k |
| `02-tools/tool-patterns.md` | ToolNode, ToolRuntime, composition | < 2k |

⚠️ **Act Convention:** Tools MUST be in `modules/tools/` (never in cast directory)

### 🧠 Memory & Persistence

| Resource | When to Read | Token Count |
|----------|--------------|-------------|
| `03-memory/short-term-memory.md` | In-session memory via state | < 3k |
| `03-memory/long-term-memory.md` | Cross-session memory with Store | < 3k |
| `03-memory/checkpointers.md` | Persistence, thread_id, database setup | < 3k |

**Decision:** Need memory across conversations? → long-term. Within single run? → short-term.

### 🚀 Advanced Features

**Read when needed:**

| Resource | When to Read | Token Count |
|----------|--------------|-------------|
| `04-advanced/interrupts.md` | Human-in-the-loop, approval workflows | < 4k |
| `04-advanced/streaming.md` | Stream tokens/state to frontend | < 4k |
| `04-advanced/subgraphs.md` | Multi-agent teams, nested graphs | < 4k |
| `04-advanced/mcp-adapter.md` | MCP tool integration (NOT server) | < 4k |
| `04-advanced/error-handling.md` | Retry logic, fault tolerance | < 4k |

### 🎨 Patterns & Testing

| Resource | When to Read | Token Count |
|----------|--------------|-------------|
| `05-patterns/prebuilt-components.md` | create_react_agent, ToolNode shortcuts | < 3k |
| `05-patterns/testing.md` | pytest, mocks, integration tests | < 3k |

## Quick Decision Flowchart

```
Have CLAUDE.md architecture?
  ├─ YES → Start with from-architecture.md
  └─ NO  → Read quick-reference.md first

Need to implement:
  ├─ State schema? → 01-core/state.md
  ├─ Node logic? → 01-core/nodes.md
  ├─ Routing? → 01-core/edges.md
  ├─ Tool calling? → 02-tools/creating-tools.md
  ├─ Cross-session memory? → 03-memory/long-term-memory.md
  ├─ Human approval? → 04-advanced/interrupts.md
  ├─ Multi-agent team? → 04-advanced/subgraphs.md
  ├─ MCP integration? → 04-advanced/mcp-adapter.md
  └─ Not sure? → from-architecture.md

Getting errors?
  ├─ State update issues? → 01-core/state.md (reducers section)
  ├─ Node not executing? → 01-core/nodes.md (common mistakes)
  ├─ Routing wrong? → 01-core/edges.md (conditional edges)
  ├─ Tool errors? → 02-tools/tool-patterns.md (error handling)
  └─ Persistence issues? → 03-memory/checkpointers.md
```

## Act Project Conventions

**CRITICAL - These are enforced:**

### File Locations
- ✅ Tools: `modules/tools/[tool_name].py` (ONLY here)
- ✅ Nodes: `casts/[cast_name]/nodes.py`
- ✅ State: `casts/[cast_name]/state.py`
- ✅ Conditions: `casts/[cast_name]/conditions.py`
- ✅ Graph: `casts/[cast_name]/graph.py`
- ❌ Never put tools in cast directory
- ❌ Never put nodes in modules

### Base Class Inheritance
- ✅ All nodes inherit from `casts.base_node.BaseNode` or `AsyncBaseNode`
- ✅ All graphs inherit from `casts.base_graph.BaseGraph`
- ❌ Never create standalone node functions
- ❌ Never skip base class inheritance

### Method Signatures
```python
# Node execute method
def execute(self, state: YourStateClass) -> dict:
    """Returns dict of state updates."""
    return {"key": "value"}

# Graph build method
def build(self) -> CompiledStateGraph:
    """Returns compiled graph."""
    return builder.compile()
```

## Integration with Other Skills

### Before This Skill
1. **architecting-act** - Created CLAUDE.md with architecture design
2. **engineering-act** - Scaffolded cast directory structure

### During This Skill
- Reference CLAUDE.md for architecture decisions
- Use `from-architecture.md` to translate design to code
- Follow patterns in modular resources

### After This Skill
**testing-cast** - Test the implemented cast with pytest

## Common Workflows

### Workflow 1: Implementing New Cast from CLAUDE.md
1. Read `from-architecture.md` - understand translation approach
2. Implement state schema using `01-core/state.md`
3. Create node classes using `01-core/nodes.md`
4. Add routing logic using `01-core/edges.md`
5. Build graph using `01-core/graph.md`
6. If tools needed → `02-tools/creating-tools.md`
7. If persistence needed → `03-memory/checkpointers.md`

### Workflow 2: Adding Feature to Existing Cast
1. Update CLAUDE.md with architecting-act
2. Identify components to modify (state/nodes/edges/tools)
3. Read relevant resource (e.g., `01-core/nodes.md` for new node)
4. Implement following Act conventions
5. Test with testing-cast

### Workflow 3: Debugging Cast Issues
1. Identify symptom (state not updating? routing wrong? tool error?)
2. Use Quick Decision Flowchart above
3. Read relevant resource's "Common Mistakes" section
4. Check "Act Project Conventions" compliance
5. Review error handling patterns

### Workflow 4: Adding Advanced Features
1. Determine feature needed (human-in-loop? streaming? MCP?)
2. Read corresponding `04-advanced/` resource
3. Review decision frameworks and trade-offs
4. Implement minimal example first
5. Expand to production pattern

## Resource Organization Philosophy

**Why modular resources?**
- **Token efficiency** - Load only what you need
- **Faster lookup** - Navigate directly to topic
- **Reduced context** - Stay under token budgets
- **Better maintenance** - Update one topic at a time

**Resource sizing:**
- Core resources (frequently accessed): < 2k tokens
- Common resources: < 2k tokens
- Memory resources: < 3k tokens
- Advanced resources: < 4k tokens
- All resources: < 500 lines

**Content strategy:**
- **Concepts first** - Understand the "why"
- **Minimal code** - Only when necessary
- **Decision frameworks** - When to use vs alternatives
- **Act conventions** - Project-specific requirements
- **Anti-patterns** - What NOT to do

## What's NOT in This Skill

- **Architecture design** → Use architecting-act
- **Project setup** → Use engineering-act
- **Testing** → Use testing-cast
- **LangChain 0.x patterns** → Only 1.0 supported
- **Generic LangGraph tutorials** → Act-specific patterns only

## Key Principles

### Object-Oriented Implementation
All code examples demonstrate:
- Inheritance from BaseNode or BaseGraph
- Class-based patterns (not standalone functions)
- Proper OOP principles

### LangGraph 1.0 Only
- All APIs verified against current docs
- No deprecated patterns
- Released October 2025

### Act Project Standards
- Tools in modules/tools
- Base class inheritance required
- Consistent file structure
- Production-ready patterns

### Decision-Focused Guidance
Every resource includes:
- "When to use this" section
- Trade-offs vs alternatives
- Common mistakes
- Anti-patterns

## Getting Help

**Resource not clear?** Check:
1. "Common Mistakes" section in resource
2. Code examples for patterns
3. Decision framework for when to apply
4. Anti-patterns for what to avoid

**Still stuck?** Verify:
1. Following Act project conventions
2. Using correct LangGraph 1.0 APIs
3. Inheriting from base classes correctly
4. Tools in correct location (modules/tools)

**Pattern not working?** Review:
1. Error message against "Common Mistakes"
2. State schema for reducer issues
3. Node signature for parameter issues
4. Graph compilation for structure issues

## Version Information

- **LangGraph:** 1.0+ (released October 2025)
- **Skill created:** November 2025
- **Python:** 3.11+ recommended for async features
- **Act Operator:** Compatible with current scaffold

## Quick Reference Summary

**Most common operations:**
- Create state schema → `01-core/state.md`
- Create node class → `01-core/nodes.md`
- Add conditional routing → `01-core/edges.md`
- Create tool → `02-tools/creating-tools.md`
- Add persistence → `03-memory/checkpointers.md`
- Add human approval → `04-advanced/interrupts.md`

**Most common mistakes:**
- Tools not in modules/tools → Check file locations above
- Node not inheriting BaseNode → Check base class inheritance
- State not updating → Check reducers in `01-core/state.md`
- Routing not working → Check conditions in `01-core/edges.md`
- Config not passed → Check node signatures in `01-core/nodes.md`

**Most common questions:**
- "Where do tools go?" → `modules/tools/` (see conventions)
- "How do I access runtime?" → `01-core/nodes.md` (execute signature)
- "How do I add memory?" → `03-memory/` (short vs long term)
- "How do I get thread_id?" → `01-core/nodes.md` (get_thread_id method)
- "How do I test?" → `05-patterns/testing.md`

## Resource Index

All resources alphabetically:

- `01-core/edges.md` - Static, conditional, and dynamic routing
- `01-core/graph.md` - Building and compiling graphs
- `01-core/nodes.md` - Node classes with BaseNode inheritance
- `01-core/state.md` - State schemas, reducers, channels
- `02-tools/creating-tools.md` - @tool decorator and tool creation
- `02-tools/tool-patterns.md` - ToolNode, ToolRuntime, composition
- `03-memory/checkpointers.md` - Persistence and thread management
- `03-memory/long-term-memory.md` - Cross-session Store memory
- `03-memory/short-term-memory.md` - In-session state memory
- `04-advanced/error-handling.md` - Retry logic and fault tolerance
- `04-advanced/interrupts.md` - Human-in-the-loop workflows
- `04-advanced/mcp-adapter.md` - Model Context Protocol integration
- `04-advanced/streaming.md` - Token and state streaming
- `04-advanced/subgraphs.md` - Nested graphs and multi-agent teams
- `05-patterns/prebuilt-components.md` - create_react_agent and shortcuts
- `05-patterns/testing.md` - pytest, mocks, integration tests
- `from-architecture.md` - Translating CLAUDE.md to implementation
- `quick-reference.md` - One-page cheatsheet

---

**Remember:** This is an INDEX. Navigate to specific resources for implementation details. Each resource is standalone and token-optimized for quick loading.
