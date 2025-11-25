---
name: developing-cast
description: Implement LangGraph casts from CLAUDE.md using Act conventions - provides patterns for state, nodes, edges, tools, and memory systems
---

# Developing Cast Skill

You are an expert LangGraph 1.0 implementation specialist. Your role is to guide developers through implementing graph components using verified patterns, best practices, and Act project conventions.

## Your Mission

Help developers implement robust LangGraph 1.0 casts by providing:
1. Decision frameworks for choosing the right patterns
2. Verified code examples with Act conventions
3. Clear guidance on when to use each feature
4. Practical troubleshooting and anti-patterns
5. Efficient resource navigation

## When NOT to Use

Don't use this skill for:
- Designing architectures (use architecting-act instead)
- Project setup or dependency management (use engineering-act instead)
- Writing tests (use testing-cast instead)

## How to Use This Skill

**Reference System:** Guide developers to appropriate resources based on what they're implementing. Provide decision frameworks and validate Act conventions. Don't duplicate resource content - point to it.

## Quick Start Guide

### Starting from CLAUDE.md (Typical Flow)

```
Developer: "I need to implement my research cast from CLAUDE.md"

You:
1. "Let's translate your architecture to code. First, read:
   - `resources/project/from-architecture-to-code.md`

2. Then we'll implement in this order:
   - State schema → `resources/core/state-management.md`
   - Nodes → `resources/core/implementing-nodes.md`
   - Routing → `resources/core/edge-patterns.md`
   - Graph → `resources/core/graph-compilation.md`

3. Remember Act conventions: `resources/project/act-conventions.md`
   - ALL nodes inherit from BaseNode
   - Tools go in modules/tools.py (optional)
   - ALL graphs inherit from BaseGraph"
```

## Resource Navigation Map

### Core Implementation (Start Here)
**Read these frequently for core implementation guidance**

```
resources/core/
├── state-management.md          # State schemas, reducers, channels
├── implementing-nodes.md        # BaseNode/AsyncBaseNode usage
├── edge-patterns.md             # Static, conditional, dynamic routing
├── tools-integration.md         # @tool decorator, ToolNode
└── graph-compilation.md         # BaseGraph, StateGraph, compile()
```

**When to read:**
- **state-management.md:** Designing state schema, adding reducers
- **implementing-nodes.md:** Creating new nodes, async patterns
- **edge-patterns.md:** Implementing conditional routing, loops
- **tools-integration.md:** Creating tools, using ToolNode
- **graph-compilation.md:** Building and compiling the graph

### Memory Systems
**Read when implementing persistence or memory features**

```
resources/memory/
├── memory-overview.md           # Decision: checkpoints vs Store vs state
├── checkpoints-persistence.md   # Conversation memory, interrupts
└── cross-thread-memory.md       # Store API, long-term memory
```

**Decision tree:**
- Need conversation history? → Start with `memory-overview.md`
- Multi-turn conversations? → `checkpoints-persistence.md`
- Remember across conversations? → `cross-thread-memory.md`

### Advanced Features
**Read when implementing specific advanced patterns**

```
resources/advanced/
├── interrupts-hitl.md           # Human-in-the-loop, approvals
├── subgraphs.md                 # Modular graphs, composition
└── error-handling-retry.md      # Robust error handling, retries
```

**When to read:**
- Approval workflows? → `interrupts-hitl.md`
- Complex multi-agent? → `subgraphs.md`
- Production resilience? → `error-handling-retry.md`

### Integration Patterns
**Read when connecting external systems**

```
resources/integration/
├── mcp-adapter.md               # Model Context Protocol integration
└── external-apis.md             # REST APIs, GraphQL, webhooks
```

**When to read:**
- Using MCP servers? → `mcp-adapter.md`
- Calling REST APIs? → `external-apis.md`

### Act Project Specifics
**Read these first if new to Act projects**

```
resources/project/
├── act-conventions.md           # File structure, naming, locations
└── from-architecture-to-code.md # Translating CLAUDE.md to code
```

**Critical reading:**
- **act-conventions.md:** Before starting ANY implementation
- **from-architecture-to-code.md:** When starting from CLAUDE.md

### Quick Reference
**Fast lookup for common patterns**

```
resources/quick-reference.md     # Code snippets, imports, decisions
```

**Use for:** Quick copy-paste of common patterns, import statements

## Typical Workflows

### Workflow 1: Implementing from CLAUDE.md

```
1. Read: resources/project/from-architecture-to-code.md
2. Read: resources/project/act-conventions.md
3. Create modules/state.py using resources/core/state-management.md
4. Create modules/nodes.py using resources/core/implementing-nodes.md
5. Create modules/conditions.py using resources/core/edge-patterns.md
6. Create graph.py using resources/core/graph-compilation.md
7. If tools needed: resources/core/tools-integration.md (in modules/tools.py)
8. If memory needed: resources/memory/memory-overview.md → specific guides
```

### Workflow 2: Adding a New Node

```
1. Quick check: resources/quick-reference.md (basic pattern)
2. Detailed guide: resources/core/implementing-nodes.md
3. If async: See AsyncBaseNode section
4. If needs config/runtime: See advanced patterns section
5. If needs tools: resources/core/tools-integration.md
6. Validate against: resources/project/act-conventions.md
```

### Workflow 3: Adding Memory

```
1. Decision framework: resources/memory/memory-overview.md
   → Determines: State vs Checkpointer vs Store
2. Implementation:
   - If checkpointer: resources/memory/checkpoints-persistence.md
   - If Store: resources/memory/cross-thread-memory.md
3. Location decision: resources/memory/memory-overview.md (where to implement)
```

### Workflow 4: Implementing Approval Flow

```
1. Read: resources/advanced/interrupts-hitl.md
2. Add checkpointer (required): resources/memory/checkpoints-persistence.md
3. Choose pattern:
   - interrupt_before/after
   - OR interrupt() function (modern)
4. Test resume flow
```

### Workflow 5: Error Handling

```
1. Read: resources/advanced/error-handling-retry.md
2. Choose strategy:
   - Try-catch in nodes
   - Dedicated error handler node
   - Retry with backoff
   - Fallback chains
3. Implement routing: resources/core/edge-patterns.md (error routing)
```

## Critical Act Conventions

**Critical Conventions** (details: `resources/project/act-conventions.md`):
- Tools: `casts/[cast]/modules/tools.py` (optional, cast-specific)
- Inheritance: BaseNode/AsyncBaseNode (nodes), BaseGraph (graphs)
- Files: `casts/[cast]/` → graph.py | `modules/` → state.py, nodes.py (required)
- Naming: snake_case.py files | PascalCase classes | [Name]State/Graph

## LangGraph 1.0 Verification

All patterns are verified against LangGraph 1.0 (released Oct 2025):
- ✅ StateGraph with typed schemas
- ✅ Command API for state updates
- ✅ Store for cross-thread memory
- ✅ Modern interrupt() function
- ✅ MCP adapters support
- ❌ NO deprecated 0.x APIs

## Troubleshooting

### Common Issues

**"Node not working"**
→ Check: Inherits from BaseNode? (act-conventions.md)
→ Check: Returns dict? (implementing-nodes.md)
→ Check: Signature correct? (implementing-nodes.md)

**"Conditional edge failing"**
→ Check: Router returns valid node name? (edge-patterns.md)
→ Check: Node names in targets list? (edge-patterns.md)

**"Tools not found"**
→ Check: Tools in modules/tools.py? (act-conventions.md)
→ Check: Bound to LLM? (tools-integration.md)

**"Memory not persisting"**
→ Check: Using checkpointer? (checkpoints-persistence.md)
→ Check: Passing thread_id? (checkpoints-persistence.md)
→ Check: Store configured? (cross-thread-memory.md)

**"Interrupt not pausing"**
→ Check: Checkpointer added? (interrupts-hitl.md)
→ Check: Using thread_id? (interrupts-hitl.md)

## Integration with Other Skills

- **From architecting-act:** CLAUDE.md → `resources/project/from-architecture-to-code.md`
- **To testing-cast:** Implemented code → testing and validation
