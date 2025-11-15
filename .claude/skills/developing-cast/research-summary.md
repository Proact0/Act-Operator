# LangGraph 1.0 Research Summary

## Research Completed: 2025-11-15

### Sources Reviewed:
- LangChain/LangGraph official documentation (limited access via web search)
- LangGraph cheatsheet (GitHub gist)
- Multiple 2025 tutorials (Real Python, DataCamp, Analytics Vidhya, Medium)
- LangChain blog announcements
- GitHub issues and discussions

---

## Major Implementation Areas Discovered

### 1. Core Components (Always Needed - Frequent Access)

#### State Management
- **TypedDict** for state schema definition
- **Annotated fields** with reducers: `Annotated[list, operator.add]` for append-only
- Plain fields for overwrite semantics
- State channels and update patterns
- **Token target: < 2k** (frequently accessed)

#### Node Patterns
- Function-based nodes: `def node(state: StateType) -> dict`
- Async nodes: `async def node(state: StateType) -> dict`
- **BaseNode inheritance** (Act-specific OOP pattern)
- `execute(self, state)` method signature
- **Token target: < 2k** (frequently accessed)

#### Edge Patterns
- Static edges: `add_edge(source, target)`
- Conditional edges: `add_conditional_edges(source, router_fn, mapping)`
- Dynamic routing: router function `(state) -> str`
- **conditions.py** for routing logic (Act convention)
- **Token target: < 2k** (frequently accessed)

#### Graph Construction
- `StateGraph(StateType)` instantiation
- `add_node(name, function)`
- `set_entry_point(name)` or `set_entry_point(START)`
- `add_edge()` and `add_conditional_edges()`
- `compile(checkpointer=...)` to create runnable
- `invoke(state)` or `ainvoke(state)` for execution
- **Token target: < 2k** (frequently accessed)

---

### 2. Tools (Common - Frequent Access)

#### Tool Creation
- **@tool decorator** for creating tools
- Function signature becomes tool schema
- Docstrings become tool descriptions
- **Location: modules/tools/** (Act convention - STRICT)
- **Token target: < 2k** (frequently accessed)

#### Tool Integration
- **bind_tools(tools)** to attach tools to LLM
- **ToolNode** for executing tool calls
- **ToolRuntime** for context access (Act-specific pattern)
- Tool composition patterns
- Error handling in tools
- **Token target: < 2k** (frequently accessed)

---

### 3. Memory & Persistence (Common - Moderate Access)

#### Short-term Memory (Thread-Scoped)
- Implemented via **checkpointers**
- **MemorySaver**: in-memory, temporary
- **SqliteSaver**: SQLite-backed, persistent across restarts
- PostgresSaver: production-grade (LangGraph Cloud)
- Checkpoint saves after each super-step
- **Token target: < 4k**

#### Long-term Memory (Cross-Thread)
- **Store API** for cross-session persistence
- **InMemoryStore**: development/testing
- **MongoDBStore**: MongoDB-backed with vector search
- **RedisStore**: Redis-backed
- **Namespaces** for organizing memories
- **Token target: < 4k**

---

### 4. Advanced Features (Occasional Access)

#### Interrupts (Human-in-the-Loop)
- **interrupt() function** (recommended since v0.2.31)
- Replaces older NodeInterrupt and static breakpoints
- Approval patterns: `is_approved = interrupt({...})`
- Resume with `Command(goto=...)`
- Use cases: approval, rejection, routing
- **Token target: < 4k**

#### Streaming
- **astream_events()** method (async)
- Token streaming: filter `on_chat_model_stream` events
- State streaming: track node execution
- Custom events: user-defined signals
- Requires streaming-enabled LLM
- **Token target: < 4k**

#### Subgraphs
- Compose graphs as nodes in other graphs
- **Shared state**: pass compiled subgraph to add_node
- **Different state**: transform state in/out in wrapper function
- Multi-agent teams with separate state
- Nested graphs (parent → child → grandchild)
- **Token target: < 4k**

#### MCP Integration
- **langchain-mcp-adapters** package
- **MultiServerMCPClient** manages connections
- Converts MCP tools to LangChain-compatible tools
- Transport methods: stdio, streamable_http, SSE
- **MCP Adapter** (NOT Server) - client-side integration
- **Token target: < 4k**

---

### 5. Cross-Cutting Patterns (Occasional Access)

#### Async Patterns
- `async def` node functions
- `await model.ainvoke(messages)`
- **ainvoke()** vs **invoke()** on graph
- Critical: async checkpointer requires ainvoke()
- `asyncio.gather()` for parallel execution
- `asyncio.to_thread()` for wrapping sync functions
- **Token target: < 4k**

#### Error Handling & Retries
- Try/except in node functions
- Retry patterns with max_retries
- `asyncio.wait_for()` for timeouts
- Error propagation through state
- ToolExceptions and error recovery
- **Token target: < 4k**

---

## Act Project Conventions (Critical - Frequent Access)

### Strict Requirements:
1. **Tools location**: ONLY in `modules/tools/` - NO exceptions
2. **Node inheritance**: All nodes MUST inherit from `casts/base_node.py`
3. **Graph inheritance**: All graphs MUST inherit from `casts/base_graph.py`
4. **Routing logic**: Use `conditions.py` for conditional edge functions
5. **OOP patterns**: Always class-based, never standalone functions
6. **Memory placement**: Depends on use case:
   - In-session: State or checkpointers
   - Cross-session: Store
   - Tool-specific: Within tool using ToolRuntime

**Token target: < 2k** (frequently accessed, critical for compliance)

---

## Resource Structure Design

### Optimized for Token Efficiency and Navigation

```
resources/
├── core/                           # Always needed (< 2k each)
│   ├── state-management.md         # State schemas, reducers, channels
│   ├── node-patterns.md            # Node implementation, BaseNode OOP
│   ├── edge-patterns.md            # Static, conditional, dynamic routing
│   └── graph-construction.md       # Building and compiling graphs
├── tools/                          # Common (< 2k each)
│   ├── tool-creation.md            # @tool decorator, schemas
│   └── tool-runtime.md             # Act-specific ToolRuntime patterns
├── memory/                         # Moderate use (< 4k each)
│   ├── short-term-memory.md        # Checkpointers, thread-scoped
│   └── long-term-memory.md         # Store, cross-session
├── advanced/                       # Occasional (< 4k each)
│   ├── interrupts.md               # interrupt(), human-in-the-loop
│   ├── streaming.md                # astream_events, tokens
│   ├── subgraphs.md                # Composition, multi-agent
│   └── mcp-integration.md          # MCP Adapter patterns
└── patterns/                       # Cross-cutting (< 4k each)
    ├── async-patterns.md           # async/await, ainvoke
    ├── error-handling.md           # Retries, timeouts, recovery
    └── act-conventions.md          # Act-specific rules (< 2k)
```

### Resource Categorization Logic:

**Core (< 2k tokens):**
- Used in almost every cast implementation
- Need quick access
- Should be scannable
- Examples: state, nodes, edges, graph

**Tools (< 2k tokens):**
- Very common but self-contained
- Act-specific conventions are critical
- Frequently referenced during development

**Memory (< 4k tokens):**
- Important but not always needed
- Can be more detailed
- Decision frameworks included

**Advanced (< 4k tokens):**
- Specialized features
- Used occasionally
- Can include more comprehensive examples

**Patterns (< 4k tokens, except act-conventions < 2k):**
- Cross-cutting concerns
- Apply across multiple areas
- Act conventions critical for compliance

---

## Key Insights for Skill Design

### 1. Decision Frameworks Are Critical
Developers need clear "when to use X vs Y" guidance:
- State reducers vs plain fields
- Short-term vs long-term memory
- Interrupts vs conditional edges
- Sync vs async nodes

### 2. Act Conventions Must Be Enforced
- Tools ONLY in modules/tools (no exceptions)
- Always inherit from base classes
- OOP patterns throughout
- These are non-negotiable

### 3. Code Examples Should Be Minimal
- Show the pattern, not exhaustive implementations
- Always demonstrate base class inheritance
- Focus on decision-making, not mechanics
- Include only when concept requires code

### 4. Integration with CLAUDE.md
CLAUDE.md (from architecting-act) contains architecture:
- developing-cast translates architecture → implementation
- SKILL.md should guide: "For X in CLAUDE.md, see Y resource"
- Seamless workflow: design → implement

### 5. Common Mistakes Must Be Highlighted
From research, common issues:
- Using invoke with async checkpointer (hangs)
- Forgetting to await ainvoke
- Tools outside modules/tools
- Not inheriting from base classes
- Confusing NodeInterrupt (deprecated) with interrupt() (current)

---

## Next Steps

1. **RED Phase**: Run baseline tests without skill
   - Test pressure scenarios with subagent
   - Document gaps, confusions, errors
   - Identify what agents struggle with

2. **GREEN Phase**: Write minimal skill
   - SKILL.md index (< 5k tokens)
   - Core resources (< 2k each)
   - Tools resources (< 2k each)
   - Advanced resources (< 4k each)
   - All with Act conventions

3. **REFACTOR Phase**: Close loopholes
   - Test with skill present
   - Identify remaining gaps
   - Update resources
   - Verify token limits
