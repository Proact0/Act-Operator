# Stream Filtering

Filter v3 event streams by projection, graph_name, message.node, or LLM tag.

`casts/{cast_name}/modules/` and `casts/{cast_name}/graph.py` are reserved for graph definition. Stream consumption code is **consumer-side** — place it anywhere else (additional cast module, external runtime/API module, script, test). Model definitions with tag configuration live in `casts/{cast_name}/modules/models.py` — explicit paths shown on each block.

## Contents

- Filter by Projection
- Filter by Message Node
- Filter by Subgraph / Subagent Name
- Filter by LLM Tag
- Suppress Output (nostream)
- Combined Filters

## Filter by Projection

The first level of filtering is the projection itself — only iterate what you need:

```python
graph = {{ cookiecutter.cast_snake }}_graph()

stream = await graph.astream_events(inputs, config=config, version="v3")

# Only LLM tokens
async for message in stream.messages:
    async for token in message.text:
        print(token, end="", flush=True)

# Only tool execution
async for call in stream.tool_calls:
    print(call.tool_name, call.input)

# Only subagents
async for subagent in stream.subagents:
    print(subagent.name)
```

---

## Filter by Message Node

`message.node` identifies the graph node that invoked the LLM:

```python
stream = await graph.astream_events(inputs, config=config, version="v3")

async for message in stream.messages:
    # Only tokens from the "model" node (agent graphs)
    if message.node != "model":
        continue
    async for token in message.text:
        print(token, end="", flush=True)
```

For custom StateGraph, filter by your `add_node("YourNodeName", ...)` name.

---

## Filter by Subgraph / Subagent Name

```python
stream = await graph.astream_events(inputs, config=config, version="v3")

# Specific subgraph
async for subgraph in stream.subgraphs:
    if subgraph.graph_name != "researcher":
        continue
    async for message in subgraph.messages:
        async for token in message.text:
            print(token, end="", flush=True)

# Specific delegated subagent (Deep Agents only)
async for subagent in stream.subagents:
    if subagent.name != "writer":
        continue
    async for message in subagent.messages:
        print(message.text)
```

---

## Filter by LLM Tag

Tag models during initialization (in the cast's model module), then filter by tag on the finalized message output (in the stream consumer):

```python
# casts/{cast_name}/modules/models.py
from langchain.chat_models import init_chat_model


def get_primary_model():
    return init_chat_model("openai:gpt-5.4", tags=["primary"])
```

```python
# stream consumer — location flexible
stream = await graph.astream_events(inputs, config=config, version="v3")

async for message in stream.messages:
    # `message.output` is the finalized AIMessage with run metadata
    tags = (message.output.response_metadata or {}).get("tags", [])
    if "primary" in tags:
        async for token in message.text:
            print(token, end="", flush=True)
```

---

## Suppress Output (nostream)

`langgraph.constants.TAG_NOSTREAM` excludes a model's tokens from `stream.messages` entirely. The model still runs and produces output; tokens are simply not emitted to the projection:

```python
# casts/{cast_name}/modules/models.py
from langchain.chat_models import init_chat_model
from langgraph.constants import TAG_NOSTREAM, TAG_HIDDEN


def get_background_model():
    # TAG_NOSTREAM ("nostream") — suppresses message stream for this model
    return init_chat_model("openai:gpt-5.4-mini", tags=[TAG_NOSTREAM])


def get_internal_node_model():
    # TAG_HIDDEN ("langsmith:hidden") — hides the node from chain events entirely
    return init_chat_model("openai:gpt-5.4-mini", tags=[TAG_HIDDEN])
```

Use cases:
- Internal-only LLM calls (structured-output generation, classification) that shouldn't stream to the client
- Avoiding duplicate output when content is also streamed through a custom channel

---

## Combined Filters

### Root Model Tokens + Subagent Status

```python
import asyncio

stream = await graph.astream_events(inputs, config=config, version="v3")

async def consume_root_tokens():
    async for message in stream.messages:
        if message.node != "model":
            continue
        async for token in message.text:
            print(token, end="", flush=True)

async def consume_subagent_status():
    async for subagent in stream.subagents:
        print(f"\n[{subagent.name}] started ({subagent.path})")
        try:
            _ = await subagent.output
            print(f"[{subagent.name}] completed")
        except Exception as e:
            print(f"[{subagent.name}] failed: {e}")

await asyncio.gather(consume_root_tokens(), consume_subagent_status())
```

### Tagged-Model Tokens from a Specific Subgraph

```python
stream = await graph.astream_events(inputs, config=config, version="v3")

async for subgraph in stream.subgraphs:
    if subgraph.graph_name != "researcher":
        continue
    async for message in subgraph.messages:
        tags = (message.output.response_metadata or {}).get("tags", [])
        if "primary" not in tags:
            continue
        async for token in message.text:
            print(token, end="")
```
