# Interrupts & Human-in-the-Loop

## When to Use This Resource
Read this when implementing approval workflows, human review steps, or any pattern where execution should pause for human input.

## What are Interrupts?

**Interrupt** = Pausing graph execution at a specific point, waiting for human input, then resuming.

**Key use cases:**
- Approval workflows (before API calls, database changes)
- Human review (validate LLM outputs before proceeding)
- Data validation (human confirms data before processing)
- Escalation (complex cases need human decision)

**Requirements:**
- Must use checkpointer (to save state during pause)
- Thread-based execution (need thread_id to resume)

## Basic Interrupt Pattern

### Using interrupt_before

```python
from langgraph.checkpoint.sqlite import SqliteSaver

graph = builder.compile(
    checkpointer=SqliteSaver.from_conn_string("checkpoints.db"),
    interrupt_before=["approval_node"]  # Pause BEFORE this node executes
)

# First invocation - pauses before approval_node
config = {"configurable": {"thread_id": "request-123"}}
result = graph.invoke({"input": "Make API call"}, config=config)

# Check current state
state = graph.get_state(config)
print(f"Paused at: {state.next}")  # ['approval_node']

# Human reviews and approves...

# Resume execution
graph.invoke(None, config=config)  # Continues from pause point
```

### Using interrupt_after

```python
graph = builder.compile(
    checkpointer=SqliteSaver.from_conn_string("checkpoints.db"),
    interrupt_after=["data_fetch"]  # Pause AFTER this node completes
)

# Pauses after data_fetch finishes
result = graph.invoke({"input": "Fetch data"}, config=config)

# Human reviews fetched data in state...

# Continue
graph.invoke(None, config=config)
```

## Modern Pattern: interrupt() Function

**As of LangGraph 0.2.31**, use the `interrupt()` function for more control:

```python
from langgraph.graph import interrupt
from casts.base_node import BaseNode

class ApprovalNode(BaseNode):
    """Requests human approval before proceeding."""

    def execute(self, state: dict) -> dict:
        # Present information to human
        action = state.get("proposed_action")

        # Pause execution and request approval
        approval = interrupt(
            {
                "action": action,
                "message": "Please review and approve this action"
            }
        )

        # After resume, approval contains human's response
        if approval.get("approved"):
            return {"status": "approved", "notes": approval.get("notes")}
        else:
            return {"status": "rejected", "reason": approval.get("reason")}
```

**How it works:**
1. `interrupt()` pauses execution
2. Data passed to `interrupt()` saved in checkpointer
3. Human reviews data
4. Resume with `invoke({"approval": {"approved": True, ...}}, config)`
5. `interrupt()` returns the approval data

## Common Approval Patterns

### Pattern 1: Approve Before Critical Action

```python
class CriticalActionNode(BaseNode):
    def execute(self, state: dict) -> dict:
        # Prepare action details
        action_plan = {
            "type": "api_call",
            "endpoint": "/delete_user",
            "params": state.get("params")
        }

        # Request approval
        approval = interrupt({
            "action_plan": action_plan,
            "prompt": "Approve deletion?"
        })

        if not approval.get("approved"):
            return {"error": "Action rejected by human"}

        # Execute action
        result = execute_critical_action(action_plan)
        return {"result": result}
```

**Usage:**
```python
# Initial invoke - pauses for approval
graph.invoke({"params": {"user_id": 123}}, config=config)

# Check what's being requested
state = graph.get_state(config)
print(state.values.get("action_plan"))

# Approve
graph.invoke({"approval": {"approved": True, "notes": "Verified"}}, config=config)
```

### Pattern 2: Review and Edit Before Proceeding

```python
class DraftReviewNode(BaseNode):
    def execute(self, state: dict) -> dict:
        draft = state.get("draft_content")

        # Show draft to human for review/editing
        edited = interrupt({
            "draft": draft,
            "prompt": "Review and edit if needed"
        })

        # Human can modify the draft
        final_content = edited.get("content", draft)

        return {"final_content": final_content, "reviewed": True}
```

**Usage:**
```python
# Pauses with draft
graph.invoke({"draft_content": "..."}, config=config)

# Human edits
edited_draft = "... human edits ..."
graph.invoke({"approval": {"content": edited_draft}}, config=config)
```

### Pattern 3: Multi-Step Approval Chain

```python
builder.add_node("plan", plan_node)
builder.add_node("approve_plan", approve_plan_node)  # Interrupt
builder.add_node("execute", execute_node)
builder.add_node("approve_execution", approve_execution_node)  # Interrupt

builder.add_edge("plan", "approve_plan")
builder.add_edge("approve_plan", "execute")
builder.add_edge("execute", "approve_execution")
builder.add_edge("approve_execution", END)

graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["approve_plan", "approve_execution"]
)
```

## Updating State During Interrupt

Modify state before resuming:

```python
# Graph is paused
state = graph.get_state(config)

# Update state with human input
graph.update_state(
    config,
    {
        "approved": True,
        "approval_notes": "Looks good",
        "approved_by": "manager@company.com"
    }
)

# Resume
graph.invoke(None, config=config)
```

## Conditional Resume

Resume to different nodes based on approval:

```python
def should_continue(state: dict) -> str:
    if state.get("approved"):
        return "execute_action"
    else:
        return "notify_rejection"

builder.add_conditional_edges(
    "approval_node",
    should_continue,
    {"execute_action": "execute_action", "notify_rejection": "notify_rejection"}
)
```

## Timeout Handling

```python
from datetime import datetime, timedelta

class ApprovalWithTimeoutNode(BaseNode):
    def execute(self, state: dict, config=None, **kwargs) -> dict:
        # Check if this is a timeout scenario
        if "timeout_at" in state:
            if datetime.now() > state["timeout_at"]:
                return {"status": "timeout", "approved": False}

        # Normal approval flow
        approval = interrupt({
            "action": state.get("action"),
            "timeout_at": datetime.now() + timedelta(hours=24)
        })

        return {"approved": approval.get("approved")}
```

## Streaming Approval UI

```python
# Stream state during interrupt
for chunk in graph.stream({"input": "..."}, config=config, stream_mode="values"):
    # Send current state to UI
    if "approval_required" in chunk:
        display_approval_ui(chunk)
```

## Common Mistakes

❌ **No checkpointer with interrupts**
```python
# ❌ Won't work - interrupts need checkpointer
graph = builder.compile(interrupt_before=["node"])

# ✅ Include checkpointer
graph = builder.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["node"]
)
```

❌ **Not using thread_id**
```python
# ❌ Can't resume without thread_id
graph.invoke({"input": "..."})

# ✅ Use thread_id
config = {"configurable": {"thread_id": "request-123"}}
graph.invoke({"input": "..."}, config=config)
```

❌ **Resuming with new input when not needed**
```python
# ❌ Unnecessary new input can cause confusion
graph.invoke({"input": "new data"}, config=config)

# ✅ Resume without input (uses interrupted state)
graph.invoke(None, config=config)

# ✅ Or with approval data if using interrupt()
graph.invoke({"approval": {"approved": True}}, config=config)
```

## Production Patterns

### Pattern: Approval Queue System
```python
class ApprovalQueue:
    def __init__(self, graph):
        self.graph = graph
        self.pending = {}  # thread_id -> approval_data

    def submit_for_approval(self, data: dict) -> str:
        thread_id = str(uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        # Start execution - will pause at approval
        self.graph.invoke(data, config=config)

        # Get interrupt data
        state = self.graph.get_state(config)
        self.pending[thread_id] = state.values

        return thread_id

    def approve(self, thread_id: str, approval_data: dict):
        config = {"configurable": {"thread_id": thread_id}}
        self.graph.invoke(approval_data, config=config)
        del self.pending[thread_id]

    def reject(self, thread_id: str, reason: str):
        config = {"configurable": {"thread_id": thread_id}}
        self.graph.invoke({"approved": False, "reason": reason}, config=config)
        del self.pending[thread_id]
```

## References
- LangGraph Interrupts: https://docs.langchain.com/oss/python/langgraph/interrupts
- Related: `../memory/checkpoints-persistence.md` (required for interrupts)
- Related: `streaming.md` (streaming during interrupts)
