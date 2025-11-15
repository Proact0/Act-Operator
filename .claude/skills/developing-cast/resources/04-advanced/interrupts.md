# Interrupts (Human-in-the-Loop)

## When to Use This Resource

Read this for approval workflows, human review steps, or pausing graph execution.

## Key Concept

**Interrupt:** Pauses graph execution, saves state, waits for human input/approval before resuming.

**Requires:** Checkpointer + thread_id

## interrupt() Function (Recommended)

```python
from langgraph.types import interrupt
from casts.base_node import BaseNode

class ReviewNode(BaseNode):
    def execute(self, state: MyState) -> dict:
        # Present data for review
        data_to_review = state["results"]

        # Pause here and wait for human input
        human_feedback = interrupt(
            f"Please review: {data_to_review}"
        )

        # Resume with feedback
        return {"approved": human_feedback == "approve"}
```

**Invocation:**
```python
config = {"configurable": {"thread_id": "123"}}

# First call: stops at interrupt
result = graph.invoke({"results": "data"}, config)
# Returns immediately with interrupt state

# Human reviews, then resume with input
from langgraph.types import Command
result = graph.invoke(
    Command(resume="approve"),  # Human's decision
    config
)
# Continues execution
```

## interrupt_before/after (Alternative)

```python
# Compile with interrupt points
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["review_node"],  # Pause before this node
)

# Or pause after node
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_after=["sensitive_operation"],
)
```

**Invocation:**
```python
config = {"configurable": {"thread_id": "123"}}

# Stops before review_node
result = graph.invoke({"task": "Review this"}, config)

# Check state
state = graph.get_state(config)
print(state.next)  # ["review_node"]

# Resume execution
graph.invoke(None, config)  # Continues
```

## Common Patterns

### Approval Gate

```python
class ApprovalNode(BaseNode):
    def execute(self, state) -> dict:
        decision = interrupt({
            "action": state["action"],
            "requires_approval": True
        })

        if decision != "approved":
            return {"status": "rejected"}

        return {"status": "approved", "proceed": True}
```

### Human Input Collection

```python
class InputNode(BaseNode):
    def execute(self, state) -> dict:
        user_input = interrupt("Enter missing information:")
        return {"user_provided": user_input}
```

### Review with Options

```python
class ChoiceNode(BaseNode):
    def execute(self, state) -> dict:
        choice = interrupt({
            "question": "Choose action:",
            "options": ["approve", "reject", "modify"]
        })

        return {"choice": choice}
```

## Resume Patterns

### Resume with Command

```python
from langgraph.types import Command

# Resume with value
graph.invoke(Command(resume="approved"), config)

# Resume with updates
graph.invoke(
    Command(resume={"status": "approved", "notes": "Looks good"}),
    config
)
```

### Resume with State Update

```python
# Update state manually
graph.update_state(
    config,
    {"human_decision": "approved"}
)

# Then resume
graph.invoke(None, config)
```

## Decision Framework

```
Need human approval?
  → Use interrupt() in approval node

Pause before sensitive operation?
  → interrupt_before=["node_name"]

Pause after operation to review results?
  → interrupt_after=["node_name"]

Multiple review points?
  → Use interrupt() in multiple nodes

Need structured input from human?
  → interrupt(structured_data)
```

## Common Mistakes

### ❌ No Checkpointer

```python
# BAD: Interrupt without checkpointer
graph = builder.compile()  # No checkpointer!
```

**Fix:**
```python
# GOOD
graph = builder.compile(checkpointer=MemorySaver())
```

### ❌ No thread_id

```python
# BAD
result = graph.invoke(input)  # Can't resume without thread_id
```

**Fix:**
```python
# GOOD
config = {"configurable": {"thread_id": "123"}}
result = graph.invoke(input, config)
```

## References

- Checkpointers: `03-memory/checkpointers.md`
- Nodes: `01-core/nodes.md`
