---
name: modules-integration
description: Integrate LangChain components (models, prompts, tools, agents). Use when adding LLMs, creating tools, using chains, or integrating LangChain modules in Act projects.
---

# Modules Integration

## Overview

Act Casts organize LangChain components into module files under `modules/`. This skill provides guidance for integrating models, prompts, tools, and agents effectively.

## When to Use This Skill

- Adding LLM models to nodes
- Creating or using tools
- Writing prompt templates
- Building agents
- Creating routing functions

## Module Selection Guide

**Required modules**:
- `state.py` - State schemas (always required)
- `nodes.py` - Node implementations (always required)

**Optional modules** (add as needed):
- `models.py` - LLM and embedding models
- `prompts.py` - Prompt templates
- `tools.py` - Tool definitions
- `agents.py` - Agent builders
- `conditions.py` - Routing functions
- `utils.py` - Helper functions

## Integration Workflow

### 1. Set Up Models

```python
# modules/models.py
from langchain.chat_models import init_chat_model

def get_primary_model():
    return init_chat_model(model="gpt-4", model_provider="openai")
```

### 2. Create Prompts

```python
# modules/prompts.py
from langchain.prompts import ChatPromptTemplate

def get_chat_prompt():
    return ChatPromptTemplate.from_messages([
        ("system", "You are helpful."),
        ("human", "{query}")
    ])
```

### 3. Define Tools

```python
# modules/tools.py
from langchain.tools import tool

@tool
def search_web(query: str) -> str:
    """Search the web."""
    return perform_search(query)
```

### 4. Use in Nodes

```python
# modules/nodes.py
from casts.base_node import BaseNode
from .models import get_primary_model
from .prompts import get_chat_prompt

class ChatNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = get_primary_model()
        self.prompt = get_chat_prompt()

    def execute(self, state):
        messages = self.prompt.format_messages(query=state.query)
        response = self.model.invoke(messages)
        return {"messages": [response]}
```

## Quick Reference

```python
# Models
from langchain.chat_models import init_chat_model
model = init_chat_model(model="gpt-4", model_provider="openai")

# Prompts
from langchain.prompts import ChatPromptTemplate
prompt = ChatPromptTemplate.from_messages([("system", "..."), ("human", "...")])

# Tools
from langchain.tools import tool
@tool
def my_tool(input: str) -> str:
    return process(input)

# Conditions
def route(state):
    return "node_a" if state.category == "A" else "node_b"
```

## Resources

### References
- `references/agents_guide.md` - LangChain agents guide
- `references/tools_guide.md` - Tools and MCP tools
- `references/prompts_guide.md` - Prompt engineering
- `references/models_guide.md` - LLM model configuration
- `references/conditions_guide.md` - Conditional routing
- `references/utils_guide.md` - Utility patterns

### Examples
- `examples/agent_node.py` - Agent with tools
- `examples/tool_node.py` - Tool execution
- `examples/prompt_examples.py` - Prompt templates
- `examples/model_setup.py` - Model configuration

### Official Documentation
- Models: https://docs.langchain.com/oss/python/langchain/models
- Prompts: https://docs.langchain.com/oss/python/langchain/prompts
- Tools: https://docs.langchain.com/oss/python/langchain/tools
- Agents: https://docs.langchain.com/oss/python/langchain/agents
