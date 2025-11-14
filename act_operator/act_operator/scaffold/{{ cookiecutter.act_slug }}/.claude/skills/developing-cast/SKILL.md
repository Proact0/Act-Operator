---
name: developing-cast
description: Use when implementing cast components (nodes, tools, state, edges) in LangGraph 1.0 - provides modular resource navigation for tokens-efficient development preventing premature implementation
---

# Developing Cast

## Overview

**Implement with guidance, not guesswork.** Reference modular resources for LangGraph 1.0 patterns as needed.

**Core principle:** Read only what you need, when you need it. Don't load all resources upfront.

## When to Use

Use when implementing:
- Nodes (graph operations)
- Tools (agent capabilities)
- State schemas (graph data)
- Edges (flow logic)
- Memory patterns (short/long-term)
- Middleware (custom behaviors)

**Prerequisite:** Architecture designed with `architecting-act` skill

## Core Workflow

### 1. Identify What You're Building

Before reading resources, determine:
- **Component type**: Node? Tool? Edge logic?
- **Dependencies**: Does it use tools? Memory? External APIs?
- **Patterns**: Human-in-the-loop? Subgraph? Streaming?

### 2. Consult Resource Index

**DON'T** read all resources. **DO** read only relevant modules:

| Building | Read These Resources |
|----------|---------------------|
| Basic node | `resources/nodes.md` |
| Node with tools | `resources/nodes.md` + `resources/tools.md` |
| Tool implementation | `resources/tools.md` |
| Memory in node | `resources/memory.md` (specify type) |
| Conditional routing | `resources/edges.md` |
| State schema | `resources/state.md` |
| Human-in-the-loop | `resources/interrupts.md` |
| Subgraph pattern | `resources/subgraphs.md` (+ `engineering-act` for new cast) |
| Custom middleware | `resources/middleware.md` |
| MCP integration | `resources/mcp-adapter.md` |

### 3. Implement with Patterns

After reading resource:
1. Follow LangGraph 1.0 APIs exactly
2. Use BaseNode pattern from `casts/base_node.py`
3. Put components in correct locations (see Project Structure)
4. Test incrementally (see `testing-cast` skill)

### 4. Verify Locations

**Critical:** Components must go in specific locations:

| Component | Location | Never Put Here |
|-----------|----------|---------------|
| Tools | `modules/tools/` | modules/agents/, modules/nodes/ |
| Nodes | `modules/nodes.py` | root, tools/ |
| State | `modules/state.py` | nodes.py, graph.py |
| Conditions | `modules/conditions.py` | nodes.py, graph.py |
| Agents | `modules/agents/` | tools/, nodes/ |

## Resource Modules

### Core Implementation

**`resources/nodes.md`**
- Using BaseNode
- execute() method signature
- State access and updates
- Runtime context
- Logging patterns

**`resources/tools.md`**
- Creating tools with @tool decorator
- Tool location (`modules/tools/`)
- Accessing ToolRuntime context
- Tool schemas and validation
- Passing tools to agents

**`resources/state.md`**
- State schema design (InputState, OutputState, State)
- Reducers and channels
- State updates in nodes
- MessagesState patterns

**`resources/edges.md`**
- Conditional routing functions
- Implementing in `modules/conditions.py`
- Route logic patterns
- Default routes and END

### Memory Patterns

**`resources/memory.md`**
- **Short-term memory** (3 types):
  1. Session state (graph state schema)
  2. Agent scratchpad (`modules/agents/`)
  3. Runtime store (thread-scoped)
- **Long-term memory** (cross-session persistence)
- **LangMem** integration

**When to use which:**
- Session state: Data needed across nodes in single run
- Agent scratchpad: Agent reasoning traces
- Runtime store: Thread-scoped memory across runs
- Long-term: Persistent memory across threads/users

### Advanced Patterns

**`resources/interrupts.md`**
- Human-in-the-loop patterns
- Approval nodes
- Input collection
- Resume after interrupt

**`resources/subgraphs.md`**
- When to use subgraphs
- Creating nested casts
- State passing between graphs
- Subgraph compilation

**`resources/middleware.md`**
- Custom middleware patterns
- Request/response interception
- Logging and observability
- Error handling middleware

**`resources/mcp-adapter.md`**
- Integrating MCP tools (NOT creating MCP servers)
- MCP client patterns
- Tool discovery from MCP
- MCP + LangGraph integration

## Quick Decision Tree

```
What are you implementing?
│
├─ Node?
│  ├─ Uses tools? → Read nodes.md + tools.md
│  ├─ Needs memory? → Read nodes.md + memory.md
│  └─ Basic? → Read nodes.md
│
├─ Tool?
│  ├─ Standalone? → Read tools.md
│  └─ Needs context? → Read tools.md (ToolRuntime section)
│
├─ State schema? → Read state.md
│
├─ Routing logic? → Read edges.md
│
├─ Memory pattern?
│  └─ What type? → Read memory.md (specific section)
│
└─ Advanced?
   ├─ Human review? → Read interrupts.md
   ├─ Nested graph? → Read subgraphs.md
   ├─ Custom behavior? → Read middleware.md
   └─ MCP integration? → Read mcp-adapter.md
```

## Common Mistakes

| Mistake | Fix | Resource |
|---------|-----|----------|
| Tool in modules/nodes/ | Move to modules/tools/ | tools.md |
| Loading all resources | Read only what's needed | This workflow |
| Wrong BaseNode usage | Check execute() signature | nodes.md |
| Unclear memory type | Clarify: session/thread/long-term | memory.md |
| Hardcoded routing | Use conditions.py | edges.md |
| State mutation | Return dict updates | state.md |
| Missing runtime access | Add runtime param | nodes.md |

## Red Flags - Consult Resources First

- "I'll guess the LangGraph API" → Read resource first
- "Tools probably go in nodes.py" → Check tools.md
- "Memory is just state, right?" → Read memory.md (3 types!)
- "I'll implement then check docs" → Read first, implement second
- "This pattern should work" → Verify against resource

## Act Project Specifics

**BaseNode location:** `casts/base_node.py` - Always extend this

**Module structure:** Each cast has:
```
casts/<cast_name>/
├── graph.py              # Graph assembly
├── modules/
│   ├── state.py          # State schemas
│   ├── nodes.py          # Node implementations
│   ├── conditions.py     # Routing logic
│   ├── tools/            # Tools ONLY
│   └── agents/           # Agent configurations
└── tests/                # Tests
```

**LangGraph 1.0 requirement:** All patterns must use LangGraph >= 1.0 APIs

**Cookiecutter templates:** Generated casts follow this structure automatically

## Real-World Impact

Modular resource approach:
- **Token efficiency**: Load 4k tokens vs 20k+ for all docs
- **Accurate patterns**: Verified LangGraph 1.0 APIs
- **Correct locations**: Tools in tools/, not scattered
- **Faster implementation**: Direct to relevant guidance

**Example:** Implementing node with tool:
- Without skill: 15 min searching + wrong location + refactor = 30 min
- With skill: Read 2 resources (2 min) + correct implementation (8 min) = 10 min

**Time saved:** 20 minutes per component × many components = hours saved per cast.
