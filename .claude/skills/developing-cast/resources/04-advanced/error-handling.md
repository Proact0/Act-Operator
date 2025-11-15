# Error Handling and Retry Logic

## When to Use This Resource

Read this for handling failures, implementing retry strategies, or building fault-tolerant casts.

## Key Patterns

### Pattern 1: Try-Except in Nodes

```python
from casts.base_node import BaseNode

class RobustNode(BaseNode):
    def execute(self, state) -> dict:
        try:
            result = self.risky_operation(state)
            return {"result": result, "error": None}

        except ValueError as e:
            self.log("Validation error", error=str(e))
            return {
                "result": None,
                "error": str(e),
                "error_type": "validation"
            }

        except Exception as e:
            self.log("Unexpected error", error=str(e))
            return {
                "result": None,
                "error": str(e),
                "error_type": "unknown"
            }
```

### Pattern 2: Retry with Counter

```python
class RetryNode(BaseNode):
    def __init__(self, max_retries=3, **kwargs):
        super().__init__(**kwargs)
        self.max_retries = max_retries

    def execute(self, state) -> dict:
        retry_count = state.get("retry_count", 0)

        if retry_count >= self.max_retries:
            return {"error": "Max retries exceeded", "failed": True}

        try:
            result = self.attempt_operation(state)
            return {"result": result, "retry_count": 0}

        except Exception as e:
            return {
                "error": str(e),
                "retry_count": retry_count + 1,
                "should_retry": True
            }
```

**With conditional edge:**
```python
def should_retry(state) -> str:
    if state.get("should_retry") and state.get("retry_count", 0) < 3:
        return "retry"
    elif state.get("failed"):
        return "error_handler"
    else:
        return "success"

builder.add_conditional_edges(
    "operation",
    should_retry,
    {"retry": "operation", "success": "next_step", "error_handler": "handle_error"}
)
```

### Pattern 3: Exponential Backoff

```python
import time

class BackoffNode(BaseNode):
    def execute(self, state) -> dict:
        retry_count = state.get("retry_count", 0)
        base_delay = 2  # seconds

        if retry_count > 0:
            delay = base_delay ** retry_count  # 2, 4, 8, 16...
            self.log(f"Waiting {delay}s before retry")
            time.sleep(min(delay, 60))  # Cap at 60s

        try:
            result = self.api_call(state)
            return {"result": result, "retry_count": 0}

        except Exception as e:
            return {"error": str(e), "retry_count": retry_count + 1}
```

### Pattern 4: Fallback Strategy

```python
class FallbackNode(BaseNode):
    def execute(self, state) -> dict:
        # Try primary method
        try:
            return {"result": self.primary_method(state)}
        except Exception as e1:
            self.log("Primary method failed", error=str(e1))

            # Try fallback method
            try:
                return {"result": self.fallback_method(state)}
            except Exception as e2:
                self.log("Fallback failed", error=str(e2))
                return {"error": f"All methods failed: {e1}, {e2}"}
```

### Pattern 5: Circuit Breaker

```python
class CircuitBreakerNode(BaseNode):
    def __init__(self, failure_threshold=5, **kwargs):
        super().__init__(**kwargs)
        self.failure_threshold = failure_threshold

    def execute(self, state) -> dict:
        failure_count = state.get("consecutive_failures", 0)

        # Circuit open: skip operation
        if failure_count >= self.failure_threshold:
            return {
                "error": "Circuit breaker open",
                "circuit_open": True
            }

        # Attempt operation
        try:
            result = self.operation(state)
            return {
                "result": result,
                "consecutive_failures": 0,  # Reset on success
                "circuit_open": False
            }

        except Exception as e:
            return {
                "error": str(e),
                "consecutive_failures": failure_count + 1
            }
```

## Checkpointer for Error Recovery

```python
# Graph with checkpoints
graph = builder.compile(checkpointer=PostgresSaver(...))

config = {"configurable": {"thread_id": "123"}}

try:
    result = graph.invoke(input, config)
except Exception as e:
    # State saved at last checkpoint
    # Can inspect and retry
    state = graph.get_state(config)
    print(f"Failed at: {state.next}")

    # Retry from checkpoint
    result = graph.invoke(None, config)
```

## Common Patterns

### Tool Error Handling

```python
from langchain_core.messages import ToolMessage

# In custom ToolNode
for tool_call in tool_calls:
    try:
        result = tool.invoke(tool_call["args"])
        messages.append(ToolMessage(content=str(result), ...))
    except Exception as e:
        messages.append(
            ToolMessage(
                content=f"Error: {e}",
                is_error=True,
                ...
            )
        )
```

### Validation Errors

```python
class ValidateNode(BaseNode):
    def execute(self, state) -> dict:
        data = state["input_data"]

        # Validate
        errors = []
        if not data.get("required_field"):
            errors.append("Missing required_field")
        if data.get("value", 0) < 0:
            errors.append("Value must be positive")

        if errors:
            return {"validation_errors": errors, "valid": False}

        return {"valid": True}
```

## Decision Framework

```
Transient errors (network, rate limits)?
  → Retry with exponential backoff

Validation errors?
  → Return error in state, route to error handler

Multiple failure methods?
  → Fallback strategy

Persistent failures?
  → Circuit breaker pattern

Need to inspect failure state?
  → Use checkpointer

Want to resume after fixing issue?
  → Checkpointer + manual state update
```

## Common Mistakes

### ❌ Swallowing Errors Silently

```python
# BAD
try:
    result = operation()
except:
    pass  # Error lost!
```

**Fix:**
```python
# GOOD
try:
    result = operation()
except Exception as e:
    self.log("Operation failed", error=str(e))
    return {"error": str(e)}
```

### ❌ Infinite Retry Loop

```python
# BAD
while True:
    try:
        return operation()
    except:
        continue  # Loops forever!
```

**Fix:**
```python
# GOOD
max_retries = 3
for attempt in range(max_retries):
    try:
        return operation()
    except Exception as e:
        if attempt == max_retries - 1:
            raise
```

## Act Project Conventions

⚠️ **Error handling:**
- Return errors in state (don't raise in execute unless fatal)
- Use conditional edges to route on error
- Log errors with self.log()

⚠️ **Retry logic:**
- Store retry_count in state
- Implement max retries
- Use exponential backoff for external APIs

## References

- Nodes: `01-core/nodes.md`
- Edges: `01-core/edges.md`
- Checkpointers: `03-memory/checkpointers.md`
