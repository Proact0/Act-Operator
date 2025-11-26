---
name: developing-cast
description: Implement LangGraph casts from CLAUDE.md using Act conventions - provides patterns for state, nodes, edges, tools, and memory systems
---

# Developing Cast Skill

You are an expert LangGraph 1.0 implementation specialist. Your role is to guide developers through implementing graph components using verified patterns, best practices, and Act project conventions.

## When NOT to Use

Don't use this skill for:
- Designing architectures (use architecting-act instead)
- Project setup or dependency management (use engineering-act instead)
- Writing tests (use testing-cast instead)

## Resource Guide

All resources are independent and self-contained. When you need to implement a feature, read the relevant resource in its entirety.

### Core Implementation

Select and read resources based on what you're implementing:

**State Design**: `resources/core/state-management.md`
- TypedDict vs Pydantic selection
- Reducer patterns (add, replace)
- State update strategies
- Channel configuration

**Node Implementation**: `resources/core/implementing-nodes.md`
- BaseNode/AsyncBaseNode usage
- Config and Runtime access
- Error handling patterns
- Sync vs async decisions

**Edge and Routing**: `resources/core/edge-patterns.md`
- Conditional routing patterns
- Dynamic routing with Send
- Loop and retry patterns
- Static edge definitions

**Tools Integration**: `resources/core/tools-integration.md`
- @tool decorator usage
- ToolNode patterns
- InjectedToolRuntime
- Act tool conventions

**Graph Compilation**: `resources/core/graph-compilation.md`
- BaseGraph usage (required)
- Checkpointer configuration
- Store setup
- Interrupt configuration

### Memory and Persistence

Read when your graph needs memory:

**Memory Strategy**: `resources/memory/memory-overview.md`
- State vs Checkpointer vs Store
- Decision matrix for memory types
- When to use each approach

**Conversation History**: `resources/memory/checkpoints-persistence.md`
- MemorySaver, SqliteSaver, PostgresSaver
- thread_id usage patterns
- Multi-turn conversation support
- Time-travel debugging

**Cross-Thread Memory**: `resources/memory/cross-thread-memory.md`
- Store API usage
- InMemoryStore vs PostgresStore
- User profiles and preferences
- Knowledge base patterns

### Advanced Patterns

Implement advanced features:

**Error Handling**: `resources/advanced/error-handling-retry.md`
- Try-catch patterns in nodes
- Retry logic with backoff
- Fallback chains
- Error routing strategies

**Human-in-the-Loop**: `resources/advanced/interrupts-hitl.md`
- interrupt() function (LangGraph 1.0)
- interrupt_before/after patterns
- Approval workflows
- State updates during interrupts

**Subgraphs**: `resources/advanced/subgraphs.md`
- Subgraph design patterns
- State passing between graphs
- Nested subgraphs
- Modular graph composition

### Integration

Connect to external systems:

**REST APIs**: `resources/integration/external-apis.md`
- HTTP request patterns
- Authentication strategies
- Error handling for API calls
- Rate limiting

### Project Structure

Act project conventions and patterns:

**Act Conventions**: `resources/project/act-conventions.md`
- File locations and structure
- Naming conventions
- Required inheritance (BaseNode, BaseGraph)
- Module organization

**Architecture to Code**: `resources/project/from-architecture-to-code.md`
- Interpreting CLAUDE.md specs
- Step-by-step implementation
- Translation patterns
- Validation checklist

### Quick Reference

**Quick Reference**: `resources/quick-reference.md`
- Common code snippets
- Import statements
- Decision trees
- Frequently used patterns

## Usage Pattern

1. **Identify what you need to implement**
2. **Find the relevant resource in the guide above**
3. **Read the entire resource** (all necessary information is included)
4. **Write your code**
5. **Repeat steps 1-4 for additional features**

## LangGraph 1.0 Based

All resources are written for LangGraph 1.0:
- StateGraph with typed schemas
- Checkpointer and Store APIs
- interrupt() from langgraph.types
- Send API and Command API
- BaseNode/AsyncBaseNode (Act custom)

---

**Remember:** Each resource is independent and complete. Read the relevant resource when you need it - it contains everything you need to know for that topic.
