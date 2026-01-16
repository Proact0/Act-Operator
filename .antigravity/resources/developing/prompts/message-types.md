# Message Types

Message objects represent conversation context for LLM interactions in LangGraph.

## Contents

- SystemMessage
- HumanMessage
- AIMessage
- ToolMessage
- Common Patterns

---

## SystemMessage

Set model behavior and role. Define in `modules/prompts.py`.

```python
# casts/{cast_name}/modules/prompts.py
from langchain.messages import SystemMessage

ASSISTANT_PROMPT = SystemMessage("You are a helpful coding assistant.")

CODE_REVIEWER_PROMPT = SystemMessage("""
You are a senior Python developer with expertise in LangGraph.
- Provide specific code examples
- Explain reasoning clearly
- Focus on best practices
""")
```

**Usage in nodes:**

```python
# casts/{cast_name}/modules/nodes.py
from langchain.messages import HumanMessage
from .prompts import ASSISTANT_PROMPT

class AgentNode(BaseNode):
    def execute(self, state):
        messages = [ASSISTANT_PROMPT, HumanMessage(state["input"])]
        response = self.agent.invoke(messages)
        return {"response": response.content}
```

---

## HumanMessage

Represents user input.

```python
# casts/{cast_name}/modules/nodes.py
from langchain.messages import HumanMessage

# Simple text
msg = HumanMessage("What is machine learning?")

# With metadata
msg = HumanMessage(
    content="Hello!",
    name="alice",  # User identifier
    id="msg_123"   # Message ID
)

# String shortcut
response = model.invoke("Hello")  # Equivalent to HumanMessage("Hello")
```

**In state schema:**

```python
# casts/{cast_name}/modules/state.py
from typing import Annotated
from typing_extensions import TypedDict
from langchain.messages import BaseMessage
from langgraph.graph import add_messages

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_input: str
```

---

## AIMessage

Model response with content, tool calls, and metadata. Returned by `model.invoke()`.

```python
# casts/{cast_name}/modules/nodes.py
from .agents import agent

class ChatNode(BaseNode):
    def execute(self, state):
        response = agent.invoke(state["messages"])
        # response is AIMessage
        return {"messages": [response]}
```

**Access attributes:**

```python
# casts/{cast_name}/modules/nodes.py
response = model.invoke("Hello")

# Content
text = response.content  # or response.text

# Tool calls
if response.tool_calls:
    for tool_call in response.tool_calls:
        name = tool_call["name"]
        args = tool_call["args"]
        call_id = tool_call["id"]

# Token usage
if response.usage_metadata:
    tokens = response.usage_metadata["total_tokens"]
```

**Manual creation:**

Useful for few-shot examples or conversation history.

```python
# casts/{cast_name}/modules/prompts.py
from langchain.messages import SystemMessage, HumanMessage, AIMessage

FEW_SHOT_EXAMPLES = [
    SystemMessage("You are a poet."),
    HumanMessage("Write a haiku about code"),
    AIMessage("Functions compile\nVariables hold secrets\nBugs flee in night"),
]
```

```python
# casts/{cast_name}/modules/nodes.py
from .prompts import FEW_SHOT_EXAMPLES

class PoetNode(BaseNode):
    def execute(self, state):
        messages = FEW_SHOT_EXAMPLES + [HumanMessage(state["request"])]
        response = self.agent.invoke(messages)
        return {"poem": response.content}
```

---

## ToolMessage

Return tool execution results to model. Must match tool call ID.

```python
# casts/{cast_name}/modules/nodes.py
from langchain.messages import ToolMessage

class ToolExecutorNode(BaseNode):
    def execute(self, state):
        last_message = state["messages"][-1]
        tool_messages = []

        for tool_call in last_message.tool_calls:
            # Execute tool
            result = self._execute_tool(tool_call["name"], tool_call["args"])

            # Create ToolMessage
            tool_msg = ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"]  # Must match
            )
            tool_messages.append(tool_msg)

        return {"messages": tool_messages}
```

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| content | str | Tool result (stringified) |
| tool_call_id | str | Must match AIMessage tool_call["id"] |

**With artifact:**

Store metadata not sent to model.

```python
# casts/{cast_name}/modules/nodes.py
from langchain.messages import ToolMessage

class SearchNode(BaseNode):
    def execute(self, state):
        tool_call = state["messages"][-1].tool_calls[0]
        result = self._search(tool_call["args"]["query"])

        tool_msg = ToolMessage(
            content=result["text"],  # Sent to model
            tool_call_id=tool_call["id"],
            artifact={  # Not sent to model
                "document_id": result["doc_id"],
                "score": result["relevance"]
            }
        )
        return {"messages": [tool_msg]}
```

Access artifacts downstream:

```python
# casts/{cast_name}/modules/nodes.py
class RenderNode(BaseNode):
    def execute(self, state):
        tool_msgs = [m for m in state["messages"] if isinstance(m, ToolMessage)]
        sources = [msg.artifact["source"] for msg in tool_msgs if msg.artifact]
        return {"sources": sources}
```

---

## Common Patterns

**Conversation history:**

```python
# casts/{cast_name}/modules/nodes.py
from .prompts import SYSTEM_PROMPT

class ChatNode(BaseNode):
    def execute(self, state):
        messages = [SYSTEM_PROMPT] + state["messages"]
        response = self.agent.invoke(messages)
        return {"messages": [response]}
```

**Message filtering:**

```python
# casts/{cast_name}/modules/nodes.py
from langchain.messages import HumanMessage, AIMessage

class SummarizeNode(BaseNode):
    def execute(self, state):
        # Get only user/assistant messages
        conversation = [
            m for m in state["messages"]
            if isinstance(m, (HumanMessage, AIMessage))
        ]
        summary = self.model.invoke(f"Summarize: {conversation}")
        return {"summary": summary.content}
```
