# Error Handling & Retry Patterns

## Table of Contents

- [When to Use This Resource](#when-to-use-this-resource)
- [Error Handling Strategies](#error-handling-strategies)
  - [Strategy 1: Try-Catch in Nodes](#strategy-1-try-catch-in-nodes)
  - [Strategy 2: Dedicated Error Handler Node](#strategy-2-dedicated-error-handler-node)
  - [Strategy 3: Retry with Backoff](#strategy-3-retry-with-backoff)
  - [Strategy 4: Fallback Chains](#strategy-4-fallback-chains)
- [Retry Patterns in Graph Structure](#retry-patterns-in-graph-structure)
  - [Pattern 1: Retry Loop with Counter](#pattern-1-retry-loop-with-counter)
  - [Pattern 2: Per-Node Retry Config](#pattern-2-per-node-retry-config)
- [Error Routing Patterns](#error-routing-patterns)
  - [Pattern 1: Error-Specific Routing](#pattern-1-error-specific-routing)
  - [Pattern 2: Circuit Breaker](#pattern-2-circuit-breaker)
- [Validation & Early Exit](#validation--early-exit)
- [Production Patterns](#production-patterns)
  - [Pattern 1: Comprehensive Error Context](#pattern-1-comprehensive-error-context)
  - [Pattern 2: Graceful Degradation](#pattern-2-graceful-degradation)
  - [Pattern 3: Error Aggregation](#pattern-3-error-aggregation)
- [Common Mistakes](#common-mistakes)
- [References](#references)

## When to Use This Resource
Read this when implementing resilient graphs, adding retry logic, handling failures gracefully, or building production-ready error handling.

## Error Handling Strategies

### Strategy 1: Try-Catch in Nodes

**When:** Single node might fail, want to handle locally.

```python
from casts.base_node import BaseNode

class RobustAPINode(BaseNode):
    """Calls API with error handling."""

    def execute(self, state) -> dict:
        try:
            result = call_external_api(state["query"])
            return {"result": result, "error": None, "status": "success"}

        except requests.Timeout:
            self.log("API timeout")
            return {"result": None, "error": "timeout", "status": "failed"}

        except requests.HTTPError as e:
            self.log(f"HTTP error: {e}")
            return {"result": None, "error": str(e), "status": "failed"}

        except Exception as e:
            self.log(f"Unexpected error: {e}")
            return {"result": None, "error": "unexpected", "status": "failed"}
```

**Pros:**
- ✅ Granular control
- ✅ Can recover immediately
- ✅ Error details in state

**Cons:**
- ❌ Repeated code if many nodes need same logic
- ❌ Harder to centralize error handling

### Strategy 2: Dedicated Error Handler Node

**When:** Want centralized error handling logic.

```python
class ErrorHandlerNode(BaseNode):
    """Handles errors from previous nodes."""

    def execute(self, state) -> dict:
        error = state.get("error")
        error_source = state.get("error_source")

        if not error:
            return {}  # No error to handle

        # Log error
        self.log(f"Error from {error_source}: {error}")

        # Decide recovery strategy
        if error == "timeout":
            return {"retry_count": state.get("retry_count", 0) + 1}
        elif error == "not_found":
            return {"use_fallback": True}
        else:
            return {"fatal_error": True}

# In graph
def should_handle_error(state: dict) -> str:
    if state.get("error"):
        return "error_handler"
    return "continue"

builder.add_conditional_edges(
    "api_call",
    should_handle_error,
    {"error_handler": "error_handler", "continue": "next_node"}
)
```

### Strategy 3: Retry with Backoff

**When:** Transient failures (network issues, rate limits).

```python
import time
from typing import Optional

class RetryNode(BaseNode):
    """Retries operation with exponential backoff."""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.max_retries = max_retries
        self.base_delay = base_delay

    def execute(self, state) -> dict:
        retries = 0

        while retries < self.max_retries:
            try:
                result = self.attempt_operation(state)
                return {"result": result, "retries": retries}

            except RetriableException as e:
                retries += 1
                if retries >= self.max_retries:
                    return {"error": f"Max retries exceeded: {e}"}

                delay = self.base_delay * (2 ** retries)  # Exponential backoff
                self.log(f"Retry {retries}/{self.max_retries} after {delay}s")
                time.sleep(delay)

        return {"error": "Max retries exceeded"}

    def attempt_operation(self, state: dict):
        """Override in subclass."""
        raise NotImplementedError
```

### Strategy 4: Fallback Chains

**When:** Multiple fallback options (try API A, then B, then local).

```python
class FallbackNode(BaseNode):
    """Tries multiple approaches in sequence."""

    def execute(self, state) -> dict:
        # Try primary approach
        try:
            result = self.primary_approach(state)
            return {"result": result, "method": "primary"}
        except Exception as e1:
            self.log(f"Primary failed: {e1}")

        # Try secondary
        try:
            result = self.secondary_approach(state)
            return {"result": result, "method": "secondary"}
        except Exception as e2:
            self.log(f"Secondary failed: {e2}")

        # Last resort
        try:
            result = self.fallback_approach(state)
            return {"result": result, "method": "fallback"}
        except Exception as e3:
            self.log(f"All approaches failed: {e3}")
            return {"error": "All fallbacks exhausted"}
```

## Retry Patterns in Graph Structure

### Pattern 1: Retry Loop with Counter

```python
# State tracks retry attempts
class GraphState(TypedDict):
    query: str
    result: Optional[str]
    retry_count: int

def should_retry(state: dict) -> str:
    """Decides whether to retry or give up."""
    if state.get("error") and state.get("retry_count", 0) < 3:
        return "retry"
    elif state.get("error"):
        return "give_up"
    else:
        return "success"

builder.add_node("attempt", AttemptNode())
builder.add_conditional_edges(
    "attempt",
    should_retry,
    {
        "retry": "attempt",  # Loop back
        "give_up": "error_handler",
        "success": "next_step"
    }
)
```

### Pattern 2: Per-Node Retry Config

**LangGraph supports `retry` parameter:**

```python
from langgraph.graph import StateGraph

builder = StateGraph(GraphState)

# Configure retry for specific node
builder.add_node(
    "flaky_api",
    flaky_node,
    retry={"retry_on": (requests.Timeout, requests.HTTPError), "max_attempts": 3}
)
```

**Supported retry config:**
- `max_attempts`: How many times to retry
- `retry_on`: Which exceptions trigger retry (tuple of exception types)
- `wait`: Delay between retries (seconds)

## Error Routing Patterns

### Pattern 1: Error-Specific Routing

```python
def route_by_error_type(state: dict) -> str:
    """Routes to different handlers based on error type."""
    error = state.get("error")

    if not error:
        return "success_path"
    elif error == "timeout":
        return "retry_handler"
    elif error == "not_found":
        return "fallback_data"
    elif error == "auth_error":
        return "reauth"
    else:
        return "fatal_error_handler"

builder.add_conditional_edges(
    "risky_node",
    route_by_error_type,
    {
        "success_path": "next_step",
        "retry_handler": "retry_node",
        "fallback_data": "fallback_node",
        "reauth": "auth_node",
        "fatal_error_handler": "error_handler"
    }
)
```

### Pattern 2: Circuit Breaker

**When:** Stop trying after repeated failures.

```python
class CircuitBreakerNode(BaseNode):
    """Implements circuit breaker pattern."""

    def __init__(self, failure_threshold: int = 5, **kwargs):
        super().__init__(**kwargs)
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.circuit_open = False

    def execute(self, state) -> dict:
        if self.circuit_open:
            return {"error": "Circuit breaker open", "circuit_open": True}

        try:
            result = self.perform_operation(state)
            self.failure_count = 0  # Reset on success
            return {"result": result}

        except Exception as e:
            self.failure_count += 1

            if self.failure_count >= self.failure_threshold:
                self.circuit_open = True
                self.log("Circuit breaker opened")

            return {"error": str(e), "circuit_open": self.circuit_open}
```

## Validation & Early Exit

```python
class ValidationNode(BaseNode):
    """Validates inputs before processing."""

    def execute(self, state) -> dict:
        # Validate required fields
        if "query" not in state or not state["query"]:
            return {"error": "Missing query", "valid": False}

        # Validate format
        if len(state["query"]) > 1000:
            return {"error": "Query too long", "valid": False}

        # All validations passed
        return {"valid": True, "error": None}

# Routing stops graph on validation failure
def check_validation(state: dict) -> str:
    if state.get("valid"):
        return "proceed"
    else:
        return END  # Stop graph immediately

builder.add_conditional_edges(
    "validate",
    check_validation,
    {"proceed": "process", END: END}
)
```

## Production Patterns

### Pattern 1: Comprehensive Error Context

```python
from datetime import datetime

class ErrorContextNode(BaseNode):
    def execute(self, state) -> dict:
        try:
            result = risky_operation(state)
            return {"result": result}

        except Exception as e:
            error_context = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "timestamp": datetime.now().isoformat(),
                "state_snapshot": state.copy(),
                "node_name": self.name,
                "traceback": traceback.format_exc()
            }

            # Log for monitoring
            logger.error(f"Error in {self.name}", extra=error_context)

            return {"error_context": error_context}
```

### Pattern 2: Graceful Degradation

```python
def route_with_degradation(state: dict) -> str:
    """Degrades gracefully through service levels."""
    error = state.get("error")

    if not error:
        return "full_service"
    elif state.get("retry_count", 0) < 2:
        return "retry"
    elif state.get("fallback_available"):
        return "limited_service"  # Degraded but functional
    else:
        return "error_response"  # Minimal error response

builder.add_conditional_edges(
    "service_node",
    route_with_degradation,
    {
        "full_service": "next_step",
        "retry": "service_node",
        "limited_service": "fallback_service",
        "error_response": "error_handler"
    }
)
```

### Pattern 3: Error Aggregation

```python
class ErrorAggregatorNode(BaseNode):
    """Collects errors from multiple parallel nodes."""

    def execute(self, state) -> dict:
        errors = []

        # Check each parallel branch
        for key in ["branch_a_error", "branch_b_error", "branch_c_error"]:
            if state.get(key):
                errors.append({"source": key, "error": state[key]})

        if errors:
            return {
                "has_errors": True,
                "error_summary": errors,
                "partial_success": len(errors) < 3
            }
        else:
            return {"has_errors": False}
```

## Common Mistakes

❌ **Not preserving error information**
```python
# ❌ Lost error details
except Exception:
    return {"error": True}

# ✅ Preserve error info
except Exception as e:
    return {"error": str(e), "error_type": type(e).__name__}
```

❌ **Infinite retry loops**
```python
# ❌ No limit
def should_retry(state):
    if state.get("error"):
        return "retry"  # Infinite loop!

# ✅ Add counter
def should_retry(state):
    if state.get("error") and state.get("retry_count", 0) < 3:
        return "retry"
    return "give_up"
```

❌ **Catching too broadly**
```python
# ❌ Hides bugs
try:
    result = operation()
except:  # Catches everything!
    return {"error": "failed"}

# ✅ Be specific
try:
    result = operation()
except (NetworkError, TimeoutError) as e:
    return {"error": str(e)}
# Let other exceptions propagate
```

## References
- Related: `../core/implementing-nodes.md` (error handling in nodes)
- Related: `../core/edge-patterns.md` (error routing)
- Related: `subgraphs.md` (error handling across subgraphs)
