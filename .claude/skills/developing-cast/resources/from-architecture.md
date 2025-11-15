# Translating CLAUDE.md to Implementation

## When to Use This Resource

Read this when you have CLAUDE.md from architecting-act and need to translate architecture to code.

## Translation Process

### Step 1: Review CLAUDE.md Architecture

**Read these sections:**
- State Schema
- Nodes and their responsibilities
- Edge routing logic
- Tools needed
- Memory requirements

### Step 2: Implement State Schema

**From CLAUDE.md state design:**
```markdown
# In CLAUDE.md
State Schema:
- messages: list of conversation messages (accumulate)
- current_task: string describing current task
- results: dict of processing results
- iteration_count: counter for loop control
```

**To state.py:**
```python
# File: casts/my_agent/state.py
from typing import TypedDict, Annotated
from operator import add
from langchain_core.messages import BaseMessage

class MyAgentState(TypedDict):
    """State for MyAgent cast."""
    messages: Annotated[list[BaseMessage], add]  # Accumulate
    current_task: str
    results: dict
    iteration_count: Annotated[int, add]  # Accumulate
```

**Resource:** `01-core/state.md`

### Step 3: Implement Nodes

**From CLAUDE.md nodes:**
```markdown
# In CLAUDE.md
Nodes:
1. StartNode: Initialize state
2. ProcessNode: Process task with LLM
3. ToolNode: Execute tools
4. ReviewNode: Check results
```

**To nodes.py:**
```python
# File: casts/my_agent/nodes.py
from casts.base_node import BaseNode

class StartNode(BaseNode):
    """Initialize agent state."""
    def execute(self, state: MyAgentState) -> dict:
        return {"iteration_count": 0}

class ProcessNode(BaseNode):
    """Process task with LLM."""
    def __init__(self, model, **kwargs):
        super().__init__(**kwargs)
        self.model = model

    def execute(self, state: MyAgentState) -> dict:
        messages = state["messages"]
        response = self.model.invoke(messages)
        return {
            "messages": [response],
            "iteration_count": 1
        }

# ... implement other nodes
```

**Resource:** `01-core/nodes.md`

### Step 4: Implement Routing Logic

**From CLAUDE.md edges:**
```markdown
# In CLAUDE.md
Routing Logic:
- After ProcessNode:
  - If has tool_calls → route to ToolNode
  - If iteration_count >= 10 → END
  - Otherwise → END
- After ToolNode → back to ProcessNode
```

**To conditions.py:**
```python
# File: casts/my_agent/conditions.py
from langchain_core.messages import AIMessage

def should_continue(state: MyAgentState) -> str:
    """Route after ProcessNode."""
    # Check iteration limit
    if state.get("iteration_count", 0) >= 10:
        return "end"

    # Check tool calls
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "continue"

    return "end"
```

**Resource:** `01-core/edges.md`

### Step 5: Create Tools

**From CLAUDE.md tools:**
```markdown
# In CLAUDE.md
Tools Needed:
1. search_database: Search knowledge base
2. calculator: Perform calculations
```

**To modules/tools/:**
```python
# File: modules/tools/search.py
from langchain_core.tools import tool

@tool
def search_database(query: str) -> list:
    """Search knowledge base for information."""
    # Implementation
    return results

# File: modules/tools/calculator.py
@tool
def calculator(operation: str, a: float, b: float) -> float:
    """Perform arithmetic operations."""
    # Implementation
    return result
```

**Resource:** `02-tools/creating-tools.md`

### Step 6: Build Graph

**From all above components:**
```python
# File: casts/my_agent/graph.py
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from casts.base_graph import BaseGraph
from casts.my_agent.state import MyAgentState
from casts.my_agent.nodes import StartNode, ProcessNode
from casts.my_agent.conditions import should_continue
from modules.tools import search_database, calculator

class MyAgentGraph(BaseGraph):
    """MyAgent implementation graph."""

    def __init__(self, model, checkpointer=None):
        super().__init__()
        self.model = model
        self.checkpointer = checkpointer or MemorySaver()
        self.tools = [search_database, calculator]

    def build(self):
        builder = StateGraph(MyAgentState)

        # Instantiate nodes
        start = StartNode()
        process = ProcessNode(self.model.bind_tools(self.tools))

        # Add nodes
        builder.add_node("start", start)
        builder.add_node("process", process)
        builder.add_node("tools", ToolNode(self.tools))

        # Add edges (from CLAUDE.md routing logic)
        builder.set_entry_point("start")
        builder.add_edge("start", "process")

        builder.add_conditional_edges(
            "process",
            should_continue,
            {"continue": "tools", "end": END}
        )

        builder.add_edge("tools", "process")

        return builder.compile(checkpointer=self.checkpointer)
```

**Resource:** `01-core/graph.md`

### Step 7: Add Memory (If Specified)

**From CLAUDE.md memory requirements:**
```markdown
# In CLAUDE.md
Memory:
- Long-term: User preferences in Store
```

**Implement in node:**
```python
from langgraph.runtime import Runtime

class UserPrefNode(BaseNode):
    def execute(
        self,
        state: MyAgentState,
        runtime: Runtime = None,
        **kwargs
    ) -> dict:
        if runtime and runtime.store:
            user_id = state.get("user_id")
            prefs = runtime.store.get(("user", user_id), "prefs")
            return {"preferences": prefs}
        return {}
```

**Resource:** `03-memory/long-term-memory.md`

## Checklist: CLAUDE.md → Code

- [ ] State schema implemented in state.py
- [ ] All nodes implemented in nodes.py
- [ ] Routing logic in conditions.py
- [ ] Tools created in modules/tools/
- [ ] Graph built in graph.py
- [ ] Memory implemented (if needed)
- [ ] Interrupts added (if approval workflows)
- [ ] Error handling in nodes
- [ ] Tests written

## Common Translation Patterns

**CLAUDE.md says "accumulate" → Use reducer:**
```python
field: Annotated[list, add]
```

**CLAUDE.md says "approval workflow" → Use interrupts:**
```python
from langgraph.types import interrupt
approval = interrupt("Review needed")
```

**CLAUDE.md says "loop until done" → Add iteration check:**
```python
def should_continue(state):
    if state["iteration_count"] >= max_iterations:
        return "end"
```

**CLAUDE.md says "multi-agent" → Use subgraphs:**
```python
specialist_graph = SpecialistGraph().build()
builder.add_node("specialist", specialist_graph)
```

## Example: Complete Translation

**CLAUDE.md:**
```markdown
# Research Agent

State:
- messages: conversation history (accumulate)
- query: current research query
- findings: list of findings (accumulate)

Nodes:
1. StartNode: Initialize
2. ResearchNode: Use LLM with search tool
3. SynthesizeNode: Combine findings

Routing:
- Start → Research → Synthesize → END

Tools:
- search_web: Search internet
```

**Implementation:**
```python
# state.py
class ResearchAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add]
    query: str
    findings: Annotated[list[dict], add]

# nodes.py
class StartNode(BaseNode):
    def execute(self, state) -> dict:
        return {"findings": []}

class ResearchNode(BaseNode):
    def __init__(self, model, **kwargs):
        super().__init__(**kwargs)
        self.model = model

    def execute(self, state) -> dict:
        # Implementation
        pass

# modules/tools/search.py
@tool
def search_web(query: str) -> str:
    """Search internet."""
    pass

# graph.py
class ResearchAgentGraph(BaseGraph):
    def build(self):
        builder = StateGraph(ResearchAgentState)
        builder.add_node("start", StartNode())
        builder.add_node("research", ResearchNode(model))
        builder.add_node("synthesize", SynthesizeNode())

        builder.set_entry_point("start")
        builder.add_edge("start", "research")
        builder.add_edge("research", "synthesize")
        builder.add_edge("synthesize", END)

        return builder.compile()
```

## Tips

1. **Start with state** - Everything flows from state design
2. **Implement nodes one at a time** - Test each independently
3. **Add edges last** - Once nodes work, connect them
4. **Use CLAUDE.md as spec** - It's your reference document
5. **Follow Act conventions** - Tools in modules/tools, inherit base classes

## References

- All implementation resources in SKILL.md
- Example: `quick-reference.md` for syntax
