# Error Handling

## When to Use This Resource
Read when implementing error handling, retries, timeouts, or production-ready error recovery.

---

## Why Error Handling Matters

**Production casts must handle:**
- API failures (network, rate limits)
- Tool errors (missing data, invalid input)
- LLM errors (context limits, timeout)
- State errors (missing fields, type mismatches)

**Without error handling:** One failure crashes entire graph

---

## Basic Try/Except in Nodes

### Simple Error Handling

```python
from casts.base_node import BaseNode

class RobustNode(BaseNode):
    """Node with error handling."""

    def execute(self, state: dict) -> dict:
        try:
            result = self.risky_operation(state)
            return {"result": result, "status": "success"}

        except Exception as e:
            self.log(f"Error: {e}")
            return {
                "result": None,
                "status": "error",
                "error_message": str(e)
            }

    def risky_operation(self, state):
        # Operation that might fail
        return state["data"] / state["divisor"]  # Might raise ZeroDivisionError
```

**Key principle:** Catch errors, return error state, don't crash graph

---

### Specific Exception Handling

```python
def execute(self, state: dict) -> dict:
    try:
        result = self.process(state)
        return {"result": result, "status": "success"}

    except ValueError as e:
        # Handle specific error type
        self.log(f"ValueError: {e}")
        return {"status": "invalid_input", "error": str(e)}

    except KeyError as e:
        # Missing state field
        self.log(f"Missing field: {e}")
        return {"status": "missing_data", "error": f"Missing {e}"}

    except Exception as e:
        # Catch-all for unexpected errors
        self.log(f"Unexpected error: {e}")
        return {"status": "unknown_error", "error": str(e)}
```

---

## Error Handling in Tools

### Tool with Error Handling

```python
# File: casts/my_cast/modules/tools/web_search.py

from langchain_core.tools import tool

@tool
def web_search(query: str) -> dict:
    """Searches the web with error handling.

    Args:
        query: Search query

    Returns:
        Results or error dict
    """
    import requests

    try:
        response = requests.get(
            "https://api.search.com/search",
            params={"q": query},
            timeout=10  # Timeout after 10 seconds
        )
        response.raise_for_status()  # Raises for 4xx/5xx errors

        return {
            "status": "success",
            "results": response.json()
        }

    except requests.Timeout:
        return {"status": "timeout", "error": "Search timed out"}

    except requests.HTTPError as e:
        return {"status": "http_error", "error": f"HTTP {e.response.status_code}"}

    except Exception as e:
        return {"status": "error", "error": str(e)}
```

---

## Retry Patterns

### Simple Retry with Backoff

```python
import time

class RetryNode(BaseNode):
    """Node with retry logic."""

    def __init__(self, max_retries=3):
        super().__init__()
        self.max_retries = max_retries

    def execute(self, state: dict) -> dict:
        last_error = None

        for attempt in range(self.max_retries):
            try:
                result = self.api_call(state)
                self.log(f"Success on attempt {attempt + 1}")
                return {"result": result, "status": "success"}

            except Exception as e:
                last_error = e
                self.log(f"Attempt {attempt + 1} failed: {e}")

                if attempt < self.max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait = 2 ** attempt
                    time.sleep(wait)

        # All retries failed
        return {
            "result": None,
            "status": "failed_after_retries",
            "error": str(last_error)
        }

    def api_call(self, state):
        # Potentially failing operation
        import requests
        response = requests.get("https://api.example.com/data")
        response.raise_for_status()
        return response.json()
```

---

### Async Retry Pattern

```python
import asyncio
from casts.base_node import AsyncBaseNode

class AsyncRetryNode(AsyncBaseNode):
    """Async node with retry logic."""

    async def execute(self, state: dict) -> dict:
        max_retries = 3

        for attempt in range(max_retries):
            try:
                result = await self.async_operation(state)
                return {"result": result, "status": "success"}

            except Exception as e:
                self.log(f"Attempt {attempt + 1} failed: {e}")

                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Backoff
                else:
                    return {"status": "error", "error": str(e)}

    async def async_operation(self, state):
        # Async operation that might fail
        await asyncio.sleep(0.1)
        return "result"
```

---

## Timeout Handling

### Sync Timeout

```python
import signal

class TimeoutNode(BaseNode):
    """Node with timeout protection."""

    def execute(self, state: dict) -> dict:
        timeout_seconds = 30

        def timeout_handler(signum, frame):
            raise TimeoutError("Operation timed out")

        # Set timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)

        try:
            result = self.slow_operation(state)
            signal.alarm(0)  # Cancel timeout
            return {"result": result, "status": "success"}

        except TimeoutError:
            return {"status": "timeout", "error": "Operation exceeded 30s"}

        except Exception as e:
            signal.alarm(0)  # Cancel timeout
            return {"status": "error", "error": str(e)}

    def slow_operation(self, state):
        # Potentially slow operation
        time.sleep(10)
        return "done"
```

---

### Async Timeout

```python
import asyncio

class AsyncTimeoutNode(AsyncBaseNode):
    """Async node with timeout."""

    async def execute(self, state: dict) -> dict:
        try:
            # Wait max 30 seconds
            result = await asyncio.wait_for(
                self.async_operation(state),
                timeout=30.0
            )
            return {"result": result, "status": "success"}

        except asyncio.TimeoutError:
            return {"status": "timeout", "error": "Operation timed out"}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def async_operation(self, state):
        # Async operation
        await asyncio.sleep(5)
        return "result"
```

---

## Error Recovery Patterns

### Fallback Strategy

```python
class FallbackNode(BaseNode):
    """Node with fallback strategy."""

    def execute(self, state: dict) -> dict:
        # Try primary method
        try:
            result = self.primary_method(state)
            return {"result": result, "method": "primary"}

        except Exception as primary_error:
            self.log(f"Primary failed: {primary_error}")

            # Try fallback method
            try:
                result = self.fallback_method(state)
                return {"result": result, "method": "fallback"}

            except Exception as fallback_error:
                self.log(f"Fallback also failed: {fallback_error}")
                return {
                    "status": "error",
                    "error": "Both primary and fallback failed"
                }

    def primary_method(self, state):
        # Preferred method (might fail)
        return "primary_result"

    def fallback_method(self, state):
        # Backup method
        return "fallback_result"
```

---

### Partial Success Handling

```python
class BatchProcessingNode(BaseNode):
    """Processes batch, handles individual failures."""

    def execute(self, state: dict) -> dict:
        items = state.get("items", [])
        results = []
        errors = []

        for item in items:
            try:
                result = self.process_item(item)
                results.append(result)

            except Exception as e:
                self.log(f"Failed to process {item}: {e}")
                errors.append({"item": item, "error": str(e)})

        return {
            "results": results,
            "errors": errors,
            "status": "partial" if errors else "success",
            "success_count": len(results),
            "error_count": len(errors)
        }

    def process_item(self, item):
        # Process single item
        return f"processed_{item}"
```

---

## Validation Patterns

### Input Validation

```python
class ValidatingNode(BaseNode):
    """Node with input validation."""

    def execute(self, state: dict) -> dict:
        # Validate required fields
        required = ["query", "user_id"]
        missing = [f for f in required if f not in state]

        if missing:
            return {
                "status": "validation_error",
                "error": f"Missing fields: {', '.join(missing)}"
            }

        # Validate types
        if not isinstance(state.get("query"), str):
            return {
                "status": "validation_error",
                "error": "query must be string"
            }

        # Proceed with valid input
        try:
            result = self.process(state)
            return {"result": result, "status": "success"}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def process(self, state):
        return f"Processed: {state['query']}"
```

---

## Logging Errors

### Structured Error Logging

```python
import logging

logger = logging.getLogger(__name__)

class LoggingNode(BaseNode):
    """Node with comprehensive logging."""

    def execute(self, state: dict) -> dict:
        try:
            result = self.operation(state)

            logger.info(
                "Operation successful",
                extra={
                    "node": self.__class__.__name__,
                    "state_fields": list(state.keys())
                }
            )

            return {"result": result, "status": "success"}

        except Exception as e:
            logger.error(
                f"Operation failed: {e}",
                extra={
                    "node": self.__class__.__name__,
                    "error_type": type(e).__name__,
                    "state": state  # Be careful with sensitive data!
                },
                exc_info=True  # Include stack trace
            )

            return {"status": "error", "error": str(e)}

    def operation(self, state):
        return "result"
```

---

## Anti-Patterns

### ❌ Silently Ignoring Errors

```python
def execute(self, state):
    try:
        result = self.operation(state)
    except:
        pass  # ❌ Error ignored, returns None
```

```python
def execute(self, state):
    try:
        result = self.operation(state)
        return {"result": result}
    except Exception as e:
        self.log(f"Error: {e}")  # ✓ Log it
        return {"status": "error", "error": str(e)}  # ✓ Return error state
```

---

### ❌ Raising Errors (Crashes Graph)

```python
def execute(self, state):
    if "required_field" not in state:
        raise ValueError("Missing field")  # ❌ Crashes graph
```

```python
def execute(self, state):
    if "required_field" not in state:
        return {"status": "error", "error": "Missing required_field"}  # ✓
```

---

### ❌ No Error Context

```python
except Exception:
    return {"error": "failed"}  # ❌ Not helpful
```

```python
except Exception as e:
    return {
        "error": str(e),  # ✓ What went wrong
        "node": self.__class__.__name__,  # ✓ Where
        "status": "error"  # ✓ How to handle
    }
```

---

## Decision Framework

**Q: Should I use try/except?**
- External API calls → YES
- File I/O → YES
- LLM calls → YES
- State field access (with .get()) → Usually NO
- Pure logic → Usually NO

**Q: Retry or fail immediately?**
- Transient failures (network) → Retry
- Invalid input → Fail immediately
- Rate limits → Retry with backoff

**Q: How many retries?**
- Network calls → 3-5 retries
- LLM API → 3 retries
- Database → 3 retries

**Q: What to return on error?**
- Always return dict with state updates
- Include `status`: "error" or similar
- Include `error`: descriptive message
- Consider `error_type` for routing

---

## References
- core/node-patterns.md (node implementation)
- tools/tool-creation.md (error handling in tools)
- patterns/async-patterns.md (async error handling)
