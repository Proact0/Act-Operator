---
name: modules-integration
description: Integrate LangChain components (models, prompts, tools, agents) - use when adding LLMs, creating tools, using chains, or integrating LangChain modules.
---

# Modules Integration

**Use this skill when:**
- Adding LLM models to nodes
- Creating or using tools
- Writing prompt templates
- Building agents
- Using chains
- Creating conditional routing functions
- Adding utility functions

## Overview

Act Casts organize LangChain components into module files under `modules/`. These modules contain reusable pieces (models, prompts, tools, etc.) that nodes use to implement functionality.

**Module structure:**
- `state.py` - **Required**: State schemas
- `nodes.py` - **Required**: Node implementations
- `models.py` - **Optional**: LLM and embedding models
- `prompts.py` - **Optional**: Prompt templates
- `tools.py` - **Optional**: Tool definitions
- `agents.py` - **Optional**: Agent builders
- `conditions.py` - **Optional**: Routing functions
- `utils.py` - **Optional**: Helper functions

## Models (`models.py`)

### Basic Model Setup

```python
"""Model configuration for Cast."""

from langchain.chat_models import init_chat_model

def get_primary_model():
    """Get primary chat model."""
    return init_chat_model(
        model="gpt-4",
        model_provider="openai"
    )

def get_fast_model():
    """Get fast model for simple tasks."""
    return init_chat_model(
        model="gpt-3.5-turbo",
        model_provider="openai"
    )
```

### With Environment Variables

```python
import os
from langchain_openai import ChatOpenAI

def get_model():
    """Get model from environment config."""
    return ChatOpenAI(
        model=os.getenv("MODEL_NAME", "gpt-4"),
        temperature=float(os.getenv("TEMPERATURE", "0.7")),
        api_key=os.getenv("OPENAI_API_KEY")
    )
```

### Multiple Model Providers

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

def get_openai_model():
    return ChatOpenAI(model="gpt-4")

def get_claude_model():
    return ChatAnthropic(model="claude-3-sonnet-20240229")

def get_gemini_model():
    return ChatGoogleGenerativeAI(model="gemini-1.5-pro")

def get_model(provider="openai"):
    """Get model by provider."""
    models = {
        "openai": get_openai_model,
        "anthropic": get_claude_model,
        "google": get_gemini_model
    }
    return models[provider]()
```

### Using in Nodes

```python
from casts.my_cast.modules.models import get_primary_model

class ChatNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = get_primary_model()

    def execute(self, state):
        response = self.model.invoke(state.messages)
        return {"messages": [response]}
```

## Prompts (`prompts.py`)

### Simple Prompt Template

```python
"""Prompt templates for Cast."""

from langchain.prompts import PromptTemplate

def get_query_prompt():
    """Get query processing prompt."""
    return PromptTemplate(
        template="Process this query: {query}\n\nProvide a helpful response.",
        input_variables=["query"]
    )
```

### Chat Prompt Template

```python
from langchain.prompts import ChatPromptTemplate

def get_chat_prompt():
    """Get chat prompt with system message."""
    return ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. {context}"),
        ("human", "{query}")
    ])

def get_few_shot_prompt():
    """Get few-shot prompt."""
    return ChatPromptTemplate.from_messages([
        ("system", "You are an expert classifier."),
        ("human", "Python code"),
        ("ai", "programming"),
        ("human", "Weather forecast"),
        ("ai", "weather"),
        ("human", "{input}")
    ])
```

### Structured Output Prompt

```python
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class Classification(BaseModel):
    category: str = Field(description="Category name")
    confidence: float = Field(description="Confidence score 0-1")
    reasoning: str = Field(description="Reasoning for classification")

def get_structured_prompt():
    """Get prompt for structured output."""
    return ChatPromptTemplate.from_messages([
        ("system", "Classify the input into categories."),
        ("human", "{input}")
    ])
```

### Using in Nodes

```python
from casts.my_cast.modules.prompts import get_chat_prompt
from casts.my_cast.modules.models import get_primary_model

class PromptNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = get_primary_model()
        self.prompt = get_chat_prompt()

    def execute(self, state):
        # Format prompt
        messages = self.prompt.format_messages(
            context="Be concise and accurate.",
            query=state.query
        )

        # Invoke model
        response = self.model.invoke(messages)

        return {"messages": [response]}
```

## Tools (`tools.py`)

### Basic Tool

```python
"""Tools for Cast."""

from langchain.tools import tool

@tool
def search_web(query: str) -> str:
    """Search the web for information.

    Args:
        query: Search query

    Returns:
        Search results
    """
    # Implement search logic
    results = perform_search(query)
    return results

@tool
def calculate(expression: str) -> float:
    """Calculate mathematical expression.

    Args:
        expression: Math expression (e.g., "2 + 2")

    Returns:
        Calculation result
    """
    return eval(expression)  # Use safely in production!
```

### Structured Tool

```python
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(description="Search query")
    max_results: int = Field(default=5, description="Max results")

def search_function(query: str, max_results: int = 5) -> str:
    """Perform search."""
    # Implementation
    return f"Found {max_results} results for: {query}"

search_tool = StructuredTool.from_function(
    func=search_function,
    name="search",
    description="Search for information",
    args_schema=SearchInput
)
```

### Tool List

```python
from langchain.tools import tool

@tool
def get_weather(location: str) -> str:
    """Get weather for location."""
    return f"Weather in {location}: Sunny, 72°F"

@tool
def get_time() -> str:
    """Get current time."""
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")

@tool
def search_docs(query: str) -> str:
    """Search documentation."""
    return f"Documentation for: {query}"

# Export tool list
all_tools = [get_weather, get_time, search_docs]
```

### Using Tools in Nodes

```python
from casts.my_cast.modules.tools import all_tools
from casts.my_cast.modules.models import get_primary_model

class AgentNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = get_primary_model()
        self.agent = self.model.bind_tools(all_tools)

    def execute(self, state):
        # Agent automatically calls tools as needed
        response = self.agent.invoke(state.messages)
        return {"messages": [response]}
```

## Agents (`agents.py`)

### Basic Agent

```python
"""Agents for Cast."""

from langchain.agents import create_react_agent
from langchain.prompts import PromptTemplate

def create_search_agent(model, tools):
    """Create ReAct agent."""
    prompt = PromptTemplate.from_template(
        "Answer the following question: {input}\n\n"
        "You have access to these tools:\n{tools}\n\n"
        "Use this format:\n"
        "Thought: [your reasoning]\n"
        "Action: [tool name]\n"
        "Action Input: [input]\n"
        "Observation: [result]\n"
        "...\n"
        "Final Answer: [answer]"
    )

    return create_react_agent(
        llm=model,
        tools=tools,
        prompt=prompt
    )
```

### Tool Calling Agent

```python
from langchain.agents import AgentExecutor
from casts.my_cast.modules.models import get_primary_model
from casts.my_cast.modules.tools import all_tools

def create_tool_agent():
    """Create tool-calling agent."""
    model = get_primary_model()

    # Bind tools to model
    model_with_tools = model.bind_tools(all_tools)

    # Create executor
    agent = AgentExecutor(
        agent=model_with_tools,
        tools=all_tools,
        verbose=True
    )

    return agent
```

### Using Agents in Nodes

```python
from casts.my_cast.modules.agents import create_tool_agent

class AgentNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.agent = create_tool_agent()

    def execute(self, state):
        # Agent handles tool calling automatically
        result = self.agent.invoke({
            "input": state.query,
            "chat_history": state.messages
        })

        return {"result": result["output"]}
```

## Conditions (`conditions.py`)

### Basic Condition

```python
"""Conditional routing functions for Cast."""

def route_by_category(state):
    """Route based on category."""
    if state.category == "math":
        return "math_solver"
    elif state.category == "search":
        return "web_search"
    else:
        return "general_qa"
```

### Complex Routing

```python
from langgraph.graph import END

def should_continue_loop(state):
    """Decide whether to continue loop."""
    # Check completion
    if state.complete:
        return END

    # Check max iterations
    if state.iterations >= state.max_iterations:
        return END

    # Check errors
    if state.error_count > 3:
        return "error_handler"

    # Continue processing
    return "process"
```

### Message-Based Routing

```python
def route_agent(state):
    """Route based on last message."""
    last_message = state.messages[-1]

    # Check for tool calls
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"

    # Check if response is complete
    if "FINAL ANSWER:" in last_message.content:
        return END

    # Continue agent loop
    return "agent"
```

### Using in Graph

```python
from casts.my_cast.modules.conditions import route_by_category

class MyGraph(BaseGraph):
    def build(self):
        builder = StateGraph(State)

        # Add nodes...

        # Use condition function
        builder.add_conditional_edges(
            "classifier",
            route_by_category,
            {
                "math_solver": "math_solver",
                "web_search": "web_search",
                "general_qa": "general_qa"
            }
        )

        return builder.compile()
```

## Chains

### Basic Chain

```python
from langchain.chains import LLMChain
from casts.my_cast.modules.models import get_primary_model
from casts.my_cast.modules.prompts import get_query_prompt

def create_query_chain():
    """Create query processing chain."""
    model = get_primary_model()
    prompt = get_query_prompt()

    chain = LLMChain(
        llm=model,
        prompt=prompt
    )

    return chain
```

### LCEL Chain

```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from casts.my_cast.modules.models import get_primary_model
from casts.my_cast.modules.prompts import get_chat_prompt

def create_lcel_chain():
    """Create LCEL chain."""
    model = get_primary_model()
    prompt = get_chat_prompt()
    parser = StrOutputParser()

    chain = (
        {
            "context": RunnablePassthrough(),
            "query": RunnablePassthrough()
        }
        | prompt
        | model
        | parser
    )

    return chain
```

### Using Chains in Nodes

```python
from casts.my_cast.modules.chains import create_query_chain

class ChainNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chain = create_query_chain()

    def execute(self, state):
        result = self.chain.invoke({"query": state.query})
        return {"result": result}
```

## Utils (`utils.py`)

### Helper Functions

```python
"""Utility functions for Cast."""

def format_messages(messages):
    """Format messages for display."""
    formatted = []
    for msg in messages:
        formatted.append(f"{msg.type}: {msg.content}")
    return "\n".join(formatted)

def extract_text(messages):
    """Extract text from messages."""
    return " ".join(msg.content for msg in messages)

def count_tokens(text, encoding="cl100k_base"):
    """Count tokens in text."""
    import tiktoken
    enc = tiktoken.get_encoding(encoding)
    return len(enc.encode(text))
```

### Validation Utilities

```python
def validate_email(email: str) -> bool:
    """Validate email format."""
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def validate_url(url: str) -> bool:
    """Validate URL format."""
    import re
    pattern = r'^https?://[\w\.-]+\.\w+'
    return bool(re.match(pattern, url))

def sanitize_input(text: str) -> str:
    """Sanitize user input."""
    # Remove dangerous characters
    dangerous = ['<', '>', '&', '"', "'"]
    for char in dangerous:
        text = text.replace(char, '')
    return text.strip()
```

### Using Utils in Nodes

```python
from casts.my_cast.modules.utils import validate_email, sanitize_input

class ValidationNode(BaseNode):
    def execute(self, state):
        # Sanitize input
        clean_input = sanitize_input(state.user_input)

        # Validate
        if state.email and not validate_email(state.email):
            return {"error": "Invalid email format"}

        return {"validated_input": clean_input}
```

## Best Practices

### 1. Keep Modules Focused

```python
# ✅ Good: Each module has clear purpose
# models.py - Model configuration
# prompts.py - Prompt templates
# tools.py - Tool definitions

# ❌ Bad: Everything in one file
# utils.py with models, prompts, tools, etc.
```

### 2. Use Factory Functions

```python
# ✅ Good: Factory function
def get_model():
    return ChatOpenAI(model="gpt-4")

# ❌ Bad: Global instance
model = ChatOpenAI(model="gpt-4")
```

### 3. Document Module Functions

```python
def get_classification_prompt():
    """Get prompt for text classification.

    Returns:
        ChatPromptTemplate: Prompt for classification task

    Example:
        >>> prompt = get_classification_prompt()
        >>> messages = prompt.format_messages(text="Hello")
    """
    return ChatPromptTemplate.from_messages([...])
```

### 4. Keep Tools Simple

```python
# ✅ Good: Simple, focused tool
@tool
def get_weather(location: str) -> str:
    """Get weather for location."""
    return fetch_weather(location)

# ❌ Bad: Complex tool with many responsibilities
@tool
def do_everything(input: str) -> str:
    """Does weather, search, calculation, etc."""
    # Too much responsibility
```

### 5. Reuse Components

```python
# ✅ Good: Reuse across nodes
# models.py
model = get_primary_model()

# node_a.py
class NodeA(BaseNode):
    def __init__(self):
        self.model = get_primary_model()

# node_b.py
class NodeB(BaseNode):
    def __init__(self):
        self.model = get_primary_model()
```

### 6. Handle Errors Gracefully

```python
@tool
def risky_operation(input: str) -> str:
    """Perform risky operation."""
    try:
        return perform_operation(input)
    except ValueError as e:
        return f"Error: Invalid input - {e}"
    except Exception as e:
        return f"Error: Operation failed - {e}"
```

## Module Organization

### Small Cast (Single file)

```
modules/
├── __init__.py
├── state.py          # Required
├── nodes.py          # Required
└── models.py         # Optional: All other components here
```

### Medium Cast (Organized)

```
modules/
├── __init__.py
├── state.py          # State schemas
├── nodes.py          # Node classes
├── models.py         # LLM models
├── prompts.py        # Prompt templates
└── tools.py          # Tool definitions
```

### Large Cast (Comprehensive)

```
modules/
├── __init__.py
├── state.py          # State schemas
├── nodes.py          # Node classes
├── models.py         # LLM models
├── prompts.py        # Prompt templates
├── tools.py          # Tool definitions
├── agents.py         # Agent builders
├── conditions.py     # Routing functions
└── utils.py          # Helper functions
```

## Quick Reference

```python
# Models
from langchain.chat_models import init_chat_model
def get_model():
    return init_chat_model(model="gpt-4", model_provider="openai")

# Prompts
from langchain.prompts import ChatPromptTemplate
def get_prompt():
    return ChatPromptTemplate.from_messages([
        ("system", "You are helpful."),
        ("human", "{query}")
    ])

# Tools
from langchain.tools import tool
@tool
def my_tool(input: str) -> str:
    """Tool description."""
    return process(input)

# Conditions
def route(state):
    if state.category == "A":
        return "node_a"
    return "node_b"

# Using in nodes
from casts.my_cast.modules.models import get_model
from casts.my_cast.modules.prompts import get_prompt

class MyNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = get_model()
        self.prompt = get_prompt()

    def execute(self, state):
        messages = self.prompt.format_messages(query=state.query)
        response = self.model.invoke(messages)
        return {"messages": [response]}
```

## Related Skills

- **node-implementation**: Using modules in nodes
- **graph-composition**: Using conditions in graphs
- **state-management**: State schemas for modules
- **cast-development**: Overall module organization

## References

**Official documentation:**
- Models: https://docs.langchain.com/oss/python/langchain/models
- Prompts: https://docs.langchain.com/oss/python/langchain/prompts
- Tools: https://docs.langchain.com/oss/python/langchain/tools
- Agents: https://docs.langchain.com/oss/python/langchain/agents
- Chains: https://docs.langchain.com/oss/python/langchain/chains
