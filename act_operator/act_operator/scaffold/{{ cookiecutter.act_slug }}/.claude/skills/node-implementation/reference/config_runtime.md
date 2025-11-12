# Config and Runtime Parameters

## Table of Contents

- [Introduction](#introduction)
- [Config Parameter](#config-parameter)
  - [Structure](#structure)
  - [Accessing Config](#accessing-config)
  - [Thread ID](#thread-id)
  - [Run ID](#run-id)
  - [Tags and Metadata](#tags-and-metadata)
  - [Custom Configurable Values](#custom-configurable-values)
- [Runtime Parameter](#runtime-parameter)
  - [Structure](#structure-1)
  - [Store Interface](#store-interface)
  - [Stream Interface](#stream-interface)
  - [Store Operations](#store-operations)
  - [Namespace Design](#namespace-design)
- [Practical Examples](#practical-examples)
  - [Per-Thread State](#per-thread-state)
  - [Cross-Thread Sharing](#cross-thread-sharing)
  - [Caching Pattern](#caching-pattern)
  - [User Preferences](#user-preferences)
  - [Session Management](#session-management)
- [Best Practices](#best-practices)
- [Common Patterns](#common-patterns)
- [Troubleshooting](#troubleshooting)

---

## Introduction

Config and runtime parameters provide access to execution context and persistent storage. Understanding how to use them effectively enables building stateful, multi-user applications.

**When to use:**
- **Config**: Need thread_id, run_id, tags, or custom configuration
- **Runtime**: Need persistent storage across runs or streaming

---

## Config Parameter

### Structure

```python
config: RunnableConfig = {
    "configurable": {
        "thread_id": "user-123-session-456",
        "checkpoint_ns": "",
        # ... custom values
    },
    "run_id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
    "tags": ["production", "user-tier-premium"],
    "metadata": {
        "user_id": "user-123",
        "session_start": "2024-01-15T10:30:00Z"
    },
    "callbacks": [...],  # LangChain callbacks
    "recursion_limit": 25
}
```

### Accessing Config

```python
class MyNode(BaseNode):
    def execute(self, state, config):
        # Always check if config exists
        if not config:
            # Handle missing config
            return {"result": "no config"}
        
        # Access configurable
        thread_id = config.get("configurable", {}).get("thread_id")
        
        # Access other fields
        run_id = config.get("run_id")
        tags = config.get("tags", [])
        metadata = config.get("metadata", {})
        
        return {"thread_id": thread_id}
```

### Thread ID

**Purpose:** Identify conversation/session thread

**Helper method (recommended):**
```python
def execute(self, state, config):
    thread_id = self.get_thread_id(config)
    # Returns thread_id or None if not available
```

**Manual access:**
```python
def execute(self, state, config):
    if config and "configurable" in config:
        thread_id = config["configurable"].get("thread_id")
    else:
        thread_id = None
```

**Usage patterns:**
```python
# Log thread for debugging
self.log(f"Processing thread: {thread_id}")

# Per-thread logic
if thread_id == "admin-thread":
    # Special handling
    pass

# Store thread-specific data
if runtime and runtime.store:
    runtime.store.put(("threads", thread_id), "data", value)
```

### Run ID

**Purpose:** Unique identifier for this specific graph execution

```python
def execute(self, state, config):
    run_id = config.get("run_id") if config else None
    
    # Use for correlation in logs
    self.log(f"Run {run_id}: Processing {state.query}")
    
    # Track run metrics
    if runtime and runtime.store:
        runtime.store.put(("runs",), run_id, {
            "start_time": time.time(),
            "query": state.query
        })
```

### Tags and Metadata

**Tags:** List of string labels
```python
def execute(self, state, config):
    tags = config.get("tags", []) if config else []
    
    # Conditional logic based on tags
    if "debug" in tags:
        self.log("Debug mode enabled")
        return {"verbose_output": True}
    
    if "premium" in tags:
        # Premium features
        pass
```

**Metadata:** Dictionary of additional context
```python
def execute(self, state, config):
    metadata = config.get("metadata", {}) if config else {}
    
    user_id = metadata.get("user_id")
    locale = metadata.get("locale", "en")
    
    # Use metadata for customization
    greeting = get_greeting(locale)
    return {"greeting": greeting}
```

### Custom Configurable Values

**Setting custom values:**
```python
from langgraph.graph import RunnableConfig

config = RunnableConfig(
    configurable={
        "thread_id": "thread-123",
        "model_name": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1000
    }
)

result = graph.invoke({"query": "Hello"}, config=config)
```

**Accessing in node:**
```python
def execute(self, state, config):
    configurable = config.get("configurable", {}) if config else {}
    
    model_name = configurable.get("model_name", "gpt-3.5-turbo")
    temperature = configurable.get("temperature", 0.5)
    
    # Use configuration
    model = ChatOpenAI(model=model_name, temperature=temperature)
```

---

## Runtime Parameter

### Structure

```python
runtime = RuntimeObject(
    store=BaseStore(...),  # or None
    stream=StreamInterface(...)  # or None
)
```

### Store Interface

**Core methods:**
```python
# Put: store.put(namespace_tuple, key, value)
runtime.store.put(("users", "123"), "preferences", {...})

# Get: store.get(namespace_tuple, key) -> value or None
prefs = runtime.store.get(("users", "123"), "preferences")

# Search: store.search(namespace_prefix) -> list of items
items = runtime.store.search(("users", "123"))

# Delete: store.delete(namespace_tuple, key)
runtime.store.delete(("users", "123"), "old_data")
```

### Stream Interface

**For streaming outputs:**
```python
def execute(self, state, runtime):
    if runtime and runtime.stream:
        # Stream tokens as they arrive
        for token in generate_tokens(state.query):
            runtime.stream.send(token)
    
    return {"result": "complete"}
```

### Store Operations

**Basic usage:**
```python
def execute(self, state, runtime):
    # Always check if store exists
    if not runtime or not runtime.store:
        return {"result": "no store"}
    
    # Put data
    runtime.store.put(
        namespace=("app", "cache"),
        key="computed_result",
        value={"data": [1, 2, 3], "timestamp": time.time()}
    )
    
    # Get data
    cached = runtime.store.get(("app", "cache"), "computed_result")
    
    if cached:
        return {"result": cached["data"]}
    else:
        # Compute and cache
        result = expensive_computation()
        runtime.store.put(("app", "cache"), "computed_result", result)
        return {"result": result}
```

**Listing all keys in namespace:**
```python
def execute(self, state, runtime):
    if runtime and runtime.store:
        # Get all items in namespace
        items = runtime.store.search(("users", "123"))
        
        # items is a list of (key, value) tuples
        for key, value in items:
            print(f"{key}: {value}")
    
    return {}
```

### Namespace Design

**Hierarchical organization:**
```python
# User data
("users", user_id)
("users", user_id, "preferences")
("users", user_id, "history")

# Thread data
("threads", thread_id)
("threads", thread_id, "context")

# Global data
("global", "config")
("global", "cache")

# Organization hierarchy
("org", org_id, "dept", dept_id)
("org", org_id, "dept", dept_id, "team", team_id)
```

**Best practices:**
- Use tuples for namespaces: `("a", "b")` not `"a/b"`
- Keep hierarchy shallow (2-4 levels)
- Use consistent naming
- Document namespace structure

---

## Practical Examples

### Per-Thread State

Track state per conversation thread:

```python
class ThreadAwareNode(BaseNode):
    def execute(self, state, config, runtime):
        thread_id = self.get_thread_id(config)
        
        if runtime and runtime.store and thread_id:
            # Get thread-specific counter
            counter_key = f"counter_{thread_id}"
            counter = runtime.store.get(("threads",), counter_key)
            
            if counter is None:
                counter = 0
            
            counter += 1
            
            # Update thread-specific counter
            runtime.store.put(("threads",), counter_key, counter)
            
            return {"message_count": counter}
        
        return {}
```

### Cross-Thread Sharing

Share data across threads:

```python
class SharedCacheNode(BaseNode):
    def execute(self, state, runtime):
        if not runtime or not runtime.store:
            return {}
        
        # Check global cache
        cache_key = f"result_{state.query_hash}"
        cached = runtime.store.get(("global", "cache"), cache_key)
        
        if cached:
            return {"result": cached, "from_cache": True}
        
        # Compute and cache globally
        result = expensive_operation(state.query)
        runtime.store.put(("global", "cache"), cache_key, result)
        
        return {"result": result, "from_cache": False}
```

### Caching Pattern

Implement caching with TTL:

```python
import time

class CachingNode(BaseNode):
    def __init__(self, ttl_seconds=3600, **kwargs):
        super().__init__(**kwargs)
        self.ttl = ttl_seconds
    
    def execute(self, state, runtime):
        if not runtime or not runtime.store:
            # No cache available
            return {"result": self.compute(state)}
        
        cache_key = self.get_cache_key(state)
        cached = runtime.store.get(("cache",), cache_key)
        
        # Check if cache valid
        if cached and (time.time() - cached["timestamp"]) < self.ttl:
            return {"result": cached["value"], "cache_hit": True}
        
        # Compute and cache
        result = self.compute(state)
        runtime.store.put(("cache",), cache_key, {
            "value": result,
            "timestamp": time.time()
        })
        
        return {"result": result, "cache_hit": False}
    
    def compute(self, state):
        return expensive_computation(state.input)
    
    def get_cache_key(self, state):
        import hashlib
        return hashlib.md5(state.input.encode()).hexdigest()
```

### User Preferences

Store and retrieve user preferences:

```python
class PreferenceAwareNode(BaseNode):
    def execute(self, state, config, runtime):
        if not config or not runtime or not runtime.store:
            # Use defaults
            return self.process_with_defaults(state)
        
        # Get user_id from metadata
        metadata = config.get("metadata", {})
        user_id = metadata.get("user_id")
        
        if not user_id:
            return self.process_with_defaults(state)
        
        # Load user preferences
        prefs = runtime.store.get(("users", user_id), "preferences")
        
        if not prefs:
            prefs = self.get_default_preferences()
            runtime.store.put(("users", user_id), "preferences", prefs)
        
        # Use preferences
        return self.process_with_preferences(state, prefs)
    
    def get_default_preferences(self):
        return {
            "language": "en",
            "verbosity": "normal",
            "format": "text"
        }
```

### Session Management

Track session state:

```python
class SessionNode(BaseNode):
    def execute(self, state, config, runtime):
        thread_id = self.get_thread_id(config)
        
        if not thread_id or not runtime or not runtime.store:
            return {}
        
        # Get session data
        session = runtime.store.get(("sessions",), thread_id)
        
        if not session:
            # New session
            session = {
                "created_at": time.time(),
                "message_count": 0,
                "last_activity": time.time()
            }
        
        # Update session
        session["message_count"] += 1
        session["last_activity"] = time.time()
        session["last_query"] = state.query
        
        # Save session
        runtime.store.put(("sessions",), thread_id, session)
        
        return {
            "session_message_count": session["message_count"],
            "session_duration": time.time() - session["created_at"]
        }
```

---

## Best Practices

1. **Always check if parameters exist:**
   ```python
   if config:
       thread_id = self.get_thread_id(config)
   
   if runtime and runtime.store:
       # Use store
   ```

2. **Provide fallbacks:**
   ```python
   thread_id = self.get_thread_id(config) or "default"
   ```

3. **Use helper methods:**
   ```python
   # ✅ Good
   thread_id = self.get_thread_id(config)
   
   # ❌ Verbose
   thread_id = config.get("configurable", {}).get("thread_id") if config else None
   ```

4. **Document namespace structure:**
   ```python
   """
   Store namespaces:
   - ("users", user_id): User-specific data
   - ("threads", thread_id): Thread-specific data
   - ("cache",): Global cache
   """
   ```

5. **Handle missing data gracefully:**
   ```python
   cached = runtime.store.get(namespace, key)
   if cached is None:
       # Compute default
   ```

6. **Use descriptive keys:**
   ```python
   # ✅ Good
   runtime.store.put(("users", "123"), "preferences", {...})
   
   # ❌ Bad
   runtime.store.put(("u", "123"), "p", {...})
   ```

7. **Implement cache invalidation:**
   ```python
   if should_invalidate_cache(state):
       runtime.store.delete(("cache",), cache_key)
   ```

8. **Log store operations in debug mode:**
   ```python
   if self.verbose:
       self.log(f"Cache hit for key: {key}")
   ```

---

## Common Patterns

### Pattern: Feature Flags

```python
def execute(self, state, config):
    tags = config.get("tags", []) if config else []
    
    feature_enabled = "beta-features" in tags
    
    if feature_enabled:
        return self.new_implementation(state)
    else:
        return self.stable_implementation(state)
```

### Pattern: A/B Testing

```python
def execute(self, state, config):
    metadata = config.get("metadata", {}) if config else {}
    variant = metadata.get("ab_variant", "A")
    
    if variant == "B":
        return self.variant_b_logic(state)
    else:
        return self.variant_a_logic(state)
```

### Pattern: Rate Limiting

```python
import time

def execute(self, state, config, runtime):
    thread_id = self.get_thread_id(config)
    
    if runtime and runtime.store and thread_id:
        # Check rate limit
        rate_key = f"rate_{thread_id}"
        rate_data = runtime.store.get(("rate_limits",), rate_key)
        
        now = time.time()
        
        if rate_data:
            count = rate_data.get("count", 0)
            window_start = rate_data.get("window_start", now)
            
            # Reset window if expired (60 seconds)
            if now - window_start > 60:
                count = 0
                window_start = now
            
            if count >= 10:  # Max 10 per minute
                return {"error": "Rate limit exceeded"}
            
            count += 1
        else:
            count = 1
            window_start = now
        
        runtime.store.put(("rate_limits",), rate_key, {
            "count": count,
            "window_start": window_start
        })
    
    return {"result": "processed"}
```

---

## Troubleshooting

### Issue: config is always None

**Cause:** Not passing config when invoking graph

**Fix:**
```python
from langgraph.graph import RunnableConfig

config = RunnableConfig(
    configurable={"thread_id": "thread-123"}
)
result = graph.invoke({"input": "data"}, config=config)
```

### Issue: runtime.store is None

**Cause:** Store not configured in graph compilation

**Fix:**
```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

checkpointer = MemorySaver()
store = InMemoryStore()

graph = builder.compile(
    checkpointer=checkpointer,
    store=store
)
```

### Issue: Store data not persisting

**Cause:** Using in-memory store, data lost on restart

**Fix:**
```python
# Use persistent store
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

checkpointer = PostgresSaver(...)
store = PostgresStore(...)
```

### Issue: Cannot access custom configurable values

**Cause:** Typo in key or not passing in config

**Debug:**
```python
def execute(self, state, config):
    self.log("Config:", config=config)
    configurable = config.get("configurable", {}) if config else {}
    self.log("Configurable:", configurable=configurable)
    
    value = configurable.get("my_key")
    self.log("Value:", value=value)
```

---

## Summary

**Config provides:**
- Thread identification (`thread_id`)
- Run tracking (`run_id`)
- Execution metadata (`tags`, `metadata`)
- Custom configuration values

**Runtime provides:**
- Persistent storage (`runtime.store`)
- Streaming interface (`runtime.stream`)

**Key principles:**
- Always check if parameters exist
- Use helper methods (`self.get_thread_id()`)
- Provide sensible fallbacks
- Document namespace structure
- Handle missing data gracefully
- Use descriptive keys
