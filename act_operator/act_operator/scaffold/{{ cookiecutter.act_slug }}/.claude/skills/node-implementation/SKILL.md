---
name: node-implementation
description: Implement LangGraph nodes with BaseNode - use when creating node classes, implementing execute methods, handling state updates, or working with node patterns.
---

# Node Implementation

**Use this skill when:**
- Creating new node classes
- Implementing node execute methods
- Working with state in nodes
- Adding config or runtime access
- Converting functions to node classes
- Troubleshooting node issues

## Overview

Nodes are the processing units in LangGraph graphs. Each node receives state, performs operations, and returns state updates. Act provides `BaseNode` and `AsyncBaseNode` base classes that handle runtime integration automatically.

**Key concepts:**
- **Node**: Processing unit that transforms state
- **execute()**: Abstract method you implement with your logic
- **BaseNode**: Base class for sync nodes
- **AsyncBaseNode**: Base class for async nodes
- **State updates**: Return dict with changes
- **Config**: Access to thread_id, tags, metadata
- **Runtime**: Access to store, stream writer

## Quick Start

### Simple Sync Node

Most common pattern:

```python
from casts.base_node import BaseNode
from langchain.messages import AIMessage

class WelcomeNode(BaseNode):
    """Simple sync node that only uses state."""

    def execute(self, state):
        """Process state and return updates.

        Args:
            state: Current graph state

        Returns:
            dict: State updates
        """
        return {
            "messages": [AIMessage(content=f"Hello {state.query}!")]
        }
```

### Simple Async Node

For async operations:

```python
from casts.base_node import AsyncBaseNode
from langchain.messages import AIMessage

class AsyncWelcomeNode(AsyncBaseNode):
    """Simple async node that only uses state."""

    async def execute(self, state):
        """Process state asynchronously.

        Args:
            state: Current graph state

        Returns:
            dict: State updates
        """
        # Await async operations
        result = await some_async_function(state.query)

        return {
            "messages": [AIMessage(content=result)]
        }
```

## Execute Method Signatures

BaseNode supports flexible signatures. Choose based on what you need:

### Signature 1: State Only (Most Common)

```python
def execute(self, state):
    """Only need state."""
    return {"result": process(state.input)}
```

**Use when:**
- Simple transformations
- No need for config or runtime
- Most data processing nodes

### Signature 2: With Config

```python
def execute(self, state, config=None, **kwargs):
    """Need thread_id, tags, or metadata."""
    thread_id = self.get_thread_id(config)
    tags = self.get_tags(config)

    return {
        "thread_id": thread_id,
        "result": process(state.input)
    }
```

**Use when:**
- Need thread_id for persistence
- Need tags for filtering
- Need configurable metadata

### Signature 3: With Runtime

```python
def execute(self, state, runtime=None, **kwargs):
    """Need store or stream writer."""
    if runtime and runtime.store:
        # Access persistent storage
        data = runtime.store.get("key", thread_id=state.thread_id)

    if runtime and runtime.stream_writer:
        # Stream intermediate results
        runtime.stream_writer.write({"chunk": "partial"})

    return {"result": data}
```

**Use when:**
- Need persistent storage (runtime.store)
- Need streaming (runtime.stream_writer)
- Need runtime context

### Signature 4: Full Access

```python
def execute(self, state, config=None, runtime=None, **kwargs):
    """Need everything."""
    thread_id = self.get_thread_id(config)

    if runtime and runtime.store:
        data = runtime.store.get("key", thread_id=thread_id)

    return {"result": data}
```

**Use when:**
- Need both config and runtime
- Complex nodes with multiple features

### Signature 5: Flexible (**kwargs)

```python
def execute(self, state, **kwargs):
    """Access via kwargs."""
    config = kwargs.get("config")
    runtime = kwargs.get("runtime")

    if config:
        thread_id = self.get_thread_id(config)

    return {"result": process(state.input)}
```

**Use when:**
- Want flexibility
- May add parameters later
- Debugging (can inspect kwargs)

## Node Patterns

### Pattern 1: Transformation Node

Transform data:

```python
class ProcessNode(BaseNode):
    """Transform input to output."""

    def execute(self, state):
        # Get input
        text = state.query

        # Transform
        processed = text.upper().strip()

        # Return update
        return {"processed_query": processed}
```

### Pattern 2: Agent Node

Call LLM with tools:

```python
from langchain_openai import ChatOpenAI

class AgentNode(BaseNode):
    """LLM agent with tools."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = ChatOpenAI(model="gpt-4")
        self.tools = [search_tool, calculator_tool]
        self.agent = self.model.bind_tools(self.tools)

    def execute(self, state):
        # Invoke agent
        response = self.agent.invoke(state.messages)

        # Return message update
        return {"messages": [response]}
```

### Pattern 3: Tool Execution Node

Execute tool calls:

```python
from langchain.messages import ToolMessage

class ToolNode(BaseNode):
    """Execute tool calls from messages."""

    def execute(self, state):
        # Get last message
        last_message = state.messages[-1]

        # Check for tool calls
        if not hasattr(last_message, 'tool_calls'):
            return {}

        tool_messages = []
        for tool_call in last_message.tool_calls:
            # Execute tool
            result = self.execute_tool(tool_call)

            # Create tool message
            tool_messages.append(
                ToolMessage(
                    content=result,
                    tool_call_id=tool_call['id']
                )
            )

        return {"messages": tool_messages}

    def execute_tool(self, tool_call):
        """Execute a single tool call."""
        # Implement tool execution logic
        pass
```

### Pattern 4: Conditional Node

Make routing decisions:

```python
class ClassifierNode(BaseNode):
    """Classify input for routing."""

    def execute(self, state):
        query = state.query.lower()

        # Determine category
        if "math" in query or "calculate" in query:
            category = "math"
        elif "search" in query or "find" in query:
            category = "search"
        else:
            category = "general"

        return {"category": category}
```

### Pattern 5: Stateful Node

Maintain internal state:

```python
class CounterNode(BaseNode):
    """Track call count."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.call_count = 0

    def execute(self, state):
        self.call_count += 1

        self.log(f"Called {self.call_count} times")

        return {
            "call_count": self.call_count,
            "result": process(state.input)
        }
```

### Pattern 6: Batch Processing Node

Process items in batches:

```python
class BatchNode(BaseNode):
    """Process items in batches."""

    def __init__(self, batch_size=10, **kwargs):
        super().__init__(**kwargs)
        self.batch_size = batch_size

    def execute(self, state):
        items = state.items
        current_batch = state.current_batch

        # Get batch
        start = current_batch * self.batch_size
        end = start + self.batch_size
        batch = items[start:end]

        # Process batch
        results = [self.process_item(item) for item in batch]

        return {
            "processed": results,
            "current_batch": current_batch + 1,
            "complete": end >= len(items)
        }

    def process_item(self, item):
        """Process a single item."""
        return item.upper()
```

## State Manipulation

### Reading State

```python
def execute(self, state):
    # Access state fields
    query = state.query
    messages = state.messages
    count = state.count

    # Check if field exists
    if hasattr(state, 'optional_field'):
        value = state.optional_field

    # Get with default
    value = getattr(state, 'optional_field', default_value)
```

### Updating State

```python
def execute(self, state):
    # Return dict with updates
    return {
        "result": "new value",
        "count": state.count + 1
    }

    # Multiple fields
    return {
        "field1": value1,
        "field2": value2,
        "field3": value3
    }

    # Empty dict = no changes
    return {}
```

### State Update Rules

```python
# Rule 1: Always return dict
def execute(self, state):
    return {"result": "value"}  # ✅ Good

def execute(self, state):
    return "value"  # ❌ Bad: Not a dict

# Rule 2: Only return changed fields
def execute(self, state):
    return {"result": new_value}  # ✅ Good: Only changed field

def execute(self, state):
    return {  # ❌ Bad: Returning everything
        "result": state.result,
        "query": state.query,
        # ... all fields
    }

# Rule 3: Don't modify state in-place
def execute(self, state):
    state.result = "value"  # ❌ Bad: Mutation
    return {}

def execute(self, state):
    return {"result": "value"}  # ✅ Good: Return update
```

## Error Handling

### Basic Error Handling

```python
class SafeNode(BaseNode):
    """Node with error handling."""

    def execute(self, state):
        try:
            result = risky_operation(state.input)
            return {"result": result}

        except ValueError as e:
            self.log(f"Validation error: {e}")
            return {"error": f"Invalid input: {e}"}

        except Exception as e:
            self.log(f"Unexpected error: {e}", exc_info=True)
            return {"error": str(e)}
```

### Retry Pattern

```python
class RetryNode(BaseNode):
    """Node with retry logic."""

    def __init__(self, max_retries=3, **kwargs):
        super().__init__(**kwargs)
        self.max_retries = max_retries

    def execute(self, state):
        retry_count = getattr(state, 'retry_count', 0)

        try:
            result = unstable_operation(state.input)
            return {
                "result": result,
                "retry_count": 0  # Reset on success
            }

        except Exception as e:
            if retry_count >= self.max_retries:
                return {
                    "error": f"Failed after {retry_count} retries: {e}",
                    "retry_count": retry_count
                }

            # Increment retry count
            return {
                "retry_count": retry_count + 1,
                "last_error": str(e)
            }
```

### Fallback Pattern

```python
class FallbackNode(BaseNode):
    """Try primary, fall back on error."""

    def execute(self, state):
        try:
            # Try primary method
            return {"result": primary_method(state.input)}

        except Exception as e:
            self.log(f"Primary failed: {e}, using fallback")

            # Use fallback
            try:
                return {"result": fallback_method(state.input)}
            except Exception as e2:
                return {"error": f"Both failed: {e}, {e2}"}
```

## Async Patterns

### Basic Async

```python
class AsyncFetchNode(AsyncBaseNode):
    """Fetch data asynchronously."""

    async def execute(self, state):
        # Await async operations
        data = await fetch_data(state.query)

        return {"data": data}
```

### Concurrent Operations

```python
import asyncio

class ParallelNode(AsyncBaseNode):
    """Run operations in parallel."""

    async def execute(self, state):
        # Launch multiple operations
        tasks = [
            fetch_data(state.query),
            fetch_metadata(state.query),
            fetch_related(state.query)
        ]

        # Wait for all
        results = await asyncio.gather(*tasks)

        return {
            "data": results[0],
            "metadata": results[1],
            "related": results[2]
        }
```

### Async with Streaming

```python
class StreamingNode(AsyncBaseNode):
    """Stream results as they arrive."""

    async def execute(self, state, runtime=None, **kwargs):
        if not runtime or not runtime.stream_writer:
            # No streaming available
            result = await process_all(state.input)
            return {"result": result}

        # Stream chunks
        async for chunk in process_streaming(state.input):
            runtime.stream_writer.write({"chunk": chunk})

        return {"complete": True}
```

## Using Config and Runtime

### Access Thread ID

```python
class ThreadAwareNode(BaseNode):
    """Use thread_id from config."""

    def execute(self, state, config=None, **kwargs):
        thread_id = self.get_thread_id(config)

        self.log(f"Processing for thread: {thread_id}")

        return {
            "thread_id": thread_id,
            "result": process_for_thread(state.input, thread_id)
        }
```

### Access Tags

```python
class TaggedNode(BaseNode):
    """Use tags from config."""

    def execute(self, state, config=None, **kwargs):
        tags = self.get_tags(config)

        if "debug" in tags:
            self.log("Debug mode enabled", state=state)

        return {"result": process(state.input)}
```

### Use Store

```python
class PersistentNode(BaseNode):
    """Use runtime store for persistence."""

    def execute(self, state, config=None, runtime=None, **kwargs):
        if not runtime or not runtime.store:
            return {"error": "Store not available"}

        thread_id = self.get_thread_id(config)

        # Get from store
        history = runtime.store.get("history", thread_id=thread_id) or []

        # Update history
        history.append(state.query)

        # Save to store
        runtime.store.put("history", history, thread_id=thread_id)

        return {"history_count": len(history)}
```

## Best Practices

### 1. Always Return Dict

```python
# ✅ Good
def execute(self, state):
    return {"result": "value"}

# ❌ Bad
def execute(self, state):
    return "value"
```

### 2. Use Logging

```python
class GoodNode(BaseNode):
    """Node with logging."""

    def execute(self, state):
        self.log("Starting processing", query=state.query)

        result = process(state.query)

        self.log("Processing complete", result=result)

        return {"result": result}
```

### 3. Document Execute Method

```python
def execute(self, state):
    """Process user query and generate response.

    Transforms the input query, calls the LLM, and formats
    the response for downstream nodes.

    Args:
        state: Graph state containing:
            - query (str): User's input query
            - context (dict): Additional context

    Returns:
        dict: State updates containing:
            - response (str): Generated response
            - metadata (dict): Processing metadata
    """
```

### 4. Keep Nodes Focused

```python
# ✅ Good: Single responsibility
class ValidateNode(BaseNode):
    def execute(self, state):
        return {"valid": validate(state.input)}

class ProcessNode(BaseNode):
    def execute(self, state):
        return {"result": process(state.input)}

# ❌ Bad: Too much responsibility
class DoEverythingNode(BaseNode):
    def execute(self, state):
        # Validation, processing, formatting, storage...
        pass
```

### 5. Handle Missing State Fields

```python
def execute(self, state):
    # ✅ Good: Check existence
    if hasattr(state, 'optional_field'):
        value = state.optional_field
    else:
        value = default_value

    # ✅ Good: Use getattr with default
    value = getattr(state, 'optional_field', default_value)
```

### 6. Use Descriptive Names

```python
# ✅ Good
class GenerateResponseNode(BaseNode): pass
class ValidateInputNode(BaseNode): pass
class FetchUserDataNode(BaseNode): pass

# ❌ Bad
class Node1(BaseNode): pass
class DoStuff(BaseNode): pass
class MyNode(BaseNode): pass
```

## Troubleshooting

### Issue: execute() not called

**Symptoms**: Node instance created but execute never runs

**Fix**:
```python
# ❌ Bad: Passing class
graph.add_node("my_node", MyNode)

# ✅ Good: Passing instance
graph.add_node("my_node", MyNode())
```

### Issue: State updates not working

**Symptoms**: Return value ignored

**Fix**:
```python
# ❌ Bad: Not returning dict
def execute(self, state):
    state.result = "value"  # Mutation doesn't work
    return state

# ✅ Good: Return dict
def execute(self, state):
    return {"result": "value"}
```

### Issue: Config/Runtime always None

**Symptoms**: config or runtime parameter is always None

**Fix**:
```python
# Ensure signature matches what you need
def execute(self, state, config=None, runtime=None, **kwargs):
    # BaseNode.__call__ will pass these if signature has them
    pass
```

### Issue: Async node not awaiting

**Symptoms**: AsyncBaseNode returns coroutine instead of result

**Fix**:
```python
# ❌ Bad: Forgetting await
async def execute(self, state):
    result = fetch_data(state.input)  # Missing await!
    return {"result": result}

# ✅ Good: Await async calls
async def execute(self, state):
    result = await fetch_data(state.input)
    return {"result": result}
```

## Quick Reference

```python
# Basic sync node
from casts.base_node import BaseNode

class MyNode(BaseNode):
    def execute(self, state):
        return {"result": "value"}

# Basic async node
from casts.base_node import AsyncBaseNode

class MyAsyncNode(AsyncBaseNode):
    async def execute(self, state):
        return {"result": await async_op()}

# With config and runtime
class AdvancedNode(BaseNode):
    def execute(self, state, config=None, runtime=None, **kwargs):
        thread_id = self.get_thread_id(config)
        self.log("Processing", thread_id=thread_id)
        return {"result": "value"}

# Usage in graph
node = MyNode(verbose=True)
graph.add_node("my_node", node)
```

## Related Skills

- **state-management**: Design state schemas for nodes
- **graph-composition**: Connect nodes in graphs
- **modules-integration**: Use tools, chains, agents in nodes
- **cast-development**: Overall Cast structure

## References

**Official documentation:**
- Nodes: https://docs.langchain.com/oss/python/langgraph/nodes
- Async Nodes: https://docs.langchain.com/oss/python/langgraph/async-nodes
- Runtime: https://docs.langchain.com/oss/python/langgraph/runtime
