# State Patterns Catalog

Comprehensive patterns for LangGraph state design.

## Table of Contents

1. [Basic Patterns](#basic-patterns)
2. [Message Patterns](#message-patterns)
3. [Data Processing Patterns](#data-processing-patterns)
4. [Control Flow Patterns](#control-flow-patterns)
5. [Error Handling Patterns](#error-handling-patterns)
6. [Multi-Agent Patterns](#multi-agent-patterns)

## Basic Patterns

### Minimal State

Simplest possible state structure:

```python
@dataclass(kw_only=True)
class State:
    input: str
    output: str = ""
```

**Use when:**
- Simple input → output transformation
- No intermediate state needed
- Single-pass processing

### Accumulator State

State that accumulates values:

```python
def accumulate_list(old: list, new: list) -> list:
    return old + new

@dataclass(kw_only=True)
class State:
    items: Annotated[list[str], accumulate_list] = None
    count: Annotated[int, lambda old, new: old + new] = 0
```

**Use when:**
- Collecting items across nodes
- Aggregating metrics
- Building result lists

### Versioned State

Track state versions:

```python
@dataclass(kw_only=True)
class State:
    data: dict
    version: int = 0
    history: list[dict] = None

def update_node(state: State) -> dict:
    return {
        "data": new_data,
        "version": state.version + 1,
        "history": state.history + [state.data] if state.history else [state.data]
    }
```

**Use when:**
- Need to track changes
- Rollback capability required
- Debugging state evolution

## Message Patterns

### Basic Chat

Standard chat application:

```python
@dataclass(kw_only=True)
class State:
    messages: Annotated[list[AnyMessage], add_messages]

def chat_node(state: State) -> dict:
    response = model.invoke(state.messages)
    return {"messages": [response]}
```

### System Prompt Injection

Add system prompt dynamically:

```python
@dataclass(kw_only=True)
class State:
    messages: Annotated[list[AnyMessage], add_messages]
    system_context: str = ""

def prepare_node(state: State) -> dict:
    system_msg = SystemMessage(content=state.system_context)
    return {"messages": [system_msg]}
```

### Message Filtering

Filter messages before processing:

```python
def filter_node(state: State) -> dict:
    # Keep only last 10 messages
    recent = state.messages[-10:]

    # Or filter by type
    user_messages = [m for m in state.messages if isinstance(m, HumanMessage)]

    # Return filtered (this replaces messages!)
    # Be careful: this pattern needs custom reducer
    return {"filtered_messages": recent}
```

### Conversation Summarization

Summarize long conversations:

```python
@dataclass(kw_only=True)
class State:
    messages: Annotated[list[AnyMessage], add_messages]
    summary: str = ""
    summary_threshold: int = 20

def maybe_summarize(state: State) -> dict:
    if len(state.messages) > state.summary_threshold:
        # Summarize old messages
        summary = summarize_messages(state.messages[:-10])

        # Keep recent messages + summary
        return {
            "summary": summary,
            "messages": state.messages[-10:]  # Careful: replaces!
        }
    return {}
```

## Data Processing Patterns

### Pipeline State

Multi-stage data processing:

```python
@dataclass(kw_only=True)
class State:
    raw_data: bytes = None
    parsed_data: list = None
    cleaned_data: list = None
    transformed_data: list = None
    result: dict = None

    # Metadata
    stage: str = "start"
    errors: Annotated[list[str], lambda old, new: old + new] = None

# Stage 1: Parse
def parse_node(state: State) -> dict:
    parsed = parse_raw(state.raw_data)
    return {
        "parsed_data": parsed,
        "stage": "parsed"
    }

# Stage 2: Clean
def clean_node(state: State) -> dict:
    cleaned = clean_data(state.parsed_data)
    return {
        "cleaned_data": cleaned,
        "stage": "cleaned"
    }
```

### Batch Processing

Process items in batches:

```python
@dataclass(kw_only=True)
class State:
    items: list[str]
    processed: Annotated[list[dict], lambda old, new: old + new] = None
    current_batch: int = 0
    batch_size: int = 10

def process_batch(state: State) -> dict:
    start = state.current_batch * state.batch_size
    end = start + state.batch_size
    batch = state.items[start:end]

    results = [process_item(item) for item in batch]

    return {
        "processed": results,
        "current_batch": state.current_batch + 1
    }
```

### Streaming Results

Accumulate streaming data:

```python
@dataclass(kw_only=True)
class State:
    query: str
    chunks: Annotated[list[str], lambda old, new: old + new] = None
    complete: bool = False

def stream_node(state: State) -> dict:
    for chunk in stream_data(state.query):
        yield {"chunks": [chunk]}

    yield {"complete": True}
```

## Control Flow Patterns

### Retry State

Track retry attempts:

```python
@dataclass(kw_only=True)
class State:
    task: str
    result: str = None
    retry_count: int = 0
    max_retries: int = 3
    last_error: str = None

def task_node(state: State) -> dict:
    try:
        result = perform_task(state.task)
        return {"result": result}
    except Exception as e:
        return {
            "retry_count": state.retry_count + 1,
            "last_error": str(e)
        }

def should_retry(state: State) -> str:
    if state.result:
        return "success"
    if state.retry_count >= state.max_retries:
        return "fail"
    return "retry"
```

### Iteration State

Count iterations:

```python
@dataclass(kw_only=True)
class State:
    input: str
    output: str = None
    iterations: int = 0
    max_iterations: int = 5

def iterate_node(state: State) -> dict:
    output = improve_output(state.input, state.output)
    return {
        "output": output,
        "iterations": state.iterations + 1
    }

def should_continue(state: State) -> str:
    if is_good_enough(state.output):
        return "done"
    if state.iterations >= state.max_iterations:
        return "max_reached"
    return "continue"
```

### Branching State

Track which branch taken:

```python
@dataclass(kw_only=True)
class State:
    input: str
    branch: str = ""
    result_a: str = None
    result_b: str = None

def router(state: State) -> str:
    if should_use_a(state.input):
        return "branch_a"
    return "branch_b"

def branch_a(state: State) -> dict:
    return {
        "result_a": process_a(state.input),
        "branch": "a"
    }

def branch_b(state: State) -> dict:
    return {
        "result_b": process_b(state.input),
        "branch": "b"
    }
```

## Error Handling Patterns

### Error Accumulation

Collect errors across nodes:

```python
@dataclass(kw_only=True)
class State:
    tasks: list[str]
    results: list[dict] = None
    errors: Annotated[list[dict], lambda old, new: old + new] = None

def task_node(state: State) -> dict:
    try:
        result = process_task(state.tasks[0])
        return {"results": [result]}
    except Exception as e:
        return {"errors": [{
            "task": state.tasks[0],
            "error": str(e),
            "timestamp": datetime.now()
        }]}
```

### Error Recovery State

Track and recover from errors:

```python
@dataclass(kw_only=True)
class State:
    input: str
    output: str = None
    error: str = None
    recovery_attempted: bool = False

def main_node(state: State) -> dict:
    try:
        return {"output": process(state.input)}
    except Exception as e:
        return {"error": str(e)}

def recover_node(state: State) -> dict:
    try:
        # Attempt recovery
        return {
            "output": recover(state.input, state.error),
            "recovery_attempted": True
        }
    except Exception as e:
        return {
            "error": f"Recovery failed: {e}",
            "recovery_attempted": True
        }
```

### Validation State

Track validation results:

```python
@dataclass(kw_only=True)
class State:
    data: dict
    validated: bool = False
    validation_errors: list[str] = None

def validate_node(state: State) -> dict:
    errors = validate_data(state.data)

    return {
        "validated": len(errors) == 0,
        "validation_errors": errors if errors else None
    }
```

## Multi-Agent Patterns

### Agent Registry

Track multiple agents:

```python
@dataclass(kw_only=True)
class State:
    messages: Annotated[list[AnyMessage], add_messages]
    current_agent: str = "coordinator"
    agent_outputs: dict = None

def coordinator(state: State) -> dict:
    next_agent = decide_next_agent(state.messages)
    return {"current_agent": next_agent}

def agent_a(state: State) -> dict:
    response = agent_a_logic(state.messages)
    return {
        "messages": [response],
        "agent_outputs": {**state.agent_outputs, "agent_a": response}
    }
```

### Shared Context

Agents share context:

```python
@dataclass(kw_only=True)
class State:
    query: str
    context: dict = None
    agent_results: Annotated[list[dict], lambda old, new: old + new] = None

def researcher(state: State) -> dict:
    findings = research(state.query)
    return {
        "context": {**state.context, "research": findings},
        "agent_results": [{"agent": "researcher", "data": findings}]
    }

def analyst(state: State) -> dict:
    # Use context from researcher
    analysis = analyze(state.context.get("research", {}))
    return {
        "context": {**state.context, "analysis": analysis},
        "agent_results": [{"agent": "analyst", "data": analysis}]
    }
```

### Parallel Agent Execution

Execute agents in parallel:

```python
@dataclass(kw_only=True)
class State:
    input: str
    agent_1_result: str = None
    agent_2_result: str = None
    agent_3_result: str = None
    combined_result: str = None

# Parallel nodes
def agent_1(state: State) -> dict:
    return {"agent_1_result": process_1(state.input)}

def agent_2(state: State) -> dict:
    return {"agent_2_result": process_2(state.input)}

def agent_3(state: State) -> dict:
    return {"agent_3_result": process_3(state.input)}

# Combine results
def combine(state: State) -> dict:
    results = [
        state.agent_1_result,
        state.agent_2_result,
        state.agent_3_result
    ]
    return {"combined_result": merge_results(results)}
```

## Advanced Patterns

### Subgraph State

State for nested subgraphs:

```python
@dataclass(kw_only=True)
class ParentState:
    query: str
    subgraph_result: dict = None
    final_result: str = None

@dataclass(kw_only=True)
class SubgraphState:
    # Inherits from parent
    query: str
    # Subgraph-specific
    intermediate: str = None
    result: dict = None

# Subgraph returns only 'result' to parent
def subgraph_node(state: SubgraphState) -> dict:
    return {
        "intermediate": process(state.query),
        "result": finalize(state.intermediate)
    }
```

### Channel State

Custom channels for specific data:

```python
from langgraph.graph import StateGraph
from langgraph.channels import LastValue, Topic

# Define channels
channels = {
    "input": LastValue(str),
    "output": LastValue(str),
    "logs": Topic(list[str]),  # Accumulates
}

@dataclass(kw_only=True)
class State:
    input: str
    output: str
    logs: list[str]
```

### Private State

Hide state from external API:

```python
@dataclass(kw_only=True)
class InputState:
    query: str

@dataclass(kw_only=True)
class OutputState:
    answer: str

@dataclass(kw_only=True)
class State:
    # Public
    query: str
    answer: str

    # Private (not in Input/Output)
    _api_key: str = None
    _cache: dict = None
    _debug: list = None
```

## Best Practices Summary

1. **Use three-layer state** (Input/Output/State) for clear API boundaries
2. **Choose reducers carefully** - messages accumulate, status replaces
3. **Document state fields** with clear docstrings
4. **Keep state flat** when possible
5. **Use typed annotations** for better IDE support
6. **Provide defaults** for optional fields
7. **Track metadata** (iterations, errors, timestamps)
8. **Version state** for debugging and rollback

## References

- LangGraph State API: https://docs.langchain.com/oss/python/langgraph/graph-api#state
- Reducers: https://docs.langchain.com/oss/python/langgraph/graph-api#reducers
- Messages: https://docs.langchain.com/oss/python/langchain/messages
