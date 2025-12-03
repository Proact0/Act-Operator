---
name: developing-cast
description: Use when implementing cast from CLAUDE.md, building nodes/agents/tools from scratch, or need LangGraph patterns for state/edge/graph - provides systematic workflow from architecture to working code
---

# Developing Cast

Implement LangGraph casts following Act-Operator patterns.

## When to Use

- Have CLAUDE.md and need to implement
- Building nodes, agents, tools, or graphs
- Need LangGraph implementation patterns

## When NOT to Use

- Architecture design → `architecting-act`
- Project setup → `engineering-act`
- Testing → `testing-cast`

---

## Mode 1: From Architecture (CLAUDE.md exists)

**Use:** [from-architecture-to-code.md](usage/from-architecture-to-code.md)

1. Read CLAUDE.md → 2. Implement: state → other modules → nodes → conditions(if need) → graph

---

## Mode 2: Direct Implementation

### Core Components

| Use when... | Resource |
|-------------|----------|
| defining graph state with TypedDict | [core/state.md](usage/core/state.md) |
| implementing sync/async node classes | [core/node.md](usage/core/node.md) |
| setting up edges or conditional routing | [core/edge.md](usage/core/edge.md) |
| assembling StateGraph and compiling | [core/graph.md](usage/core/graph.md) |
| reusing graphs as subgraphs | [core/subgraph.md](usage/core/subgraph.md) |

### Prompts & Messages

| Use when... | Resource |
|-------------|----------|
| creating System/Human/AI/Tool messages | [prompts/message-types.md](usage/prompts/message-types.md) |
| handling image/audio/PDF inputs | [prompts/multimodal.md](usage/prompts/multimodal.md) |

### Models & Agents

| Use when... | Resource |
|-------------|----------|
| choosing between OpenAI/Anthropic/Google | [models/select-chat-models.md](usage/models/select-chat-models.md) |
| configuring model (temperature, tokens) | [models/standalone-model.md](usage/models/standalone-model.md) |
| need model to return Pydantic schema | [models/structured-output.md](usage/models/structured-output.md) |
| creating agent with tools | [agents/configuration.md](usage/agents/configuration.md) |
| need agent to return Pydantic schema | [agents/structured-output.md](usage/agents/structured-output.md) |

### Tools

| Use when... | Resource |
|-------------|----------|
| creating simple tool with @tool | [tools/basic-tool.md](usage/tools/basic-tool.md) |
| tool needs complex Pydantic inputs | [tools/tool-with-complex-inputs.md](usage/tools/tool-with-complex-inputs.md) |
| tool needs to read/write state or store | [tools/access-context.md](usage/tools/access-context.md) |

### Memory

| Use when... | Resource |
|-------------|----------|
| adding conversation memory to agent | [memory/short-term/add-to-agent.md](usage/memory/short-term/add-to-agent.md) |
| customizing agent memory storage | [memory/short-term/customize-agent-memory.md](usage/memory/short-term/customize-agent-memory.md) |
| trimming/deleting/summarizing history | [memory/short-term/manage-conversations.md](usage/memory/short-term/manage-conversations.md) |
| accessing memory from middleware/tools | [memory/short-term/access-and-modify-memory.md](usage/memory/short-term/access-and-modify-memory.md) |
| persisting data across sessions (Store) | [memory/long-term/memory-storage.md](usage/memory/long-term/memory-storage.md) |
| accessing Store from within tools | [memory/long-term/in-tools.md](usage/memory/long-term/in-tools.md) |

### Middleware - Reliability

| Use when... | Resource |
|-------------|----------|
| LLM calls fail intermittently | [middlewares/provider-agnostic/model-retry.md](usage/middlewares/provider-agnostic/model-retry.md) |
| tool execution fails intermittently | [middlewares/provider-agnostic/tool-retry.md](usage/middlewares/provider-agnostic/tool-retry.md) |
| need backup model when primary fails | [middlewares/provider-agnostic/model-fallback.md](usage/middlewares/provider-agnostic/model-fallback.md) |

### Middleware - Safety & Control

| Use when... | Resource |
|-------------|----------|
| validating/blocking inappropriate content | [middlewares/provider-agnostic/guardrails.md](usage/middlewares/provider-agnostic/guardrails.md) |
| preventing infinite LLM call loops | [middlewares/provider-agnostic/model-call-limit.md](usage/middlewares/provider-agnostic/model-call-limit.md) |
| limiting tool calls to control costs | [middlewares/provider-agnostic/tool-call-limit.md](usage/middlewares/provider-agnostic/tool-call-limit.md) |
| requiring human approval at checkpoints | [middlewares/provider-agnostic/human-in-the-loop.md](usage/middlewares/provider-agnostic/human-in-the-loop.md) |

### Middleware - Tool Management

| Use when... | Resource |
|-------------|----------|
| dynamically selecting relevant tools | [middlewares/provider-agnostic/llm-tool-selector.md](usage/middlewares/provider-agnostic/llm-tool-selector.md) |
| emulating tools with LLM for testing | [middlewares/provider-agnostic/llm-tool-emulator.md](usage/middlewares/provider-agnostic/llm-tool-emulator.md) |
| agent needs persistent shell session | [middlewares/provider-agnostic/shell-tool.md](usage/middlewares/provider-agnostic/shell-tool.md) |
| agent needs to search files (glob/grep) | [middlewares/provider-agnostic/file-search.md](usage/middlewares/provider-agnostic/file-search.md) |
| agent needs task planning/tracking | [middlewares/provider-agnostic/to-do-list.md](usage/middlewares/provider-agnostic/to-do-list.md) |

### Middleware - Context

| Use when... | Resource |
|-------------|----------|
| modifying/removing messages at runtime | [middlewares/provider-agnostic/context-editing.md](usage/middlewares/provider-agnostic/context-editing.md) |
| auto-summarizing near token limits | [middlewares/provider-agnostic/summarization.md](usage/middlewares/provider-agnostic/summarization.md) |

### Middleware - Provider-Specific

| Use when... | Resource |
|-------------|----------|
| using OpenAI moderation API | [middlewares/provider-specific/openai.md](usage/middlewares/provider-specific/openai.md) |
| using Claude caching/bash/text-editor | [middlewares/provider-specific/anthropic.md](usage/middlewares/provider-specific/anthropic.md) |
| building custom before/after/wrap hooks | [middlewares/custom.md](usage/middlewares/custom.md) |

### Integrations

| Use when... | Resource |
|-------------|----------|
| converting text to embedding vectors | [integrations/embedding.md](usage/integrations/embedding.md) |
| using FAISS/Pinecone/Chroma stores | [integrations/vector-stores.md](usage/integrations/vector-stores.md) |
| splitting long documents into chunks | [integrations/text-spliter.md](usage/integrations/text-spliter.md) |

---

## Implementation Order

```
1. State (state.py)           # Foundation
   ↓
2. Dependencies modules       # models, tools, prompts, middlewares, agents, utils (if needed)
   ↓
3. Nodes (nodes.py)           # Business logic
   ↓
4. Conditions (conditions.py) # Routing (if needed)
   ↓
5. Graph (graph.py)           # Assembly
```

---

## Verification

- [ ] Files in order: state → deps → nodes → conditions → graph
- [ ] Node names lowercase in graph.py
- [ ] START/END imported from `langgraph.graph`
- [ ] Nodes added as instances
- [ ] Graph compiles

---

## Next Steps

1. **Test:** `testing-cast` skill
2. **Debug:** `uv run langgraph dev`
