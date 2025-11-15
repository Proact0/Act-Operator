---
name: developing-cast
description: Use when implementing LangGraph 1.0 cast components (state, nodes, edges, tools, memory, routing) in Act projects after architecture is designed - provides modular implementation patterns, OOP examples with BaseNode/BaseGraph inheritance, decision frameworks for pattern selection, and Act project conventions
---

# Developing Cast

## Overview

**Comprehensive implementation reference for LangGraph 1.0 cast components in Act projects.**

This skill provides modular, token-efficient resources for implementing casts. Use after completing architecture in CLAUDE.md (from architecting-act skill). Each resource is self-contained, concise (< 4k tokens), and follows Act project conventions.

**Core principle:** Find the right pattern quickly, apply it correctly, follow Act conventions strictly.

---

## When to Use This Skill

Use developing-cast when:
- ✓ CLAUDE.md architecture is complete (from architecting-act)
- ✓ Cast has been scaffolded (from engineering-act)
- ✓ Ready to IMPLEMENT components (state, nodes, tools, edges, memory)
- ✓ Need LangGraph 1.0 patterns and best practices
- ✓ Following Act project conventions (BaseNode, BaseGraph, tools in modules/tools)

**NOT for:**
- ✗ Designing architecture (use architecting-act)
- ✗ Scaffolding project structure (use engineering-act)
- ✗ Testing implementation (use testing-cast)

---

## Resource Navigation

### 🔥 Start Here (Most Frequent)

**For EVERY cast implementation, read:**
1. **patterns/act-conventions.md** - Act project rules (file structure, BaseNode, BaseGraph, tools location)
2. **core/state-management.md** - State schemas, reducers, TypedDict patterns
3. **core/node-patterns.md** - BaseNode inheritance, execute() method, OOP patterns
4. **core/graph-construction.md** - StateGraph, compilation, BaseGraph usage

---

### 📁 Core Components (< 2k tokens each - frequently accessed)

**Building blocks for every cast:**

| Resource | When to Read | Key Topics |
|----------|--------------|------------|
| **core/state-management.md** | Defining state schema | TypedDict, Annotated reducers, channels, state updates |
| **core/node-patterns.md** | Creating nodes | BaseNode inheritance, execute(), async nodes, OOP |
| **core/edge-patterns.md** | Connecting nodes | Static edges, conditional routing, dynamic routing |
| **core/graph-construction.md** | Building graph | StateGraph, BaseGraph, add_node, compile, invoke |

---

### 🛠️ Tools (< 2k tokens each - very common)

**Tool creation and integration:**

| Resource | When to Read | Key Topics |
|----------|--------------|------------|
| **tools/tool-creation.md** | Creating tools | @tool decorator, schemas, modules/tools location |
| **tools/tool-runtime.md** | Accessing context in tools | ToolRuntime, config, Store access (Act-specific) |

---

### 💾 Memory & Persistence (< 4k tokens each - common)

**Short-term vs long-term memory:**

| Resource | When to Read | Key Topics |
|----------|--------------|------------|
| **memory/short-term-memory.md** | Thread-scoped memory | Checkpointers (MemorySaver, SqliteSaver), thread_id |
| **memory/long-term-memory.md** | Cross-session memory | Store API, InMemoryStore, MongoDBStore, namespaces |

**Decision:** In-session → checkpointers; Cross-session → Store

---

### 🚀 Advanced Features (< 4k tokens each - occasional)

**Specialized patterns:**

| Resource | When to Read | Key Topics |
|----------|--------------|------------|
| **advanced/interrupts.md** | Human approval needed | interrupt() function, approval patterns, Command() |
| **advanced/streaming.md** | Real-time output | astream_events, token streaming, state streaming |
| **advanced/subgraphs.md** | Composing casts | Subgraph patterns, shared/separate state, multi-agent |
| **advanced/mcp-integration.md** | Using MCP tools | MCP Adapter, MultiServerMCPClient, tool conversion |

---

### 🔧 Cross-Cutting Patterns (< 4k tokens each)

**Patterns that apply across components:**

| Resource | When to Read | Key Topics |
|----------|--------------|------------|
| **patterns/async-patterns.md** | Async operations needed | async def, ainvoke vs invoke, asyncio.gather, timeouts |
| **patterns/error-handling.md** | Production error handling | Try/except, retries, timeouts, error recovery |
| **patterns/act-conventions.md** | **START HERE - REQUIRED** | File structure, BaseNode, BaseGraph, tools location rules |

---

## Quick Decision Flowchart

```
Start implementing cast
    ↓
Read: patterns/act-conventions.md (REQUIRED)
    ↓
Define state schema? → core/state-management.md
    ↓
Create nodes? → core/node-patterns.md
    ↓
Create tools?
    ├─ Tool basics → tools/tool-creation.md
    └─ Need context access → tools/tool-runtime.md
    ↓
Connect nodes?
    ├─ Simple sequence → core/edge-patterns.md (static edges)
    └─ Conditional routing → core/edge-patterns.md (conditional edges)
    ↓
Need memory?
    ├─ Within session → memory/short-term-memory.md
    └─ Across sessions → memory/long-term-memory.md
    ↓
Build graph → core/graph-construction.md
    ↓
Need advanced features?
    ├─ Human approval → advanced/interrupts.md
    ├─ Streaming → advanced/streaming.md
    ├─ Compose casts → advanced/subgraphs.md
    └─ MCP tools → advanced/mcp-integration.md
    ↓
Handle errors? → patterns/error-handling.md
    ↓
Async operations? → patterns/async-patterns.md
```

---

## Integration with CLAUDE.md

**Workflow: Architecture → Implementation**

CLAUDE.md (from architecting-act) contains your cast architecture. Use this skill to translate architecture into code:

| CLAUDE.md Section | developing-cast Resources |
|-------------------|---------------------------|
| **State Schema** | → core/state-management.md |
| **Node Definitions** | → core/node-patterns.md |
| **Tool Requirements** | → tools/tool-creation.md, tools/tool-runtime.md |
| **Routing Logic** | → core/edge-patterns.md |
| **Memory Requirements** | → memory/short-term-memory.md OR memory/long-term-memory.md |
| **Human-in-the-Loop** | → advanced/interrupts.md |
| **Multi-Agent** | → advanced/subgraphs.md |
| **Error Handling** | → patterns/error-handling.md |

**Process:**
1. Read CLAUDE.md section
2. Identify component type
3. Navigate to corresponding resource
4. Apply pattern with Act conventions
5. Iterate until complete

---

## Act Project Conventions (Critical)

⚠️ **ALWAYS follow these rules (detailed in patterns/act-conventions.md):**

### File Structure:
```
casts/cast_name/
  ├── state.py           # State schemas (REQUIRED)
  ├── nodes.py           # Node implementations (REQUIRED)
  ├── graph.py           # Graph definition (REQUIRED)
  ├── conditions.py      # Routing functions (if conditional edges)
  └── modules/
      └── tools/         # Tools ONLY here (STRICT)
          └── *.py
```

### OOP Requirements:
- ✓ ALL nodes inherit from `casts.base_node.BaseNode`
- ✓ ALL graphs inherit from `casts.base_graph.BaseGraph`
- ✓ Use class-based implementation (not standalone functions)

### Tool Placement:
- ✓ Tools ONLY in `modules/tools/` - NO exceptions
- ✗ NEVER put tools in nodes.py, graph.py, or anywhere else

**Read patterns/act-conventions.md FIRST for complete rules.**

---

## Common Mistakes (Anti-Patterns)

❌ **Don't:**
- Skip patterns/act-conventions.md (leads to wrong file structure)
- Put tools outside modules/tools/ (breaks Act conventions)
- Forget to inherit from BaseNode/BaseGraph (breaks OOP pattern)
- Use `invoke()` with async checkpointer (causes hangs - use `ainvoke()`)
- Mix deprecated 0.x APIs with 1.0 (check docs for current APIs)
- Return wrong types from reducers (e.g., string instead of list for operator.add)
- Skip error handling (production code needs try/except)

✅ **Do:**
- Read patterns/act-conventions.md FIRST
- Inherit from base classes (BaseNode, BaseGraph)
- Use minimal code examples as templates
- Follow decision frameworks for pattern selection
- Validate all code against LangGraph 1.0 docs
- Include error handling from the start

---

## Resource File Structure

```
developing-cast/
├── SKILL.md                          # This file (< 5k tokens)
├── resources/
│   ├── core/                         # Core components (< 2k each)
│   │   ├── state-management.md
│   │   ├── node-patterns.md
│   │   ├── edge-patterns.md
│   │   └── graph-construction.md
│   ├── tools/                        # Tool patterns (< 2k each)
│   │   ├── tool-creation.md
│   │   └── tool-runtime.md
│   ├── memory/                       # Memory patterns (< 4k each)
│   │   ├── short-term-memory.md
│   │   └── long-term-memory.md
│   ├── advanced/                     # Advanced features (< 4k each)
│   │   ├── interrupts.md
│   │   ├── streaming.md
│   │   ├── subgraphs.md
│   │   └── mcp-integration.md
│   └── patterns/                     # Cross-cutting (< 4k each, except act-conventions < 2k)
│       ├── act-conventions.md        # READ FIRST (< 2k)
│       ├── async-patterns.md
│       └── error-handling.md
└── test-scenarios.md                 # Testing scenarios for skill validation
```

---

## Quick Reference: What Goes Where

| Component | File Location | Base Class | Resource |
|-----------|---------------|------------|----------|
| **State schema** | `state.py` | TypedDict | core/state-management.md |
| **Nodes** | `nodes.py` | BaseNode | core/node-patterns.md |
| **Tools** | `modules/tools/*.py` | @tool | tools/tool-creation.md |
| **Routing** | `conditions.py` | (state) -> str | core/edge-patterns.md |
| **Graph** | `graph.py` | BaseGraph | core/graph-construction.md |
| **Checkpointer** | Pass to compile() | MemorySaver/SqliteSaver | memory/short-term-memory.md |
| **Store** | Pass to compile() | InMemoryStore/etc | memory/long-term-memory.md |

---

## Token Efficiency Guide

**Resources are sized by access frequency:**

- **< 2k tokens**: Core (state, nodes, edges, graph), Tools, Act conventions
  - Accessed frequently, must be quick to read

- **< 4k tokens**: Memory, Advanced features, Patterns
  - Accessed occasionally, can be more detailed

**All resources:**
- Self-contained (can read independently)
- Minimal code (only when necessary)
- Decision-focused (when to use, trade-offs)
- OOP examples (BaseNode, BaseGraph)
- Act-compliant (follow conventions)

---

## Example Usage Flow

**Implementing a Chat Cast with Tools:**

1. **Read conventions:**
   - `patterns/act-conventions.md` → Understand file structure, rules

2. **Define state:**
   - `core/state-management.md` → Create state.py with messages reducer

3. **Create tools:**
   - `tools/tool-creation.md` → Create modules/tools/web_search.py with @tool
   - `tools/tool-runtime.md` → Add runtime context access if needed

4. **Create nodes:**
   - `core/node-patterns.md` → Create nodes.py inheriting from BaseNode

5. **Add routing:**
   - `core/edge-patterns.md` → Create conditions.py for tool/chat routing

6. **Build graph:**
   - `core/graph-construction.md` → Create graph.py inheriting from BaseGraph

7. **Add memory (if needed):**
   - `memory/short-term-memory.md` → Add checkpointer for conversation history

8. **Add error handling:**
   - `patterns/error-handling.md` → Wrap tool calls in try/except

**Result:** Production-ready cast following Act conventions with LangGraph 1.0 best practices.

---

## Verification Checklist

Before considering implementation complete:

**Act Conventions:**
- [ ] All tools in `modules/tools/` (checked patterns/act-conventions.md)
- [ ] All nodes inherit from BaseNode
- [ ] Graph inherits from BaseGraph
- [ ] File structure matches Act conventions

**LangGraph 1.0:**
- [ ] Using current APIs (not deprecated 0.x)
- [ ] State uses TypedDict with correct reducers
- [ ] Nodes return dict with state updates
- [ ] Graph compiled with checkpointer (if memory needed)

**Quality:**
- [ ] Error handling in place (checked patterns/error-handling.md)
- [ ] Async patterns used correctly (if applicable)
- [ ] Code follows OOP principles
- [ ] Minimal, maintainable implementation

---

## Next Steps

After implementation:
1. **Test:** Use testing-cast skill for comprehensive testing
2. **Iterate:** Fix issues, refine based on test results
3. **Document:** Update cast-specific docs (README, etc.)
4. **Deploy:** Follow deployment procedures

**Remember:** This skill is for IMPLEMENTATION. For architecture design, use architecting-act. For testing, use testing-cast.

---

## The Bottom Line

**Developing-cast is your implementation co-pilot.**

- **Navigation hub:** Find the right resource quickly
- **Minimal patterns:** Apply proven LangGraph 1.0 code
- **Decision frameworks:** Choose the right approach
- **Act compliance:** Follow project conventions strictly
- **Token efficient:** Read only what you need, when you need it

Start with patterns/act-conventions.md, then navigate to the components you're implementing. Each resource is self-contained, concise, and ready to use.

**Quality over coverage. Precision over volume. Act conventions always.**
