# Async Patterns for LangGraph Nodes

Comprehensive guide to async/await patterns for building asynchronous LangGraph nodes.

## Table of Contents

1. [Introduction](#introduction)
2. [AsyncBaseNode Fundamentals](#asyncbasenode-fundamentals)
   - [Basic Structure](#basic-structure)
   - [Lifecycle](#lifecycle)
   - [Async vs Sync](#async-vs-sync)
3. [Core Async Patterns](#core-async-patterns)
   - [Single Async Operation](#single-async-operation)
   - [Multiple Sequential Operations](#multiple-sequential-operations)
   - [Concurrent Operations](#concurrent-operations)
   - [Async Context Managers](#async-context-managers)
4. [Advanced Patterns](#advanced-patterns)
   - [Async Generators](#async-generators)
   - [Timeout Handling](#timeout-handling)
   - [Rate Limiting](#rate-limiting)
   - [Connection Pooling](#connection-pooling)
   - [Streaming Responses](#streaming-responses)
5. [Error Handling](#error-handling)
   - [Try-Except in Async](#try-except-in-async)
   - [Async Error Recovery](#async-error-recovery)
   - [Timeout Errors](#timeout-errors)
   - [Cancellation](#cancellation)
6. [Concurrency Control](#concurrency-control)
   - [asyncio.gather](#asynciogather)
   - [asyncio.wait](#asynciowait)
   - [Semaphores](#semaphores)
   - [Task Groups](#task-groups)
7. [Integration Patterns](#integration-patterns)
   - [Async HTTP Clients](#async-http-clients)
   - [Async Database Operations](#async-database-operations)
   - [Async File I/O](#async-file-io)
   - [Mixed Sync/Async Code](#mixed-syncasync-code)
8. [Best Practices](#best-practices)
9. [Common Pitfalls](#common-pitfalls)
10. [Performance Optimization](#performance-optimization)
11. [Testing Async Nodes](#testing-async-nodes)
12. [Troubleshooting](#troubleshooting)

---

## Introduction

Asynchronous programming in LangGraph enables high-performance, non-blocking node operations. This is essential for:
- **I/O-bound operations**: API calls, database queries, file operations
- **Concurrent processing**: Multiple operations simultaneously
- **Scalability**: Handle many requests efficiently
- **Responsive applications**: Don't block on slow operations

**When to use async:**
- Making HTTP/API calls
- Database queries
- File I/O operations
- Multiple independent operations
- Streaming data processing

**When to use sync:**
- CPU-bound operations (computation)
- Simple state transformations
- No I/O operations
- Legacy code integration

---

## AsyncBaseNode Fundamentals

### Basic Structure

```python
from act_operator_lib.base_node import AsyncBaseNode
from dataclasses import dataclass

@dataclass(kw_only=True)
class State:
    query: str
    result: str = None

class MyAsyncNode(AsyncBaseNode):
    async def execute(self, state):
        """Async execute method - note the 'async' keyword."""
        # Await async operations
        result = await self.fetch_data(state.query)
        return {"result": result}

    async def fetch_data(self, query):
        """Helper async method."""
        # Simulate async operation
        await asyncio.sleep(1)
        return f"Data for {query}"
```

**Key points:**
- Use `AsyncBaseNode` instead of `BaseNode`
- Mark `execute` method as `async`
- Use `await` for async operations
- Return dict just like sync nodes

### Lifecycle

```
Graph invokes node
    ↓
await node(state, config, runtime)
    ↓
__call__ inspects execute() signature
    ↓
await execute(state, config?, runtime?)
    ↓
Return dict of state updates
    ↓
Graph merges updates into state
```

**Example execution:**
```python
# In graph
node = MyAsyncNode()

# LangGraph calls
updates = await node(state, config=config, runtime=runtime)

# Internally
# await self.execute(state)
# Returns: {"result": "value"}
```

### Async vs Sync

**AsyncBaseNode:**
```python
class AsyncNode(AsyncBaseNode):
    async def execute(self, state):
        data = await fetch_from_api()
        return {"data": data}

# Usage in graph
result = await graph.ainvoke({"query": "test"})
```

**BaseNode (sync):**
```python
class SyncNode(BaseNode):
    def execute(self, state):
        data = fetch_from_api_sync()
        return {"data": data}

# Usage in graph
result = graph.invoke({"query": "test"})
```

**When to choose:**
- **AsyncBaseNode**: I/O operations, concurrent tasks, modern APIs
- **BaseNode**: CPU-bound, simple transforms, sync libraries

---

## Core Async Patterns

### Single Async Operation

Simplest pattern - one async operation:

```python
import aiohttp

class FetchNode(AsyncBaseNode):
    async def execute(self, state):
        """Single async HTTP request."""
        async with aiohttp.ClientSession() as session:
            async with session.get(state.url) as response:
                data = await response.json()
                return {"data": data}
```

**Use when:**
- Single API call
- One database query
- Simple async operation

### Multiple Sequential Operations

Operations that depend on each other:

```python
class SequentialNode(AsyncBaseNode):
    async def execute(self, state):
        """Execute operations in sequence."""
        # Step 1: Fetch user
        user = await self.fetch_user(state.user_id)

        # Step 2: Fetch user's posts (depends on user)
        posts = await self.fetch_posts(user["id"])

        # Step 3: Fetch comments (depends on posts)
        comments = await self.fetch_comments(posts[0]["id"])

        return {
            "user": user,
            "posts": posts,
            "comments": comments
        }

    async def fetch_user(self, user_id):
        await asyncio.sleep(0.1)  # Simulate API call
        return {"id": user_id, "name": "Alice"}

    async def fetch_posts(self, user_id):
        await asyncio.sleep(0.1)
        return [{"id": 1, "title": "Post 1"}]

    async def fetch_comments(self, post_id):
        await asyncio.sleep(0.1)
        return [{"id": 1, "text": "Comment 1"}]
```

**Pattern:**
```python
result1 = await operation1()
result2 = await operation2(result1)  # Depends on result1
result3 = await operation3(result2)  # Depends on result2
```

### Concurrent Operations

Operations that can run in parallel:

```python
import asyncio

class ConcurrentNode(AsyncBaseNode):
    async def execute(self, state):
        """Execute multiple operations concurrently."""
        # Start all operations simultaneously
        user_task = self.fetch_user(state.user_id)
        weather_task = self.fetch_weather(state.location)
        news_task = self.fetch_news(state.topic)

        # Wait for all to complete
        user, weather, news = await asyncio.gather(
            user_task,
            weather_task,
            news_task
        )

        return {
            "user": user,
            "weather": weather,
            "news": news
        }

    async def fetch_user(self, user_id):
        await asyncio.sleep(1)
        return {"id": user_id}

    async def fetch_weather(self, location):
        await asyncio.sleep(1)
        return {"temp": 72}

    async def fetch_news(self, topic):
        await asyncio.sleep(1)
        return {"articles": []}
```

**Benefits:**
- 3x faster than sequential (1 second vs 3 seconds)
- Maximizes I/O parallelism
- Better resource utilization

**Pattern:**
```python
# Concurrent - 1 second total
results = await asyncio.gather(op1(), op2(), op3())

# Sequential - 3 seconds total
r1 = await op1()
r2 = await op2()
r3 = await op3()
```

### Async Context Managers

Properly manage resources:

```python
class DatabaseNode(AsyncBaseNode):
    async def execute(self, state):
        """Use async context manager for connections."""
        async with self.get_connection() as conn:
            # Connection automatically closed after block
            result = await conn.execute(state.query)
            return {"result": result}

    async def get_connection(self):
        """Return async context manager."""
        return AsyncDatabaseConnection()

class AsyncDatabaseConnection:
    async def __aenter__(self):
        """Called on 'async with' entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Called on 'async with' exit."""
        await self.disconnect()

    async def connect(self):
        await asyncio.sleep(0.1)

    async def disconnect(self):
        await asyncio.sleep(0.1)

    async def execute(self, query):
        await asyncio.sleep(0.1)
        return "result"
```

**Common uses:**
- Database connections
- HTTP sessions
- File handles
- Locks and semaphores

---

## Advanced Patterns

### Async Generators

Stream results as they arrive:

```python
class StreamingNode(AsyncBaseNode):
    async def execute(self, state):
        """Process streaming data."""
        results = []

        # Consume async generator
        async for item in self.fetch_stream(state.query):
            results.append(item)

        return {"results": results}

    async def fetch_stream(self, query):
        """Async generator - yields items one at a time."""
        for i in range(5):
            await asyncio.sleep(0.1)
            yield {"item": i, "query": query}

# Alternative: Process as they arrive
class StreamingProcessNode(AsyncBaseNode):
    async def execute(self, state):
        """Process items as they stream in."""
        processed = []

        async for item in self.fetch_stream(state.query):
            # Process immediately
            result = await self.process_item(item)
            processed.append(result)

        return {"processed": processed}

    async def fetch_stream(self, query):
        for i in range(5):
            await asyncio.sleep(0.1)
            yield {"data": i}

    async def process_item(self, item):
        await asyncio.sleep(0.05)
        return {"processed": item}
```

**Use cases:**
- Streaming API responses
- Processing large datasets
- Real-time data feeds
- Incremental results

### Timeout Handling

Prevent operations from hanging:

```python
class TimeoutNode(AsyncBaseNode):
    async def execute(self, state):
        """Execute with timeout."""
        try:
            # Timeout after 5 seconds
            result = await asyncio.wait_for(
                self.slow_operation(state.input),
                timeout=5.0
            )
            return {"result": result, "timed_out": False}

        except asyncio.TimeoutError:
            self.log("Operation timed out")
            return {"result": None, "timed_out": True}

    async def slow_operation(self, input_data):
        """Potentially slow operation."""
        await asyncio.sleep(10)  # Takes 10 seconds
        return "result"

# Multiple operations with timeout
class MultiTimeoutNode(AsyncBaseNode):
    async def execute(self, state):
        """Multiple operations with individual timeouts."""
        tasks = [
            asyncio.wait_for(self.op1(), timeout=1.0),
            asyncio.wait_for(self.op2(), timeout=2.0),
            asyncio.wait_for(self.op3(), timeout=3.0),
        ]

        # gather with return_exceptions to handle timeouts
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        valid_results = []
        errors = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                errors.append(f"Operation {i} failed: {result}")
            else:
                valid_results.append(result)

        return {
            "results": valid_results,
            "errors": errors
        }

    async def op1(self):
        await asyncio.sleep(0.5)
        return "result1"

    async def op2(self):
        await asyncio.sleep(1.5)
        return "result2"

    async def op3(self):
        await asyncio.sleep(5)  # Will timeout
        return "result3"
```

### Rate Limiting

Control request rate:

```python
import time

class RateLimitedNode(AsyncBaseNode):
    def __init__(self, requests_per_second=10, **kwargs):
        super().__init__(**kwargs)
        self.rate_limit = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0

    async def execute(self, state):
        """Execute with rate limiting."""
        results = []

        for item in state.items:
            # Rate limit
            await self.rate_limit_wait()

            # Make request
            result = await self.fetch_item(item)
            results.append(result)

        return {"results": results}

    async def rate_limit_wait(self):
        """Wait to respect rate limit."""
        now = time.time()
        time_since_last = now - self.last_request_time

        if time_since_last < self.min_interval:
            wait_time = self.min_interval - time_since_last
            await asyncio.sleep(wait_time)

        self.last_request_time = time.time()

    async def fetch_item(self, item):
        await asyncio.sleep(0.1)
        return f"Result for {item}"

# Token bucket rate limiter
class TokenBucketNode(AsyncBaseNode):
    def __init__(self, rate=10, capacity=10, **kwargs):
        super().__init__(**kwargs)
        self.rate = rate  # Tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = asyncio.Lock()

    async def execute(self, state):
        """Execute with token bucket rate limiting."""
        results = []

        for item in state.items:
            # Acquire token
            await self.acquire_token()

            # Make request
            result = await self.fetch_item(item)
            results.append(result)

        return {"results": results}

    async def acquire_token(self):
        """Acquire a token, waiting if necessary."""
        async with self.lock:
            # Refill tokens based on time passed
            now = time.time()
            time_passed = now - self.last_update
            self.tokens = min(
                self.capacity,
                self.tokens + time_passed * self.rate
            )
            self.last_update = now

            # Wait if no tokens available
            while self.tokens < 1:
                wait_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)

                now = time.time()
                time_passed = now - self.last_update
                self.tokens = min(
                    self.capacity,
                    self.tokens + time_passed * self.rate
                )
                self.last_update = now

            # Consume token
            self.tokens -= 1

    async def fetch_item(self, item):
        await asyncio.sleep(0.1)
        return f"Result for {item}"
```

### Connection Pooling

Reuse connections efficiently:

```python
import aiohttp

class PooledHTTPNode(AsyncBaseNode):
    def __init__(self, pool_size=10, **kwargs):
        super().__init__(**kwargs)
        self.pool_size = pool_size
        self.session = None

    async def execute(self, state):
        """Execute with connection pooling."""
        # Initialize session if needed
        if self.session is None:
            connector = aiohttp.TCPConnector(limit=self.pool_size)
            self.session = aiohttp.ClientSession(connector=connector)

        # Make concurrent requests using pool
        tasks = [
            self.fetch_url(url)
            for url in state.urls
        ]

        results = await asyncio.gather(*tasks)

        return {"results": results}

    async def fetch_url(self, url):
        """Fetch URL using pooled session."""
        async with self.session.get(url) as response:
            return await response.text()

    async def cleanup(self):
        """Close session when done."""
        if self.session:
            await self.session.close()
```

### Streaming Responses

Stream LLM responses:

```python
from langchain_core.messages import AIMessage

class StreamingLLMNode(AsyncBaseNode):
    async def execute(self, state):
        """Stream LLM response tokens."""
        chunks = []

        # Stream tokens
        async for chunk in self.llm.astream(state.messages):
            chunks.append(chunk.content)

            # Optional: yield intermediate updates
            # Note: LangGraph supports streaming updates

        # Combine chunks
        full_response = "".join(chunks)

        return {"messages": [AIMessage(content=full_response)]}

# With runtime streaming
class RuntimeStreamNode(AsyncBaseNode):
    async def execute(self, state, runtime):
        """Stream using runtime interface."""
        chunks = []

        async for chunk in self.llm.astream(state.messages):
            chunks.append(chunk.content)

            # Stream to runtime
            if runtime and runtime.stream:
                runtime.stream.send(chunk.content)

        full_response = "".join(chunks)
        return {"messages": [AIMessage(content=full_response)]}
```

---

## Error Handling

### Try-Except in Async

Handle async errors:

```python
class ErrorHandlingNode(AsyncBaseNode):
    async def execute(self, state):
        """Handle async errors."""
        try:
            result = await self.risky_operation(state.input)
            return {"result": result, "error": None}

        except asyncio.TimeoutError:
            self.log("Operation timed out")
            return {"result": None, "error": "timeout"}

        except aiohttp.ClientError as e:
            self.log("HTTP error", error=str(e))
            return {"result": None, "error": f"http: {e}"}

        except Exception as e:
            self.log("Unexpected error", error=str(e))
            return {"result": None, "error": str(e)}

    async def risky_operation(self, input_data):
        """Operation that might fail."""
        await asyncio.sleep(0.1)
        if input_data == "fail":
            raise ValueError("Invalid input")
        return f"Processed {input_data}"
```

### Async Error Recovery

Retry failed operations:

```python
class RetryNode(AsyncBaseNode):
    def __init__(self, max_retries=3, backoff=1.0, **kwargs):
        super().__init__(**kwargs)
        self.max_retries = max_retries
        self.backoff = backoff

    async def execute(self, state):
        """Execute with exponential backoff retry."""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                result = await self.operation(state.input)
                return {"result": result, "attempts": attempt + 1}

            except Exception as e:
                last_error = e
                self.log(f"Attempt {attempt + 1} failed: {e}")

                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    wait_time = self.backoff * (2 ** attempt)
                    await asyncio.sleep(wait_time)

        # All retries failed
        return {
            "result": None,
            "error": str(last_error),
            "attempts": self.max_retries
        }

    async def operation(self, input_data):
        """Operation that might fail."""
        await asyncio.sleep(0.1)
        import random
        if random.random() < 0.5:
            raise ValueError("Random failure")
        return f"Success: {input_data}"
```

### Timeout Errors

Handle various timeout scenarios:

```python
class TimeoutHandlingNode(AsyncBaseNode):
    async def execute(self, state):
        """Handle different timeout scenarios."""
        results = {}

        # Individual operation with timeout
        try:
            results["quick"] = await asyncio.wait_for(
                self.quick_op(),
                timeout=1.0
            )
        except asyncio.TimeoutError:
            results["quick"] = None

        # Multiple operations with timeout
        tasks = {
            "op1": self.slow_op1(),
            "op2": self.slow_op2(),
            "op3": self.slow_op3(),
        }

        done, pending = await asyncio.wait(
            tasks.values(),
            timeout=2.0,
            return_when=asyncio.ALL_COMPLETED
        )

        # Cancel pending tasks
        for task in pending:
            task.cancel()

        # Get completed results
        for task in done:
            try:
                result = await task
                # Find which operation
                for name, op_task in tasks.items():
                    if op_task == task:
                        results[name] = result
                        break
            except Exception as e:
                self.log(f"Task failed: {e}")

        return {"results": results}

    async def quick_op(self):
        await asyncio.sleep(0.5)
        return "quick"

    async def slow_op1(self):
        await asyncio.sleep(1.5)
        return "op1"

    async def slow_op2(self):
        await asyncio.sleep(1.0)
        return "op2"

    async def slow_op3(self):
        await asyncio.sleep(3.0)
        return "op3"
```

### Cancellation

Handle task cancellation:

```python
class CancellableNode(AsyncBaseNode):
    async def execute(self, state):
        """Support cancellation."""
        try:
            # Long-running operation
            for i in range(100):
                # Check for cancellation
                await asyncio.sleep(0.1)

                # Cooperative cancellation check
                if state.get("cancel_requested"):
                    return {"result": None, "cancelled": True}

                # Process item
                await self.process_item(i)

            return {"result": "complete", "cancelled": False}

        except asyncio.CancelledError:
            # Handle cancellation
            self.log("Task was cancelled")
            # Cleanup if needed
            await self.cleanup()
            raise  # Re-raise to propagate cancellation

    async def process_item(self, item):
        await asyncio.sleep(0.01)

    async def cleanup(self):
        """Cleanup on cancellation."""
        self.log("Cleaning up...")
        await asyncio.sleep(0.1)
```

---

## Concurrency Control

### asyncio.gather

Execute multiple coroutines concurrently:

```python
class GatherNode(AsyncBaseNode):
    async def execute(self, state):
        """Use gather for concurrent execution."""
        # Basic gather
        results = await asyncio.gather(
            self.fetch_user(state.user_id),
            self.fetch_posts(state.user_id),
            self.fetch_comments(state.user_id)
        )

        user, posts, comments = results

        return {
            "user": user,
            "posts": posts,
            "comments": comments
        }

    async def fetch_user(self, user_id):
        await asyncio.sleep(1)
        return {"id": user_id}

    async def fetch_posts(self, user_id):
        await asyncio.sleep(1)
        return []

    async def fetch_comments(self, user_id):
        await asyncio.sleep(1)
        return []

# Gather with error handling
class GatherErrorHandlingNode(AsyncBaseNode):
    async def execute(self, state):
        """Gather with return_exceptions."""
        results = await asyncio.gather(
            self.operation1(),
            self.operation2(),
            self.operation3(),
            return_exceptions=True  # Don't fail on first error
        )

        # Separate successes and failures
        successes = []
        failures = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failures.append({"op": i, "error": str(result)})
            else:
                successes.append({"op": i, "result": result})

        return {
            "successes": successes,
            "failures": failures
        }

    async def operation1(self):
        await asyncio.sleep(0.1)
        return "success1"

    async def operation2(self):
        await asyncio.sleep(0.1)
        raise ValueError("Operation 2 failed")

    async def operation3(self):
        await asyncio.sleep(0.1)
        return "success3"
```

### asyncio.wait

More control over task completion:

```python
class WaitNode(AsyncBaseNode):
    async def execute(self, state):
        """Use wait for flexible completion."""
        tasks = [
            asyncio.create_task(self.fast_op()),
            asyncio.create_task(self.medium_op()),
            asyncio.create_task(self.slow_op()),
        ]

        # Wait for first to complete
        done, pending = await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED
        )

        # Get first result
        first_result = done.pop().result()

        # Cancel remaining
        for task in pending:
            task.cancel()

        return {"first_result": first_result}

    async def fast_op(self):
        await asyncio.sleep(0.1)
        return "fast"

    async def medium_op(self):
        await asyncio.sleep(0.5)
        return "medium"

    async def slow_op(self):
        await asyncio.sleep(1.0)
        return "slow"

# Wait with timeout
class WaitTimeoutNode(AsyncBaseNode):
    async def execute(self, state):
        """Wait with timeout."""
        tasks = [
            asyncio.create_task(self.op1()),
            asyncio.create_task(self.op2()),
            asyncio.create_task(self.op3()),
        ]

        # Wait up to 2 seconds
        done, pending = await asyncio.wait(
            tasks,
            timeout=2.0
        )

        # Get completed results
        results = []
        for task in done:
            try:
                result = task.result()
                results.append(result)
            except Exception as e:
                self.log(f"Task failed: {e}")

        # Cancel incomplete tasks
        for task in pending:
            task.cancel()

        return {
            "completed": results,
            "incomplete_count": len(pending)
        }

    async def op1(self):
        await asyncio.sleep(1)
        return "op1"

    async def op2(self):
        await asyncio.sleep(1.5)
        return "op2"

    async def op3(self):
        await asyncio.sleep(3)
        return "op3"
```

### Semaphores

Limit concurrent operations:

```python
class SemaphoreNode(AsyncBaseNode):
    def __init__(self, max_concurrent=5, **kwargs):
        super().__init__(**kwargs)
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def execute(self, state):
        """Limit concurrent operations."""
        # Process many items with concurrency limit
        tasks = [
            self.process_with_limit(item)
            for item in state.items
        ]

        results = await asyncio.gather(*tasks)

        return {"results": results}

    async def process_with_limit(self, item):
        """Process item with semaphore."""
        async with self.semaphore:
            # Only max_concurrent will run at once
            return await self.process_item(item)

    async def process_item(self, item):
        await asyncio.sleep(0.1)
        return f"Processed {item}"

# Example: Limit API calls
class RateLimitedAPINode(AsyncBaseNode):
    def __init__(self, max_concurrent=3, **kwargs):
        super().__init__(**kwargs)
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def execute(self, state):
        """Rate limit API calls."""
        tasks = [
            self.fetch_with_limit(url)
            for url in state.urls
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter successful results
        successful = [r for r in results if not isinstance(r, Exception)]

        return {"results": successful}

    async def fetch_with_limit(self, url):
        """Fetch URL with semaphore."""
        async with self.semaphore:
            # Simulate API call
            await asyncio.sleep(0.5)
            return f"Data from {url}"
```

### Task Groups

Python 3.11+ task groups:

```python
class TaskGroupNode(AsyncBaseNode):
    async def execute(self, state):
        """Use task group for structured concurrency."""
        results = []

        # TaskGroup ensures all tasks complete or all fail
        async with asyncio.TaskGroup() as tg:
            task1 = tg.create_task(self.operation1())
            task2 = tg.create_task(self.operation2())
            task3 = tg.create_task(self.operation3())

        # All tasks completed successfully
        return {
            "results": [
                task1.result(),
                task2.result(),
                task3.result()
            ]
        }

    async def operation1(self):
        await asyncio.sleep(0.1)
        return "result1"

    async def operation2(self):
        await asyncio.sleep(0.2)
        return "result2"

    async def operation3(self):
        await asyncio.sleep(0.3)
        return "result3"
```

---

## Integration Patterns

### Async HTTP Clients

Using aiohttp:

```python
import aiohttp

class HTTPNode(AsyncBaseNode):
    async def execute(self, state):
        """Make HTTP requests with aiohttp."""
        async with aiohttp.ClientSession() as session:
            # GET request
            async with session.get(state.url) as response:
                data = await response.json()

            # POST request
            async with session.post(
                state.api_url,
                json={"query": state.query}
            ) as response:
                result = await response.json()

        return {"data": data, "result": result}

# With error handling
class RobustHTTPNode(AsyncBaseNode):
    async def execute(self, state):
        """HTTP with error handling."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    state.url,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return {"data": data, "error": None}

            except aiohttp.ClientError as e:
                self.log(f"HTTP error: {e}")
                return {"data": None, "error": str(e)}

            except asyncio.TimeoutError:
                return {"data": None, "error": "timeout"}
```

### Async Database Operations

Using asyncpg (PostgreSQL):

```python
import asyncpg

class DatabaseNode(AsyncBaseNode):
    async def execute(self, state):
        """Query database asynchronously."""
        # Connect to database
        conn = await asyncpg.connect(
            user='user',
            password='password',
            database='database',
            host='localhost'
        )

        try:
            # Execute query
            rows = await conn.fetch(
                'SELECT * FROM users WHERE id = $1',
                state.user_id
            )

            # Process results
            users = [dict(row) for row in rows]

            return {"users": users}

        finally:
            await conn.close()

# With connection pool
class PooledDatabaseNode(AsyncBaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pool = None

    async def execute(self, state):
        """Use connection pool."""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                user='user',
                password='password',
                database='database',
                host='localhost',
                min_size=10,
                max_size=20
            )

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                'SELECT * FROM users WHERE id = $1',
                state.user_id
            )
            return {"users": [dict(row) for row in rows]}
```

### Async File I/O

Using aiofiles:

```python
import aiofiles

class FileNode(AsyncBaseNode):
    async def execute(self, state):
        """Read/write files asynchronously."""
        # Read file
        async with aiofiles.open(state.input_file, 'r') as f:
            content = await f.read()

        # Process content
        processed = content.upper()

        # Write file
        async with aiofiles.open(state.output_file, 'w') as f:
            await f.write(processed)

        return {"processed": True}

# Process multiple files concurrently
class MultiFileNode(AsyncBaseNode):
    async def execute(self, state):
        """Process multiple files concurrently."""
        tasks = [
            self.process_file(file_path)
            for file_path in state.files
        ]

        results = await asyncio.gather(*tasks)

        return {"results": results}

    async def process_file(self, file_path):
        """Process single file."""
        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()

        # Process
        processed = len(content)

        return {"file": file_path, "length": processed}
```

### Mixed Sync/Async Code

Run sync code in async context:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class MixedNode(AsyncBaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.executor = ThreadPoolExecutor(max_workers=5)

    async def execute(self, state):
        """Mix sync and async operations."""
        # Async operation
        async_result = await self.async_operation(state.input)

        # Run sync operation in thread pool
        loop = asyncio.get_event_loop()
        sync_result = await loop.run_in_executor(
            self.executor,
            self.sync_operation,
            state.input
        )

        return {
            "async_result": async_result,
            "sync_result": sync_result
        }

    async def async_operation(self, input_data):
        """Async operation."""
        await asyncio.sleep(1)
        return f"Async: {input_data}"

    def sync_operation(self, input_data):
        """Blocking sync operation."""
        import time
        time.sleep(1)  # Blocks thread, not event loop
        return f"Sync: {input_data}"
```

---

## Best Practices

### 1. Always await async operations

```python
# ✅ Correct
result = await async_function()

# ❌ Wrong - doesn't wait
result = async_function()  # Returns coroutine, not result
```

### 2. Use async context managers

```python
# ✅ Correct - properly closes
async with aiohttp.ClientSession() as session:
    await session.get(url)

# ❌ Wrong - might leak connections
session = aiohttp.ClientSession()
await session.get(url)
# session.close() might not be called
```

### 3. Handle errors in concurrent operations

```python
# ✅ Correct - handles errors
results = await asyncio.gather(
    op1(), op2(), op3(),
    return_exceptions=True
)

# ❌ Wrong - first error stops everything
results = await asyncio.gather(op1(), op2(), op3())
```

### 4. Use semaphores for rate limiting

```python
# ✅ Correct - limits concurrency
semaphore = asyncio.Semaphore(5)
async with semaphore:
    await expensive_operation()

# ❌ Wrong - no limits
await expensive_operation()
```

### 5. Set timeouts for external calls

```python
# ✅ Correct - won't hang forever
result = await asyncio.wait_for(api_call(), timeout=30)

# ❌ Wrong - might hang indefinitely
result = await api_call()
```

### 6. Clean up resources

```python
# ✅ Correct
try:
    conn = await connect()
    result = await conn.query()
finally:
    await conn.close()

# Or use context manager
async with connect() as conn:
    result = await conn.query()
```

### 7. Don't mix blocking and async

```python
# ✅ Correct - use async library
async with aiofiles.open(file) as f:
    content = await f.read()

# ❌ Wrong - blocks event loop
with open(file) as f:
    content = f.read()
```

### 8. Use appropriate concurrency patterns

```python
# ✅ Parallel independent operations
results = await asyncio.gather(op1(), op2(), op3())

# ✅ Sequential dependent operations
r1 = await op1()
r2 = await op2(r1)
r3 = await op3(r2)
```

---

## Common Pitfalls

### 1. Forgetting await

```python
# ❌ Wrong
async def execute(self, state):
    result = self.async_operation()  # Forgot await
    return {"result": result}  # Returns coroutine object!

# ✅ Correct
async def execute(self, state):
    result = await self.async_operation()
    return {"result": result}
```

### 2. Using time.sleep instead of asyncio.sleep

```python
# ❌ Wrong - blocks event loop
async def execute(self, state):
    time.sleep(1)  # Blocks everything!
    return {}

# ✅ Correct
async def execute(self, state):
    await asyncio.sleep(1)
    return {}
```

### 3. Not handling cancellation

```python
# ❌ Wrong - no cleanup
async def execute(self, state):
    await long_operation()
    return {}

# ✅ Correct
async def execute(self, state):
    try:
        await long_operation()
        return {}
    except asyncio.CancelledError:
        await self.cleanup()
        raise
```

### 4. Creating too many concurrent tasks

```python
# ❌ Wrong - no limits
tasks = [self.fetch(url) for url in urls]  # 1000 URLs!
results = await asyncio.gather(*tasks)

# ✅ Correct - use semaphore
semaphore = asyncio.Semaphore(10)
async def fetch_limited(url):
    async with semaphore:
        return await self.fetch(url)

tasks = [fetch_limited(url) for url in urls]
results = await asyncio.gather(*tasks)
```

### 5. Not setting timeouts

```python
# ❌ Wrong - might hang forever
result = await external_api_call()

# ✅ Correct
try:
    result = await asyncio.wait_for(
        external_api_call(),
        timeout=30
    )
except asyncio.TimeoutError:
    result = None
```

---

## Performance Optimization

### 1. Use connection pooling

```python
# ✅ Reuse connections
class OptimizedNode(AsyncBaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = None

    async def execute(self, state):
        if self.session is None:
            self.session = aiohttp.ClientSession()

        # Reuse session
        async with self.session.get(url) as response:
            return await response.json()
```

### 2. Batch operations

```python
# ✅ Batch requests
async def execute(self, state):
    # Batch into groups of 10
    results = []
    for i in range(0, len(state.items), 10):
        batch = state.items[i:i+10]
        batch_results = await asyncio.gather(
            *[self.process(item) for item in batch]
        )
        results.extend(batch_results)

    return {"results": results}
```

### 3. Use appropriate concurrency levels

```python
# ✅ Tune concurrency
semaphore = asyncio.Semaphore(optimal_level)
# Test with different values: 5, 10, 20, 50
```

### 4. Cache results

```python
# ✅ Cache expensive operations
class CachedNode(AsyncBaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cache = {}

    async def execute(self, state):
        key = state.query

        if key in self.cache:
            return self.cache[key]

        result = await expensive_operation(key)
        self.cache[key] = result
        return result
```

---

## Testing Async Nodes

### Unit testing

```python
import pytest

@pytest.mark.asyncio
async def test_async_node():
    """Test async node."""
    node = MyAsyncNode()

    state = {"input": "test"}
    result = await node(state)

    assert "output" in result
    assert result["output"] == "expected"

# With mocking
@pytest.mark.asyncio
async def test_with_mock():
    """Test with mocked async function."""
    node = MyAsyncNode()

    # Mock async method
    async def mock_fetch():
        return "mocked data"

    node.fetch_data = mock_fetch

    state = {"input": "test"}
    result = await node(state)

    assert result["data"] == "mocked data"
```

### Testing timeouts

```python
@pytest.mark.asyncio
async def test_timeout():
    """Test timeout handling."""
    node = TimeoutNode()

    state = {"slow": True}
    result = await node(state)

    assert result["timed_out"] is True
```

### Testing concurrent operations

```python
@pytest.mark.asyncio
async def test_concurrent():
    """Test concurrent execution."""
    node = ConcurrentNode()

    state = {"items": [1, 2, 3]}

    import time
    start = time.time()
    result = await node(state)
    elapsed = time.time() - start

    # Should be concurrent, not sequential
    assert elapsed < 2  # Not 3+ seconds
    assert len(result["results"]) == 3
```

---

## Troubleshooting

### Issue: "RuntimeError: This event loop is already running"

**Cause:** Trying to run async code in already-running loop

**Fix:**
```python
# ❌ Wrong - in Jupyter/async context
asyncio.run(my_coroutine())

# ✅ Correct
await my_coroutine()
```

### Issue: "coroutine was never awaited"

**Cause:** Forgot to await async function

**Fix:**
```python
# ❌ Wrong
result = async_function()

# ✅ Correct
result = await async_function()
```

### Issue: Slow performance despite async

**Cause:** Not actually running concurrently

**Fix:**
```python
# ❌ Wrong - sequential
for item in items:
    result = await process(item)

# ✅ Correct - concurrent
results = await asyncio.gather(*[process(item) for item in items])
```

### Issue: "TimeoutError" on slow operations

**Cause:** Timeout too short

**Fix:**
```python
# Increase timeout
result = await asyncio.wait_for(operation(), timeout=60)

# Or remove timeout for very slow operations
result = await operation()
```

### Issue: Resource leaks

**Cause:** Not closing connections properly

**Fix:**
```python
# ✅ Use context managers
async with aiohttp.ClientSession() as session:
    await session.get(url)

# Or ensure cleanup
session = aiohttp.ClientSession()
try:
    await session.get(url)
finally:
    await session.close()
```

---

## Summary

**Key takeaways:**
- Use `AsyncBaseNode` for I/O-bound operations
- Always `await` async operations
- Use `asyncio.gather()` for concurrency
- Set timeouts on external calls
- Use semaphores for rate limiting
- Handle errors with `return_exceptions=True`
- Use async context managers for resources
- Test with `@pytest.mark.asyncio`

**When to use async:**
- HTTP/API calls
- Database queries
- File I/O
- Multiple independent operations
- Streaming data

**When to use sync:**
- CPU-bound operations
- Simple transformations
- No I/O operations
- Legacy sync libraries

**References:**
- Python asyncio: https://docs.python.org/3/library/asyncio.html
- aiohttp: https://docs.aiohttp.org/
- asyncpg: https://magicstack.github.io/asyncpg/
- LangChain async: https://python.langchain.com/docs/how_to/async
